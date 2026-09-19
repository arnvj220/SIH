from __future__ import annotations

from ..attacks.contracts import (
    Decision,
    DetectionOutcome,
    ThreatType,
    VerificationContext,
)


class DetectionService:
    """
    Application-level detection service.

    Combines deterministic verification checks and returns
    a structured DetectionOutcome.
    """

    def detect(
        self,
        context: VerificationContext,
    ) -> DetectionOutcome:
        threats: list[ThreatType] = []
        evidence: list[dict] = []

        if context.signer_id != context.expected_signer_id:
            threats.append(ThreatType.IMPERSONATION)
            evidence.append(
                {
                    "type": "signer_mismatch",
                    "signer_id": context.signer_id,
                    "expected_signer_id": context.expected_signer_id,
                }
            )

        if context.message_digest != context.signed_digest:
            threats.append(ThreatType.FORGERY)
            evidence.append(
                {
                    "type": "message_digest_mismatch",
                    "message_digest": context.message_digest,
                    "signed_digest": context.signed_digest,
                }
            )

        if context.error_rate > 0.20:
            threats.append(ThreatType.CHANNEL_MANIPULATION)
            evidence.append(
                {
                    "type": "high_measurement_error",
                    "error_rate": context.error_rate,
                    "threshold": 0.20,
                }
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