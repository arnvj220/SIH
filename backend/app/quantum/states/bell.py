"""
Bell-state generation for the quantum simulation layer.

Bell states:

    |Φ+> = (|00> + |11>) / √2
    |Φ-> = (|00> - |11>) / √2
    |Ψ+> = (|01> + |10>) / √2
    |Ψ-> = (|01> - |10>) / √2

The default construction starts from |00> and applies:

    H ⊗ I
    CNOT
"""

from __future__ import annotations

import numpy as np

from ..gates import (
    CNOT,
    HADAMARD,
    IDENTITY,
    PAULI_X,
    PAULI_Z,
)
from .pauli_states import zero_state
from .state_utils import ComplexVector, apply_gate, tensor_product


def phi_plus() -> ComplexVector:
    """
    Generate the Bell state |Φ+>.

        |Φ+> = (|00> + |11>) / √2
    """

    state = tensor_product(
        zero_state(),
        zero_state(),
    )

    hadamard_first = np.kron(
        HADAMARD,
        IDENTITY,
    )

    state = apply_gate(hadamard_first, state)
    state = apply_gate(CNOT, state)

    return state


def phi_minus() -> ComplexVector:
    """
    Generate the Bell state |Φ->.

        |Φ-> = (|00> - |11>) / √2
    """

    state = phi_plus()

    # Apply Z to the first qubit.
    z_first = np.kron(
        PAULI_Z,
        IDENTITY,
    )

    return apply_gate(z_first, state)


def psi_plus() -> ComplexVector:
    """
    Generate the Bell state |Ψ+>.

        |Ψ+> = (|01> + |10>) / √2
    """

    state = phi_plus()

    # Apply X to the second qubit.
    x_second = np.kron(
        IDENTITY,
        PAULI_X,
    )

    return apply_gate(x_second, state)


def psi_minus() -> ComplexVector:
    """
    Generate the Bell state |Ψ->.

        |Ψ-> = (|01> - |10>) / √2
    """

    state = psi_plus()

    # Apply Z to the first qubit.
    z_first = np.kron(
        PAULI_Z,
        IDENTITY,
    )

    return apply_gate(z_first, state)


def get_bell_state(name: str) -> ComplexVector:
    """
    Return a Bell state by name.

    Supported names:
        phi_plus
        phi_minus
        psi_plus
        psi_minus
    """

    states = {
        "phi_plus": phi_plus,
        "phi_minus": phi_minus,
        "psi_plus": psi_plus,
        "psi_minus": psi_minus,
    }

    name = name.lower()

    if name not in states:
        raise ValueError(
            "Unknown Bell state. "
            "Expected one of: phi_plus, phi_minus, "
            "psi_plus, psi_minus."
        )

    return states[name]()