"""
Domain model for quantum measurement results.

This layer contains application-level representations only.
It does not perform measurement or security decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class PauliBasis(str, Enum):
    X = "X"
    Y = "Y"
    Z = "Z"


@dataclass(frozen=True)
class Measurement:
    """A single measurement round."""

    index: int
    basis: str
    expected: int
    observed: int

    def __post_init__(self) -> None:
        if self.index < 0:
            raise ValueError("Measurement index must be non-negative.")

        if self.basis.upper() not in {"X", "Y", "Z"}:
            raise ValueError("Measurement basis must be X, Y, or Z.")

        if self.expected not in (0, 1):
            raise ValueError("Expected measurement must be 0 or 1.")

        if self.observed not in (0, 1):
            raise ValueError("Observed measurement must be 0 or 1.")

    @property
    def is_error(self) -> bool:
        return self.expected != self.observed


@dataclass(frozen=True)
class MeasurementBatch:
    """
    Aggregate of all measurement rounds for one verification event.

    Produced by the quantum engine; consumed by verification and
    statistical detection.
    """

    verification_id: str
    rounds: int
    measurements: tuple[Measurement, ...] = ()
    seed: int | None = None
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.rounds < 0:
            raise ValueError("Rounds must be non-negative.")
        if len(self.measurements) > self.rounds:
            raise ValueError("Number of measurements cannot exceed declared rounds.")

    def error_count(self) -> int:
        """Number of rounds where observed != expected."""
        return sum(1 for m in self.measurements if m.is_error)

    def error_rate(self) -> float:
        """
        Fraction of rounds that were errors. 0.0 if no rounds.

        Number of errors / Total number of measurements
        """
        if not self.measurements:
            return 0.0
        return self.error_count() / len(self.measurements)

    def outcome_counts(self, basis: str | None = None) -> dict[int, int]:
        """Count observed outcomes (0/1), optionally filtered by basis."""
        counts = {0: 0, 1: 0}
        for m in self.measurements:
            if basis is None or m.basis.upper() == basis.upper():
                counts[m.observed] += 1
        return counts