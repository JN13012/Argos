import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock
from uuid import UUID, uuid4

import httpx
import pytest

from argos import cli
from argos.osint.connectors import SireneConnector
from argos.osint.models import (
    CoverageStatus,
    Entity,
    EntityType,
    Identifier,
    Observation,
    SearchScope,
    SearchStatus,
)
from argos.osint.storage import SQLiteStorage

QUERY = (
    "periode(activitePrincipaleEtablissement:45.20A) AND codeCommuneEtablissement:13055"
)


def arguments(path: Path) -> list[str]:
    return [
        "osint",
        "discover",
        "--activity",
        "garage automobile",
        "--location",
        "Marseille",
        "--query",
        QUERY,
        "--max-pages",
        "2",
        "--db",
        str(path),
    ]


def search_id(output: str) -> UUID:
    match = re.search(r"Search ID: ([0-9a-f-]+)", output)
    assert match is not None
    return UUID(match.group(1))


@pytest.fixture
def connector(monkeypatch: pytest.MonkeyPatch) -> Mock:
    mocked = Mock(spec=SireneConnector)
    monkeypatch.setattr(cli, "SireneConnector", lambda: mocked)
    return mocked


def test_parser_accepts_discovery_options(tmp_path: Path) -> None:
    path = tmp_path / "chosen.sqlite3"
    parsed = cli.build_parser().parse_args(arguments(path))

    assert parsed.activity == "garage automobile"
    assert parsed.location == "Marseille"
    assert parsed.query == QUERY
    assert parsed.max_pages == 2
    assert parsed.db == str(path)
    defaults = cli.build_parser().parse_args(arguments(path)[:-4])
    assert defaults.max_pages == 5
    assert defaults.db == ".argos/osint/argos.sqlite3"


def test_cli_runs_engine_and_displays_persisted_results(
    tmp_path: Path,
    connector: Mock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = tmp_path / "chosen.sqlite3"
    old_time = datetime(2020, 1, 1, tzinfo=UTC)
    known = Entity(uuid4(), EntityType.ESTABLISHMENT, "Old name", old_time, old_time)
    with SQLiteStorage(path) as storage:
        storage.save_entity(known)
        storage.add_identifier(
            Identifier(known.id, "siret", "12345678900012", "fixture")
        )
        storage.add_observation(
            Observation(uuid4(), known.id, "activity", "45.20B", "fixture", old_time)
        )
    connector.search_establishments.return_value = {
        "header": {"curseur": "*", "curseurSuivant": "*"},
        "etablissements": [
            {
                "siret": siret,
                "siren": "123456789",
                "uniteLegale": {"denominationUniteLegale": name},
                "adresseEtablissement": {
                    "numeroVoieEtablissement": "12",
                    "typeVoieEtablissement": "RUE",
                    "libelleVoieEtablissement": "DU PORT",
                    "codePostalEtablissement": "13001",
                    "libelleCommuneEtablissement": "MARSEILLE",
                },
                "periodesEtablissement": [
                    {
                        "dateFin": None,
                        "activitePrincipaleEtablissement": "45.20A",
                        "etatAdministratifEtablissement": "A",
                    }
                ],
            }
            for siret, name in (
                ("12345678900012", "GARAGE MARTIN"),
                ("12345678900013", "AUTO SERVICE MARSEILLE"),
            )
        ],
    }

    assert cli.main(arguments(path)) == 0

    captured = capsys.readouterr()
    assert captured.err == ""
    for expected in (
        "GARAGE MARTIN",
        "AUTO SERVICE MARSEILLE",
        "SIRET: 12345678900012",
        "SIREN: 123456789",
        "Status: completed",
        "Created: 1",
        "Reused: 1",
        "Records: 2",
        "Pages: 1",
        "Coverage: complete_for_source",
        "Activity: 45.20A",
        "Address:",
        "MARSEILLE",
        "Administrative status: A",
    ):
        assert expected in captured.out
    assert "45.20B" not in captured.out
    assert "12 RUE DU PORT" in captured.out
    assert "13001 MARSEILLE" in captured.out
    assert "libelleCommuneEtablissement" not in captured.out
    connector.search_establishments.assert_called_once_with(query=QUERY, cursor="*")
    with SQLiteStorage(path) as storage:
        search = storage.get_search(search_id(captured.out))
        assert search is not None
        assert search.scope == SearchScope("garage automobile", "Marseille")
        assert search.query == QUERY
        assert search.status is SearchStatus.COMPLETED
        results = storage.get_search_results(search.id)
        assert len(results) == 2
        assert known.id in {result.entity_id for result in results}


def test_cli_honors_page_limit_and_displays_truncation(
    tmp_path: Path,
    connector: Mock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = tmp_path / "limited.sqlite3"
    argv = arguments(path)
    argv[argv.index("--max-pages") + 1] = "1"
    connector.search_establishments.return_value = {
        "header": {"curseur": "*", "curseurSuivant": "next"},
        "etablissements": [{"siret": "12345678900012"}],
    }

    assert cli.main(argv) == 0

    captured = capsys.readouterr()
    assert "Status: partial" in captured.out
    assert "Coverage: truncated" in captured.out
    assert captured.err == ""
    connector.search_establishments.assert_called_once_with(query=QUERY, cursor="*")


@pytest.mark.parametrize("partial", [False, True])
def test_api_error_has_nonzero_exit_and_persisted_coverage(
    tmp_path: Path,
    connector: Mock,
    capsys: pytest.CaptureFixture[str],
    partial: bool,
) -> None:
    path = tmp_path / "errors.sqlite3"
    response = httpx.Response(
        503, request=httpx.Request("GET", "https://api.insee.fr/api-sirene/3.11/siret")
    )
    error = httpx.HTTPStatusError(
        "503 Service Unavailable", request=response.request, response=response
    )
    connector.search_establishments.side_effect = (
        [
            {
                "header": {"curseur": "*", "curseurSuivant": "next"},
                "etablissements": [{"siret": "12345678900012"}],
            },
            error,
        ]
        if partial
        else error
    )

    assert cli.main(arguments(path)) != 0

    captured = capsys.readouterr()
    assert "503 Service Unavailable" in captured.err
    assert "Traceback" not in captured.err
    with SQLiteStorage(path) as storage:
        search = storage.get_search(search_id(captured.out))
        assert search is not None
        assert search.status is (
            SearchStatus.PARTIAL if partial else SearchStatus.FAILED
        )
        coverage = storage.get_coverage(search.id, "sirene")
        assert coverage is not None
        assert coverage.status is (
            CoverageStatus.PARTIAL if partial else CoverageStatus.FAILED
        )
        assert coverage.errors == ["HTTPStatusError: 503 Service Unavailable"]
        assert len(storage.get_search_results(search.id)) == int(partial)


def test_missing_api_key_fails_before_network_call(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.delenv("INSEE_API_KEY", raising=False)

    def unexpected_request(*args: object, **kwargs: object) -> None:
        pytest.fail("Missing API key must not trigger a network call")

    monkeypatch.setattr(httpx, "get", unexpected_request)
    assert cli.main(arguments(tmp_path / "missing-key.sqlite3")) != 0
    captured = capsys.readouterr()
    assert "INSEE_API_KEY is required" in captured.err
    assert "Status: failed" in captured.out


@pytest.mark.parametrize(
    "argv",
    [
        ["osint", "discover"],
        ["osint", "unknown"],
        [
            "osint",
            "discover",
            "--activity",
            "garage",
            "--location",
            "Marseille",
            "--query",
            QUERY,
            "--max-pages",
            "invalid",
        ],
    ],
)
def test_invalid_arguments_are_handled_by_argparse(
    argv: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit) as raised:
        cli.main(argv)
    assert raised.value.code == 2
    assert "error:" in capsys.readouterr().err


def test_module_entrypoint_displays_help_without_running_discovery() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "argos", "osint", "discover", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    for option in ("--activity", "--location", "--query", "--max-pages", "--db"):
        assert option in result.stdout
