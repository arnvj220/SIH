"""
Statistical computations used by detection rules.

Pure functions. No state, no side effects, no thresholds.
Threshold logic lives in thresholds.py; rule definitions in rules.py.
"""

from __future__ import annotations

from collections.abc import Sequence


def error_rate(expected: Sequence[int], observed: Sequence[int]) -> float:
    """Fraction of rounds where observed != expected. 0.0 if empty."""
    if not expected:
        return 0.0
    errors = sum(1 for e, o in zip(expected, observed) if e != o)
    return errors / len(expected)


def outcome_probabilities(outcomes: Sequence[int]) -> dict[int, float]:
    """Empirical P(outcome=0) and P(outcome=1)."""
    if not outcomes:
        return {0: 0.0, 1: 0.0}
    total = len(outcomes)
    return {
        0: outcomes.count(0) / total,
        1: outcomes.count(1) / total,
    }


def total_variation_distance(
    p: dict[int, float], q: dict[int, float]
) -> float:
    """
    TV distance between two discrete distributions over outcomes {0, 1}.
    Range: [0, 1]. 0 = identical, 1 = disjoint support.
    """
    keys = set(p) | set(q)
    return 0.5 * sum(abs(p.get(k, 0.0) - q.get(k, 0.0)) for k in keys)


def measurement_deviation(
    observed_outcomes: Sequence[int],
    expected_p0: float,
) -> float:
    """
    TV distance between the observed outcome distribution and the
    baseline expectation. Uses total_variation_distance under the hood.
    """
    observed = outcome_probabilities(observed_outcomes)
    expected = {0: expected_p0, 1: 1.0 - expected_p0}
    return total_variation_distance(observed, expected)