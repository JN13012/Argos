"""Fundamental OSINT records, independent of connectors and storage."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from uuid import UUID


def _require_utc(value: datetime, name: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{name} must be timezone-aware and in UTC")


@dataclass(frozen=True)
class SearchScope:
    activity: str
    location: str

    def __post_init__(self) -> None:
        for name in ("activity", "location"):
            value = getattr(self, name).strip()
            if not value:
                raise ValueError(f"{name} must not be blank")
            object.__setattr__(self, name, value)


class EntityType(str, Enum):
    ESTABLISHMENT = "establishment"


@dataclass
class Entity:
    id: UUID
    entity_type: EntityType
    display_name: str
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if not self.display_name.strip():
            raise ValueError("display_name must not be blank")
        _require_utc(self.created_at, "created_at")
        _require_utc(self.updated_at, "updated_at")


@dataclass(frozen=True)
class Identifier:
    entity_id: UUID
    scheme: str
    value: str
    source: str

    def __post_init__(self) -> None:
        for name in ("scheme", "value", "source"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} must not be blank")


@dataclass(frozen=True)
class Observation:
    id: UUID
    entity_id: UUID
    field: str
    value: str
    source: str
    observed_at: datetime

    def __post_init__(self) -> None:
        for name in ("field", "source"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} must not be blank")
        _require_utc(self.observed_at, "observed_at")


class SearchStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"


@dataclass
class Search:
    id: UUID
    scope: SearchScope
    query: str
    started_at: datetime
    completed_at: datetime | None
    status: SearchStatus

    def __post_init__(self) -> None:
        if not self.query.strip():
            raise ValueError("query must not be blank")
        _require_utc(self.started_at, "started_at")
        if self.completed_at is not None:
            _require_utc(self.completed_at, "completed_at")


@dataclass(frozen=True)
class SearchResult:
    search_id: UUID
    entity_id: UUID
    connector: str
    discovered_at: datetime

    def __post_init__(self) -> None:
        if not self.connector.strip():
            raise ValueError("connector must not be blank")
        _require_utc(self.discovered_at, "discovered_at")


class CoverageStatus(str, Enum):
    COMPLETE_FOR_SOURCE = "complete_for_source"
    PARTIAL = "partial"
    TRUNCATED = "truncated"
    FAILED = "failed"


@dataclass
class Coverage:
    search_id: UUID
    connector: str
    status: CoverageStatus
    pages_processed: int
    records_seen: int
    entities_created: int
    entities_reused: int
    pagination_exhausted: bool
    truncated: bool
    exclusions: dict[str, int] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.connector.strip():
            raise ValueError("connector must not be blank")
        for name in (
            "pages_processed",
            "records_seen",
            "entities_created",
            "entities_reused",
        ):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must not be negative")
        if any(count < 0 for count in self.exclusions.values()):
            raise ValueError("exclusion counts must not be negative")
