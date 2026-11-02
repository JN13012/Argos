"""Bounded, durable Nmap evidence; all fixtures are synthetic."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from argos.backend.attack.pentest.evidence_store import (
    EvidenceIntegrityError,
    EvidenceStore,
    ScanEvidence,
)
from argos.backend.attack.pentest.models import PortObservation, ScanObservation
from argos.backend.attack.pentest.nmap_parser import MAX_XML_BYTES

XML = (
    b'<nmaprun><host><address addr="127.0.0.1" addrtype="ipv4"/>'
    b'</host></nmaprun>'
)


def sample() -> ScanEvidence:
    now = datetime.now(UTC)
    return ScanEvidence(
        uuid4(), uuid4(), "127.0.0.1", "initial", "completed",
        ("nmap", "-sT", "127.0.0.1"),
        now - timedelta(seconds=1), now, 0, XML, b"",
        ScanObservation(
            "127.0.0.1",
            (PortObservation("127.0.0.1", 22, "tcp", "open", "ssh"),),
        ),
    )


def test_round_trip_verifies_raw_output_and_observations(tmp_path):
    db = tmp_path / "evidence.sqlite3"
    original = sample()
    with EvidenceStore(db) as store:
        receipt = store.save(original)
        assert len(receipt.record_sha256) == 64
        assert len(receipt.xml_sha256) == 64
        assert store.list_for_mission(original.mission_id) == (original.job_id,)
    with EvidenceStore(db) as store:
        restored = store.get_verified(original.job_id)
        assert restored is not None
        assert restored.record == original
        assert restored.receipt == receipt
        assert store.get_verified(uuid4()) is None


def test_write_once_rejects_duplicate_job(tmp_path):
    original = sample()
    with EvidenceStore(tmp_path / "evidence.db") as store:
        store.save(original)
        with pytest.raises(Exception, match="UNIQUE"):
            store.save(original)


def test_tampered_xml_or_metadata_is_detected(tmp_path):
    db = tmp_path / "evidence.db"
    record = sample()
    with EvidenceStore(db) as store:
        store.save(record)
        store._db.execute(
            "UPDATE pentest_scan_evidence SET stdout_xml = ? WHERE job_id = ?",
            (b"modified", str(record.job_id)),
        )
        store._db.commit()
        with pytest.raises(EvidenceIntegrityError, match="output hash"):
            store.get_verified(record.job_id)


def test_tampered_metadata_is_detected(tmp_path):
    record = sample()
    with EvidenceStore(tmp_path / "evidence.db") as store:
        store.save(record)
        store._db.execute(
            "UPDATE pentest_scan_evidence SET phase = ? WHERE job_id = ?",
            ("changed", str(record.job_id)),
        )
        store._db.commit()
        with pytest.raises(EvidenceIntegrityError, match="metadata hash"):
            store.get_verified(record.job_id)


def test_bounded_and_terminal_only(tmp_path):
    record = sample()
    with EvidenceStore(tmp_path / "evidence.db") as store:
        with pytest.raises(ValueError, match="terminal"):
            store.save(replace(record, state="running"))
        with pytest.raises(ValueError, match="limit"):
            store.save(replace(record, stdout_xml=b"x" * (MAX_XML_BYTES + 1)))
        with pytest.raises(ValueError, match="target"):
            store.save(replace(record, target_ip="127.0.0.2"))


def test_failed_scan_evidence_without_xml(tmp_path):
    record = replace(
        sample(), state="failed", exit_code=2, stdout_xml=None,
        stderr=b"failed", observation=None, error="Nmap exited with status 2",
    )
    with EvidenceStore(tmp_path / "evidence.db") as store:
        store.save(record)
        restored = store.get_verified(record.job_id)
        assert restored is not None
        assert restored.record == record
