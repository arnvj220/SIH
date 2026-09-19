"""
Domain models for reproducible security experiments.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExperimentConfig:
    """Configuration for an experiment run."""

    name: str
    scenario: str

    seed: int = 0
    rounds: int = 200

    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExperimentResult:
    """Result of an experiment execution."""

    experiment_id: str
    name: str
    scenario: str

    total_samples: int
    detected_samples: int
    false_positives: int
    false_negatives: int

    detection_rate: float
    false_positive_rate: float
    false_negative_rate: float

    duration_seconds: float

    metadata: dict[str, Any] = field(default_factory=dict)