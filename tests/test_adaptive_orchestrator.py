"""Adaptive phase tests use an in-memory job manager, never real Nmap."""

import threading
from datetime import UTC, datetime
from uuid import uuid4

from argos.backend.attack.pentest.adaptive_orchestrator import (
    AdaptiveReconOrchestrator,
)
from argos.backend.attack.pentest.evidence_store import (
    EvidenceReceipt,
    ScanEvidence,
    VerifiedEvidence,
)
from argos.backend.attack.pentest.execution_manager import JobSnapshot, JobState
from argos.backend.attack.pentest.models import PortObservation, ScanObservation
from argos.backend.attack.pentest.nmap_runner import ExecutedScan


class FakeManager:
    def __init__(self, ports, *, stop_at=None, revoke_at=None):
        self.ports = ports
        self.stop_at = stop_at
        self.revoke_at = revoke_at
        self.jobs = {}
        self.calls = []
        self.cancelled = []

    def submit(self, mission_id, target, plan):
        from argos.backend.attack.pentest.nmap_runner import ScanExecutionError

        if self.revoke_at == len(self.calls):
            raise ScanExecutionError("Mission approval is invalid")
        job = uuid4()
        self.calls.append(plan)
        state = (
            self.stop_at
            if self.stop_at is not None and len(self.calls) == 1
            else JobState.COMPLETED
        )
        ports = (
            tuple(
                PortObservation(target, p, "tcp", "open")
                for p in self.ports
            )
            if len(self.calls) == 1 else
            tuple(
                PortObservation(target, p, "tcp", "open", "ssh", "9.2")
                for p in plan.ports
            )
        )
        scan = ExecutedScan(
            ("nmap", plan.phase, target),
            ScanObservation(target, ports),
        )
        self.jobs[job] = (state, mission_id, target, plan, scan)
        return job

    def get(self, job_id):
        state, mission, target, _plan, _scan = self.jobs[job_id]
        return JobSnapshot(
            job_id, mission, target, state, datetime.now(UTC), None, None,
            "Simulated scan failure" if state is JobState.FAILED else None,
        )

    def result(self, job_id):
        return self.jobs[job_id][4]

    def verified_evidence(self, job_id):
        state, mission, target, plan, scan = self.jobs[job_id]
        if state is not JobState.COMPLETED:
            return None
        return VerifiedEvidence(
            ScanEvidence(
                job_id, mission, target, plan.phase,
                "completed", scan.arguments, datetime.now(UTC),
                datetime.now(UTC), 0, b"<nmaprun/>", b"",
                scan.observation,
            ),
            EvidenceReceipt(job_id, "a" * 64, "b" * 64, None),
        )

    def cancel(self, job_id):
        self.cancelled.append(job_id)
        state, mission, target, plan, scan = self.jobs[job_id]
        self.jobs[job_id] = (
            JobState.CANCELLED, mission, target, plan, scan
        )
        return True


def test_two_phases_are_selected_from_open_ports():
    manager = FakeManager((22, 80))
    mission = uuid4()
    result = AdaptiveReconOrchestrator(manager).run(
        mission, "127.0.0.1"
    )
    assert result.state is JobState.COMPLETED
    assert len(result.phases) == 2
    assert manager.calls[0].identify_versions is False
    assert manager.calls[1].ports == (22, 80)
    assert manager.calls[1].identify_versions is True
    assert all(phase.receipt is not None for phase in result.phases)
    assert [r.key for r in result.recommendations] == [
        "tcp-22", "tcp-80",
    ]


def test_no_open_ports_stops_after_discovery():
    manager = FakeManager(())
    result = AdaptiveReconOrchestrator(manager).run(
        uuid4(), "127.0.0.1"
    )
    assert result.state is JobState.COMPLETED
    assert len(result.phases) == 1
    assert result.recommendations == ()


def test_revocation_prevents_second_scan():
    manager = FakeManager((22,), revoke_at=1)
    result = AdaptiveReconOrchestrator(manager).run(
        uuid4(), "127.0.0.1"
    )
    assert result.state is JobState.FAILED
    assert result.error == "Mission approval is invalid"
    assert len(manager.calls) == 1
    assert len(result.phases) == 1
    assert "approval" in result.error


def test_initial_failure_has_no_followup():
    manager = FakeManager((22,), stop_at=JobState.FAILED)
    result = AdaptiveReconOrchestrator(manager).run(
        uuid4(), "127.0.0.1"
    )
    assert result.state is JobState.FAILED
    assert result.error == "Simulated scan failure"
    assert len(manager.calls) == 1
    assert len(result.phases) == 1


def test_explicit_cancellation_prevents_all_scans():
    cancelled = threading.Event()
    cancelled.set()
    manager = FakeManager((22,))
    result = AdaptiveReconOrchestrator(manager).run(
        uuid4(), "127.0.0.1", cancel=cancelled
    )
    assert result.state is JobState.CANCELLED
    assert manager.calls == []


def test_missing_evidence_prevents_followup():
    manager = FakeManager((22,))
    manager.verified_evidence = lambda job_id: None
    result = AdaptiveReconOrchestrator(manager).run(
        uuid4(), "127.0.0.1"
    )
    assert result.state is JobState.FAILED
    assert len(manager.calls) == 1
    assert "Evidence" in result.error
