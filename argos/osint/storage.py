"""SQLite persistence for OSINT models, using only the standard library."""

import json
import sqlite3
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from types import TracebackType
from typing import Self
from uuid import UUID

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

_SCHEMA = """
CREATE TABLE IF NOT EXISTS entities (
    id TEXT PRIMARY KEY NOT NULL,
    entity_type TEXT NOT NULL,
    display_name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS identifiers (
    entity_id TEXT NOT NULL REFERENCES entities(id),
    scheme TEXT NOT NULL,
    value TEXT NOT NULL,
    source TEXT NOT NULL,
    PRIMARY KEY (entity_id, scheme, value, source)
);

CREATE TABLE IF NOT EXISTS observations (
    id TEXT PRIMARY KEY NOT NULL,
    entity_id TEXT NOT NULL REFERENCES entities(id),
    field TEXT NOT NULL,
    value TEXT NOT NULL,
    source TEXT NOT NULL,
    observed_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS searches (
    id TEXT PRIMARY KEY NOT NULL,
    activity TEXT NOT NULL,
    location TEXT NOT NULL,
    query TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS search_results (
    search_id TEXT NOT NULL REFERENCES searches(id),
    entity_id TEXT NOT NULL REFERENCES entities(id),
    connector TEXT NOT NULL,
    discovered_at TEXT NOT NULL,
    PRIMARY KEY (search_id, entity_id, connector)
);

CREATE TABLE IF NOT EXISTS coverage (
    search_id TEXT NOT NULL REFERENCES searches(id),
    connector TEXT NOT NULL,
    status TEXT NOT NULL,
    pages_processed INTEGER NOT NULL,
    records_seen INTEGER NOT NULL,
    entities_created INTEGER NOT NULL,
    entities_reused INTEGER NOT NULL,
    pagination_exhausted INTEGER NOT NULL,
    truncated INTEGER NOT NULL,
    exclusions TEXT NOT NULL,
    errors TEXT NOT NULL,
    PRIMARY KEY (search_id, connector)
);
"""


class SQLiteStorage:
    """Persist each write immediately; close the connection on context exit."""

    def __init__(self, database_path: str | Path) -> None:
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(database_path)
        self._connection.row_factory = sqlite3.Row
        try:
            self._connection.execute("PRAGMA foreign_keys = ON")
            self._connection.executescript(_SCHEMA)
        except sqlite3.Error:
            self._connection.close()
            raise

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        self._connection.close()

    def save_entity(self, entity: Entity) -> None:
        """Create or update an entity by UUID, preserving its creation date."""
        entity = replace(entity)
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO entities (id, entity_type, display_name, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT (id) DO UPDATE SET
                    entity_type = excluded.entity_type,
                    display_name = excluded.display_name,
                    updated_at = excluded.updated_at
                """,
                (
                    str(entity.id), entity.entity_type.value, entity.display_name,
                    entity.created_at.isoformat(), entity.updated_at.isoformat(),
                ),
            )

    def get_entity(self, entity_id: UUID) -> Entity | None:
        row = self._connection.execute(
            "SELECT * FROM entities WHERE id = ?", (str(entity_id),),
        ).fetchone()
        if row is None:
            return None
        return Entity(
            id=UUID(row["id"]),
            entity_type=EntityType(row["entity_type"]),
            display_name=row["display_name"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def add_identifier(self, identifier: Identifier) -> None:
        """Keep identifiers and their provenance; repeated identical records are ignored."""
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO identifiers (entity_id, scheme, value, source)
                VALUES (?, ?, ?, ?)
                ON CONFLICT (entity_id, scheme, value, source) DO NOTHING
                """,
                (str(identifier.entity_id), identifier.scheme, identifier.value, identifier.source),
            )

    def get_identifiers(self, entity_id: UUID) -> list[Identifier]:
        rows = self._connection.execute(
            """
            SELECT * FROM identifiers WHERE entity_id = ?
            ORDER BY scheme, value, source
            """,
            (str(entity_id),),
        ).fetchall()
        return [
            Identifier(UUID(row["entity_id"]), row["scheme"], row["value"], row["source"])
            for row in rows
        ]

    def add_observation(self, observation: Observation) -> None:
        """Append a fact. Reusing an observation UUID raises sqlite3.IntegrityError."""
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO observations (id, entity_id, field, value, source, observed_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    str(observation.id), str(observation.entity_id), observation.field,
                    observation.value, observation.source, observation.observed_at.isoformat(),
                ),
            )

    def get_observations(self, entity_id: UUID) -> list[Observation]:
        rows = self._connection.execute(
            """
            SELECT * FROM observations WHERE entity_id = ?
            ORDER BY observed_at, id
            """,
            (str(entity_id),),
        ).fetchall()
        return [
            Observation(
                id=UUID(row["id"]),
                entity_id=UUID(row["entity_id"]),
                field=row["field"],
                value=row["value"],
                source=row["source"],
                observed_at=datetime.fromisoformat(row["observed_at"]),
            )
            for row in rows
        ]

    def save_search(self, search: Search) -> None:
        """Create or update a search without copying the referenced entities."""
        search = replace(search)
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO searches
                    (id, activity, location, query, started_at, completed_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (id) DO UPDATE SET
                    activity = excluded.activity,
                    location = excluded.location,
                    query = excluded.query,
                    started_at = excluded.started_at,
                    completed_at = excluded.completed_at,
                    status = excluded.status
                """,
                (
                    str(search.id), search.scope.activity, search.scope.location, search.query,
                    search.started_at.isoformat(),
                    search.completed_at.isoformat() if search.completed_at is not None else None,
                    search.status.value,
                ),
            )

    def get_search(self, search_id: UUID) -> Search | None:
        row = self._connection.execute(
            "SELECT * FROM searches WHERE id = ?", (str(search_id),),
        ).fetchone()
        if row is None:
            return None
        return Search(
            id=UUID(row["id"]),
            scope=SearchScope(activity=row["activity"], location=row["location"]),
            query=row["query"],
            started_at=datetime.fromisoformat(row["started_at"]),
            completed_at=(
                datetime.fromisoformat(row["completed_at"])
                if row["completed_at"] is not None else None
            ),
            status=SearchStatus(row["status"]),
        )

    def add_search_result(self, result: SearchResult) -> None:
        """Link an existing entity to a search, retaining its first discovery per source."""
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO search_results (search_id, entity_id, connector, discovered_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT (search_id, entity_id, connector) DO NOTHING
                """,
                (
                    str(result.search_id), str(result.entity_id), result.connector,
                    result.discovered_at.isoformat(),
                ),
            )

    def get_search_results(self, search_id: UUID) -> list[SearchResult]:
        rows = self._connection.execute(
            """
            SELECT * FROM search_results WHERE search_id = ?
            ORDER BY discovered_at, entity_id, connector
            """,
            (str(search_id),),
        ).fetchall()
        return [
            SearchResult(
                search_id=UUID(row["search_id"]),
                entity_id=UUID(row["entity_id"]),
                connector=row["connector"],
                discovered_at=datetime.fromisoformat(row["discovered_at"]),
            )
            for row in rows
        ]

    def save_coverage(self, coverage: Coverage) -> None:
        """Create or update the coverage report for one search and source."""
        coverage = replace(coverage)
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO coverage (
                    search_id, connector, status, pages_processed, records_seen,
                    entities_created, entities_reused, pagination_exhausted,
                    truncated, exclusions, errors
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (search_id, connector) DO UPDATE SET
                    status = excluded.status,
                    pages_processed = excluded.pages_processed,
                    records_seen = excluded.records_seen,
                    entities_created = excluded.entities_created,
                    entities_reused = excluded.entities_reused,
                    pagination_exhausted = excluded.pagination_exhausted,
                    truncated = excluded.truncated,
                    exclusions = excluded.exclusions,
                    errors = excluded.errors
                """,
                (
                    str(coverage.search_id), coverage.connector, coverage.status.value,
                    coverage.pages_processed, coverage.records_seen, coverage.entities_created,
                    coverage.entities_reused, int(coverage.pagination_exhausted),
                    int(coverage.truncated), json.dumps(coverage.exclusions),
                    json.dumps(coverage.errors),
                ),
            )

    def get_coverage(self, search_id: UUID, connector: str) -> Coverage | None:
        row = self._connection.execute(
            "SELECT * FROM coverage WHERE search_id = ? AND connector = ?",
            (str(search_id), connector),
        ).fetchone()
        if row is None:
            return None
        return Coverage(
            search_id=UUID(row["search_id"]),
            connector=row["connector"],
            status=CoverageStatus(row["status"]),
            pages_processed=row["pages_processed"],
            records_seen=row["records_seen"],
            entities_created=row["entities_created"],
            entities_reused=row["entities_reused"],
            pagination_exhausted=bool(row["pagination_exhausted"]),
            truncated=bool(row["truncated"]),
            exclusions=json.loads(row["exclusions"]),
            errors=json.loads(row["errors"]),
        )
