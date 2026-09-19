from __future__ import annotations

from fastapi import APIRouter

from ..attacks.contracts import VerificationContext


router = APIRouter(
    prefix="/metrics",
    tags=["metrics"],
)


@router.post(
    "/verification",
)
def verification_metrics(
    context: VerificationContext,
) -> dict:
    total = len(context.measurements)

    if total == 0:
        error_rate = 0.0
    else:
        errors = sum(
            measurement.expected != measurement.observed
            for measurement in context.measurements
        )
        error_rate = errors / total

    return {
        "context_id": context.context_id,
        "total_measurements": total,
        "errors": errors if total else 0,
        "error_rate": error_rate,
        "protocol_version": context.protocol_version,
    }