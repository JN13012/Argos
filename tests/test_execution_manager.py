"""Lifecycle tests use fake subprocesses; they never scan a real host."""

import threading
import time
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest

from argos.backend.attack.pentest.authorized_execution import AuthorizedNmapRunner
from argos.backend.attack.pentest.execution_manager import (
    ExecutionManager,
    JobState,
)
from argos.backend.attack.pentest.planner import ScanPlanner
from argos.backend.core.approvals import ApprovalVerifier, issue_offline_approval
from argos.backend.core.mission_store import MissionRecord, MissionStore
from argos.backend.core.missions import Mission
from argos.backend.core.policy import Action
from argos.backend.core.scope import TargetScope
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

def approved(tmp_path):
    key = Ed25519PrivateKey.generate()
    record = MissionRecord(
        Mission.draft(
            "test", "reviewed",
            datetime.now(UTC) + timedelta(hours=2),
        ),
        TargetScope(("127.0.0.1/32",)),
        frozenset({Action.TCP_CONNECT_SCAN}),
    )
    path = tmp_path / "jobs.db"
    with MissionStore(path) as store:
        store.create(record)
        store.activate_reviewed(
            record.mission.id,
            issue_offline_approval(
                record, "reviewer",
                datetime.now(UTC) + timedelta(hours=1), key
            ),
            ApprovalVerifier(key.public_key()),
        )
    return (
        AuthorizedNmapRunner(
            path, ApprovalVerifier(key.public_key()), executable="nmap"
        ),
        record.mission.id,
    )


def wait_state(manager, job_id, desired):
    for _ in range(200):
        snapshot = manager.get(job_id)
        if snapshot is not None and snapshot.state == desired:
            return snapshot
        time.sleep(0.01)
    pytest.fail(f"Job did not reach {desired}")


def test_lifecycle_completed_and_result(tmp_path):
    runner, mission_id = approved(tmp_path)
    xml = (
        b'<nmaprun><host><address addr="127.0.0.1" '
        b'addrtype="ipv4"/></host></nmaprun>'
    )

    class Finished:
        returncode = 0

        def __init__(self, args, **kwargs):
            self.args = args
            kwargs["stdout"].write(xml)

        def poll(self):
            return 0

        def wait(self, timeout=None):
            return self.returncode

    with patch(
        "argos.backend.attack.pentest.execution_manager.subprocess.Popen",
        Finished,
    ):
        with ExecutionManager(runner, concurrency=1) as manager:
            job_id = manager.submit(
                mission_id, "127.0.0.1", ScanPlanner().initial()
            )
            snap = wait_state(manager, job_id, JobState.COMPLETED)
            assert snap.started_at and snap.finished_at
            assert manager.result(job_id).observation.target == "127.0.0.1"


def test_cancel_terminates_running_job(tmp_path):
    runner, mission_id = approved(tmp_path)
    started = threading.Event()

    class Hanging:
        returncode = None

        def __init__(self, *args, **kwargs):
            started.set()

        def poll(self):
            return self.returncode

        def terminate(self):
            self.returncode = -15

        def wait(self, timeout=None):
            return self.returncode

    with patch(
        "argos.backend.attack.pentest.execution_manager.subprocess.Popen",
        Hanging,
    ):
        with ExecutionManager(
            runner, concurrency=1, poll_seconds=0.01
        ) as manager:
            job_id = manager.submit(
                mission_id, "127.0.0.1", ScanPlanner().initial()
            )
            assert started.wait(2)
            assert manager.cancel(job_id)
            wait_state(manager, job_id, JobState.CANCELLED)
            assert not manager.cancel(job_id)


def test_unknown_job_and_capacity(tmp_path):
    runner, mission_id = approved(tmp_path)
    with patch(
        "argos.backend.attack.pentest.execution_manager.subprocess.Popen"
    ) as popen:
        popen.side_effect = OSError("stub")
        with ExecutionManager(
            runner, concurrency=1, max_jobs=1
        ) as manager:
            job_id = manager.submit(
                mission_id, "127.0.0.1", ScanPlanner().initial()
            )
            with pytest.raises(RuntimeError, match="capacity"):
                manager.submit(
                    mission_id, "127.0.0.1", ScanPlanner().initial()
                )
            wait_state(manager, job_id, JobState.FAILED)
