"""
Deterministic detection rules.

A rule maps a measured metric to a threat decision using a
configurable threshold. Rules are data — not code — so they can be
inspected, exported, and calibrated without changing the engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.attacks.contracts import ThreatType
from app.detection.thresholds import crosses


class Severity(str, Enum):
    INFO = "INFO"
    SUSPICIOUS = "SUSPICIOUS"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class RuleOperator(str, Enum):
    GT = ">"
    GE = ">="
    LT = "<"
    LE = "<="
    EQ = "=="
    NE = "!="


@dataclass(frozen=True)
class Rule:
    """A single deterministic detection rule."""

    rule_id: str
    threat_type: ThreatType
    metric: str
    operator: RuleOperator
    threshold: float
    severity: Severity
    explanation_template: str

    def triggers(self, observed: float) -> bool:
        return crosses(observed, self.operator.value, self.threshold)

    def explain(self, observed: float, expected: float) -> str:
        """Render the explanation with the actual values."""
        return self.explanation_template.format(
            observed=observed, expected=expected, threshold=self.threshold
        )

# Note: REPLAY, IMPERSONATION, and UNAUTHORIZED_VERIFICATION checks are
# implemented structurally in engine.py, not as rules in this file.

DEFAULT_RULES: tuple[Rule, ...] = (
    Rule(
        rule_id="FORGERY_ERROR_RATE_01",
        threat_type=ThreatType.FORGERY,
        metric="error_rate",
        operator=RuleOperator.GT,
        threshold=0.15,
        severity=Severity.HIGH,
        explanation_template=(
            "Round error rate {observed:.3f} exceeded "
            "forgery threshold {threshold:.3f}"
        ),
    ),
    Rule(
        rule_id="CHANNEL_DIST_SHIFT_01",
        threat_type=ThreatType.CHANNEL_MANIPULATION,
        metric="distribution_shift",
        operator=RuleOperator.GT,
        threshold=0.25,
        severity=Severity.HIGH,
        explanation_template=(
            "Outcome distribution shift {observed:.3f} exceeded "
            "channel threshold {threshold:.3f}"
        ),
    ),
)