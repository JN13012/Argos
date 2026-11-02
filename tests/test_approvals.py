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
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

SIGNING_KEY = Ed25519PrivateKey.generate()
VERIFIER = ApprovalVerifier(SIGNING_KEY.public_key())


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
        record, "lab-reviewer", datetime.now(UTC) + timedelta(hours=1), SIGNING_KEY
    )


def test_reviewed_mission_persists_and_verifies(tmp_path) -> None:
    path = tmp_path / "missions.db"
    record = draft()
    approval = sign(record)
    with MissionStore(path) as store:
        store.create(record)
        store.activate_reviewed(record.mission.id, approval, VERIFIER)
        assert store.get_reviewed(record.mission.id, VERIFIER)
    with MissionStore(path) as store:
        restored = store.get_reviewed(record.mission.id, VERIFIER)
        assert restored.mission.state is MissionState.ACTIVE
        assert restored.scope == record.scope


def test_unreviewed_and_wrong_key_denied() -> None:
    record = draft()
    with MissionStore(":memory:") as store:
        store.create(record)
        with pytest.raises(PermissionError):
            store.get_reviewed(record.mission.id, VERIFIER)
        with pytest.raises(PermissionError):
            store.activate_reviewed(
                record.mission.id, sign(record),
                ApprovalVerifier(Ed25519PrivateKey.generate().public_key()),
            )


def test_scope_and_action_changes_invalidate_grant() -> None:
    record = draft()
    approval = sign(record)
    verifier = VERIFIER
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
    verifier = VERIFIER
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
            store.activate_reviewed(record.mission.id, forged, VERIFIER)


def test_invalid_secret_and_overlong_grant_denied() -> None:
    record = draft()
    with pytest.raises(TypeError):
        ApprovalVerifier(SIGNING_KEY)
    with pytest.raises(ValueError):
        issue_offline_approval(
            record, "reviewer",
            record.mission.expires_at + timedelta(seconds=1), SIGNING_KEY,
        )

def test_legacy_hmac_signature_is_rejected() -> None:
    record = draft()
    legacy = replace(sign(record), signature="0" * 64)
    assert not VERIFIER.verify(record, legacy)


def test_reviewer_identity_is_integrity_protected() -> None:
    record = draft()
    approval = sign(record)
    assert not VERIFIER.verify(
        record, replace(approval, reviewer="another-reviewer")
    )
