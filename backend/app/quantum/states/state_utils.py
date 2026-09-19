"""
Core utilities for representing and manipulating quantum states.

This module provides the low-level state-vector operations used by the
quantum simulation layer.

Convention:
    A single qubit is represented as a 2-element complex vector:

        |ψ> = α|0> + β|1>
        |ψ> = [α, β]

    For n qubits, the state vector has 2^n amplitudes.

Basis ordering:
    |00...0>, |00...1>, ..., |11...1>

All state vectors are expected to be normalized:

    Σ |α_i|² = 1
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


ComplexVector = NDArray[np.complex128]
ComplexMatrix = NDArray[np.complex128]


# ---------------------------------------------------------------------------
# State validation
# ---------------------------------------------------------------------------

def validate_state(state: ComplexVector, tolerance: float = 1e-10) -> None:
    """
    Validate that a vector is a valid quantum state.

    A valid state must:
    - be one-dimensional
    - contain at least one amplitude
    - have a dimension that is a power of two
    - be normalized

    Raises:
        ValueError: If the state is invalid.
    """

    state = np.asarray(state, dtype=np.complex128)

    if state.ndim != 1:
        raise ValueError("Quantum state must be a one-dimensional vector.")

    if state.size == 0:
        raise ValueError("Quantum state cannot be empty.")

    # A system of n qubits has exactly 2^n amplitudes.
    if state.size & (state.size - 1):
        raise ValueError(
            "Quantum state dimension must be a power of two."
        )

    norm = np.linalg.norm(state)

    if not np.isclose(norm, 1.0, atol=tolerance):
        raise ValueError(
            f"Quantum state must be normalized. "
            f"Received norm={norm:.12f}."
        )


# ---------------------------------------------------------------------------
# State normalization
# ---------------------------------------------------------------------------

def normalize_state(state: ComplexVector) -> ComplexVector:
    """
    Normalize a quantum state vector.

    Given:

        |ψ> = [α, β]

    returns:

        |ψ_normalized> = |ψ> / ||ψ||

    Args:
        state: State vector to normalize.

    Returns:
        Normalized complex state vector.

    Raises:
        ValueError: If the state is empty or has zero norm.
    """

    state = np.asarray(state, dtype=np.complex128)

    norm = np.linalg.norm(state)

    if np.isclose(norm, 0.0):
        raise ValueError("Cannot normalize a zero vector.")

    return state / norm


# ---------------------------------------------------------------------------
# Tensor product
# ---------------------------------------------------------------------------

def tensor_product(
    state_a: ComplexVector,
    state_b: ComplexVector,
) -> ComplexVector:
    """
    Combine two quantum states using the tensor product.

    Example:

        |0> ⊗ |1> = |01>

    With:

        |0> = [1, 0]
        |1> = [0, 1]

    the result is:

        [0, 1, 0, 0]

    corresponding to:

        |00>, |01>, |10>, |11>

    Args:
        state_a: First quantum state.
        state_b: Second quantum state.

    Returns:
        Combined quantum state.
    """

    validate_state(state_a)
    validate_state(state_b)

    return np.kron(state_a, state_b).astype(np.complex128)


# ---------------------------------------------------------------------------
# Gate application
# ---------------------------------------------------------------------------

def apply_gate(
    gate: ComplexMatrix,
    state: ComplexVector,
) -> ComplexVector:
    """
    Apply a quantum gate to a state vector.

    Mathematically:

        |ψ'> = U|ψ>

    where:
        U  = quantum gate matrix
        |ψ> = current state
        |ψ'> = resulting state

    Args:
        gate: Square complex gate matrix.
        state: Quantum state vector.

    Returns:
        Resulting state vector.

    Raises:
        ValueError: If dimensions are incompatible.
    """

    gate = np.asarray(gate, dtype=np.complex128)
    state = np.asarray(state, dtype=np.complex128)

    validate_state(state)

    if gate.ndim != 2:
        raise ValueError("Quantum gate must be a two-dimensional matrix.")

    if gate.shape[0] != gate.shape[1]:
        raise ValueError("Quantum gate must be square.")

    if gate.shape[1] != state.size:
        raise ValueError(
            f"Gate dimension {gate.shape} is incompatible with "
            f"state dimension {state.size}."
        )

    result = gate @ state

    return normalize_state(result)