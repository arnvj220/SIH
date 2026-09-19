import numpy as np
import pytest

from app.quantum.states.pauli_states import (
    zero_state,
    one_state,
    plus_state,
    minus_state,
    plus_i_state,
    minus_i_state,
    get_pauli_eigenstate,
)


# ============================================================
# Z / Computational Basis
# ============================================================

def test_zero_state():
    expected = np.array([1, 0], dtype=np.complex128)

    assert np.allclose(zero_state(), expected)


def test_one_state():
    expected = np.array([0, 1], dtype=np.complex128)

    assert np.allclose(one_state(), expected)


# ============================================================
# X Eigenstates
# ============================================================

def test_plus_state():
    expected = np.array(
        [1 / np.sqrt(2), 1 / np.sqrt(2)],
        dtype=np.complex128,
    )

    assert np.allclose(plus_state(), expected)


def test_minus_state():
    expected = np.array(
        [1 / np.sqrt(2), -1 / np.sqrt(2)],
        dtype=np.complex128,
    )

    assert np.allclose(minus_state(), expected)


# ============================================================
# Y Eigenstates
# ============================================================

def test_plus_i_state():
    expected = np.array(
        [1 / np.sqrt(2), 1j / np.sqrt(2)],
        dtype=np.complex128,
    )

    assert np.allclose(plus_i_state(), expected)


def test_minus_i_state():
    expected = np.array(
        [1 / np.sqrt(2), -1j / np.sqrt(2)],
        dtype=np.complex128,
    )

    assert np.allclose(minus_i_state(), expected)


# ============================================================
# Normalization
# ============================================================

@pytest.mark.parametrize(
    "state_function",
    [
        zero_state,
        one_state,
        plus_state,
        minus_state,
        plus_i_state,
        minus_i_state,
    ],
)
def test_all_states_are_normalized(state_function):
    state = state_function()

    probability = np.sum(np.abs(state) ** 2)

    assert np.isclose(probability, 1.0)


# ============================================================
# Generic Pauli Eigenstate Lookup
# ============================================================

@pytest.mark.parametrize(
    "pauli, eigenvalue, expected_function",
    [
        ("Z", +1, zero_state),
        ("Z", -1, one_state),
        ("X", +1, plus_state),
        ("X", -1, minus_state),
        ("Y", +1, plus_i_state),
        ("Y", -1, minus_i_state),
    ],
)
def test_get_pauli_eigenstate(
    pauli,
    eigenvalue,
    expected_function,
):
    actual = get_pauli_eigenstate(pauli, eigenvalue)
    expected = expected_function()

    assert np.allclose(actual, expected)


def test_pauli_operator_is_case_insensitive():
    assert np.allclose(
        get_pauli_eigenstate("x", +1),
        plus_state(),
    )


# ============================================================
# Invalid Inputs
# ============================================================

def test_invalid_pauli_operator():
    with pytest.raises(ValueError):
        get_pauli_eigenstate("A", +1)


def test_invalid_eigenvalue():
    with pytest.raises(ValueError):
        get_pauli_eigenstate("X", 0)


# ============================================================
# Actual Eigenvalue Equations
# ============================================================

def test_z_eigenstates():
    Z = np.array(
        [
            [1, 0],
            [0, -1],
        ],
        dtype=np.complex128,
    )

    assert np.allclose(
        Z @ zero_state(),
        +zero_state(),
    )

    assert np.allclose(
        Z @ one_state(),
        -one_state(),
    )


def test_x_eigenstates():
    X = np.array(
        [
            [0, 1],
            [1, 0],
        ],
        dtype=np.complex128,
    )

    assert np.allclose(
        X @ plus_state(),
        +plus_state(),
    )

    assert np.allclose(
        X @ minus_state(),
        -minus_state(),
    )


def test_y_eigenstates():
    Y = np.array(
        [
            [0, -1j],
            [1j, 0],
        ],
        dtype=np.complex128,
    )

    assert np.allclose(
        Y @ plus_i_state(),
        +plus_i_state(),
    )

    assert np.allclose(
        Y @ minus_i_state(),
        -minus_i_state(),
    )