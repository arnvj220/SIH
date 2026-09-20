import numpy as np

from app.attacks.quantum_adapter import (
    quantum_rounds_provider,
    validate_rounds_provider,
)
from app.attacks.contracts import BASES, MeasurementRound


def test_quantum_provider_returns_correct_number_of_rounds():
    rounds = quantum_rounds_provider(
        np.random.default_rng(42),
        100,
        0.01,
    )

    assert len(rounds) == 100


def test_quantum_provider_returns_measurement_rounds():
    rounds = quantum_rounds_provider(
        np.random.default_rng(42),
        100,
        0.01,
    )

    assert all(
        isinstance(r, MeasurementRound)
        for r in rounds
    )


def test_all_three_bases_are_present():
    rounds = quantum_rounds_provider(
        np.random.default_rng(42),
        600,
        0.01,
    )

    bases = {
        r.basis
        for r in rounds
    }

    assert bases == set(BASES)


def test_expected_and_observed_are_binary():
    rounds = quantum_rounds_provider(
        np.random.default_rng(42),
        100,
        0.01,
    )

    for r in rounds:
        assert r.expected in (0, 1)
        assert r.observed in (0, 1)


def test_provider_is_reproducible():
    a = quantum_rounds_provider(
        np.random.default_rng(123),
        100,
        0.01,
    )

    b = quantum_rounds_provider(
        np.random.default_rng(123),
        100,
        0.01,
    )

    assert a == b


def test_different_seed_changes_output():
    a = quantum_rounds_provider(
        np.random.default_rng(1),
        100,
        0.01,
    )

    b = quantum_rounds_provider(
        np.random.default_rng(2),
        100,
        0.01,
    )

    assert a != b


def test_provider_validation_passes():
    result = validate_rounds_provider(
        quantum_rounds_provider,
        n_rounds=100,
        natural_error_rate=0.01,
        seed=42,
        samples=5,
    )

    assert result["ok"] is True
    assert result["bases"] == ["X", "Y", "Z"]