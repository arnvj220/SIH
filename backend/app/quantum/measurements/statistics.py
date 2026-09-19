"""
Measurement statistics utilities.

Converts raw measurement counts into probabilities and provides
basic descriptive statistics for quantum measurement experiments.

This module does NOT make security decisions or detect attacks.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MeasurementStatistics:
    """
    Summary of a repeated quantum measurement experiment.

    Attributes:
        basis:
            Measurement basis used (X, Y, or Z).

        shots:
            Total number of measurements performed.

        counts:
            Number of times each outcome was observed.

        probabilities:
            Empirical probability of each outcome.
    """

    basis: str
    shots: int
    counts: dict[str, int]
    probabilities: dict[str, float]


def calculate_probabilities(
    counts: dict[str, int],
) -> dict[str, float]:
    """
    Convert measurement counts into empirical probabilities.

    Example:

        {
            "0": 700,
            "1": 300
        }

    becomes:

        {
            "0": 0.7,
            "1": 0.3
        }

    Args:
        counts:
            Mapping of measurement outcomes to counts.

    Returns:
        Mapping of outcomes to empirical probabilities.

    Raises:
        ValueError: If counts are invalid or total shots are zero.
    """

    if not counts:
        raise ValueError("Counts cannot be empty.")

    if any(count < 0 for count in counts.values()):
        raise ValueError("Measurement counts cannot be negative.")

    shots = sum(counts.values())

    if shots <= 0:
        raise ValueError(
            "Total measurement count must be greater than zero."
        )

    return {
        outcome: count / shots
        for outcome, count in counts.items()
    }


def create_measurement_statistics(
    basis: str,
    counts: dict[str, int],
) -> MeasurementStatistics:
    """
    Create a MeasurementStatistics object from raw counts.

    Args:
        basis:
            Measurement basis used.

        counts:
            Raw measurement outcome counts.

    Returns:
        MeasurementStatistics object.
    """

    basis = basis.upper()

    if basis not in {"X", "Y", "Z"}:
        raise ValueError(
            "Measurement basis must be X, Y, or Z."
        )

    probabilities = calculate_probabilities(counts)

    shots = sum(counts.values())

    return MeasurementStatistics(
        basis=basis,
        shots=shots,
        counts=dict(counts),
        probabilities=probabilities,
    )