"""
Fundamental quantum gates used by the quantum simulation layer.

The gates implemented here are:

    I   Identity
    X   Pauli-X
    Y   Pauli-Y
    Z   Pauli-Z
    H   Hadamard
    CNOT Controlled-NOT

Single-qubit gates are represented as 2x2 matrices.

CNOT is represented as a 4x4 matrix using the basis ordering:

    |00>, |01>, |10>, |11>

where the first qubit is the control and the second is the target.
"""

from __future__ import annotations

import numpy as np

from .states.state_utils import ComplexMatrix


# ---------------------------------------------------------------------------
# Single-qubit gates
# ---------------------------------------------------------------------------

IDENTITY: ComplexMatrix = np.array(
    [
        [1, 0],
        [0, 1],
    ],
    dtype=np.complex128,
)


PAULI_X: ComplexMatrix = np.array(
    [
        [0, 1],
        [1, 0],
    ],
    dtype=np.complex128,
)


PAULI_Y: ComplexMatrix = np.array(
    [
        [0, -1j],
        [1j, 0],
    ],
    dtype=np.complex128,
)


PAULI_Z: ComplexMatrix = np.array(
    [
        [1, 0],
        [0, -1],
    ],
    dtype=np.complex128,
)


HADAMARD: ComplexMatrix = (
    1 / np.sqrt(2)
) * np.array(
    [
        [1, 1],
        [1, -1],
    ],
    dtype=np.complex128,
)


# ---------------------------------------------------------------------------
# Two-qubit gates
# ---------------------------------------------------------------------------

CNOT: ComplexMatrix = np.array(
    [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 0],
    ],
    dtype=np.complex128,
)