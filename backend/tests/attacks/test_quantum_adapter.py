import numpy as np

from app.attacks.contracts import MeasurementRound
from app.attacks.quantum_adapter import (
    quantum_rounds_provider,
    validate_rounds_provider,
)


def test_provider_returns_requested_rounds():
    rounds = quantum_rounds_provider(
        np.random.default_rng(1),
        100,
        0.01,
    )

    assert len(rounds) == 100


def test_provider_returns_measurement_rounds():
    rounds = quantum_rounds_provider(
        np.random.default_rng(1),
        100,
        0.01,
    )

    assert all(isinstance(r, MeasurementRound) for r in rounds)


def test_provider_uses_valid_bases():
    rounds = quantum_rounds_provider(
        np.random.default_rng(1),
        100,
        0.01,
    )

    assert {r.basis for r in rounds} == {"X", "Y", "Z"}


def test_provider_uses_binary_results():
    rounds = quantum_rounds_provider(
        np.random.default_rng(1),
        100,
        0.01,
    )

    assert all(r.expected in (0, 1) for r in rounds)
    assert all(r.observed in (0, 1) for r in rounds)


def test_provider_is_reproducible():
    a = quantum_rounds_provider(
        np.random.default_rng(42),
        100,
        0.01,
    )

    b = quantum_rounds_provider(
        np.random.default_rng(42),
        100,
        0.01,
    )

    assert a == b


def test_provider_respects_noise():
    rounds = quantum_rounds_provider(
        np.random.default_rng(42),
        10000,
        0.1,
    )

    errors = sum(r.expected != r.observed for r in rounds)
    error_rate = errors / len(rounds)

    assert 0.07 < error_rate < 0.13


def test_provider_validation_passes():
    result = validate_rounds_provider(
        quantum_rounds_provider,
        n_rounds=200,
        natural_error_rate=0.01,
        seed=1,
        samples=10,
    )

    assert result["ok"] is True