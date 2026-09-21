"""
Deterministic detection engine.

Consumes a VerificationContext (from attacks.contracts) and returns
a DetectionOutcome. Uses rules from rules.py, thresholds from
thresholds.py, statistics from statistics.py.
"""

from __future__ import annotations

from app.attacks.contracts import (
    Decision,
    DetectionOutcome,
    ThreatType,
    VerificationContext,
)
from app.detection.baseline import BaselineProfile, DEFAULT_BASELINE
from app.detection.evidence import make_evidence
from app.detection.rules import DEFAULT_RULES, Rule
from app.detection.statistics import measurement_deviation


class DetectionEngine:
    """
    Rule-based deterministic detection engine. No AI/ML.

    Implements the Verifier protocol from attacks.contracts.
    """

    def __init__(
        self,
        rules: tuple[Rule, ...] = DEFAULT_RULES,
        baseline: BaselineProfile = DEFAULT_BASELINE,
    ) -> None:
        self.rules = rules
        self.baseline = baseline

    def verify(self, context: VerificationContext) -> DetectionOutcome:
        """Run all applicable rules against the context."""
        metrics = self._extract_metrics(context)
        threats: list[ThreatType] = []
        evidence: list[dict] = []

        # 1. Identity / authorization checks (structural, not statistical)
        if context.signer_id != context.expected_signer_id:
            threats.append(ThreatType.IMPERSONATION)
            evidence.append(
                make_evidence(
                    evidence_type="signer_mismatch",
                    observed=context.signer_id,
                    threshold=context.expected_signer_id,
                    rule_id="IMPERSONATION_ID_MISMATCH_01",
                    explanation=(
                        f"Presented signer {context.signer_id!r} does not match "
                        f"expected {context.expected_signer_id!r}"
                    ),
                )
            )

        # 2. Message integrity (forgery)
        if context.message_digest != context.signed_digest:
            threats.append(ThreatType.FORGERY)
            evidence.append(
                make_evidence(
                    evidence_type="message_digest_mismatch",
                    observed=context.message_digest,
                    threshold=context.signed_digest,
                    rule_id="FORGERY_DIGEST_MISMATCH_01",
                    explanation="Presented message digest does not match signed digest",
                )
            )

        # 3. Statistical rules (channel manipulation, measurement deviation)
        for rule in self.rules:
            observed = metrics.get(rule.metric)
            if observed is None:
                continue
            if rule.triggers(observed):
                threats.append(rule.threat_type)
                evidence.append(
                    make_evidence(
                        evidence_type=rule.metric,
                        observed=observed,
                        threshold=rule.threshold,
                        rule_id=rule.rule_id,
                        explanation=rule.explain(observed, expected=0.0),
                    )
                )

        if threats:
            return DetectionOutcome(
                decision=Decision.REJECT,
                threats=threats,
                evidence=evidence,
            )

        return DetectionOutcome(
            decision=Decision.ACCEPT,
            threats=[],
            evidence=evidence,
        )

    def _extract_metrics(self, context: VerificationContext) -> dict[str, float]:
        observed_outcomes = [m.observed for m in context.measurements]
        metrics: dict[str, float] = {
            "error_rate": context.error_rate,
            "measurement_deviation": measurement_deviation(
                observed_outcomes=observed_outcomes,
                expected_p0=self.baseline.expected_p0("Z"),
            ),
            # distribution_shift: same TV metric, but its rule uses a different
            # threat_type and threshold, letting the two rules coexist.
            "distribution_shift": measurement_deviation(
                observed_outcomes=observed_outcomes,
                expected_p0=self.baseline.expected_p0("Z"),
            ),
        }
        return metrics