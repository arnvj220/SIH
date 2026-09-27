"""
Workbench experiment execution.

POST /api/experiments/run   - run an attack and return aggregate metrics
GET  /api/experiments       - list past runs (newest first)
GET  /api/experiments/{id}  - fetch one run by id
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from pymongo.database import Database

from ..attacks.runner import AttackExperimentConfig, run_attack_experiment
from ..attacks.verifier_adapter import real_verifier_factory
from ..db.session import get_db

router = APIRouter(prefix="/experiments", tags=["experiments"])


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
    created_at: datetime | None = None


def _to_response(row: dict[str, Any]) -> ExperimentRunResponse:
    return ExperimentRunResponse(
        experiment_id=row["experiment_id"],
        config=row["config"],
        metrics=row["metrics"],
        attack_evidence=row["attack_evidence"],
        created_at=row.get("created_at"),
    )


def _persist_experiment_run(db: Database, document: dict[str, Any]) -> None:
    collection = db["experiment_runs"]
    collection.replace_one(
        {"experiment_id": document["experiment_id"]},
        document,
        upsert=True,
    )
    overflow = list(
        collection.find({}, {"_id": 1})
        .sort("created_at", -1)
        .skip(10)
    )
    if overflow:
        collection.delete_many({"_id": {"$in": [row["_id"] for row in overflow]}})


@router.post("/run", response_model=ExperimentRunResponse)
def run_experiment(
    request: ExperimentRunRequest,
    db: Database = Depends(get_db),
) -> ExperimentRunResponse:
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

    created_at = datetime.now(timezone.utc)
    run_id = f"run_{uuid.uuid4().hex[:12]}"
    try:
        _persist_experiment_run(
            db,
            {
                "experiment_id": run_id,
                "attack_type": report.config.attack_type,
                "config": payload["config"],
                "metrics": payload["metrics"],
                "attack_evidence": payload["attack_evidence"],
                "created_at": created_at,
            },
        )
    except Exception as exc:
        # Return the result anyway — persistence failure must not hide the run.
        print(f"[experiments] persist failed: {exc}")

    return ExperimentRunResponse(
        experiment_id=run_id,
        config=payload["config"],
        metrics=payload["metrics"],
        attack_evidence=payload["attack_evidence"],
        created_at=created_at,
    )


@router.get("", response_model=list[ExperimentRunResponse])
def list_experiments(db: Database = Depends(get_db)) -> list[ExperimentRunResponse]:
    rows = db["experiment_runs"].find().sort("created_at", -1).limit(10)
    return [_to_response(r) for r in rows]


@router.get("/{experiment_id}", response_model=ExperimentRunResponse)
def get_experiment(
    experiment_id: str,
    db: Database = Depends(get_db),
) -> ExperimentRunResponse:
    row = db["experiment_runs"].find_one({"experiment_id": experiment_id})
    if row is None:
        raise HTTPException(status_code=404, detail="Experiment not found.")
    return _to_response(row)