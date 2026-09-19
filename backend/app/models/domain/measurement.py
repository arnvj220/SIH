"""
Domain model for quantum measurement results.

This layer contains application-level representations only.
It does not perform measurement or security decisions.
"""

from __future__ import annotations

from dataclasses import dataclass


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