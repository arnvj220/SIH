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
from app.detection.stores import (
    AuthorizationStore,
    ReplayStore,
    DEFAULT_AUTHORIZATION_STORE,
    DEFAULT_REPLAY_STORE,
)


class DetectionEngine:
    """
    Rule-based deterministic detection engine. No AI/ML.

    Implements the Verifier protocol from attacks.contracts.
    """

    def __init__(
        self,
        rules: tuple[Rule, ...] = DEFAULT_RULES,
        baseline: BaselineProfile = DEFAULT_BASELINE,
        replay_store: ReplayStore | None = None,
        authorization_store: AuthorizationStore | None = None,
    ) -> None:
        self.rules = rules
        self.baseline = baseline
        self.replay_store = replay_store or DEFAULT_REPLAY_STORE
        self.authorization_store = (
            authorization_store or DEFAULT_AUTHORIZATION_STORE
        )

    def verify(self, context: VerificationContext) -> DetectionOutcome:
        """Run all applicable rules against the context."""
        metrics = self._extract_metrics(context)
        threats: list[ThreatType] = []
        evidence: list[dict] = []

        # --- Structural checks (no state) ---

        # 1. Impersonation: presenter claims one signer, session expects another.
        if context.signer_id != context.expected_signer_id:
            threats.append(ThreatType.IMPERSONATION)
            evidence.append(
                make_evidence(
                    evidence_type="signer_mismatch",
                    observed=context.signer_id,
                    threshold=context.expected_signer_id,
                    rule_id="IMPERSONATION_ID_MISMATCH_01",
                    explanation=(
                        f"Presented signer {context.signer_id!r} does not "
                        f"match expected {context.expected_signer_id!r}"
                    ),
                )
            )

        # 2. Forgery: presented message digest differs from signed digest.
        if context.message_digest != context.signed_digest:
            threats.append(ThreatType.FORGERY)
            evidence.append(
                make_evidence(
                    evidence_type="message_digest_mismatch",
                    observed=context.message_digest,
                    threshold=context.signed_digest,
                    rule_id="FORGERY_DIGEST_MISMATCH_01",
                    explanation=(
                        "Presented message digest does not match signed digest"
                    ),
                )
            )

        # 3. Unauthorized verification: verifier not permitted for signer.
        if not self.authorization_store.is_authorized(
            context.signer_id, context.verifier_id
        ):
            threats.append(ThreatType.UNAUTHORIZED_VERIFICATION)
            evidence.append(
                make_evidence(
                    evidence_type="unauthorized_verifier",
                    observed=context.verifier_id,
                    threshold=context.signer_id,
                    rule_id="UNAUTHORIZED_VERIFIER_01",
                    explanation=(
                        f"Verifier {context.verifier_id!r} is not authorized "
                        f"to verify signatures for {context.signer_id!r}"
                    ),
                )
            )

        # --- Statistical rules (rule-based, no state) ---

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

        # --- Stateful checks (only if no other threats found) ---

        # 4. Replay: a clean-looking context that reuses a consumed (session, nonce)
        #    is a replay. We check this last so that an attacker cannot "burn"
        #    a legitimate session by submitting an obviously-fake request first.
        if not threats:
            consumed = self.replay_store.consume_or_flag(
                context.session_id, context.nonce
            )
            if not consumed:
                threats.append(ThreatType.REPLAY)
                evidence.append(
                    make_evidence(
                        evidence_type="session_reuse",
                        observed=1.0,
                        threshold=0.0,
                        rule_id="REPLAY_SESSION_REUSE_01",
                        explanation=(
                            f"Session {context.session_id!r} with nonce "
                            f"{context.nonce!r} was already consumed"
                        ),
                    )
                )
        else:
            # If the context already has threats, do not consume the
            # (session, nonce). This preserves the session for legitimate use.
            # An attacker's tampered request should not lock out the real one.
            pass

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
        """Turn a VerificationContext into a flat metric dict for rules."""
        measurements = context.measurements

        # error_rate: fraction of rounds where observed != expected
        error_rate = context.error_rate

        # distribution_shift: fraction of rounds where observed is
        # anti-correlated with expected. For a perfect flip channel this
        # equals error_rate; for a biased channel it may differ.
        # Currently identical to error_rate until the quantum engine
        # exposes richer per-basis statistics.
        distribution_shift = error_rate

        return {
            "error_rate": error_rate,
            "distribution_shift": distribution_shift,
        }