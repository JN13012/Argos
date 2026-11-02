"""Append-only SQLite record of decisions made for saved missions."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

from .mission_store import MissionRecord
from .policy import Action, Decision, evaluate


@dataclass(frozen=True)
class AuditedDecision:
    id: UUID
    mission_id: UUID
    target_ip: str
    action: str
    allowed: bool
    reason: str
    timestamp: datetime


class DecisionAudit:
    def __init__(self, path: str | Path) -> None:
        path = str(path)
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(path)
        self._db.row_factory = sqlite3.Row
        self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS pentest_decisions (
                id TEXT PRIMARY KEY,
                mission_id TEXT NOT NULL,
                target_ip TEXT NOT NULL,
                action TEXT NOT NULL,
                allowed INTEGER NOT NULL CHECK (allowed IN (0, 1)),
                reason TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )
        self._db.commit()

    def __enter__(self) -> DecisionAudit:
        return self

    def __exit__(self, *_exc: object) -> None:
        self._db.close()

    def evaluate_and_record(
        self,
        record: MissionRecord,
        target_ip: str,
        action: Action,
        *,
        mandate_verified: bool = False,
        at: datetime | None = None,
    ) -> AuditedDecision:
        """Fail closed and persist the decision before returning it.

        A future trusted verification service must supply mandate_verified;
        never take it from an API request or user-controlled form.
        """
        timestamp = at or datetime.now(UTC)
        if action not in record.allowed_actions:
            decision = Decision(False, "Action is not allowed for this mission")
        else:
            decision = evaluate(
                record.mission, record.scope, target_ip, action,
                at=timestamp, mandate_verified=mandate_verified,
            )
        audited = AuditedDecision(
            uuid4(), record.mission.id, target_ip,
            action.value if isinstance(action, Action) else str(action),
            decision.allowed, decision.reason, timestamp,
        )
        with self._db:
            self._db.execute(
                """
                INSERT INTO pentest_decisions
                (id, mission_id, target_ip, action, allowed, reason, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(audited.id), str(audited.mission_id), audited.target_ip,
                    audited.action, int(audited.allowed), audited.reason,
                    audited.timestamp.isoformat(),
                ),
            )
        return audited

    def list_for_mission(self, mission_id: UUID) -> tuple[AuditedDecision, ...]:
        rows = self._db.execute(
            """
            SELECT * FROM pentest_decisions
            WHERE mission_id = ? ORDER BY timestamp, rowid
            """,
            (str(mission_id),),
        ).fetchall()
        return tuple(
            AuditedDecision(
                UUID(row["id"]), UUID(row["mission_id"]), row["target_ip"],
                row["action"], bool(row["allowed"]), row["reason"],
                datetime.fromisoformat(row["timestamp"]),
            )
            for row in rows
        )
