from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database

from ..attacks.contracts import VerificationContext
from ..db.session import get_db
from ..models.schemas.attack import (
    AttackDescription,
    AttackRequest,
    AttackResponse,
    AttackSampleResponse,
)
from ..models.schemas.verification import VerificationRequest
from ..services.attack_service import AttackService
from ..services.detection_service import DetectionService

router = APIRouter(prefix="/attacks", tags=["attacks"])

service = AttackService()
detector = DetectionService()


def _ctx_from_schema(target: VerificationRequest) -> VerificationContext:
    from ..attacks.contracts import MeasurementRound

    return VerificationContext(
        context_id=target.verification_id,
        signature_id=target.signature_id,
        signer_id=target.signer_id,
        expected_signer_id=target.expected_signer_id,
        verifier_id=target.verifier_id,
        message_id=target.message_id,
        message_digest=target.message_digest,
        signed_digest=target.signed_digest,
        session_id=target.session_id,
        nonce=target.nonce,
        issued_at=target.issued_at,
        received_at=target.received_at,
        auth_fingerprint=target.auth_fingerprint,
        measurements=tuple(
            MeasurementRound(
                index=m.index,
                basis=m.basis,
                expected=m.expected,
                observed=m.observed,
            )
            for m in target.measurements
        ),
        protocol_version=target.protocol_version,
        metadata=dict(target.metadata),
    )


@router.get("", response_model=list[AttackDescription])
def list_attacks() -> list[AttackDescription]:
    return [AttackDescription(**a) for a in service.list_attacks()]


@router.post("/execute", response_model=AttackResponse)
def execute_attack(
    attack: AttackRequest,
    target: VerificationRequest,
    db: Database = Depends(get_db),
) -> AttackResponse:
    try:
        context = _ctx_from_schema(target)
        samples = service.execute(
            attack_name=attack.attack_type,
            target=context,
            seed=attack.seed,
            parameters=attack.parameters,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Run each attacked sample through the real detector so the response
    # carries the verdict, not just the perturbed data.
    sample_responses: list[AttackSampleResponse] = []
    detection_summary: list[dict] = []
    for s in samples:
        outcome = detector.detect(s.context)
        sample_responses.append(
            AttackSampleResponse(
                context_id=s.context.context_id,
                is_attack=s.is_attack,
                expected_threat=s.expected_threat,
                role=s.role,
                evidence={
                    **s.evidence,
                    "decision": outcome.decision.value,
                    "threats": [t.value for t in outcome.threats],
                    "detection_evidence": outcome.evidence,
                },
            )
        )
        detection_summary.append(
            {
                "context_id": s.context.context_id,
                "decision": outcome.decision.value,
                "threats": [t.value for t in outcome.threats],
            }
        )

    # Persist the attack run.
    try:
        db["attacks"].insert_one(
            {
                "attack_id": attack.attack_id,
                "attack_type": attack.attack_type,
                "scenario_name": attack.attack_type,
                "seed": attack.seed,
                "parameters": attack.parameters,
                "target_context_id": context.context_id,
                "generated_samples": detection_summary,
                "evidence": {},
            }
        )
    except Exception as exc:
        print(f"[attacks] persist failed: {exc}")

    return AttackResponse(
        attack_id=attack.attack_id,
        attack_type=samples[0].expected_threat if samples else attack.attack_type,
        scenario_name=attack.attack_type,
        seed=attack.seed,
        parameters=attack.parameters,
        samples=sample_responses,
        evidence={"detection_summary": detection_summary},
    )