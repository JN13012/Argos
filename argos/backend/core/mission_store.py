"""SQLite persistence for scoped pentest mission drafts.

Storage does not verify a signed mandate or activate a mission. Those trusted
operations require a separate authorization authority and must not be exposed
through ordinary user input.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import UUID

from .missions import Mission, MissionState
from .policy import Action
from .scope import TargetScope


@dataclass(frozen=True)
class MissionRecord:
    mission: Mission
    scope: TargetScope
    allowed_actions: frozenset[Action]

    def __post_init__(self) -> None:
        if not self.allowed_actions or not all(
            type(action) is Action for action in self.allowed_actions
        ):
            raise ValueError("At least one supported action is required")


class MissionStore:
    """Local mission registry; all write statements are parameterized.

    A new record can only start in DRAFT. A separate, authenticated review
    workflow must be designed before mission activation is implemented.
    """

    def __init__(self, path: str | Path) -> None:
        path = str(path)
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(path)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA foreign_keys = ON")
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS pentest_missions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                authorization_reference TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                state TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS pentest_scope (
                mission_id TEXT NOT NULL REFERENCES pentest_missions(id),
                network TEXT NOT NULL,
                excluded INTEGER NOT NULL CHECK(excluded IN (0, 1)),
                PRIMARY KEY(mission_id, network, excluded)
            );
            CREATE TABLE IF NOT EXISTS pentest_actions (
                mission_id TEXT NOT NULL REFERENCES pentest_missions(id),
                action TEXT NOT NULL,
                PRIMARY KEY(mission_id, action)
            );
            """
        )

    def __enter__(self) -> MissionStore:
        return self

    def __exit__(self, *_exc: object) -> None:
        self._db.close()

    def create(self, record: MissionRecord) -> None:
        mission = record.mission
        if mission.state is not MissionState.DRAFT:
            raise ValueError("Mission activation requires independent review")
        try:
            with self._db:
                self._db.execute(
                    """
                    INSERT INTO pentest_missions
                    (id, title, authorization_reference, expires_at, state)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        str(mission.id), mission.title,
                        mission.authorization_reference,
                        mission.expires_at.isoformat(), mission.state.value,
                    ),
                )
                self._db.executemany(
                    """
                    INSERT INTO pentest_scope (mission_id, network, excluded)
                    VALUES (?, ?, ?)
                    """,
                    [
                        (str(mission.id), network, excluded)
                        for excluded, networks in (
                            (0, record.scope.networks),
                            (1, record.scope.excluded),
                        )
                        for network in networks
                    ],
                )
                self._db.executemany(
                    """
                    INSERT INTO pentest_actions (mission_id, action)
                    VALUES (?, ?)
                    """,
                    [
                        (str(mission.id), action.value)
                        for action in sorted(record.allowed_actions)
                    ],
                )
        except sqlite3.IntegrityError as error:
            raise ValueError("Duplicate or invalid mission record") from error

    def get(self, mission_id: UUID) -> MissionRecord | None:
        row = self._db.execute(
            "SELECT * FROM pentest_missions WHERE id = ?", (str(mission_id),)
        ).fetchone()
        if row is None:
            return None
        scope_rows = self._db.execute(
            """
            SELECT network, excluded FROM pentest_scope
            WHERE mission_id = ? ORDER BY excluded, network
            """,
            (str(mission_id),),
        ).fetchall()
        action_rows = self._db.execute(
            "SELECT action FROM pentest_actions WHERE mission_id = ?",
            (str(mission_id),),
        ).fetchall()
        return MissionRecord(
            Mission(
                UUID(row["id"]), row["title"],
                row["authorization_reference"],
                datetime.fromisoformat(row["expires_at"]),
                MissionState(row["state"]),
            ),
            TargetScope(
                tuple(r["network"] for r in scope_rows if not r["excluded"]),
                tuple(r["network"] for r in scope_rows if r["excluded"]),
            ),
            frozenset(Action(r["action"]) for r in action_rows),
        )

    def list_ids(self) -> tuple[UUID, ...]:
        rows = self._db.execute(
            "SELECT id FROM pentest_missions ORDER BY rowid"
        ).fetchall()
        return tuple(UUID(row["id"]) for row in rows)

    def revoke(self, mission_id: UUID) -> bool:
        """Revocation is irreversible in this MVP."""
        with self._db:
            cursor = self._db.execute(
                """
                UPDATE pentest_missions SET state = ?
                WHERE id = ? AND state != ?
                """,
                (
                    MissionState.REVOKED.value,
                    str(mission_id),
                    MissionState.REVOKED.value,
                ),
            )
        return cursor.rowcount == 1
