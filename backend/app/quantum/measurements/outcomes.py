"""
Quantum measurement outcome sampling.

This module takes projective measurement probabilities and samples
actual measurement outcomes over a configurable number of shots.

Example:

    probabilities = {
        "0": 0.5,
        "1": 0.5
    }

    10,000 shots might produce:

    {
        "0": 4978,
        "1": 5022
    }

The exact result is random, but should approach the theoretical
probabilities as the number of shots increases.
"""

from __future__ import annotations

from collections import Counter

import numpy as np

from ..states.state_utils import ComplexVector
from .projective import measurement_probabilities


def sample_measurements(
    state: ComplexVector,
    basis: str,
    shots: int,
    seed: int | None = None,
) -> dict[str, int]:
    """
    Perform repeated projective measurements on a quantum state.

    Args:
        state:
            Normalized single-qubit quantum state.

        basis:
            Measurement basis: "X", "Y", or "Z".

        shots:
            Number of measurements to perform.

        seed:
            Optional random seed for reproducible experiments.

    Returns:
        Dictionary containing the number of times each outcome
        was observed.

    Example:

        sample_measurements(
            zero_state(),
            "Z",
            shots=1000,
            seed=42,
        )

        might return:

        {
            "0": 1000,
            "1": 0
        }
    """

    if not isinstance(shots, int):
        raise ValueError("shots must be an integer.")

    if shots <= 0:
        raise ValueError("shots must be greater than zero.")

    probabilities = measurement_probabilities(
        state,
        basis,
    )

    rng = np.random.default_rng(seed)

    outcomes = list(probabilities.keys())
    probabilities_array = np.array(
        list(probabilities.values()),
        dtype=float,
    )

    sampled = rng.choice(
        outcomes,
        size=shots,
        p=probabilities_array,
    )

    counts = Counter(sampled)

    # Return every possible outcome, even if it occurred zero times.
    return {
        outcome: int(counts.get(outcome, 0))
        for outcome in outcomes
    }