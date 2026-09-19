import numpy as np

from app.quantum.gates import CNOT, HADAMARD
from app.quantum.states.pauli_states import (
    zero_state,
    one_state,
    plus_state,
)
from app.quantum.states.state_utils import apply_gate
from app.quantum.teleportation.circuit import (
    prepare_initial_state,
    create_bell_pair,
    entangle_unknown_with_bell,
    prepare_teleportation_state,
)


def test_initial_state_has_three_qubits():
    state = prepare_initial_state(zero_state())

    assert state.shape == (8,)


def test_initial_state_is_normalized():
    state = prepare_initial_state(plus_state())

    assert np.isclose(np.linalg.norm(state), 1.0)


def test_initial_state_zero_is_000():
    state = prepare_initial_state(zero_state())

    expected = np.zeros(8, dtype=np.complex128)
    expected[0] = 1.0

    assert np.allclose(state, expected)


def test_initial_state_one_is_100():
    state = prepare_initial_state(one_state())

    expected = np.zeros(8, dtype=np.complex128)
    expected[4] = 1.0

    assert np.allclose(state, expected)


def test_bell_pair_creation_from_zero():
    state = prepare_initial_state(zero_state())
    state = create_bell_pair(state)

    expected = np.zeros(8, dtype=np.complex128)

    # |000> + |011>
    expected[0] = 1 / np.sqrt(2)
    expected[3] = 1 / np.sqrt(2)

    assert np.allclose(state, expected)


def test_bell_pair_creation_preserves_normalization():
    state = prepare_initial_state(plus_state())
    state = create_bell_pair(state)

    assert np.isclose(np.linalg.norm(state), 1.0)


def test_entangling_operations_preserve_normalization():
    state = prepare_initial_state(plus_state())
    state = create_bell_pair(state)
    state = entangle_unknown_with_bell(state)

    assert np.isclose(np.linalg.norm(state), 1.0)


def test_full_pre_measurement_state_has_eight_amplitudes():
    state = prepare_teleportation_state(plus_state())

    assert state.shape == (8,)
    assert np.isclose(np.linalg.norm(state), 1.0)