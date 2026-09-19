"""
Standard single-qubit states used by the quantum simulation layer.

States included:
    Computational / Z basis:
        |0>, |1>

    X-Pauli eigenstates:
        |+>, |->

    Y-Pauli eigenstates:
        |+i>, |-i>
"""

from __future__ import annotations

import numpy as np

from .state_utils import ComplexVector, normalize_state


# ---------------------------------------------------------------------------
# Computational / Z basis
# ---------------------------------------------------------------------------

def zero_state() -> ComplexVector:
    """
    Return the |0> state.

        |0> = [1, 0]
    """
    return np.array([1.0, 0.0], dtype=np.complex128)


def one_state() -> ComplexVector:
    """
    Return the |1> state.

        |1> = [0, 1]
    """
    return np.array([0.0, 1.0], dtype=np.complex128)


# ---------------------------------------------------------------------------
# X-Pauli eigenstates
# ---------------------------------------------------------------------------

def plus_state() -> ComplexVector:
    """
    Return the |+> state.

        |+> = (|0> + |1>) / sqrt(2)
    """

    return normalize_state(
        np.array([1.0, 1.0], dtype=np.complex128)
    )


def minus_state() -> ComplexVector:
    """
    Return the |-> state.

        |-> = (|0> - |1>) / sqrt(2)
    """

    return normalize_state(
        np.array([1.0, -1.0], dtype=np.complex128)
    )


# ---------------------------------------------------------------------------
# Y-Pauli eigenstates
# ---------------------------------------------------------------------------

def plus_i_state() -> ComplexVector:
    """
    Return the |+i> state.

        |+i> = (|0> + i|1>) / sqrt(2)
    """

    return normalize_state(
        np.array([1.0, 1.0j], dtype=np.complex128)
    )


def minus_i_state() -> ComplexVector:
    """
    Return the |-i> state.

        |-i> = (|0> - i|1>) / sqrt(2)
    """

    return normalize_state(
        np.array([1.0, -1.0j], dtype=np.complex128)
    )


# ---------------------------------------------------------------------------
# Generic Pauli eigenstate lookup
# ---------------------------------------------------------------------------

def get_pauli_eigenstate(
    pauli: str,
    eigenvalue: int,
) -> ComplexVector:
    """
    Return an eigenstate of a Pauli operator.

    Args:
        pauli:
            "X", "Y", or "Z".

        eigenvalue:
            +1 or -1.

    Returns:
        Corresponding Pauli eigenstate.

    Examples:
        get_pauli_eigenstate("Z", +1) -> |0>
        get_pauli_eigenstate("Z", -1) -> |1>
        get_pauli_eigenstate("X", +1) -> |+>
        get_pauli_eigenstate("X", -1) -> |->
        get_pauli_eigenstate("Y", +1) -> |+i>
        get_pauli_eigenstate("Y", -1) -> |-i>
    """

    pauli = pauli.upper()

    if eigenvalue not in (+1, -1):
        raise ValueError("Eigenvalue must be either +1 or -1.")

    states = {
        "Z": {
            +1: zero_state(),
            -1: one_state(),
        },
        "X": {
            +1: plus_state(),
            -1: minus_state(),
        },
        "Y": {
            +1: plus_i_state(),
            -1: minus_i_state(),
        },
    }

    if pauli not in states:
        raise ValueError("Pauli operator must be X, Y, or Z.")

    return states[pauli][eigenvalue]