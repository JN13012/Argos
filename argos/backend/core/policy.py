"""Fail-closed policy decision for an engagement and a single numeric target."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .missions import Mission
from .scope import TargetScope


class Action(StrEnum):
    PASSIVE_REVIEW = "passive_review"
    TCP_CONNECT_SCAN = "tcp_connect_scan"
    SERVICE_IDENTIFICATION = "service_identification"


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str


def evaluate(
    mission: Mission,
    scope: TargetScope,
    target_ip: str,
    action: Action,
    *,
    at: datetime | None = None,
    mandate_verified: bool = False,
) -> Decision:
    """Default deny. Independent mandate verification is mandatory.

    mandate_verified is a trust-boundary input supplied only by a future
    authenticated authorization subsystem; never expose it as a user API flag.
    """
    if not mandate_verified:
        return Decision(False, "Mandate has not been independently verified")
    if not mission.is_active(at):
        return Decision(False, "Mission is not active or authorization expired")
    if not isinstance(action, Action):
        return Decision(False, "Unsupported action")
    if not scope.permits(target_ip):
        return Decision(False, "Target is outside authorized scope")
    return Decision(True, "Authorized target and action")
