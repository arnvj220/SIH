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

# Thresholds calibrated against the real quantum noise floor
# (see backend/scripts/check_sampling.py):
#   - legitimate error_rate ≈ 0.02
#   - legitimate per-basis skew ≈ 0.04
# Forgery threshold set to 5× noise floor; channel threshold set
# to 2.5× legit skew. Recalibrate if shots_per_basis changes
# (noise scales as 1/√shots).

# Threshold calibrated against 100-shot per-basis sampling noise.
# Legit skew typically ≈ 0.05; threshold at 0.15 gives 3× margin.
# Increasing shots_per_basis would lower the noise floor and could
# permit a lower threshold. See docs/architecture.md §9.

DEFAULT_RULES: tuple[Rule, ...] = (
    Rule(
        rule_id="FORGERY_ERROR_RATE_01",
        threat_type=ThreatType.FORGERY,
        metric="error_rate",
        operator=RuleOperator.GT,
        threshold=0.10, # was 0.15 — calibrated against real 2% noise floor
        severity=Severity.HIGH,
        explanation_template=(
            "Round error rate {observed:.3f} exceeded "
            "forgery threshold {threshold:.3f}"
        ),
    ),

    # Note: distribution_shift currently equals error_rate, so this rule
    # partially overlaps with FORGERY_ERROR_RATE_01. Threshold 0.30 is
    # above the expected quantum-noise floor (~15%) but below a level
    # that would miss moderate channel tampering. Will be revised when
    # per-basis statistics are available from the quantum engine.
    Rule(
        rule_id="CHANNEL_DIST_SHIFT_01",
        threat_type=ThreatType.CHANNEL_MANIPULATION,
        metric="distribution_shift",
        operator=RuleOperator.GT,
        # was 0.30, now 0.10 — calibrated against real 4% skew noise
        # was 0.10, now 0.15 — calibrated against 100-shot noise floor
        threshold=0.15,  
        severity=Severity.HIGH,
        explanation_template=(
            "Outcome distribution shift {observed:.3f} exceeded "
            "channel threshold {threshold:.3f}"
        ),
    ),
)