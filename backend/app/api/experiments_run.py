"""
Workbench experiment execution.

POST /api/experiments/run   - run an attack against N legitimate contexts,
                              return aggregate distributions + metrics
GET  /api/experiments       - list past runs
GET  /api/experiments/{id}  - fetch one run by id

Backed by app.attacks.runner.run_attack_experiment so the API and the
benchmark scripts produce identical numbers.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..attacks.runner import AttackExperimentConfig, run_attack_experiment
from ..attacks.verifier_adapter import real_verifier_factory

router = APIRouter(prefix="/experiments", tags=["experiments"])

# In-memory result store for the prototype. A DB-backed version can replace
# this without changing the routes.
_RUNS: dict[str, dict[str, Any]] = {}


class ExperimentRunRequest(BaseModel):
    attack_type: str = Field(min_length=1, max_length=64)
    parameters: dict[str, Any] = Field(default_factory=dict)
    n_targets: int = Field(default=100, ge=1, le=10_000)
    seed: int = 12345
    rounds: int = Field(default=100, ge=1, le=100_000)
    natural_error_rate: float = Field(default=0.01, ge=0.0, lt=0.5)


class ExperimentRunResponse(BaseModel):
    experiment_id: str
    config: dict[str, Any]
    metrics: dict[str, Any]
    attack_evidence: dict[str, Any]


@router.post("/run", response_model=ExperimentRunResponse)
def run_experiment(request: ExperimentRunRequest) -> ExperimentRunResponse:
    try:
        config = AttackExperimentConfig(
            attack_type=request.attack_type,
            parameters=request.parameters,
            n_targets=request.n_targets,
            seed=request.seed,
            rounds=request.rounds,
            natural_error_rate=request.natural_error_rate,
        )
        report = run_attack_experiment(config, verifier_factory=real_verifier_factory)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    payload = report.to_dict()
    _RUNS[report.config.experiment_id] = payload

    return ExperimentRunResponse(
        experiment_id=report.config.experiment_id,
        config=payload["config"],
        metrics=payload["metrics"],
        attack_evidence=payload["attack_evidence"],
    )


@router.get("", response_model=list[ExperimentRunResponse])
def list_experiments() -> list[ExperimentRunResponse]:
    return [
        ExperimentRunResponse(
            experiment_id=payload["experiment_id"],
            config=payload["config"],
            metrics=payload["metrics"],
            attack_evidence=payload["attack_evidence"],
        )
        for payload in _RUNS.values()
    ]


@router.get("/{experiment_id}", response_model=ExperimentRunResponse)
def get_experiment(experiment_id: str) -> ExperimentRunResponse:
    payload = _RUNS.get(experiment_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Experiment not found.")
    return ExperimentRunResponse(
        experiment_id=payload["experiment_id"],
        config=payload["config"],
        metrics=payload["metrics"],
        attack_evidence=payload["attack_evidence"],
    )
