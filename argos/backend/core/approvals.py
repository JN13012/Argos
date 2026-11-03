"""Ed25519-reviewed mission approvals with public-key-only verification.

Approval issuance is an offline, trusted reviewer operation. The execution
runtime must receive only the public key, never the private signing key.
A signature establishes reviewer authenticity, not legal target ownership.
"""

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from .mission_store import MissionRecord

_SIGNATURE_PREFIX = "ed25519-v1:"
_DOMAIN_SEPARATOR = b"ARGOS-PENTEST-APPROVAL/v1\x00"


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
    data = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    return _DOMAIN_SEPARATOR + data


class ApprovalVerifier:
    """Verify grants using only the Ed25519 public key."""

    def __init__(self, public_key: Ed25519PublicKey) -> None:
        if not isinstance(public_key, Ed25519PublicKey):
            raise TypeError("An Ed25519 public key is required")
        self._public_key = public_key

    def verify(
        self,
        record: MissionRecord,
        approval: SignedApproval,
        *,
        at: datetime | None = None,
    ) -> bool:
        instant = at or datetime.now(UTC)
        if (
            instant.tzinfo is None
            or approval.mission_id != record.mission.id
            or not approval.reviewer.strip()
            or approval.expires_at.tzinfo is None
            or approval.expires_at <= instant
            or approval.expires_at > record.mission.expires_at
            or record.mission.expires_at <= instant
            or not approval.signature.startswith(_SIGNATURE_PREFIX)
        ):
            return False
        signature_hex = approval.signature[len(_SIGNATURE_PREFIX):]
        if re.fullmatch(r"[0-9a-f]{128}", signature_hex) is None:
            return False
        try:
            self._public_key.verify(
                bytes.fromhex(signature_hex),
                _payload(record, approval.reviewer, approval.expires_at),
            )
        except InvalidSignature:
            return False
        return True


def issue_offline_approval(
    record: MissionRecord,
    reviewer: str,
    expires_at: datetime,
    private_key: Ed25519PrivateKey,
) -> SignedApproval:
    """Reviewer-side only: do not expose this function via the ARGOS API.

    The reviewer must independently confirm written authorization and scope.
    No code can establish the legitimacy of an engagement from a signature.
    """
    if not isinstance(private_key, Ed25519PrivateKey):
        raise TypeError("A private signing key is required")
    if not reviewer.strip() or expires_at.tzinfo is None:
        raise ValueError("Reviewer and timezone-aware expiry are required")
    if expires_at <= datetime.now(UTC):
        raise ValueError("Approval expiry must be in the future")
    if expires_at > record.mission.expires_at:
        raise ValueError("Approval must not outlive the mission")
    signature = _SIGNATURE_PREFIX + private_key.sign(
        _payload(record, reviewer, expires_at)
    ).hex()
    return SignedApproval(record.mission.id, reviewer, expires_at, signature)
