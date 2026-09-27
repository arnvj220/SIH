"""Persist alerts and events derived from detection outcomes."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from pymongo.database import Database

from ..attacks.contracts import DetectionOutcome, VerificationContext


_SEVERITY_BY_THREAT = {
    "FORGERY": "HIGH",
    "IMPERSONATION": "HIGH",
    "REPLAY": "MEDIUM",
    "UNAUTHORIZED_VERIFICATION": "MEDIUM",
    "CHANNEL_MANIPULATION": "HIGH",
}


def _short_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def persist_verification_and_alerts(
    db: Database,
    context: VerificationContext,
    outcome: DetectionOutcome,
) -> list[str]:
    """Save the verification event + one alert per threat. Returns alert ids."""
    alert_ids: list[str] = []

    # One event per verification attempt (always).
    db["events"].insert_one(
        {
            "event_id": _short_id("evt"),
            "event_type": "VERIFICATION",
            "entity_type": "verification",
            "entity_id": context.context_id,
            "severity": "INFO" if not outcome.detected else "WARN",
            "payload": {
                "decision": outcome.decision.value,
                "threats": [t.value for t in outcome.threats],
                "error_rate": context.error_rate,
                "signer_id": context.signer_id,
                "verifier_id": context.verifier_id,
            },
            "created_at": datetime.now(timezone.utc),
        }
    )

    # One alert per detected threat.
    for threat in outcome.threats:
        alert_id = _short_id("alt")
        db["alerts"].insert_one(
            {
                "alert_id": alert_id,
                "alert_type": threat.value,
                "severity": _SEVERITY_BY_THREAT.get(threat.value, "MEDIUM"),
                "status": "OPEN",
                "verification_id": context.context_id,
                "attack_id": None,
                "title": f"{threat.value.replace('_', ' ').title()} detected",
                "description": (
                    f"Verification {context.context_id} flagged {threat.value} "
                    f"for signer={context.signer_id} verifier={context.verifier_id}"
                ),
                "evidence": outcome.evidence,
                "created_at": datetime.now(timezone.utc),
                "resolved_at": None,
            }
        )
        alert_ids.append(alert_id)

    return alert_ids