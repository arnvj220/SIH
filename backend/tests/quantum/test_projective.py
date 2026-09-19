import numpy as np
import pytest

from app.quantum.measurements.projective import (
    measurement_probabilities,
)

from app.quantum.states.pauli_states import (
    zero_state,
    one_state,
    plus_state,
    minus_state,
    plus_i_state,
    minus_i_state,
)


# ============================================================
# Z-Basis Measurements
# ============================================================

def test_zero_measured_in_z_basis():
    probabilities = measurement_probabilities(
        zero_state(),
        "Z",
    )

    assert np.isclose(probabilities["0"], 1.0)
    assert np.isclose(probabilities["1"], 0.0)


def test_one_measured_in_z_basis():
    probabilities = measurement_probabilities(
        one_state(),
        "Z",
    )

    assert np.isclose(probabilities["0"], 0.0)
    assert np.isclose(probabilities["1"], 1.0)


# ============================================================
# X-Basis Measurements
# ============================================================

def test_plus_measured_in_x_basis():
    probabilities = measurement_probabilities(
        plus_state(),
        "X",
    )

    assert np.isclose(probabilities["+"], 1.0)
    assert np.isclose(probabilities["-"], 0.0)


def test_minus_measured_in_x_basis():
    probabilities = measurement_probabilities(
        minus_state(),
        "X",
    )

    assert np.isclose(probabilities["+"], 0.0)
    assert np.isclose(probabilities["-"], 1.0)


# ============================================================
# Y-Basis Measurements
# ============================================================

def test_plus_i_measured_in_y_basis():
    probabilities = measurement_probabilities(
        plus_i_state(),
        "Y",
    )

    assert np.isclose(probabilities["+i"], 1.0)
    assert np.isclose(probabilities["-i"], 0.0)


def test_minus_i_measured_in_y_basis():
    probabilities = measurement_probabilities(
        minus_i_state(),
        "Y",
    )

    assert np.isclose(probabilities["+i"], 0.0)
    assert np.isclose(probabilities["-i"], 1.0)


# ============================================================
# Superposition Measurements
# ============================================================

def test_zero_measured_in_x_basis_is_50_50():
    probabilities = measurement_probabilities(
        zero_state(),
        "X",
    )

    assert np.isclose(probabilities["+"], 0.5)
    assert np.isclose(probabilities["-"], 0.5)


def test_one_measured_in_x_basis_is_50_50():
    probabilities = measurement_probabilities(
        one_state(),
        "X",
    )

    assert np.isclose(probabilities["+"], 0.5)
    assert np.isclose(probabilities["-"], 0.5)


def test_zero_measured_in_y_basis_is_50_50():
    probabilities = measurement_probabilities(
        zero_state(),
        "Y",
    )

    assert np.isclose(probabilities["+i"], 0.5)
    assert np.isclose(probabilities["-i"], 0.5)


# ============================================================
# Probability Distribution
# ============================================================

@pytest.mark.parametrize(
    "state",
    [
        zero_state(),
        one_state(),
        plus_state(),
        minus_state(),
        plus_i_state(),
        minus_i_state(),
    ],
)
@pytest.mark.parametrize("basis", ["X", "Y", "Z"])
def test_probabilities_sum_to_one(state, basis):
    probabilities = measurement_probabilities(
        state,
        basis,
    )

    assert np.isclose(
        sum(probabilities.values()),
        1.0,
    )


# ============================================================
# Basis Validation
# ============================================================

def test_invalid_measurement_basis():
    with pytest.raises(ValueError):
        measurement_probabilities(
            zero_state(),
            "A",
        )


def test_basis_is_case_insensitive():
    lower = measurement_probabilities(
        zero_state(),
        "z",
    )

    upper = measurement_probabilities(
        zero_state(),
        "Z",
    )

    assert lower == upper


# ============================================================
# State Validation
# ============================================================

def test_rejects_non_normalized_state():
    state = np.array(
        [1, 1],
        dtype=np.complex128,
    )

    with pytest.raises(ValueError):
        measurement_probabilities(
            state,
            "Z",
        )


def test_rejects_multi_qubit_state_for_now():
    state = np.array(
        [1, 0, 0, 0],
        dtype=np.complex128,
    )

    with pytest.raises(ValueError):
        measurement_probabilities(
            state,
            "Z",
        )