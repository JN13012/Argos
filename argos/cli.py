"""Terminal interface to the existing OSINT discovery engine."""

import argparse
import sqlite3
import sys
from pathlib import Path
from uuid import UUID

from dotenv import load_dotenv

from .backend.intel.osint.connectors import SireneConnector
from .backend.intel.osint.discovery import DiscoveryEngine
from .backend.intel.osint.models import Coverage, Search, SearchScope, SearchStatus
from .backend.intel.osint.reporting import (
    format_address as _format_address,
)
from .backend.intel.osint.reporting import (
    write_search_report,
)
from .backend.intel.osint.storage import SQLiteStorage


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="argos", description="Argos OSINT")
    commands = parser.add_subparsers(required=True)
    osint = commands.add_parser("osint", help="OSINT commands")
    osint_commands = osint.add_subparsers(required=True)
    discover = osint_commands.add_parser(
        "discover", help="Discover Sirene establishments"
    )
    discover.set_defaults(action="discover")
    discover.add_argument("--activity", required=True, help="Search scope activity")
    discover.add_argument("--location", required=True, help="Search scope location")
    discover.add_argument("--query", required=True, help="Explicit Sirene query")
    discover.add_argument(
        "--max-pages", type=int, default=5, help="Maximum pages (default: 5)"
    )
    discover.add_argument(
        "--db", default=".argos/osint/argos.sqlite3", help="SQLite database path"
    )
    discover.add_argument(
        "--output-dir", default="outputs", help="Readable reports directory"
    )
    discover.add_argument("--name", help="Readable research name for the output folder")
    report = osint_commands.add_parser(
        "report", help="Export a saved search without API calls"
    )
    report.set_defaults(action="report")
    report.add_argument(
        "--search-id", type=UUID, required=True, help="Saved search UUID"
    )
    report.add_argument(
        "--db", default=".argos/osint/argos.sqlite3", help="SQLite database path"
    )
    report.add_argument(
        "--output-dir", default="outputs", help="Readable reports directory"
    )
    report.add_argument("--name", help="Readable research name for the output folder")
    return parser


def _print_search(storage: SQLiteStorage, search: Search, coverage: Coverage) -> None:
    print("Argos OSINT\n")
    print(f"Search: {search.scope.activity} — {search.scope.location}")
    print(f"Search ID: {search.id}")
    print("Source: SIRENE\n")
    print(f"Status: {search.status.value}")
    print(f"Records: {coverage.records_seen}")
    print(f"Created: {coverage.entities_created}")
    print(f"Reused: {coverage.entities_reused}")
    print(f"Pages: {coverage.pages_processed}")
    print(f"Coverage: {coverage.status.value}")
    print("\nResults:")
    results = storage.get_search_results(search.id)
    if not results:
        print("  No results.")
    for number, result in enumerate(results, start=1):
        entity = storage.get_entity(result.entity_id)
        if entity is None:
            raise ValueError("Search result refers to a missing Entity")
        print(f"\n{number}. {entity.display_name}")
        identifiers = storage.get_identifiers(entity.id)
        for label, scheme in (("SIRET", "siret"), ("SIREN", "siren")):
            values = sorted(
                {item.value for item in identifiers if item.scheme == scheme}
            )
            if values:
                print(f"   {label}: {', '.join(values)}")
        # Storage returns observations in ascending observed_at order.
        latest = {
            item.field: item.value for item in storage.get_observations(entity.id)
        }
        for label, field in (
            ("Activity", "activity"),
            ("Address", "address"),
            ("Administrative status", "administrative_status"),
        ):
            if field in latest:
                value = (
                    _format_address(latest[field])
                    if field == "address"
                    else latest[field]
                )
                print(f"   {label}: {value}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.action == "report" and not Path(args.db).is_file():
            raise ValueError("Saved search database does not exist")
        with SQLiteStorage(args.db) as storage:
            if args.action == "report":
                search = storage.get_search(args.search_id)
                if search is None:
                    raise ValueError("Saved search not found")
            else:
                load_dotenv(dotenv_path=Path.cwd() / ".env", override=False)
                scope = SearchScope(args.activity, args.location)
                engine = DiscoveryEngine(storage, SireneConnector())
                search = engine.discover_sirene(
                    scope=scope,
                    query=args.query,
                    max_pages=args.max_pages,
                )
            coverage = storage.get_coverage(search.id, "sirene")
            if coverage is None:
                raise ValueError("Search coverage is missing")
            if args.action == "discover":
                _print_search(storage, search, coverage)
            report = write_search_report(
                storage, search, coverage, args.output_dir, name=args.name
            )
            print(f"Report: {report}")
            if args.action == "report":
                return 0
            for error in coverage.errors:
                print(f"Error: {error.splitlines()[0]}", file=sys.stderr)
            return int(bool(coverage.errors) or search.status is SearchStatus.FAILED)
    except (OSError, ValueError, sqlite3.Error) as error:
        print(f"Error: {str(error).splitlines()[0]}", file=sys.stderr)
        return 1
