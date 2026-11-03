"""Job audit is append-only and survives reopening a SQLite connection."""

from datetime import UTC, datetime
from uuid import uuid4

from argos.backend.attack.pentest.execution_manager import (
    JobSnapshot,
    JobState,
)
from argos.backend.attack.pentest.job_audit import JobAudit


def test_job_events_persist_in_order(tmp_path):
    db = tmp_path / "audit.db"
    job_id = uuid4()
    mission_id = uuid4()
    snapshot = JobSnapshot(
        job_id, mission_id, "127.0.0.1",
        JobState.PENDING, datetime.now(UTC), None, None, None,
    )
    with JobAudit(db) as store:
        store.append(snapshot)
        store.append(
            JobSnapshot(
                job_id, mission_id, "127.0.0.1",
                JobState.CANCELLED, snapshot.submitted_at, None,
                datetime.now(UTC), None,
            )
        )
    with JobAudit(db) as store:
        events = store.list_for_job(job_id)
    assert [item.state for item in events] == [
        JobState.PENDING, JobState.CANCELLED,
    ]
    assert all(item.mission_id == mission_id for item in events)
