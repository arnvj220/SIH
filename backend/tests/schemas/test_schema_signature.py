"""Tests for app.models.schemas.signature."""

from datetime import datetime
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.models.schemas.signature import (
    QuantumEvidenceSchema,
    SignatureCreate,
    SignatureResponse,
)

DIGEST = "a" * 64


def evidence_payload(**overrides):
    payload = {
        "input_state": [[1.0, 0.0], [0.0, 0.0]],
        "measurement_bits": "01",
        "correction_bits": "10",
        "correction_operator": "X",
        "bob_state_before_correction": [[0.0, 0.0], [1.0, 0.0]],
        "bob_state_after_correction": [[1.0, 0.0], [0.0, 0.0]],
        "seed": 7,
    }
    payload.update(overrides)
    return payload


class TestQuantumEvidenceSchema:
    def test_accepts_a_valid_payload(self):
        evidence = QuantumEvidenceSchema(**evidence_payload())

        assert evidence.measurement_bits == "01"
        assert evidence.correction_bits == "10"
        assert evidence.correction_operator == "X"
        assert evidence.seed == 7

    def test_seed_is_optional(self):
        payload = evidence_payload()
        payload.pop("seed")

        assert QuantumEvidenceSchema(**payload).seed is None

    @pytest.mark.parametrize("bits", ["00", "01", "10", "11"])
    def test_accepts_every_two_bit_pattern(self, bits):
        evidence = QuantumEvidenceSchema(
            **evidence_payload(measurement_bits=bits, correction_bits=bits)
        )

        assert evidence.measurement_bits == bits

    @pytest.mark.parametrize("bits", ["0", "111", "", "0a", "22", "0 1"])
    def test_rejects_malformed_measurement_bits(self, bits):
        with pytest.raises(ValidationError):
            QuantumEvidenceSchema(**evidence_payload(measurement_bits=bits))

    @pytest.mark.parametrize("bits", ["0", "111", "", "2b"])
    def test_rejects_malformed_correction_bits(self, bits):
        with pytest.raises(ValidationError):
            QuantumEvidenceSchema(**evidence_payload(correction_bits=bits))

    def test_amplitudes_are_pairs_of_floats(self):
        evidence = QuantumEvidenceSchema(**evidence_payload())

        assert evidence.input_state == [[1.0, 0.0], [0.0, 0.0]]
        assert all(isinstance(part, float) for pair in evidence.input_state for part in pair)

    def test_rejects_non_numeric_amplitudes(self):
        with pytest.raises(ValidationError):
            QuantumEvidenceSchema(**evidence_payload(input_state=[["real", "imag"]]))

    def test_rejects_flat_amplitude_list(self):
        with pytest.raises(ValidationError):
            QuantumEvidenceSchema(**evidence_payload(input_state=[1.0, 0.0]))


class TestSignatureCreate:
    def payload(self, **overrides):
        values = {
            "signature_id": "sig_1",
            "signer_id": "usr_alice",
            "message_id": "msg_1",
            "session_id": "sess_1",
            "message": "transfer 100 credits",
            "input_state": [[1.0, 0.0], [0.0, 0.0]],
            "seed": 42,
        }
        values.update(overrides)
        return values

    def test_accepts_a_valid_payload(self):
        request = SignatureCreate(**self.payload())

        assert request.signature_id == "sig_1"
        assert request.signer_id == "usr_alice"
        assert request.message == "transfer 100 credits"
        assert request.seed == 42

    def test_seed_is_optional(self):
        values = self.payload()
        values.pop("seed")

        assert SignatureCreate(**values).seed is None

    @pytest.mark.parametrize(
        "field_name",
        ["signature_id", "signer_id", "message_id", "session_id", "message"],
    )
    def test_rejects_empty_string_fields(self, field_name):
        with pytest.raises(ValidationError):
            SignatureCreate(**self.payload(**{field_name: ""}))

    @pytest.mark.parametrize(
        "field_name",
        ["signature_id", "signer_id", "message_id", "session_id"],
    )
    def test_rejects_identifiers_longer_than_128_chars(self, field_name):
        with pytest.raises(ValidationError):
            SignatureCreate(**self.payload(**{field_name: "x" * 129}))

    @pytest.mark.parametrize(
        "field_name",
        ["signature_id", "signer_id", "message_id", "session_id", "message", "input_state"],
    )
    def test_rejects_missing_required_field(self, field_name):
        values = self.payload()
        values.pop(field_name)

        with pytest.raises(ValidationError):
            SignatureCreate(**values)

    def test_long_message_is_allowed(self):
        assert len(SignatureCreate(**self.payload(message="m" * 5000)).message) == 5000


class TestSignatureResponse:
    def payload(self, **overrides):
        values = {
            "signature_id": "sig_1",
            "signer_id": "usr_alice",
            "message_id": "msg_1",
            "protocol_version": "qds-v1",
            "session_id": "sess_1",
            "message_digest": DIGEST,
            "quantum_evidence": evidence_payload(),
        }
        values.update(overrides)
        return values

    def test_accepts_a_valid_payload(self):
        response = SignatureResponse(**self.payload())

        assert response.signature_id == "sig_1"
        assert response.protocol_version == "qds-v1"
        assert response.message_digest == DIGEST

    def test_nested_evidence_is_parsed_into_its_schema(self):
        response = SignatureResponse(**self.payload())

        assert isinstance(response.quantum_evidence, QuantumEvidenceSchema)
        assert response.quantum_evidence.correction_operator == "X"

    def test_created_at_defaults_to_none(self):
        assert SignatureResponse(**self.payload()).created_at is None

    def test_accepts_created_at(self):
        moment = datetime(2026, 1, 1, 12, 0, 0)

        assert SignatureResponse(**self.payload(created_at=moment)).created_at == moment

    def test_invalid_nested_evidence_is_rejected(self):
        bad = evidence_payload(measurement_bits="not-bits")

        with pytest.raises(ValidationError):
            SignatureResponse(**self.payload(quantum_evidence=bad))

    def test_can_be_built_from_an_orm_style_object(self):
        """model_config sets from_attributes, so attribute access is supported."""
        obj = SimpleNamespace(**self.payload(), created_at=None)

        response = SignatureResponse.model_validate(obj)

        assert response.signature_id == "sig_1"
        assert response.quantum_evidence.seed == 7

    def test_round_trips_through_json(self):
        response = SignatureResponse(**self.payload())

        restored = SignatureResponse.model_validate_json(response.model_dump_json())

        assert restored == response
