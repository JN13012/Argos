"""Offline-reviewed, HMAC-authenticated mission grants.

The signing secret belongs to a separate trusted reviewer workflow. Never
accept a signing secret, approval assertion or verification override over HTTP.
A signature establishes review within this deployment, not legal permission
to assess a third party.
"""

import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from .mission_store import MissionRecord


@dataclass(frozen=True)
class SignedApproval:
    mission_id: UUID
    reviewer: str
    expires_at: datetime
    signature: str


def _payload(
    record: MissionRecord, reviewer: str, expires_at: datetime
) -> bytes:
    mission = record.mission
    body = {
        "mission_id": str(mission.id),
        "title": mission.title,
        "reference": mission.authorization_reference,
        "mission_expiry": mission.expires_at.isoformat(),
        "allowed_networks": sorted(record.scope.networks),
        "excluded_networks": sorted(record.scope.excluded),
        "actions": sorted(action.value for action in record.allowed_actions),
        "reviewer": reviewer,
        "approval_expiry": expires_at.isoformat(),
    }
    return json.dumps(body, sort_keys=True, separators=(",", ":")).encode()


class ApprovalVerifier:
    """Validate grant authenticity and exact scope binding at each execution."""

    def __init__(self, secret: bytes) -> None:
        if len(secret) < 32:
            raise ValueError("Approval secret requires at least 32 bytes")
        self._secret = secret

    def verify(
        self,
        record: MissionRecord,
        approval: SignedApproval,
        *,
        at: datetime | None = None,
    ) -> bool:
        instant = at or datetime.now(UTC)
        if (
            approval.mission_id != record.mission.id
            or not approval.reviewer.strip()
            or approval.expires_at.tzinfo is None
            or approval.expires_at <= instant
            or approval.expires_at > record.mission.expires_at
            or record.mission.expires_at <= instant
        ):
            return False
        expected = hmac.new(
            self._secret,
            _payload(record, approval.reviewer, approval.expires_at),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, approval.signature)


def issue_offline_approval(
    record: MissionRecord,
    reviewer: str,
    expires_at: datetime,
    secret: bytes,
) -> SignedApproval:
    """Reviewer-side utility: DO NOT call from the runtime or expose via API.

    Approval issuance is a separate operational trust boundary. Reviewers must
    verify ownership, authorization documents and action scope independently.
    """
    if len(secret) < 32:
        raise ValueError("Approval secret requires at least 32 bytes")
    if not reviewer.strip() or expires_at.tzinfo is None:
        raise ValueError("Approval reviewer and timezone-aware expiry required")
    if expires_at > record.mission.expires_at:
        raise ValueError("Approval must not outlive the mission")
    signature = hmac.new(
        secret, _payload(record, reviewer, expires_at), hashlib.sha256
    ).hexdigest()
    return SignedApproval(record.mission.id, reviewer, expires_at, signature)
