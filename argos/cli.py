"""Terminal interface to the existing OSINT discovery engine."""

import argparse
import json
import sqlite3
import sys

from .osint.connectors import SireneConnector
from .osint.discovery import DiscoveryEngine
from .osint.models import Coverage, Search, SearchScope, SearchStatus
from .osint.storage import SQLiteStorage


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="argos", description="Argos OSINT")
    commands = parser.add_subparsers(required=True)
    osint = commands.add_parser("osint", help="OSINT commands")
    osint_commands = osint.add_subparsers(required=True)
    discover = osint_commands.add_parser(
        "discover", help="Discover Sirene establishments"
    )
    discover.add_argument("--activity", required=True, help="Search scope activity")
    discover.add_argument("--location", required=True, help="Search scope location")
    discover.add_argument("--query", required=True, help="Explicit Sirene query")
    discover.add_argument(
        "--max-pages", type=int, default=5, help="Maximum pages (default: 5)"
    )
    discover.add_argument(
        "--db", default=".argos/osint/argos.sqlite3", help="SQLite database path"
    )
    return parser


def _format_address(value: str) -> str:
    """Render the stored address JSON without exposing source field names."""
    try:
        address = json.loads(value)
    except ValueError:
        return value
    if not isinstance(address, dict):
        return value
    parts = []
    for keys in (
        ("complementAdresseEtablissement",),
        (
            "numeroVoieEtablissement",
            "indiceRepetitionEtablissement",
            "typeVoieEtablissement",
            "libelleVoieEtablissement",
        ),
        ("distributionSpecialeEtablissement",),
        (
            "codePostalEtablissement",
            "libelleCommuneEtablissement",
            "libelleCommuneEtrangerEtablissement",
        ),
        ("libellePaysEtrangerEtablissement",),
    ):
        part = " ".join(str(address[key]) for key in keys if address.get(key))
        if part:
            parts.append(part)
    return ", ".join(parts) or value


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
        scope = SearchScope(args.activity, args.location)
        with SQLiteStorage(args.db) as storage:
            engine = DiscoveryEngine(storage, SireneConnector())
            search = engine.discover_sirene(
                scope=scope,
                query=args.query,
                max_pages=args.max_pages,
            )
            coverage = storage.get_coverage(search.id, "sirene")
            if coverage is None:
                raise ValueError("Search coverage is missing")
            _print_search(storage, search, coverage)
            for error in coverage.errors:
                print(f"Error: {error.splitlines()[0]}", file=sys.stderr)
            return int(bool(coverage.errors) or search.status is SearchStatus.FAILED)
    except (OSError, ValueError, sqlite3.Error) as error:
        print(f"Error: {str(error).splitlines()[0]}", file=sys.stderr)
        return 1
