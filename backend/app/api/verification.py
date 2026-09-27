from __future__ import annotations

from fastapi import APIRouter, Depends
from pymongo.database import Database

from ..attacks.contracts import MeasurementRound, VerificationContext
from ..db.session import get_db
from ..models.schemas.verification import (
    VerificationRequest,
    VerificationResponse,
)
from ..services.alert_service import persist_verification_and_alerts
from ..services.detection_service import DetectionService


router = APIRouter(prefix="/verification", tags=["verification"])

detection_service = DetectionService()


def _build_context(request: VerificationRequest) -> VerificationContext:
    measurements = tuple(
        MeasurementRound(
            index=m.index,
            basis=m.basis,
            expected=m.expected,
            observed=m.observed,
        )
        for m in request.measurements
    )

    return VerificationContext(
        context_id=request.verification_id,
        signature_id=request.signature_id,
        signer_id=request.signer_id,
        expected_signer_id=request.expected_signer_id,
        verifier_id=request.verifier_id,
        message_id=request.message_id,
        message_digest=request.message_digest,
        signed_digest=request.signed_digest,
        session_id=request.session_id,
        nonce=request.nonce,
        issued_at=request.issued_at,
        received_at=request.received_at,
        auth_fingerprint=request.auth_fingerprint,
        measurements=measurements,
        protocol_version=request.protocol_version,
        metadata=dict(request.metadata),
    )


@router.post("", response_model=VerificationResponse)
def verify_signature(
    request: VerificationRequest,
    db: Database = Depends(get_db),
) -> VerificationResponse:
    context = _build_context(request)
    outcome = detection_service.detect(context)

    try:
        persist_verification_and_alerts(db, context, outcome)
    except Exception as exc:
        # Never let persistence failure hide the security decision.
        print(f"[verification] persist failed: {exc}")

    return VerificationResponse(
        verification_id=request.verification_id,
        decision=outcome.decision,
        threats=outcome.threats,
        evidence=outcome.evidence,
        detected=outcome.detected,
        error_rate=context.error_rate,
    )