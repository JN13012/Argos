"""Bounded Sirene discovery and persistence through the existing storage API."""

import json
from dataclasses import replace
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from .connectors.sirene import SireneConnector
from .models import (
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
from .storage import SQLiteStorage


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


class DiscoveryEngine:
    def __init__(self, storage: SQLiteStorage, connector: SireneConnector) -> None:
        self._storage = storage
        self._connector = connector

    def discover_sirene(
        self,
        scope: SearchScope,
        query: str,
        *,
        max_pages: int = 5,
    ) -> Search:
        """Persist a bounded discovery and return its finalized Search.

        Coverage and results can be read from storage using the search UUID.
        Collection errors are recorded in Coverage; persisted results remain.
        """
        if max_pages < 1:
            raise ValueError("max_pages must be positive")
        search = Search(
            uuid4(), scope, query, datetime.now(UTC), None, SearchStatus.RUNNING
        )
        self._storage.save_search(search)
        coverage = Coverage(
            search.id,
            "sirene",
            CoverageStatus.FAILED,
            0,
            0,
            0,
            0,
            False,
            False,
        )
        cursor = "*"
        try:
            for _ in range(max_pages):
                page = self._connector.search_establishments(query=query, cursor=cursor)
                coverage.pages_processed += 1
                coverage.records_seen += len(page["etablissements"])
                for record in page["etablissements"]:
                    created = self._save_establishment(record, search)
                    if created:
                        coverage.entities_created += 1
                    else:
                        coverage.entities_reused += 1
                next_cursor = page["header"].get("curseurSuivant")
                if not isinstance(next_cursor, str) or not next_cursor:
                    raise ValueError("Sirene response is missing a pagination cursor")
                if next_cursor == cursor:
                    coverage.pagination_exhausted = True
                    coverage.status = CoverageStatus.COMPLETE_FOR_SOURCE
                    break
                cursor = next_cursor
            else:
                coverage.status = CoverageStatus.TRUNCATED
                coverage.truncated = True
        except Exception as error:
            coverage.errors.append(f"{type(error).__name__}: {error}")
            coverage.status = (
                CoverageStatus.PARTIAL
                if coverage.entities_created + coverage.entities_reused > 0
                else CoverageStatus.FAILED
            )

        search.status = {
            CoverageStatus.COMPLETE_FOR_SOURCE: SearchStatus.COMPLETED,
            CoverageStatus.TRUNCATED: SearchStatus.PARTIAL,
            CoverageStatus.PARTIAL: SearchStatus.PARTIAL,
            CoverageStatus.FAILED: SearchStatus.FAILED,
        }[coverage.status]
        search.completed_at = datetime.now(UTC)
        self._storage.save_coverage(coverage)
        self._storage.save_search(search)
        return search

    def _save_establishment(self, record: dict[str, Any], search: Search) -> bool:
        siret = _text(record.get("siret"))
        if not siret:
            raise ValueError("Sirene establishment is missing its SIRET")
        unit = record.get("uniteLegale") or {}
        current = next(
            (
                period
                for period in record.get("periodesEtablissement") or []
                if period.get("dateFin") is None
            ),
            {},
        )
        name = (
            _text(unit.get("denominationUniteLegale"))
            or " ".join(
                filter(
                    None,
                    (
                        _text(current.get(f"enseigne{line}Etablissement"))
                        for line in (1, 2, 3)
                    ),
                )
            )
            or _text(current.get("denominationUsuelleEtablissement"))
            or _text(unit.get("denominationUsuelle1UniteLegale"))
            or " ".join(
                filter(
                    None,
                    (
                        _text(unit.get("prenomUsuelUniteLegale")),
                        _text(unit.get("nomUsageUniteLegale"))
                        or _text(unit.get("nomUniteLegale")),
                    ),
                )
            )
        )
        address = {
            key: value
            for key, value in (record.get("adresseEtablissement") or {}).items()
            if _text(value)
        }
        facts = {
            "name": name,
            "address": json.dumps(address, ensure_ascii=False, sort_keys=True)
            if address
            else "",
            "activity": _text(current.get("activitePrincipaleEtablissement")),
            "administrative_status": _text(
                current.get("etatAdministratifEtablissement")
            ),
        }
        now = datetime.now(UTC)
        entity = self._storage.find_entity_by_identifier("siret", siret)
        created = entity is None
        if entity is None:
            entity = Entity(uuid4(), EntityType.ESTABLISHMENT, name or siret, now, now)
        else:
            entity = replace(
                entity, display_name=name or entity.display_name, updated_at=now
            )
        self._storage.save_entity(entity)
        self._storage.add_identifier(Identifier(entity.id, "siret", siret, "sirene"))
        siren = _text(record.get("siren"))
        if siren:
            self._storage.add_identifier(
                Identifier(entity.id, "siren", siren, "sirene")
            )
        for field, value in facts.items():
            if value:
                self._storage.add_observation(
                    Observation(uuid4(), entity.id, field, value, "sirene", now),
                )
        self._storage.add_search_result(
            SearchResult(search.id, entity.id, "sirene", now)
        )
        return created
