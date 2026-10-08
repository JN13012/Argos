import json
from pathlib import Path

import pytest
from pydantic import TypeAdapter
from sqlalchemy import inspect, select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from argos.cli import main
from argos.discovery.enrichment import WebEnricher
from argos.discovery.models import DiscoveryResult, ProviderError, SearchQuery, WebsiteHint
from argos.discovery.providers import FixtureProvider, FrenchCompanyProvider
from argos.discovery.repository import SearchRecord, SQLiteRepository
from argos.discovery.service import DiscoveryService
from conftest import COLLECTED, ROOT, response


@pytest.fixture
def result(http_factory):
    fixtures = ROOT / "examples/discovery"
    payload = json.loads((fixtures / "companies.json").read_text())
    pages = json.loads((fixtures / "pages.json").read_text())
    hints = TypeAdapter(list[WebsiteHint]).validate_json((fixtures / "website-hints.json").read_bytes())
    def handler(request):
        key = f'{request.url.scheme}://{request.headers["host"]}{request.url.path}'
        page = pages.get(key, {"status": 503, "body": ""})
        return response(page.get("body", ""), status=page["status"], headers=page.get("headers"))
    engine = WebEnricher(http_factory(handler), clock=lambda: COLLECTED, sleep=lambda _s: None)
    return DiscoveryService(FixtureProvider(payload), engine, clock=lambda: COLLECTED).run(
        SearchQuery(activity="garage automobile", location="Marseille"), hints=hints, source_mode="synthetic_demo")


def test_service_preserves_sources_contacts_and_qualification(result):
    assert len(result.qualifications) == 4
    classical = result.qualifications[1]
    assert classical.business.professional_email == "contact@garage-classique.example"
    assert classical.business.phone == "+33400000000"
    assert classical.business.contact_policy.contact_type == "public_business_contact"
    assert classical.business.contact_policy.do_not_contact is True
    assert classical.business.contact_policy.source == "Public website (passive HTML)"
    assert next(o.raw_value for o in classical.business.observations if o.field == "phone") == ["tel:0400000000"]
    assert classical.scores.website_opportunity_score.value == 55
    assert classical.scores.ai_automation_opportunity_score.value == 40
    assert classical.scores.cybersecurity_opportunity_score.value == 10
    assert any(o.field == "content_sha256" for o in classical.enrichment.observations)
    for item in result.qualifications:
        assert item.business.source_references
        assert item.business.observations
    assert DiscoveryResult.model_validate_json(result.model_dump_json()) == result


def test_sqlite_roundtrip_snapshots_and_transactions(result, tmp_path):
    repository = SQLiteRepository(tmp_path / "discovery.sqlite3")
    try:
        repository.save(result)
        assert repository.load(result.search_id) == result
        assert repository.load("missing") is None
        assert set(inspect(repository.engine).get_table_names()) == {"searches", "businesses", "observations", "enrichment_runs", "scores"}
        with pytest.raises(IntegrityError):
            repository.save(result)
        # The failed duplicate insert cannot leave a partial search or entities.
        assert repository.load(result.search_id) == result
        next_result = result.model_copy(deep=True)
        next_result.search_id = "second-search"
        for item in next_result.qualifications:
            item.enrichment.id += "-second"
        next_result.qualifications[0].business.legal_name = "Later name"
        repository.save(next_result)
        assert repository.load(result.search_id).qualifications[0].business.legal_name != "Later name"
        assert repository.load(next_result.search_id).qualifications[0].business.legal_name == "Later name"
        with Session(repository.engine) as session:
            assert session.scalar(select(func.count()).select_from(SearchRecord)) == 2
    finally:
        repository.close()


def test_repository_never_overwrites_non_sqlite_file(tmp_path):
    path = tmp_path / "input.db"
    path.write_text("input content")
    with pytest.raises(ValueError, match="non-SQLite"):
        SQLiteRepository(path)
    assert path.read_text() == "input content"


def command(tmp_path, *extra):
    return ["discover", "businesses", "--activity", "garage automobile", "--location", "Marseille",
            "--demo", "--database", str(tmp_path / "discovery.sqlite3"), *extra]


def test_cli_demo_complete_offline_path_and_export(tmp_path, capsys):
    output = tmp_path / "result.json"
    assert main(command(tmp_path, "--json", str(output))) == 0
    stdout = capsys.readouterr().out
    assert "Garage Démo Classique" in stdout
    assert "SIRET" in stdout
    assert "potential service opportunities" in stdout
    result = DiscoveryResult.model_validate_json(output.read_bytes())
    assert len(result.qualifications) == 4
    repository = SQLiteRepository(tmp_path / "discovery.sqlite3")
    try:
        assert repository.load(result.search_id) == result
    finally:
        repository.close()


def test_cli_result_limit_and_selected_scores(tmp_path):
    output = tmp_path / "result.json"
    assert main(command(tmp_path, "--limit", "2", "--opportunity", "website", "--json", str(output))) == 0
    result = DiscoveryResult.model_validate_json(output.read_bytes())
    assert len(result.qualifications) == 2
    assert all(item.scores.ai_automation_opportunity_score is None for item in result.qualifications)


def test_cli_skip_web_works_without_network(tmp_path):
    output = tmp_path / "result.json"
    assert main(command(tmp_path, "--skip-web", "--json", str(output))) == 0
    result = DiscoveryResult.model_validate_json(output.read_bytes())
    assert all(item.enrichment.status == "skipped" for item in result.qualifications)
    assert all(not item.enrichment.pages for item in result.qualifications)


@pytest.mark.parametrize("extra", [["--limit", "0"], ["--opportunity", "invalid"], ["--activity", " "],
                                 ["--location", "Lyon"], ["--opportunity", "ai", "--opportunity", "ai"]])
def test_cli_errors_are_clean_and_do_not_create_database(tmp_path, extra, capsys):
    assert main(command(tmp_path, *extra)) == 2
    text = capsys.readouterr()
    assert "Traceback" not in text.err
    assert not (tmp_path / "discovery.sqlite3").exists()


def test_cli_preserves_existing_export_and_inputs(tmp_path, capsys):
    output = tmp_path / "result.json"
    output.write_text("original")
    assert main(command(tmp_path, "--json", str(output))) == 2
    assert output.read_text() == "original"
    assert not (tmp_path / "discovery.sqlite3").exists()
    source = ROOT / "examples/discovery/companies.json"
    before = source.read_bytes()
    assert main(command(tmp_path, "--json", str(source))) == 2
    assert source.read_bytes() == before
    output.unlink()
    assert main(command(tmp_path, "--json", str(tmp_path / "discovery.sqlite3"))) == 2


def test_cli_provider_failure_is_clean_and_never_persisted(tmp_path, capsys, monkeypatch):
    def fail(_self, _query):
        raise ProviderError("Official provider unavailable")
    monkeypatch.setattr(FrenchCompanyProvider, "discover", fail)
    args = [arg for arg in command(tmp_path) if arg != "--demo"]
    assert main(args) == 2
    assert "Official provider unavailable" in capsys.readouterr().err
    assert not (tmp_path / "discovery.sqlite3").exists()


def test_schema_matches_the_public_models():
    schema = json.loads((ROOT / "schemas/discovery.schema.json").read_text())
    assert schema == DiscoveryResult.model_json_schema()
