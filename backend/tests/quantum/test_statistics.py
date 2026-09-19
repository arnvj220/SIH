import numpy as np
import pytest

from app.quantum.measurements.statistics import (
    MeasurementStatistics,
    calculate_probabilities,
    create_measurement_statistics,
)


# ============================================================
# Probability Calculation
# ============================================================

def test_calculate_probabilities():
    counts = {
        "0": 700,
        "1": 300,
    }

    probabilities = calculate_probabilities(counts)

    assert np.isclose(probabilities["0"], 0.7)
    assert np.isclose(probabilities["1"], 0.3)


def test_probabilities_sum_to_one():
    counts = {
        "0": 250,
        "1": 750,
    }

    probabilities = calculate_probabilities(counts)

    assert np.isclose(
        sum(probabilities.values()),
        1.0,
    )


def test_deterministic_distribution():
    counts = {
        "0": 1000,
        "1": 0,
    }

    probabilities = calculate_probabilities(counts)

    assert probabilities["0"] == 1.0
    assert probabilities["1"] == 0.0


# ============================================================
# MeasurementStatistics
# ============================================================

def test_create_measurement_statistics():
    counts = {
        "0": 600,
        "1": 400,
    }

    result = create_measurement_statistics(
        basis="Z",
        counts=counts,
    )

    assert isinstance(result, MeasurementStatistics)

    assert result.basis == "Z"
    assert result.shots == 1000
    assert result.counts == counts

    assert np.isclose(
        result.probabilities["0"],
        0.6,
    )

    assert np.isclose(
        result.probabilities["1"],
        0.4,
    )


def test_basis_is_normalized_to_uppercase():
    result = create_measurement_statistics(
        basis="x",
        counts={
            "+": 500,
            "-": 500,
        },
    )

    assert result.basis == "X"


# ============================================================
# Validation
# ============================================================

def test_empty_counts_are_rejected():
    with pytest.raises(ValueError):
        calculate_probabilities({})


def test_zero_total_counts_are_rejected():
    with pytest.raises(ValueError):
        calculate_probabilities(
            {
                "0": 0,
                "1": 0,
            }
        )


def test_negative_counts_are_rejected():
    with pytest.raises(ValueError):
        calculate_probabilities(
            {
                "0": 100,
                "1": -1,
            }
        )


def test_invalid_measurement_basis():
    with pytest.raises(ValueError):
        create_measurement_statistics(
            basis="A",
            counts={
                "0": 100,
                "1": 0,
            },
        )


# ============================================================
# Different Measurement Bases
# ============================================================

@pytest.mark.parametrize(
    "basis, counts",
    [
        ("X", {"+": 500, "-": 500}),
        ("Y", {"+i": 700, "-i": 300}),
        ("Z", {"0": 900, "1": 100}),
    ],
)
def test_supported_bases(basis, counts):
    result = create_measurement_statistics(
        basis=basis,
        counts=counts,
    )

    assert result.basis == basis
    assert result.shots == sum(counts.values())
    assert np.isclose(
        sum(result.probabilities.values()),
        1.0,
    )