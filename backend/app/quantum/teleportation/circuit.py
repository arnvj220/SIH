"""
Quantum teleportation circuit construction.

Qubit ordering:

    q0 = Alice's unknown state
    q1 = Alice's Bell-pair qubit
    q2 = Bob's Bell-pair qubit

The circuit prepares the Bell pair and performs the
entangling operations required before measurement.
"""

from __future__ import annotations

import numpy as np

from ..gates import CNOT, HADAMARD
from ..states.pauli_states import zero_state
from ..states.state_utils import (
    ComplexVector,
    apply_gate,
    tensor_product,
)


def prepare_initial_state(
    unknown_state: ComplexVector,
) -> ComplexVector:
    """
    Prepare the three-qubit state:

        |ψ> ⊗ |0> ⊗ |0>

    where |ψ> is Alice's unknown state.
    """
    return tensor_product(
        tensor_product(unknown_state, zero_state()),
        zero_state(),
    )


def create_bell_pair(state: ComplexVector) -> ComplexVector:
    """
    Create a Bell pair between q1 and q2.

    Applies:
        H on q1
        CNOT(q1, q2)
    """
    # H on q1:
    # I ⊗ H ⊗ I
    identity = np.eye(2, dtype=np.complex128)

    h_q1 = np.kron(
        np.kron(identity, HADAMARD),
        identity,
    )

    state = apply_gate(h_q1, state)

    # CNOT(q1, q2)
    # The existing CNOT acts on adjacent qubits q1 and q2.
    # We construct the 3-qubit version explicitly.
    cnot_q1_q2 = np.kron(identity, CNOT)

    return apply_gate(cnot_q1_q2, state)


def entangle_unknown_with_bell(
    state: ComplexVector,
) -> ComplexVector:
    """
    Perform Alice's teleportation entangling operations.

    Applies:
        CNOT(q0, q1)
        H(q0)
    """
    identity = np.eye(2, dtype=np.complex128)

    # CNOT(q0, q1) ⊗ I
    cnot_q0_q1 = np.kron(CNOT, identity)

    state = apply_gate(cnot_q0_q1, state)

    # H(q0) ⊗ I ⊗ I
    h_q0 = np.kron(
        np.kron(HADAMARD, identity),
        identity,
    )

    return apply_gate(h_q0, state)


def prepare_teleportation_state(
    unknown_state: ComplexVector,
) -> ComplexVector:
    """
    Run the quantum-state preparation portion of teleportation.

    This does NOT perform measurement or Pauli correction.

    Returns:
        The three-qubit state immediately before Alice's
        two-qubit measurement.
    """
    state = prepare_initial_state(unknown_state)
    state = create_bell_pair(state)
    state = entangle_unknown_with_bell(state)

    return state