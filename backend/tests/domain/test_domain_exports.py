"""Tests for the public surface of app.models.domain."""

import pytest

from app.models import domain

EXPECTED_EXPORTS = {
    "AlertSeverity",
    "AlertStatus",
    "SecurityAlert",
    "AttackRequest",
    "AttackResult",
    "AttackType",
    "ExperimentConfig",
    "ExperimentResult",
    "Measurement",
    "Signature",
    "VerificationDecision",
    "VerificationRequest",
    "VerificationResult",
}


def test_all_lists_the_expected_names():
    assert set(domain.__all__) == EXPECTED_EXPORTS


def test_all_has_no_duplicates():
    assert len(domain.__all__) == len(set(domain.__all__))


@pytest.mark.parametrize("name", sorted(EXPECTED_EXPORTS))
def test_every_exported_name_is_importable(name):
    assert getattr(domain, name) is not None
