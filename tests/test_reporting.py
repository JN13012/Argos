import json
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest
from argos import cli
from argos.backend.intel.osint.models import (
    Coverage,
    CoverageStatus,
    Entity,
    EntityType,
    Identifier,
    Observation,
    Search,
    SearchResult,
    SearchScope,
    SearchStatus,
)
from argos.backend.intel.osint.reporting import write_search_report
from argos.backend.intel.osint.storage import SQLiteStorage


def save_fixture(storage: SQLiteStorage) -> tuple[Search, Coverage]:
    start = datetime(2026, 10, 13, 7, tzinfo=UTC)
    search = Search(
        uuid4(),
        SearchScope("garage", "Marseille"),
        "query",
        start,
        start + timedelta(minutes=1),
        SearchStatus.PARTIAL,
    )
    coverage = Coverage(
        search.id, "sirene", CoverageStatus.TRUNCATED, 1, 1, 1, 0, False, True
    )
    storage.save_search(search)
    storage.save_coverage(coverage)
    entity = Entity(uuid4(), EntityType.ESTABLISHMENT, "Later name", start, start)
    storage.save_entity(entity)
    storage.add_identifier(Identifier(entity.id, "siret", "01234567800012", "sirene"))
    storage.add_search_result(SearchResult(search.id, entity.id, "sirene", start))
    for field, value in {
        "name": "GARAGE <script> | [link](https://example.com)",
        "administrative_status": "F",
        "activity": "45.20A",
        "address": json.dumps(
            {
                "libelleVoieEtablissement": "DU PORT",
                "codePostalEtablissement": "13001",
                "libelleCommuneEtablissement": "MARSEILLE",
            }
        ),
    }.items():
        storage.add_observation(
            Observation(uuid4(), entity.id, field, value, "sirene", start)
        )
    storage.add_observation(
        Observation(
            uuid4(),
            entity.id,
            "name",
            "NEWER SEARCH NAME",
            "sirene",
            start + timedelta(days=1),
        )
    )
    return search, coverage


def test_report_preserves_search_facts_and_escapes_source_text(tmp_path: Path) -> None:
    with SQLiteStorage(tmp_path / "data.sqlite3") as storage:
        search, coverage = save_fixture(storage)
        report = write_search_report(storage, search, coverage, tmp_path / "reports")
    text = report.read_text(encoding="utf-8")
    assert (
        report
        == tmp_path / "reports" / "sirene" / "garage-marseille" / "rapport-001.md"
    )
    assert "Résultats partiels" in text and "n'est pas exhaustive" in text
    assert "Fermé" in text and "01234567800012" in text
    assert "DU PORT, 13001 MARSEILLE" in text
    assert "09:00:00 (Europe/Paris)" in text
    assert "NEWER SEARCH NAME" not in text and "Later name" not in text
    assert "<script>" not in text and "&lt;script&gt;" in text
    assert r"\[link\]" in text


def test_report_command_uses_saved_search_without_api_or_env(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    database = tmp_path / "data.sqlite3"
    with SQLiteStorage(database) as storage:
        search, _ = save_fixture(storage)
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("INSEE_API_KEY=must-not-be-loaded\n")
    monkeypatch.delenv("INSEE_API_KEY", raising=False)

    def forbidden(*args: object, **kwargs: object) -> None:
        pytest.fail("Reporting must not load credentials or call SIRENE")

    monkeypatch.setattr(cli, "SireneConnector", forbidden)
    monkeypatch.setattr(cli, "load_dotenv", forbidden)
    assert (
        cli.main(
            ["osint", "report", "--search-id", str(search.id), "--db", str(database)]
        )
        == 0
    )
    assert (tmp_path / "outputs/sirene/garage-marseille/rapport-001.md").is_file()
    output = capsys.readouterr()
    assert "Report:" in output.out and output.err == ""


def test_report_command_does_not_create_missing_database(tmp_path: Path) -> None:
    database = tmp_path / "missing.sqlite3"
    assert (
        cli.main(
            ["osint", "report", "--search-id", str(uuid4()), "--db", str(database)]
        )
        == 1
    )
    assert not database.exists()


def test_new_search_increments_and_reexport_updates_in_named_group(
    tmp_path: Path,
) -> None:
    with SQLiteStorage(tmp_path / "data.sqlite3") as storage:
        search, coverage = save_fixture(storage)
        first = write_search_report(
            storage, search, coverage, tmp_path / "outputs", name="Garages Marseille"
        )
        original = first.read_text(encoding="utf-8")
        # A new execution of the same scope keeps the named folder and its history.
        second_search = replace(search, id=uuid4())
        second_coverage = replace(coverage, search_id=second_search.id)
        storage.save_search(second_search)
        storage.save_coverage(second_coverage)
        second = write_search_report(
            storage, second_search, second_coverage, tmp_path / "outputs"
        )
        assert (
            first.parent
            == second.parent
            == tmp_path / "outputs/sirene/garages-marseille"
        )
        assert first.name == "rapport-001.md" and second.name == "rapport-002.md"
        assert first.read_text(encoding="utf-8") == original
        coverage.pages_processed = 2
        updated = write_search_report(storage, search, coverage, tmp_path / "outputs")
        assert updated == first
        assert "**Pages consultées :** 2" in first.read_text(encoding="utf-8")
        assert len(list(first.parent.glob("rapport-*.md"))) == 2


def test_report_name_is_normalized_and_cannot_escape_output(tmp_path: Path) -> None:
    with SQLiteStorage(tmp_path / "data.sqlite3") as storage:
        search, coverage = save_fixture(storage)
        report = write_search_report(
            storage,
            search,
            coverage,
            tmp_path / "outputs",
            name="../../Réparation / Marseille",
        )
        assert report == tmp_path / "outputs/sirene/reparation-marseille/rapport-001.md"
        with pytest.raises(ValueError, match="Report name"):
            write_search_report(
                storage, search, coverage, tmp_path / "outputs", name="../"
            )
