from __future__ import annotations

import time
from typing import Any

from ..qds.signature import QDSSignature
from ..attacks.contracts import (
    VerificationContext,
    derive_auth_fingerprint,
)

from app.detection.measurement_builder import BuilderConfig, build_measurements


class VerificationService:
    """Builds verification contexts from QDS signatures."""

    def __init__(self, *, shots_per_basis: int = 100) -> None:
        self._shots_per_basis = shots_per_basis

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

        # Build measurement rounds by sampling:
        #   - expected from Alice's original input state
        #   - observed from Bob's state after teleportation + correction
        # Under legitimate teleportation these agree statistically;
        # under attack they diverge. See
        # app/detection/measurement_builder.py for details.
        measurements = build_measurements(
            evidence,
            BuilderConfig(
                shots_per_basis=self._shots_per_basis,
                seed=evidence.seed,
            ),
        )

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