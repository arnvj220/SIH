"""
Add workbench endpoints to the backend.

Creates / extends:
    app/api/experiments_run.py   NEW   - run + list + fetch experiments
    app/api/verifications.py     NEW   - list verification events
    app/api/signatures_list.py   NEW   - list signatures
    app/api/router.py            PATCH - include the three new routers

Idempotent: re-running is safe (overwrites the new files, checks for
duplicate includes in router.py).

Usage:
    cd backend
    python scripts/add_workbench_endpoints.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
APP = BACKEND / "app"
API = APP / "api"


EXPERIMENTS_RUN = '''"""
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
'''


VERIFICATIONS_LIST = '''"""GET /api/verifications - list verification events."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db.models.verification import VerificationModel
from ..db.session import get_db

router = APIRouter(prefix="/verifications", tags=["verifications"])


@router.get("")
def list_verifications(db: Session = Depends(get_db)) -> list[dict]:
    rows = (
        db.query(VerificationModel)
        .order_by(VerificationModel.created_at.desc())
        .limit(500)
        .all()
    )
    return [
        {
            "verification_id": getattr(r, "verification_id", None) or getattr(r, "id", None),
            "signature_id": getattr(r, "signature_id", None),
            "verifier_id": getattr(r, "verifier_id", None),
            "decision": getattr(r, "decision", None),
            "detected": getattr(r, "detected", None),
            "error_rate": getattr(r, "error_rate", None),
            "created_at": getattr(r, "created_at", None),
        }
        for r in rows
    ]
'''


SIGNATURES_LIST = '''"""GET /api/signatures - list signatures."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db.models.signature import SignatureModel
from ..db.session import get_db

router = APIRouter(prefix="/signatures", tags=["signatures"])


@router.get("")
def list_signatures(db: Session = Depends(get_db)) -> list[dict]:
    rows = (
        db.query(SignatureModel)
        .order_by(SignatureModel.created_at.desc())
        .limit(500)
        .all()
    )
    return [
        {
            "signature_id": getattr(r, "signature_id", None) or getattr(r, "id", None),
            "signer_id": getattr(r, "signer_id", None),
            "message_id": getattr(r, "message_id", None),
            "session_id": getattr(r, "session_id", None),
            "protocol_version": getattr(r, "protocol_version", None),
            "created_at": getattr(r, "created_at", None),
        }
        for r in rows
    ]
'''


def write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    print(f"  wrote {path.relative_to(BACKEND)}")


def patch_router() -> None:
    router_file = API / "router.py"
    text = router_file.read_text(encoding="utf-8")

    additions = [
        ("experiments_run", "experiments_run_router"),
        ("verifications", "verifications_router"),
        ("signatures_list", "signatures_list_router"),
    ]

    changed = False
    for module, alias in additions:
        import_line = f"from .{module} import router as {alias}\n"
        include_line = f"router.include_router({alias})\n"
        if import_line not in text:
            text = text.replace(
                "from .alerts import router as alerts_router\n",
                f"from .alerts import router as alerts_router\n{import_line}",
            )
            changed = True
        if include_line not in text:
            text = text.rstrip() + f"\n{include_line}"
            changed = True

    if changed:
        router_file.write_text(text, encoding="utf-8")
        print(f"  patched {router_file.relative_to(BACKEND)}")
    else:
        print(f"  {router_file.relative_to(BACKEND)} already patched")


def main() -> int:
    print("Adding workbench endpoints...")
    print()
    print("New route files:")
    write(API / "experiments_run.py", EXPERIMENTS_RUN)
    write(API / "verifications.py", VERIFICATIONS_LIST)
    write(API / "signatures_list.py", SIGNATURES_LIST)
    print()
    print("Updating router.py:")
    patch_router()
    print()
    print("Done. Restart the backend and run scripts/audit_api.py to verify.")
    print()
    print("New endpoints available:")
    print("  POST /api/experiments/run")
    print("  GET  /api/experiments")
    print("  GET  /api/experiments/{experiment_id}")
    print("  GET  /api/verifications")
    print("  GET  /api/signatures")
    return 0


if __name__ == "__main__":
    sys.exit(main())