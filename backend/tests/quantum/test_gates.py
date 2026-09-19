import numpy as np

from app.quantum.gates import (
    IDENTITY,
    PAULI_X,
    PAULI_Y,
    PAULI_Z,
    HADAMARD,
    CNOT,
)

from app.quantum.states.pauli_states import (
    zero_state,
    one_state,
    plus_state,
    minus_state,
)

from app.quantum.states.state_utils import (
    apply_gate,
    tensor_product,
)


# ============================================================
# Matrix Properties
# ============================================================

def test_identity_matrix():
    expected = np.eye(2, dtype=np.complex128)

    assert np.allclose(IDENTITY, expected)


def test_pauli_x_matrix():
    expected = np.array(
        [
            [0, 1],
            [1, 0],
        ],
        dtype=np.complex128,
    )

    assert np.allclose(PAULI_X, expected)


def test_pauli_y_matrix():
    expected = np.array(
        [
            [0, -1j],
            [1j, 0],
        ],
        dtype=np.complex128,
    )

    assert np.allclose(PAULI_Y, expected)


def test_pauli_z_matrix():
    expected = np.array(
        [
            [1, 0],
            [0, -1],
        ],
        dtype=np.complex128,
    )

    assert np.allclose(PAULI_Z, expected)


def test_hadamard_matrix():
    expected = (1 / np.sqrt(2)) * np.array(
        [
            [1, 1],
            [1, -1],
        ],
        dtype=np.complex128,
    )

    assert np.allclose(HADAMARD, expected)


# ============================================================
# Gate Dimensions
# ============================================================

def test_single_qubit_gates_are_2x2():
    gates = [
        IDENTITY,
        PAULI_X,
        PAULI_Y,
        PAULI_Z,
        HADAMARD,
    ]

    for gate in gates:
        assert gate.shape == (2, 2)


def test_cnot_is_4x4():
    assert CNOT.shape == (4, 4)


# ============================================================
# X Gate
# ============================================================

def test_x_flips_zero_to_one():
    result = apply_gate(PAULI_X, zero_state())

    assert np.allclose(result, one_state())


def test_x_flips_one_to_zero():
    result = apply_gate(PAULI_X, one_state())

    assert np.allclose(result, zero_state())


# ============================================================
# Z Gate
# ============================================================

def test_z_keeps_zero_unchanged():
    result = apply_gate(PAULI_Z, zero_state())

    assert np.allclose(result, zero_state())


def test_z_flips_phase_of_one():
    result = apply_gate(PAULI_Z, one_state())

    expected = np.array(
        [0, -1],
        dtype=np.complex128,
    )

    assert np.allclose(result, expected)


# ============================================================
# Y Gate
# ============================================================

def test_y_on_zero():
    result = apply_gate(PAULI_Y, zero_state())

    expected = np.array(
        [0, 1j],
        dtype=np.complex128,
    )

    assert np.allclose(result, expected)


def test_y_on_one():
    result = apply_gate(PAULI_Y, one_state())

    expected = np.array(
        [-1j, 0],
        dtype=np.complex128,
    )

    assert np.allclose(result, expected)


# ============================================================
# Hadamard Gate
# ============================================================

def test_hadamard_zero_creates_plus():
    result = apply_gate(HADAMARD, zero_state())

    assert np.allclose(result, plus_state())


def test_hadamard_one_creates_minus():
    result = apply_gate(HADAMARD, one_state())

    assert np.allclose(result, minus_state())


def test_hadamard_plus_returns_zero():
    result = apply_gate(HADAMARD, plus_state())

    assert np.allclose(result, zero_state())


def test_hadamard_minus_returns_one():
    result = apply_gate(HADAMARD, minus_state())

    assert np.allclose(result, one_state())


# ============================================================
# Identity
# ============================================================

def test_identity_does_nothing():
    state = plus_state()

    result = apply_gate(IDENTITY, state)

    assert np.allclose(result, state)


# ============================================================
# CNOT
# ============================================================

def test_cnot_zero_zero():
    state = tensor_product(
        zero_state(),
        zero_state(),
    )

    result = apply_gate(CNOT, state)

    expected = np.array(
        [1, 0, 0, 0],
        dtype=np.complex128,
    )

    assert np.allclose(result, expected)


def test_cnot_zero_one():
    state = tensor_product(
        zero_state(),
        one_state(),
    )

    result = apply_gate(CNOT, state)

    expected = np.array(
        [0, 1, 0, 0],
        dtype=np.complex128,
    )

    assert np.allclose(result, expected)


def test_cnot_one_zero():
    state = tensor_product(
        one_state(),
        zero_state(),
    )

    result = apply_gate(CNOT, state)

    expected = np.array(
        [0, 0, 0, 1],
        dtype=np.complex128,
    )

    assert np.allclose(result, expected)


def test_cnot_one_one():
    state = tensor_product(
        one_state(),
        one_state(),
    )

    result = apply_gate(CNOT, state)

    expected = np.array(
        [0, 0, 1, 0],
        dtype=np.complex128,
    )

    assert np.allclose(result, expected)

def test_hadamard_then_cnot_creates_phi_plus():
    # Start with |00>
    state = tensor_product(
        zero_state(),
        zero_state(),
    )

    # Apply H to the first qubit.
    #
    # For now we construct H ⊗ I explicitly.
    hadamard_first = np.kron(
        HADAMARD,
        IDENTITY,
    )

    state = apply_gate(
        hadamard_first,
        state,
    )

    # Entangle the two qubits.
    state = apply_gate(
        CNOT,
        state,
    )

    expected = np.array(
        [
            1 / np.sqrt(2),
            0,
            0,
            1 / np.sqrt(2),
        ],
        dtype=np.complex128,
    )

    assert np.allclose(state, expected)