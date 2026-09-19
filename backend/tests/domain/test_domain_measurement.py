"""Tests for app.models.domain.measurement."""

import dataclasses

import pytest

from app.models.domain import Measurement


def test_accepts_valid_round():
    measurement = Measurement(index=3, basis="Z", expected=1, observed=0)

    assert measurement.index == 3
    assert measurement.basis == "Z"
    assert measurement.expected == 1
    assert measurement.observed == 0


@pytest.mark.parametrize("basis", ["X", "Y", "Z"])
def test_accepts_every_supported_basis(basis):
    measurement = Measurement(index=0, basis=basis, expected=0, observed=0)

    assert measurement.basis == basis


@pytest.mark.parametrize("basis", ["x", "y", "z"])
def test_accepts_lowercase_basis_and_preserves_original_casing(basis):
    """Validation upper-cases before checking, but the value is stored as given."""
    measurement = Measurement(index=0, basis=basis, expected=0, observed=0)

    assert measurement.basis == basis


def test_is_error_true_when_observed_differs_from_expected():
    assert Measurement(index=0, basis="X", expected=1, observed=0).is_error is True


def test_is_error_false_when_observed_matches_expected():
    assert Measurement(index=0, basis="X", expected=1, observed=1).is_error is False


def test_rejects_negative_index():
    with pytest.raises(ValueError, match="non-negative"):
        Measurement(index=-1, basis="X", expected=0, observed=0)


def test_index_zero_is_valid():
    assert Measurement(index=0, basis="X", expected=0, observed=0).index == 0


@pytest.mark.parametrize("basis", ["A", "W", "", "XY", "1"])
def test_rejects_unsupported_basis(basis):
    with pytest.raises(ValueError, match="basis"):
        Measurement(index=0, basis=basis, expected=0, observed=0)


@pytest.mark.parametrize("expected", [-1, 2, 10])
def test_rejects_expected_outside_zero_one(expected):
    with pytest.raises(ValueError, match="Expected"):
        Measurement(index=0, basis="X", expected=expected, observed=0)


@pytest.mark.parametrize("observed", [-1, 2, 10])
def test_rejects_observed_outside_zero_one(observed):
    with pytest.raises(ValueError, match="Observed"):
        Measurement(index=0, basis="X", expected=0, observed=observed)


def test_is_frozen():
    measurement = Measurement(index=0, basis="X", expected=0, observed=0)

    with pytest.raises(dataclasses.FrozenInstanceError):
        measurement.observed = 1


def test_equality_is_by_value():
    a = Measurement(index=1, basis="Y", expected=0, observed=1)
    b = Measurement(index=1, basis="Y", expected=0, observed=1)
    c = Measurement(index=2, basis="Y", expected=0, observed=1)

    assert a == b
    assert a != c
