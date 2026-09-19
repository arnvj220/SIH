"""
API schemas for experiments and benchmarks.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ExperimentCreate(BaseModel):
    """Create an experiment run."""

    experiment_id: str = Field(
        min_length=1,
        max_length=128,
    )

    name: str = Field(
        min_length=1,
        max_length=256,
    )

    scenario: str = Field(
        min_length=1,
        max_length=128,
    )

    seed: int = 0

    parameters: dict = Field(
        default_factory=dict,
    )


class ExperimentResult(BaseModel):
    """Result of an experiment or benchmark."""

    experiment_id: str

    name: str

    scenario: str

    seed: int

    parameters: dict

    total_samples: int = Field(
        ge=0,
    )

    detected_samples: int = Field(
        ge=0,
    )

    detection_rate: float = Field(
        ge=0.0,
        le=1.0,
    )

    false_positive_rate: float = Field(
        ge=0.0,
        le=1.0,
    )

    false_negative_rate: float = Field(
        ge=0.0,
        le=1.0,
    )

    verification_latency_ms: float | None = Field(
        default=None,
        ge=0.0,
    )

    simulation_throughput: float | None = Field(
        default=None,
        ge=0.0,
    )

    metrics: dict = Field(
        default_factory=dict,
    )

    created_at: datetime | None = None