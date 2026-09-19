from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..experiments.config import ExperimentConfig


@dataclass(frozen=True)
class ExperimentRequest:
    name: str
    attack: str
    seed: int = 0
    parameters: dict[str, Any] | None = None


class ExperimentService:
    """Application boundary for experiment execution."""

    def create_config(
        self,
        request: ExperimentRequest,
    ) -> ExperimentConfig:
        return ExperimentConfig(
            name=request.name,
            attack=request.attack,
            seed=request.seed,
            parameters=request.parameters or {},
        )