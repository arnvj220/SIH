from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models.schemas.experiment import (
    ExperimentCreate,
    ExperimentResult,
)
from ..services.experiment_service import (
    ExperimentRequest,
    ExperimentService,
)


router = APIRouter(
    prefix="/experiments",
    tags=["experiments"],
)


service = ExperimentService()


@router.post(
    "",
    status_code=201,
)
def create_experiment(
    request: ExperimentCreate,
) -> dict:
    try:
        config = service.create_config(
            ExperimentRequest(
                name=request.name,
                attack=request.scenario,
                seed=request.seed,
                parameters=request.parameters,
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return {
        "experiment_id": request.experiment_id,
        "name": config.name,
        "scenario": config.attack,
        "seed": config.seed,
        "parameters": config.parameters,
    }