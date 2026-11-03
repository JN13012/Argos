from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest
from argos.backend.core.missions import Mission, MissionState
from argos.backend.core.policy import Action, evaluate
from argos.backend.core.scope import TargetScope


def mission() -> Mission:
    return replace(
        Mission.draft(
            "Lab test", "signed-lab-mandate", datetime.now(UTC) + timedelta(hours=1)
        ),
        state=MissionState.ACTIVE,
    )


def test_missing_mandate_fails_closed() -> None:
    result = evaluate(
        mission(),
        TargetScope(("127.0.0.1/32",)),
        "127.0.0.1",
        Action.TCP_CONNECT_SCAN,
    )
    assert not result.allowed
    assert "verified" in result.reason


def test_authorized_target_and_verified_mandate() -> None:
    result = evaluate(
        mission(), TargetScope(("127.0.0.1/32",)), "127.0.0.1",
        Action.TCP_CONNECT_SCAN, mandate_verified=True,
    )
    assert result.allowed


@pytest.mark.parametrize("target", ["127.0.0.2", "example.org", "127.0.0.1;echo bad"])
def test_out_of_scope_and_non_numeric_targets_denied(target: str) -> None:
    assert not evaluate(
        mission(), TargetScope(("127.0.0.1/32",)), target,
        Action.TCP_CONNECT_SCAN, mandate_verified=True,
    ).allowed


def test_excluded_address_denied() -> None:
    assert not evaluate(
        mission(), TargetScope(("127.0.0.0/24",), ("127.0.0.1/32",)),
        "127.0.0.1", Action.TCP_CONNECT_SCAN, mandate_verified=True,
    ).allowed


@pytest.mark.parametrize(
    "state",
    [
        MissionState.DRAFT,
        MissionState.PAUSED,
        MissionState.REVOKED,
        MissionState.COMPLETED,
    ],
)
def test_inactive_mission_denied(state: MissionState) -> None:
    assert not evaluate(
        replace(mission(), state=state), TargetScope(("127.0.0.1/32",)),
        "127.0.0.1", Action.TCP_CONNECT_SCAN, mandate_verified=True,
    ).allowed


def test_expired_mission_denied() -> None:
    expired = replace(mission(), expires_at=datetime.now(UTC) - timedelta(seconds=1))
    assert not evaluate(
        expired, TargetScope(("127.0.0.1/32",)),
        "127.0.0.1", Action.TCP_CONNECT_SCAN, mandate_verified=True,
    ).allowed


def test_unknown_action_denied() -> None:
    assert not evaluate(
        mission(), TargetScope(("127.0.0.1/32",)), "127.0.0.1",
        "arbitrary_command", mandate_verified=True,  # type: ignore[arg-type]
    ).allowed


def test_empty_and_unbounded_scopes_rejected() -> None:
    with pytest.raises(ValueError):
        TargetScope(())
    with pytest.raises(ValueError):
        TargetScope(("0.0.0.0/0",))
