import numpy as np
import pytest

from app.quantum.states.bell import (
    phi_plus,
    phi_minus,
    psi_plus,
    psi_minus,
    get_bell_state,
)


SQRT_HALF = 1 / np.sqrt(2)


# ============================================================
# Bell State Definitions
# ============================================================

def test_phi_plus():
    expected = np.array(
        [SQRT_HALF, 0, 0, SQRT_HALF],
        dtype=np.complex128,
    )

    assert np.allclose(phi_plus(), expected)


def test_phi_minus():
    expected = np.array(
        [SQRT_HALF, 0, 0, -SQRT_HALF],
        dtype=np.complex128,
    )

    assert np.allclose(phi_minus(), expected)


def test_psi_plus():
    expected = np.array(
        [0, SQRT_HALF, SQRT_HALF, 0],
        dtype=np.complex128,
    )

    assert np.allclose(psi_plus(), expected)


def test_psi_minus():
    expected = np.array(
        [0, SQRT_HALF, -SQRT_HALF, 0],
        dtype=np.complex128,
    )

    assert np.allclose(psi_minus(), expected)


# ============================================================
# Normalization
# ============================================================

@pytest.mark.parametrize(
    "bell_state",
    [
        phi_plus,
        phi_minus,
        psi_plus,
        psi_minus,
    ],
)
def test_bell_states_are_normalized(bell_state):
    state = bell_state()

    assert np.isclose(np.linalg.norm(state), 1.0)


# ============================================================
# Bell State Lookup
# ============================================================

@pytest.mark.parametrize(
    "name, expected_function",
    [
        ("phi_plus", phi_plus),
        ("phi_minus", phi_minus),
        ("psi_plus", psi_plus),
        ("psi_minus", psi_minus),
    ],
)
def test_get_bell_state(name, expected_function):
    assert np.allclose(
        get_bell_state(name),
        expected_function(),
    )


def test_bell_state_lookup_is_case_insensitive():
    assert np.allclose(
        get_bell_state("PHI_PLUS"),
        phi_plus(),
    )


def test_invalid_bell_state():
    with pytest.raises(ValueError):
        get_bell_state("not_a_bell_state")


# ============================================================
# Bell States Are Distinct
# ============================================================

def test_bell_states_are_distinct():
    states = [
        phi_plus(),
        phi_minus(),
        psi_plus(),
        psi_minus(),
    ]

    for i in range(len(states)):
        for j in range(i + 1, len(states)):
            assert not np.allclose(states[i], states[j])