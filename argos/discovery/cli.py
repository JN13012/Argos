"""Typer discovery commands, imported only when the discovery entry point is used."""

from datetime import datetime
from pathlib import Path
from typing import Annotated

import httpx
from pydantic import TypeAdapter, ValidationError
from sqlalchemy.exc import SQLAlchemyError
import typer

from argos.storage import ValidationError as OutputError, load_document, write_output
from .enrichment import WebEnricher
from .http import PublicHttpClient
from .models import Opportunity, SearchQuery, WebsiteHint
from .providers import FixtureProvider, FrenchCompanyProvider
from .repository import SQLiteRepository
from .service import DiscoveryService


app = typer.Typer(help="Argos Discovery V0 — public business qualification, with conservative potential-opportunity scores",
                  no_args_is_help=True, pretty_exceptions_enable=False)


@app.callback()
def discovery():
    """Discover and qualify public businesses without contacting them."""


def safe_cell(value: str, limit=45) -> str:
    return "".join(c if c.isprintable() else " " for c in value).replace("\u001b", " ")[:limit]


def _display(result):
    typer.echo(f"{'Company':45} {'SIRET':14} {'Website':>7} {'AI':>4} {'Cyber':>5} {'Confidence':>10}")
    for item in result.qualifications:
        scores = item.scores
        numbers = [scores.website_opportunity_score, scores.ai_automation_opportunity_score,
                   scores.cybersecurity_opportunity_score, scores.data_confidence_score]
        values = [str(score.value) if score is not None else '-' for score in numbers]
        identifier = item.business.official_identifiers.get("siret", "-")
        typer.echo(f"{safe_cell(item.business.trading_name or item.business.legal_name):45} {identifier:14} "
                   f"{values[0]:>7} {values[1]:>4} {values[2]:>5} {values[3]:>10}")
    typer.echo("Scores indicate potential service opportunities, not proven needs or vulnerabilities.")
    typer.echo(f"Search: {result.search_id} | mode: {result.source_mode}")
    for warning in result.warnings:
        typer.echo("Warning: " + safe_cell(warning, limit=2000), err=True)


def _protect_paths(database, output, protected):
    paths = [("database", database)] + ([("JSON output", output)] if output is not None else [])
    for label, path in paths:
        if path.is_symlink():
            raise ValueError(label + " must not be a symbolic link")
        for source in protected:
            if (path.resolve() == source.resolve() or
                    path.exists() and source.exists() and path.samefile(source)):
                raise ValueError(label + " must not overwrite an input file")
    if output is not None and (database.resolve() == output.resolve() or
                              database.exists() and output.exists() and database.samefile(output)):
        raise ValueError("Database and JSON output must be different files")
    if output is not None and output.exists():
        raise ValueError("JSON output already exists; choose another path")


@app.command("businesses")
def businesses(
    activity: Annotated[str, typer.Option(help="Activity phrase or NAF Rev.2 code")],
    location: Annotated[str, typer.Option(help="Exact French commune name")],
    opportunity: Annotated[list[Opportunity] | None, typer.Option("--opportunity", help="Repeat to select scores")] = None,
    limit: Annotated[int, typer.Option(min=1, max=100)] = 20,
    json_output: Annotated[Path | None, typer.Option("--json", help="New JSON export file")] = None,
    database: Annotated[Path, typer.Option(help="Local SQLite snapshots")] = Path(".argos/discovery.sqlite3"),
    website_hints: Annotated[Path | None, typer.Option(help="Local SIRET-to-official-website declarations")] = None,
    demo: Annotated[bool, typer.Option(help="Use synthetic companies and mock websites without network access")] = False,
    skip_web: Annotated[bool, typer.Option(help="Skip website enrichment")] = False,
):
    http, repository = None, None
    try:
        query = SearchQuery(activity=activity, location=location, requested_opportunities=opportunity or list(Opportunity), limit=limit)
        protected = [website_hints] if website_hints else []
        fixtures = Path(__file__).resolve().parents[2] / "examples/discovery"
        if demo:
            if website_hints:
                raise ValueError("--demo uses bundled website declarations; omit --website-hints")
            protected.extend([fixtures / "companies.json", fixtures / "website-hints.json", fixtures / "pages.json"])
        _protect_paths(database, json_output, protected)
        if demo:
            payload = load_document(fixtures / "companies.json")
            hints = TypeAdapter(list[WebsiteHint]).validate_python(load_document(fixtures / "website-hints.json"))
            pages = load_document(fixtures / "pages.json")

            def handler(request):
                scheme, host, path = request.url.scheme, request.headers["host"], request.url.path
                key = f"{scheme}://{host}{path}"
                page = pages.get(key)
                if page is None:
                    raise httpx.ConnectError("Synthetic inaccessible website", request=request)
                return httpx.Response(page["status"], headers=page.get("headers", {}),
                                      stream=httpx.ByteStream(page.get("body", "").encode()))

            http = PublicHttpClient(transport=httpx.MockTransport(handler), resolver=lambda _host, _port: "93.184.216.34")
            provider = FixtureProvider(payload)
            clock = lambda: datetime.fromisoformat("2026-10-08T00:00:00+00:00")
            enricher = WebEnricher(http, clock=clock, sleep=lambda _seconds: None)
        else:
            hints = TypeAdapter(list[WebsiteHint]).validate_python(load_document(website_hints)) if website_hints else []
            http = PublicHttpClient()
            provider = FrenchCompanyProvider(http)
            enricher = WebEnricher(http)
            from .models import utc_now
            clock = utc_now
        result = DiscoveryService(provider, enricher, clock=clock).run(
            query, hints=hints, skip_web=skip_web, source_mode="synthetic_demo" if demo else "official_api")
        repository = SQLiteRepository(database)
        repository.save(result)
        if json_output:
            # Atomic export; never silently replace a source or earlier result.
            write_output(json_output, result.model_dump_json(indent=2) + "\n", protected=[database, *protected])
        _display(result)
        typer.echo(f"Stored in {database}" + (f" | JSON: {json_output}" if json_output else ""))
    except (ValueError, ValidationError, OutputError) as exc:
        typer.echo(f"argos discover: {str(exc)}", err=True)
        raise typer.Exit(2) from exc
    except (OSError, SQLAlchemyError) as exc:
        typer.echo(f"argos discover: storage operation failed ({type(exc).__name__})", err=True)
        raise typer.Exit(1) from exc
    finally:
        if http:
            http.close()
        if repository:
            repository.close()


def main(argv=None):
    try:
        app(args=argv, prog_name="argos discover", standalone_mode=True)
    except SystemExit as exc:
        return exc.code
    return 0
