from __future__ import annotations

import time
from typing import Any

from ..qds.signature import QDSSignature
from ..attacks.contracts import (
    VerificationContext,
    derive_auth_fingerprint,
)


class VerificationService:
    """Builds verification contexts from QDS signatures."""

    def build_context(
        self,
        signature: QDSSignature,
        *,
        verifier_id: str,
        message: str,
        expected_signer_id: str | None = None,
        nonce: str = "default-nonce",
        received_at: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> VerificationContext:
        evidence = signature.quantum_evidence

        from ..qds.protocol import compute_message_digest

        message_digest = compute_message_digest(message)

        # The current simulator does not yet expose signed
        # measurement rounds directly, so derive the verification
        # measurement from the teleportation evidence.
        measurements = self._build_measurements(evidence)

        issued_at = time.time()
        received = received_at if received_at is not None else issued_at

        signer = signature.signer_id

        return VerificationContext(
            context_id=f"verify_{signature.signature_id}",
            signature_id=signature.signature_id,
            signer_id=signer,
            expected_signer_id=(
                expected_signer_id
                if expected_signer_id is not None
                else signer
            ),
            verifier_id=verifier_id,
            message_id=signature.message_id,
            message_digest=message_digest,
            signed_digest=signature.message_digest,
            session_id=signature.session_id,
            nonce=nonce,
            issued_at=issued_at,
            received_at=received,
            auth_fingerprint=derive_auth_fingerprint(signer),
            measurements=measurements,
            protocol_version=signature.protocol_version,
            metadata=metadata or {},
        )

    @staticmethod
    def _build_measurements(evidence):
        from ..attacks.contracts import MeasurementRound

        bits = evidence.measurement_bits

        return tuple(
            MeasurementRound(
                index=index,
                basis="Z",
                expected=int(bit),
                observed=int(bit),
            )
            for index, bit in enumerate(bits)
        )                                                                                           