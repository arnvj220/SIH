import numpy as np
import pytest

from app.quantum.measurements.outcomes import (
    sample_measurements,
)

from app.quantum.states.pauli_states import (
    zero_state,
    one_state,
    plus_state,
    minus_state,
)


# ============================================================
# Deterministic Measurements
# ============================================================

def test_zero_state_z_measurement_is_always_zero():
    counts = sample_measurements(
        zero_state(),
        "Z",
        shots=1000,
        seed=42,
    )

    assert counts["0"] == 1000
    assert counts["1"] == 0


def test_one_state_z_measurement_is_always_one():
    counts = sample_measurements(
        one_state(),
        "Z",
        shots=1000,
        seed=42,
    )

    assert counts["0"] == 0
    assert counts["1"] == 1000


def test_plus_state_x_measurement_is_always_plus():
    counts = sample_measurements(
        plus_state(),
        "X",
        shots=1000,
        seed=42,
    )

    assert counts["+"] == 1000
    assert counts["-"] == 0


def test_minus_state_x_measurement_is_always_minus():
    counts = sample_measurements(
        minus_state(),
        "X",
        shots=1000,
        seed=42,
    )

    assert counts["+"] == 0
    assert counts["-"] == 1000


# ============================================================
# Shot Count
# ============================================================

def test_total_number_of_outcomes_equals_shots():
    shots = 5000

    counts = sample_measurements(
        zero_state(),
        "Z",
        shots=shots,
        seed=42,
    )

    assert sum(counts.values()) == shots


# ============================================================
# Random Measurement Distribution
# ============================================================

def test_zero_state_x_measurement_is_approximately_fifty_fifty():
    shots = 10000

    counts = sample_measurements(
        zero_state(),
        "X",
        shots=shots,
        seed=42,
    )

    probability_plus = counts["+"] / shots
    probability_minus = counts["-"] / shots

    assert np.isclose(
        probability_plus,
        0.5,
        atol=0.03,
    )

    assert np.isclose(
        probability_minus,
        0.5,
        atol=0.03,
    )


# ============================================================
# Reproducibility
# ============================================================

def test_same_seed_produces_same_results():
    result_a = sample_measurements(
        zero_state(),
        "X",
        shots=1000,
        seed=42,
    )

    result_b = sample_measurements(
        zero_state(),
        "X",
        shots=1000,
        seed=42,
    )

    assert result_a == result_b


def test_different_seed_can_produce_different_results():
    result_a = sample_measurements(
        zero_state(),
        "X",
        shots=1000,
        seed=42,
    )

    result_b = sample_measurements(
        zero_state(),
        "X",
        shots=1000,
        seed=123,
    )

    assert result_a != result_b


# ============================================================
# Input Validation
# ============================================================

def test_shots_must_be_positive():
    with pytest.raises(ValueError):
        sample_measurements(
            zero_state(),
            "Z",
            shots=0,
        )


def test_negative_shots_are_rejected():
    with pytest.raises(ValueError):
        sample_measurements(
            zero_state(),
            "Z",
            shots=-10,
        )


def test_non_integer_shots_are_rejected():
    with pytest.raises(ValueError):
        sample_measurements(
            zero_state(),
            "Z",
            shots=100.5,
        )