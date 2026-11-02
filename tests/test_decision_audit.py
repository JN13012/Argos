from dataclasses import replace
from datetime import UTC, datetime, timedelta

from argos.backend.core.decision_audit import DecisionAudit
from argos.backend.core.mission_store import MissionRecord
from argos.backend.core.missions import Mission, MissionState
from argos.backend.core.policy import Action
from argos.backend.core.scope import TargetScope


def lab_record() -> MissionRecord:
    return MissionRecord(
        replace(
            Mission.draft(
                "Audit lab", "independently-reviewed-reference",
                datetime.now(UTC) + timedelta(hours=1),
            ),
            state=MissionState.ACTIVE,
        ),
        TargetScope(("127.0.0.1/32",)),
        frozenset({Action.TCP_CONNECT_SCAN}),
    )


def test_denial_is_persisted_across_connections(tmp_path) -> None:
    path = tmp_path / "audit.db"
    record = lab_record()
    with DecisionAudit(path) as audit:
        denied = audit.evaluate_and_record(
            record, "127.0.0.1", Action.TCP_CONNECT_SCAN
        )
        assert not denied.allowed
    with DecisionAudit(path) as audit:
        assert audit.list_for_mission(record.mission.id) == (denied,)


def test_action_not_in_mission_is_denied_even_if_mandate_verified() -> None:
    record = lab_record()
    with DecisionAudit(":memory:") as audit:
        decision = audit.evaluate_and_record(
            record, "127.0.0.1", Action.SERVICE_IDENTIFICATION,
            mandate_verified=True,
        )
        assert not decision.allowed
        assert "not allowed" in decision.reason


def test_valid_decision_and_out_of_scope_denial_are_audited() -> None:
    record = lab_record()
    with DecisionAudit(":memory:") as audit:
        approved = audit.evaluate_and_record(
            record, "127.0.0.1", Action.TCP_CONNECT_SCAN,
            mandate_verified=True,
        )
        refused = audit.evaluate_and_record(
            record, "127.0.0.2", Action.TCP_CONNECT_SCAN,
            mandate_verified=True,
        )
        assert approved.allowed
        assert not refused.allowed
        assert audit.list_for_mission(record.mission.id) == (approved, refused)
