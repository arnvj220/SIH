"""Tests for app.models.schemas.attack."""

import pytest
from pydantic import ValidationError

from app.attacks.contracts import ThreatType
from app.models.schemas.attack import (
    AttackDescription,
    AttackRequest,
    AttackResponse,
    AttackSampleResponse,
)


class TestAttackRequest:
    def payload(self, **overrides):
        values = {
            "attack_id": "atk_1",
            "attack_type": "FORGERY",
            "seed": 42,
            "parameters": {"mode": "signature_alter"},
        }
        values.update(overrides)
        return values

    def test_accepts_a_valid_payload(self):
        request = AttackRequest(**self.payload())

        assert request.attack_id == "atk_1"
        assert request.attack_type == "FORGERY"
        assert request.seed == 42
        assert request.parameters == {"mode": "signature_alter"}

    def test_defaults(self):
        request = AttackRequest(attack_id="atk_1", attack_type="FORGERY")

        assert request.seed == 0
        assert request.parameters == {}

    def test_attack_type_is_a_free_form_string_here(self):
        """The request side is not constrained to the ThreatType enum."""
        assert AttackRequest(**self.payload(attack_type="CUSTOM_SCENARIO")).attack_type == (
            "CUSTOM_SCENARIO"
        )

    @pytest.mark.parametrize("field_name", ["attack_id", "attack_type"])
    def test_rejects_empty_string_fields(self, field_name):
        with pytest.raises(ValidationError):
            AttackRequest(**self.payload(**{field_name: ""}))

    def test_rejects_attack_id_longer_than_128_chars(self):
        with pytest.raises(ValidationError):
            AttackRequest(**self.payload(attack_id="x" * 129))

    def test_rejects_attack_type_longer_than_64_chars(self):
        with pytest.raises(ValidationError):
            AttackRequest(**self.payload(attack_type="x" * 65))

    @pytest.mark.parametrize("field_name", ["attack_id", "attack_type"])
    def test_rejects_missing_required_field(self, field_name):
        values = self.payload()
        values.pop(field_name)

        with pytest.raises(ValidationError):
            AttackRequest(**values)

    def test_rejects_non_integer_seed(self):
        with pytest.raises(ValidationError):
            AttackRequest(**self.payload(seed="not-a-number"))


class TestAttackSampleResponse:
    def payload(self, **overrides):
        values = {
            "context_id": "ctx_1",
            "is_attack": True,
            "expected_threat": ThreatType.FORGERY,
            "role": "attack",
        }
        values.update(overrides)
        return values

    def test_accepts_a_valid_payload(self):
        sample = AttackSampleResponse(**self.payload())

        assert sample.context_id == "ctx_1"
        assert sample.is_attack is True
        assert sample.expected_threat is ThreatType.FORGERY
        assert sample.role == "attack"

    def test_evidence_defaults_to_empty_dict(self):
        assert AttackSampleResponse(**self.payload()).evidence == {}

    @pytest.mark.parametrize("threat", list(ThreatType))
    def test_accepts_every_threat_type(self, threat):
        assert AttackSampleResponse(**self.payload(expected_threat=threat)).expected_threat is threat

    def test_accepts_threat_as_plain_string(self):
        sample = AttackSampleResponse(**self.payload(expected_threat="REPLAY"))

        assert sample.expected_threat is ThreatType.REPLAY

    def test_rejects_unknown_threat_type(self):
        with pytest.raises(ValidationError):
            AttackSampleResponse(**self.payload(expected_threat="SPOOFING"))

    def test_supports_control_samples(self):
        sample = AttackSampleResponse(
            **self.payload(is_attack=False, expected_threat=ThreatType.NONE, role="control")
        )

        assert sample.is_attack is False
        assert sample.role == "control"

    @pytest.mark.parametrize("field_name", ["context_id", "is_attack", "expected_threat", "role"])
    def test_rejects_missing_required_field(self, field_name):
        values = self.payload()
        values.pop(field_name)

        with pytest.raises(ValidationError):
            AttackSampleResponse(**values)


class TestAttackResponse:
    def payload(self, **overrides):
        values = {
            "attack_id": "atk_1",
            "attack_type": ThreatType.FORGERY,
            "scenario_name": "forgery_signature_alter",
            "seed": 42,
            "parameters": {"mode": "signature_alter"},
            "samples": [
                {
                    "context_id": "ctx_1",
                    "is_attack": True,
                    "expected_threat": "FORGERY",
                    "role": "attack",
                }
            ],
        }
        values.update(overrides)
        return values

    def test_accepts_a_valid_payload(self):
        response = AttackResponse(**self.payload())

        assert response.attack_id == "atk_1"
        assert response.attack_type is ThreatType.FORGERY
        assert response.scenario_name == "forgery_signature_alter"
        assert response.seed == 42

    def test_samples_are_parsed_into_sample_schemas(self):
        response = AttackResponse(**self.payload())

        assert len(response.samples) == 1
        assert isinstance(response.samples[0], AttackSampleResponse)
        assert response.samples[0].expected_threat is ThreatType.FORGERY

    def test_accepts_an_empty_sample_list(self):
        assert AttackResponse(**self.payload(samples=[])).samples == []

    def test_evidence_defaults_to_empty_dict(self):
        assert AttackResponse(**self.payload()).evidence == {}

    def test_rejects_invalid_sample_entry(self):
        bad = [{"context_id": "ctx_1", "is_attack": True, "expected_threat": "NOPE", "role": "a"}]

        with pytest.raises(ValidationError):
            AttackResponse(**self.payload(samples=bad))

    def test_rejects_unknown_attack_type(self):
        with pytest.raises(ValidationError):
            AttackResponse(**self.payload(attack_type="SPOOFING"))

    @pytest.mark.parametrize(
        "field_name",
        ["attack_id", "attack_type", "scenario_name", "seed", "parameters", "samples"],
    )
    def test_rejects_missing_required_field(self, field_name):
        values = self.payload()
        values.pop(field_name)

        with pytest.raises(ValidationError):
            AttackResponse(**values)

    def test_round_trips_through_json(self):
        response = AttackResponse(**self.payload())

        restored = AttackResponse.model_validate_json(response.model_dump_json())

        assert restored == response


class TestAttackDescription:
    def payload(self, **overrides):
        values = {
            "name": "forgery",
            "threat_type": ThreatType.FORGERY,
            "description": "Alters a signature or the message it covers.",
        }
        values.update(overrides)
        return values

    def test_accepts_a_valid_payload(self):
        description = AttackDescription(**self.payload())

        assert description.name == "forgery"
        assert description.threat_type is ThreatType.FORGERY

    def test_defaults(self):
        description = AttackDescription(**self.payload())

        assert description.modes == []
        assert description.default_parameters == {}

    def test_carries_modes_and_default_parameters(self):
        description = AttackDescription(
            **self.payload(
                modes=["signature_alter", "message_alter"],
                default_parameters={"mode": "signature_alter"},
            )
        )

        assert description.modes == ["signature_alter", "message_alter"]
        assert description.default_parameters == {"mode": "signature_alter"}

    def test_rejects_unknown_threat_type(self):
        with pytest.raises(ValidationError):
            AttackDescription(**self.payload(threat_type="SPOOFING"))

    @pytest.mark.parametrize("field_name", ["name", "threat_type", "description"])
    def test_rejects_missing_required_field(self, field_name):
        values = self.payload()
        values.pop(field_name)

        with pytest.raises(ValidationError):
            AttackDescription(**values)
