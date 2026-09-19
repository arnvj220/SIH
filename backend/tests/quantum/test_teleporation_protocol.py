import numpy as np

from app.quantum.measurements.evidence import QuantumEvidence
from app.quantum.states.pauli_states import (
    zero_state,
    one_state,
    plus_state,
    minus_state,
    plus_i_state,
    minus_i_state,
)
from app.quantum.teleportation.protocol import teleport


def states_match_up_to_global_phase(
    state_a,
    state_b,
    tolerance=1e-10,
):
    """
    Quantum states that differ only by a global phase
    represent the same physical state.
    """
    state_a = np.asarray(state_a)
    state_b = np.asarray(state_b)

    overlap = np.vdot(state_b, state_a)

    if np.isclose(abs(overlap), 0.0):
        return False

    phase = overlap / abs(overlap)

    return np.allclose(
        state_a,
        phase * state_b,
        atol=tolerance,
    )


def test_teleport_returns_quantum_evidence():
    result = teleport(zero_state(), seed=42)

    assert isinstance(result, QuantumEvidence)


def test_teleport_zero_state():
    result = teleport(zero_state(), seed=42)

    assert states_match_up_to_global_phase(
        result.bob_state_after_correction,
        zero_state(),
    )


def test_teleport_one_state():
    result = teleport(one_state(), seed=42)

    assert states_match_up_to_global_phase(
        result.bob_state_after_correction,
        one_state(),
    )


def test_teleport_plus_state():
    result = teleport(plus_state(), seed=42)

    assert states_match_up_to_global_phase(
        result.bob_state_after_correction,
        plus_state(),
    )


def test_teleport_minus_state():
    result = teleport(minus_state(), seed=42)

    assert states_match_up_to_global_phase(
        result.bob_state_after_correction,
        minus_state(),
    )


def test_teleport_plus_i_state():
    result = teleport(plus_i_state(), seed=42)

    assert states_match_up_to_global_phase(
        result.bob_state_after_correction,
        plus_i_state(),
    )


def test_teleport_minus_i_state():
    result = teleport(minus_i_state(), seed=42)

    assert states_match_up_to_global_phase(
        result.bob_state_after_correction,
        minus_i_state(),
    )


def test_measurement_bits_are_two_bits():
    result = teleport(plus_state(), seed=42)

    assert result.measurement_bits in {
        "00",
        "01",
        "10",
        "11",
    }


def test_correction_bits_match_measurement_bits():
    result = teleport(plus_state(), seed=42)

    assert result.correction_bits == result.measurement_bits


def test_correction_operator_matches_measurement():
    expected = {
        "00": "I",
        "01": "X",
        "10": "Z",
        "11": "XZ",
    }

    result = teleport(plus_state(), seed=42)

    assert (
        result.correction_operator
        == expected[result.measurement_bits]
    )


def test_before_and_after_correction_are_available():
    result = teleport(plus_i_state(), seed=42)

    assert result.bob_state_before_correction.shape == (2,)
    assert result.bob_state_after_correction.shape == (2,)


def test_teleportation_is_reproducible_with_seed():
    result_1 = teleport(plus_i_state(), seed=123)
    result_2 = teleport(plus_i_state(), seed=123)

    assert result_1.measurement_bits == result_2.measurement_bits

    assert np.allclose(
        result_1.bob_state_before_correction,
        result_2.bob_state_before_correction,
    )

    assert np.allclose(
        result_1.bob_state_after_correction,
        result_2.bob_state_after_correction,
    )


def test_seed_is_recorded():
    result = teleport(zero_state(), seed=123)

    assert result.seed == 123