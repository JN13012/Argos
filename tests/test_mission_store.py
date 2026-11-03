from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from argos.backend.core.mission_store import MissionRecord, MissionStore
from argos.backend.core.missions import Mission, MissionState
from argos.backend.core.policy import Action
from argos.backend.core.scope import TargetScope


def record() -> MissionRecord:
    return MissionRecord(
        Mission.draft(
            "Authorized lab", "MANDATE-001",
            datetime.now(UTC) + timedelta(days=1),
        ),
        TargetScope(("127.0.0.0/24",), ("127.0.0.1/32",)),
        frozenset({Action.TCP_CONNECT_SCAN, Action.SERVICE_IDENTIFICATION}),
    )


def test_persists_mission_scope_and_actions_across_connections(tmp_path) -> None:
    path = tmp_path / "engagements.sqlite3"
    item = record()
    with MissionStore(path) as store:
        store.create(item)
        assert store.list_ids() == (item.mission.id,)
    with MissionStore(path) as store:
        restored = store.get(item.mission.id)
        assert restored == item
        assert restored is not None
        assert not restored.scope.permits("127.0.0.1")
        assert restored.scope.permits("127.0.0.2")
        assert restored.mission.state is MissionState.DRAFT


def test_duplicate_missions_are_rejected_atomically(tmp_path) -> None:
    item = record()
    with MissionStore(tmp_path / "missions.db") as store:
        store.create(item)
        with pytest.raises(ValueError, match="Duplicate"):
            store.create(item)
        assert store.list_ids() == (item.mission.id,)


def test_active_mission_cannot_be_created_without_review() -> None:
    item = record()
    with MissionStore(":memory:") as store:
        with pytest.raises(ValueError, match="review"):
            store.create(
                replace(item, mission=replace(
                    item.mission, state=MissionState.ACTIVE
                ))
            )
        assert store.list_ids() == ()


def test_revoke_is_persistent_and_not_reversible(tmp_path) -> None:
    path = tmp_path / "missions.db"
    item = record()
    with MissionStore(path) as store:
        store.create(item)
        assert store.revoke(item.mission.id)
        assert not store.revoke(item.mission.id)
        assert not store.revoke(uuid4())
    with MissionStore(path) as store:
        restored = store.get(item.mission.id)
        assert restored is not None
        assert restored.mission.state is MissionState.REVOKED


def test_missing_mission_and_invalid_actions_fail_closed() -> None:
    with MissionStore(":memory:") as store:
        assert store.get(uuid4()) is None
    with pytest.raises(ValueError, match="supported action"):
        replace(record(), allowed_actions=frozenset({"arbitrary"}))


def test_sql_input_is_stored_as_data() -> None:
    item = record()
    name = "lab'); DROP TABLE pentest_missions; --"
    item = replace(item, mission=replace(item.mission, title=name))
    with MissionStore(":memory:") as store:
        store.create(item)
        assert store.get(item.mission.id).mission.title == name
        assert len(store.list_ids()) == 1
