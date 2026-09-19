"""
Projective measurement utilities.

This module calculates measurement probabilities for single-qubit
states in the X, Y and Z Pauli bases.

Measurement does not yet handle repeated shots or statistical
aggregation. Those responsibilities belong to the measurement
outcome/statistics modules.
"""

from __future__ import annotations

import numpy as np

from ..states.state_utils import ComplexVector, validate_state
from ..states.pauli_states import (
    zero_state,
    one_state,
    plus_state,
    minus_state,
    plus_i_state,
    minus_i_state,
)


# ---------------------------------------------------------------------------
# Measurement bases
# ---------------------------------------------------------------------------

MEASUREMENT_BASES = {
    "Z": {
        "0": zero_state(),
        "1": one_state(),
    },
    "X": {
        "+": plus_state(),
        "-": minus_state(),
    },
    "Y": {
        "+i": plus_i_state(),
        "-i": minus_i_state(),
    },
}


# ---------------------------------------------------------------------------
# Projective measurement probabilities
# ---------------------------------------------------------------------------

def measurement_probabilities(
    state: ComplexVector,
    basis: str,
) -> dict[str, float]:
    """
    Calculate projective measurement probabilities.

    For each basis state |b_i>:

        P(b_i) = |<b_i|ψ>|²

    Args:
        state:
            Normalized single-qubit state vector.

        basis:
            Measurement basis: "X", "Y", or "Z".

    Returns:
        Dictionary mapping measurement outcomes to probabilities.

    Example:

        measurement_probabilities(
            zero_state(),
            "Z"
        )

        returns approximately:

        {
            "0": 1.0,
            "1": 0.0
        }
    """

    state = np.asarray(state, dtype=np.complex128)

    validate_state(state)

    if state.size != 2:
        raise ValueError(
            "Projective measurement currently supports "
            "single-qubit states only."
        )

    basis = basis.upper()

    if basis not in MEASUREMENT_BASES:
        raise ValueError(
            "Measurement basis must be X, Y, or Z."
        )

    probabilities = {}

    for outcome, basis_state in MEASUREMENT_BASES[basis].items():
        # <basis_state | state>
        amplitude = np.vdot(basis_state, state)

        # Born rule:
        # P(outcome) = |amplitude|²
        probability = float(np.abs(amplitude) ** 2)

        probabilities[outcome] = probability

    # Numerical floating-point errors can produce values such as
    # 1.0000000000000002, so normalize the final distribution.
    total = sum(probabilities.values())

    if np.isclose(total, 0.0):
        raise ValueError(
            "Measurement probabilities sum to zero."
        )

    probabilities = {
        outcome: probability / total
        for outcome, probability in probabilities.items()
    }

    return probabilities