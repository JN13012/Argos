"""Signed approvals bind mission identity, limits and reviewer decision."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest
from argos.backend.core.approvals import (
    ApprovalVerifier,
    issue_offline_approval,
)
from argos.backend.core.mission_store import MissionRecord, MissionStore
from argos.backend.core.missions import Mission, MissionState
from argos.backend.core.policy import Action
from argos.backend.core.scope import TargetScope

KEY = b"offline-reviewer-key-with-at-least-32-bytes"


def draft() -> MissionRecord:
    return MissionRecord(
        Mission.draft(
            "Lab", "signed-mandate",
            datetime.now(UTC) + timedelta(days=2),
        ),
        TargetScope(("192.168.56.10/32",)),
        frozenset({Action.TCP_CONNECT_SCAN}),
    )


def sign(record: MissionRecord):
    return issue_offline_approval(
        record, "lab-reviewer", datetime.now(UTC) + timedelta(hours=1), KEY
    )


def test_reviewed_mission_persists_and_verifies(tmp_path) -> None:
    path = tmp_path / "missions.db"
    record = draft()
    approval = sign(record)
    with MissionStore(path) as store:
        store.create(record)
        store.activate_reviewed(record.mission.id, approval, ApprovalVerifier(KEY))
        assert store.get_reviewed(record.mission.id, ApprovalVerifier(KEY))
    with MissionStore(path) as store:
        restored = store.get_reviewed(record.mission.id, ApprovalVerifier(KEY))
        assert restored.mission.state is MissionState.ACTIVE
        assert restored.scope == record.scope


def test_unreviewed_and_wrong_key_denied() -> None:
    record = draft()
    with MissionStore(":memory:") as store:
        store.create(record)
        with pytest.raises(PermissionError):
            store.get_reviewed(record.mission.id, ApprovalVerifier(KEY))
        with pytest.raises(PermissionError):
            store.activate_reviewed(
                record.mission.id, sign(record),
                ApprovalVerifier(b"another-independent-reviewer-secret-32bytes"),
            )


def test_scope_and_action_changes_invalidate_grant() -> None:
    record = draft()
    approval = sign(record)
    verifier = ApprovalVerifier(KEY)
    assert verifier.verify(record, approval)
    assert not verifier.verify(
        replace(record, scope=TargetScope(("192.168.56.11/32",))),
        approval,
    )
    assert not verifier.verify(
        replace(record, allowed_actions=frozenset({Action.SERVICE_IDENTIFICATION})),
        approval,
    )


def test_expiry_and_revocation_are_enforced() -> None:
    record = draft()
    approval = sign(record)
    verifier = ApprovalVerifier(KEY)
    assert not verifier.verify(
        record, approval, at=datetime.now(UTC) + timedelta(hours=2)
    )
    with MissionStore(":memory:") as store:
        store.create(record)
        store.activate_reviewed(record.mission.id, approval, verifier)
        assert store.revoke(record.mission.id)
        with pytest.raises(PermissionError):
            store.get_reviewed(record.mission.id, verifier)


def test_forged_signature_is_denied() -> None:
    record = draft()
    forged = replace(sign(record), signature="0" * 64)
    with MissionStore(":memory:") as store:
        store.create(record)
        with pytest.raises(PermissionError):
            store.activate_reviewed(record.mission.id, forged, ApprovalVerifier(KEY))


def test_invalid_secret_and_overlong_grant_denied() -> None:
    record = draft()
    with pytest.raises(ValueError):
        ApprovalVerifier(b"short")
    with pytest.raises(ValueError):
        issue_offline_approval(
            record, "reviewer",
            record.mission.expires_at + timedelta(seconds=1), KEY,
        )
