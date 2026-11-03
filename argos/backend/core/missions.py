"""Minimal, immutable engagement contracts.

These objects describe authorization; they do not themselves prove that an
engagement mandate is authentic. Scan execution must require independent
authorization verification before enabling the runner.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class MissionState(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    REVOKED = "revoked"


@dataclass(frozen=True)
class Mission:
    id: UUID
    title: str
    authorization_reference: str
    expires_at: datetime
    state: MissionState = MissionState.DRAFT

    @classmethod
    def draft(cls, title: str, reference: str, expires_at: datetime) -> "Mission":
        return cls(uuid4(), title, reference, expires_at)

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("Mission title is required")
        if not self.authorization_reference.strip():
            raise ValueError("Authorization reference is required")
        if self.expires_at.tzinfo is None:
            raise ValueError("Mission expiry must be timezone-aware")

    def is_active(self, at: datetime | None = None) -> bool:
        instant = at or datetime.now(UTC)
        return self.state is MissionState.ACTIVE and instant < self.expires_at
