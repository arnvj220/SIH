"""
Evidence construction helpers.

Evidence is a plain dict at this layer (matching the current
DetectionService shape in services/detection_service.py).
Typed evidence objects can be introduced later without breaking
the API.
"""

from __future__ import annotations

from typing import Any


def make_evidence(
    evidence_type: str,
    observed: Any,
    threshold: Any,
    rule_id: str,
    explanation: str,
) -> dict[str, Any]:
    """Standard evidence record used by all detection rules."""
    return {
        "type": evidence_type,
        "observed": observed,
        "threshold": threshold,
        "rule_id": rule_id,
        "explanation": explanation,
    }