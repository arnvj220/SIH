from __future__ import annotations

import numpy as np
from fastapi import APIRouter, HTTPException

from ..models.schemas.signature import SignatureCreate, SignatureResponse
from ..services.signature_service import SignatureRequest, SignatureService


router = APIRouter(
    prefix="/signatures",
    tags=["signatures"],
)

signature_service = SignatureService()


def _state_from_schema(
    values: list[list[float]],
) -> np.ndarray:
    try:
        state = np.array(
            [
                complex(real, imaginary)
                for real, imaginary in values
            ],
            dtype=np.complex128,
        )
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="input_state must contain [real, imaginary] pairs.",
        )

    return state


def _complex_state_to_schema(
    state: np.ndarray,
) -> list[list[float]]:
    return [
        [float(value.real), float(value.imag)]
        for value in state
    ]


def _evidence_to_response(evidence):
    return {
        "input_state": _complex_state_to_schema(
            evidence.input_state
        ),
        "measurement_bits": evidence.measurement_bits,
        "correction_bits": evidence.correction_bits,
        "correction_operator": evidence.correction_operator,
        "bob_state_before_correction": _complex_state_to_schema(
            evidence.bob_state_before_correction
        ),
        "bob_state_after_correction": _complex_state_to_schema(
            evidence.bob_state_after_correction
        ),
        "seed": evidence.seed,
    }


@router.post(
    "",
    response_model=SignatureResponse,
)
def create_signature(
    request: SignatureCreate,
) -> SignatureResponse:
    try:
        state = _state_from_schema(request.input_state)

        signature = signature_service.create_signature(
            SignatureRequest(
                signature_id=request.signature_id,
                signer_id=request.signer_id,
                message_id=request.message_id,
                session_id=request.session_id,
                message=request.message,
                input_state=state,
                seed=request.seed,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return SignatureResponse(
        signature_id=signature.signature_id,
        signer_id=signature.signer_id,
        message_id=signature.message_id,
        protocol_version=signature.protocol_version,
        session_id=signature.session_id,
        message_digest=signature.message_digest,
        quantum_evidence=_evidence_to_response(
            signature.quantum_evidence
        ),
    )