from datetime import UTC, datetime, timedelta
from subprocess import CompletedProcess
from unittest.mock import patch

import pytest
from argos.backend.attack.pentest.authorized_execution import (
    AuthorizedNmapRunner,
    ExecutionLimits,
)
from argos.backend.attack.pentest.nmap_runner import ScanExecutionError
from argos.backend.attack.pentest.planner import ScanPlanner
from argos.backend.core.approvals import (
    ApprovalVerifier,
    issue_offline_approval,
)
from argos.backend.core.decision_audit import DecisionAudit
from argos.backend.core.mission_store import MissionRecord, MissionStore
from argos.backend.core.missions import Mission
from argos.backend.core.policy import Action
from argos.backend.core.scope import TargetScope
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

SIGNING_KEY = Ed25519PrivateKey.generate()


def approved_db(tmp_path):
    db = tmp_path / "missions.db"
    record = MissionRecord(
        Mission.draft(
            "Approved private lab", "reviewed-authorization",
            datetime.now(UTC) + timedelta(hours=2),
        ),
        TargetScope(("192.168.56.10/32",)),
        frozenset({Action.TCP_CONNECT_SCAN, Action.SERVICE_IDENTIFICATION}),
    )
    verifier = ApprovalVerifier(SIGNING_KEY.public_key())
    approval = issue_offline_approval(
        record, "authorized-reviewer",
        datetime.now(UTC) + timedelta(hours=1), SIGNING_KEY,
    )
    with MissionStore(db) as store:
        store.create(record)
        store.activate_reviewed(record.mission.id, approval, verifier)
    return db, record.mission.id, verifier


def test_outside_scope_denied_and_audited(tmp_path) -> None:
    db, mission_id, verifier = approved_db(tmp_path)
    with patch(
        "argos.backend.attack.pentest.authorized_execution.subprocess.run"
    ) as run:
        with pytest.raises(ScanExecutionError, match="scope"):
            AuthorizedNmapRunner(db, verifier, executable="nmap").execute(
                mission_id, "192.168.56.11", ScanPlanner().initial()
            )
        run.assert_not_called()
    with DecisionAudit(db) as audit:
        decisions = audit.list_for_mission(mission_id)
        assert len(decisions) == 1
        assert not decisions[0].allowed


def test_signed_scope_approved_scan_runs_without_shell(tmp_path) -> None:
    db, mission_id, verifier = approved_db(tmp_path)
    xml = (
        b'<nmaprun><host><address addr="192.168.56.10" '
        b'addrtype="ipv4"/><ports><port protocol="tcp" portid="22">'
        b'<state state="open"/></port></ports></host></nmaprun>'
    )
    with patch(
        "argos.backend.attack.pentest.authorized_execution.subprocess.run"
    ) as run:
        run.return_value = CompletedProcess(
            args=[], returncode=0, stdout=xml, stderr=b""
        )
        result = AuthorizedNmapRunner(
            db, verifier, executable="nmap"
        ).execute(mission_id, "192.168.56.10", ScanPlanner().initial())
        assert run.call_args.kwargs["shell"] is False
        assert run.call_args.args[0][-1] == "192.168.56.10"
    assert result.observation.open_tcp_ports == frozenset({22})
    with DecisionAudit(db) as audit:
        assert audit.list_for_mission(mission_id)[0].allowed


def test_revoked_mission_fails_before_subprocess(tmp_path) -> None:
    db, mission_id, verifier = approved_db(tmp_path)
    with MissionStore(db) as store:
        store.revoke(mission_id)
    with patch(
        "argos.backend.attack.pentest.authorized_execution.subprocess.run"
    ) as run:
        with pytest.raises(ScanExecutionError, match="approval"):
            AuthorizedNmapRunner(db, verifier, executable="nmap").execute(
                mission_id, "192.168.56.10", ScanPlanner().initial()
            )
        run.assert_not_called()


def test_verifier_with_wrong_secret_fails(tmp_path) -> None:
    db, mission_id, _verifier = approved_db(tmp_path)
    with pytest.raises(ScanExecutionError, match="approval"):
        AuthorizedNmapRunner(
            db,
            ApprovalVerifier(Ed25519PrivateKey.generate().public_key()),
            executable="nmap",
        ).execute(mission_id, "192.168.56.10", ScanPlanner().initial())


def test_limits_reject_invalid_values() -> None:
    with pytest.raises(ValueError):
        ExecutionLimits(timeout_seconds=0)
    with pytest.raises(ValueError):
        ExecutionLimits(max_ports=100)
