from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Iterable

import numpy as np

from .contracts import AttackedSample, MeasurementRound, ThreatType, VerificationContext

class AttackConfigError(ValueError):
    """Invalid or unsupported attack configuration."""


def check_choice(name: str, value: Any, choices: Iterable[Any]) -> None:
    choices = tuple(choices)
    if value not in choices:
        raise AttackConfigError(f"'{name}' must be one of {choices}, got {value!r}")


def check_number(
    name: str,
    value: Any,
    lo: float,
    hi: float,
    *,
    lo_open: bool = False,
    integer: bool = False,
) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise AttackConfigError(f"'{name}' must be a number, got {value!r}")
    if integer and int(value) != value:
        raise AttackConfigError(f"'{name}' must be an integer, got {value!r}")
    too_low = value <= lo if lo_open else value < lo
    if too_low or value > hi:
        bracket = "(" if lo_open else "["
        raise AttackConfigError(f"'{name}' must be in {bracket}{lo}, {hi}], got {value!r}")


def randomize_rounds(
    rng: np.random.Generator,
    measurements: tuple[MeasurementRound, ...],
    fraction: float,
) -> tuple[tuple[MeasurementRound, ...], int]:
   
    n = len(measurements)
    k = int(round(fraction * n))
    if k == 0:
        return measurements, 0
    chosen = set(rng.choice(n, size=k, replace=False).tolist())
    out: list[MeasurementRound] = []
    changed = 0
    for pos, m in enumerate(measurements):
        if pos in chosen:
            new_bit = int(rng.integers(0, 2))
            changed += int(new_bit != m.observed)
            out.append(MeasurementRound(m.index, m.basis, m.expected, new_bit))
        else:
            out.append(m)
    return tuple(out), changed


def count_errors_by_basis(
    measurements: tuple[MeasurementRound, ...],
) -> dict[str, dict[str, float]]:
    stats: dict[str, dict[str, float]] = {}
    for basis in ("X", "Y", "Z"):
        rounds = [m for m in measurements if m.basis == basis]
        errs = sum(m.is_error for m in rounds)
        stats[basis] = {
            "rounds": len(rounds),
            "errors": errs,
            "error_rate": (errs / len(rounds)) if rounds else 0.0,
        }
    return stats


class AttackScenario(ABC):
    attack_type: ClassVar[ThreatType]
    name: ClassVar[str]
    description: ClassVar[str]
    defaults: ClassVar[dict[str, Any]] = {}

    def __init__(self, seed: int = 0, parameters: dict[str, Any] | None = None):
        self.seed = seed
        self.parameters: dict[str, Any] = {}
        self._rng: np.random.Generator = np.random.default_rng(seed)
        self._evidence: dict[str, Any] = {}
        self.initialize()
        self.configure(parameters or {})

    
    def initialize(self) -> None:
        self._rng = np.random.default_rng(self.seed)
        self._evidence = {"contexts_generated": 0}
        self.parameters = dict(self.defaults)

    def configure(self, parameters: dict[str, Any]) -> None:
        unknown = set(parameters) - set(self.defaults)
        if unknown:
            raise AttackConfigError(
                f"Unsupported parameter(s) for '{self.name}': {sorted(unknown)}. "
                f"Supported: {sorted(self.defaults)}"
            )
        merged = {**self.defaults, **parameters}
        self.validate(merged)
        self.parameters = merged

    def validate(self, params: dict[str, Any]) -> None:  
        return None

    @abstractmethod
    def execute(self, target: VerificationContext) -> list[AttackedSample]:
      """"""

    def collect_evidence(self) -> dict[str, Any]:
        return {
            "attack": self.name,
            "seed": self.seed,
            "parameters": dict(self.parameters),
            **self._evidence,
        }

    def reset(self) -> None:
       
        params = dict(self.parameters)
        self.initialize()
        self.parameters = params

    
    def _new_id(self, prefix: str, nbytes: int = 6) -> str:
        return f"{prefix}_{self._rng.bytes(nbytes).hex()}"

    def _tag(self, target: VerificationContext, **extra: Any) -> dict[str, Any]:
        meta = dict(target.metadata)
        meta.update({"origin": "attack", "attack": self.name, **extra})
        return meta

    def _count(self, n: int = 1) -> None:
        self._evidence["contexts_generated"] += n
