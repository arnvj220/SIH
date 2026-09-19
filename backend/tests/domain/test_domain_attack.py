"""Tests for app.models.domain.attack."""

import dataclasses

import pytest

from app.models.domain import AttackRequest, AttackResult, AttackType


class TestAttackType:
    def test_has_exactly_the_expected_members(self):
        assert {member.value for member in AttackType} == {
            "FORGERY",
            "REPLAY",
            "IMPERSONATION",
            "CHANNEL_MANIPULATION",
        }

    def test_is_a_string_enum(self):
        assert AttackType.FORGERY == "FORGERY"
        assert isinstance(AttackType.REPLAY, str)


class TestAttackRequest:
    def test_defaults(self):
        request = AttackRequest(attack_type=AttackType.FORGERY)

        assert request.parameters == {}
        assert request.seed == 0

    def test_carries_parameters_and_seed(self):
        request = AttackRequest(
            attack_type=AttackType.REPLAY,
            parameters={"mode": "stale_nonce"},
            seed=42,
        )

        assert request.attack_type is AttackType.REPLAY
        assert request.parameters == {"mode": "stale_nonce"}
        assert request.seed == 42

    def test_parameters_default_is_not_shared_between_instances(self):
        first = AttackRequest(attack_type=AttackType.FORGERY)
        second = AttackRequest(attack_type=AttackType.FORGERY)

        first.parameters["mode"] = "signature_alter"

        assert second.parameters == {}

    def test_is_frozen(self):
        request = AttackRequest(attack_type=AttackType.FORGERY)

        with pytest.raises(dataclasses.FrozenInstanceError):
            request.seed = 1


class TestAttackResult:
    def build(self, **overrides):
        values = {
            "attack_id": "atk_1",
            "attack_type": AttackType.FORGERY,
            "is_attack": True,
            "expected_threat": "FORGERY",
        }
        values.update(overrides)
        return AttackResult(**values)

    def test_defaults(self):
        result = self.build()

        assert result.role == "attack"
        assert result.evidence == {}
        assert result.metadata == {}

    def test_carries_required_fields(self):
        result = self.build()

        assert result.attack_id == "atk_1"
        assert result.attack_type is AttackType.FORGERY
        assert result.is_attack is True
        assert result.expected_threat == "FORGERY"

    def test_supports_control_samples(self):
        result = self.build(is_attack=False, expected_threat="NONE", role="control")

        assert result.is_attack is False
        assert result.role == "control"
        assert result.expected_threat == "NONE"

    def test_mutable_defaults_are_not_shared_between_instances(self):
        first = self.build()
        second = self.build()

        first.evidence["tampered"] = True
        first.metadata["run"] = 1

        assert second.evidence == {}
        assert second.metadata == {}

    def test_is_frozen(self):
        result = self.build()

        with pytest.raises(dataclasses.FrozenInstanceError):
            result.is_attack = False
