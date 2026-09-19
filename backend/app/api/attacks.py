from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..attacks.contracts import VerificationContext
from ..models.schemas.attack import (
    AttackDescription,
    AttackRequest,
    AttackResponse,
    AttackSampleResponse,
)
from ..models.schemas.verification import VerificationRequest
from ..services.attack_service import AttackService

router = APIRouter(
    prefix="/attacks",
    tags=["attacks"],
)

service = AttackService()


@router.get(
    "",
    response_model=list[AttackDescription],
)
def list_attacks() -> list[AttackDescription]:
    return [
        AttackDescription(**attack)
        for attack in service.list_attacks()
    ]


@router.post(
    "/execute",
    response_model=AttackResponse,
)
def execute_attack(
    request: AttackRequest,
    target: VerificationRequest,
) -> AttackResponse:
    try:
        context = VerificationContext(
            **target.model_dump(),
        )

        samples = service.execute(
            attack_name=request.attack_type,
            target=context,
            seed=request.seed,
            parameters=request.parameters,
        )

    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return AttackResponse(
        attack_id=request.attack_id,
        attack_type=(
            samples[0].expected_threat
            if samples
            else request.attack_type
        ),
        scenario_name=request.attack_type,
        seed=request.seed,
        parameters=request.parameters,
        samples=[
            AttackSampleResponse(
                context_id=sample.context.context_id,
                is_attack=sample.is_attack,
                expected_threat=sample.expected_threat,
                role=sample.role,
                evidence=sample.evidence,
            )
            for sample in samples
        ],
        evidence={},
    )