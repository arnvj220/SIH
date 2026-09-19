from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExperimentConfig:
    """Configuration for a reproducible QDS experiment."""

    name: str
    attack: str
    seed: int = 0
    parameters: dict[str, Any] = field(default_factory=dict)