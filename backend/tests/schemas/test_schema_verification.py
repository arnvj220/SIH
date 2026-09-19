"""Tests for app.models.schemas.verification."""

import pytest
from pydantic import ValidationError

from app.attacks.contracts import Decision, ThreatType
from app.models.schemas.verification import (
    MeasurementRoundSchema,
    VerificationRequest,
    VerificationResponse,
)

DIGEST = "a" * 64
OTHER_DIGEST = "b" * 64


class TestMeasurementRoundSchema:
    def test_accepts_a_valid_round(self):
        round_ = MeasurementRoundSchema(index=0, basis="X", expected=1, observed=0)

        assert round_.index == 0
        assert round_.basis == "X"
        assert round_.expected == 1
        assert round_.observed == 0

    @pytest.mark.parametrize("basis", ["X", "Y", "Z"])
    def test_accepts_every_supported_basis(self, basis):
        assert MeasurementRoundSchema(index=0, basis=basis, expected=0, observed=0).basis == basis

    @pytest.mark.parametrize("basis", ["x", "y", "z", "A", "", "XY"])
    def test_rejects_unsupported_basis(self, basis):
        """Unlike the domain model, the schema pattern is case-sensitive."""
        with pytest.raises(ValidationError):
            MeasurementRoundSchema(index=0, basis=basis, expected=0, observed=0)

    def test_rejects_negative_index(self):
        with pytest.raises(ValidationError):
            MeasurementRoundSchema(index=-1, basis="X", expected=0, observed=0)

    @pytest.mark.parametrize("value", [-1, 2, 5])
    def test_rejects_expected_outside_zero_one(self, value):
        with pytest.raises(ValidationError):
            MeasurementRoundSchema(index=0, basis="X", expected=value, observed=0)

    @pytest.mark.parametrize("value", [-1, 2, 5])
    def test_rejects_observed_outside_zero_one(self, value):
        with pytest.raises(ValidationError):
            MeasurementRoundSchema(index=0, basis="X", expected=0, observed=value)


class TestVerificationRequest:
    def payload(self, **overrides):
        values = {
            "verification_id": "ver_1",
            "signature_id": "sig_1",
            "signer_id": "usr_alice",
            "expected_signer_id": "usr_alice",
            "verifier_id": "usr_bob",
            "message_id": "msg_1",
            "message_digest": DIGEST,
            "signed_digest": DIGEST,
            "session_id": "sess_1",
            "nonce": "nonce_abc",
            "issued_at": 1_700_000_000.0,
            "received_at": 1_700_000_001.0,
            "auth_fingerprint": "fp_abc123",
            "measurements": [
                {"index": 0, "basis": "X", "expected": 1, "observed": 1},
                {"index": 1, "basis": "Z", "expected": 0, "observed": 1},
            ],
        }
        values.update(overrides)
        return values

    def test_accepts_a_valid_payload(self):
        request = VerificationRequest(**self.payload())

        assert request.verification_id == "ver_1"
        assert request.signer_id == "usr_alice"
        assert request.verifier_id == "usr_bob"
        assert request.issued_at == pytest.approx(1_700_000_000.0)

    def test_defaults(self):
        request = VerificationRequest(**self.payload())

        assert request.protocol_version == "qds-v1"
        assert request.metadata == {}

    def test_measurements_are_parsed_into_round_schemas(self):
        request = VerificationRequest(**self.payload())

        assert len(request.measurements) == 2
        assert all(isinstance(m, MeasurementRoundSchema) for m in request.measurements)
        assert request.measurements[1].basis == "Z"

    def test_accepts_an_empty_measurement_list(self):
        assert VerificationRequest(**self.payload(measurements=[])).measurements == []

    def test_rejects_invalid_measurement_entry(self):
        bad = [{"index": 0, "basis": "Q", "expected": 0, "observed": 0}]

        with pytest.raises(ValidationError):
            VerificationRequest(**self.payload(measurements=bad))

    @pytest.mark.parametrize("field_name", ["message_digest", "signed_digest"])
    @pytest.mark.parametrize("length", [63, 65, 0])
    def test_digests_must_be_exactly_64_chars(self, field_name, length):
        with pytest.raises(ValidationError):
            VerificationRequest(**self.payload(**{field_name: "a" * length}))

    def test_message_digest_may_differ_from_signed_digest(self):
        """A mismatch is a detection concern, not a validation error."""
        request = VerificationRequest(
            **self.payload(message_digest=DIGEST, signed_digest=OTHER_DIGEST)
        )

        assert request.message_digest != request.signed_digest

    @pytest.mark.parametrize(
        "field_name",
        [
            "verification_id",
            "signature_id",
            "signer_id",
            "expected_signer_id",
            "verifier_id",
            "message_id",
            "session_id",
            "nonce",
            "auth_fingerprint",
        ],
    )
    def test_rejects_empty_identifier_fields(self, field_name):
        with pytest.raises(ValidationError):
            VerificationRequest(**self.payload(**{field_name: ""}))

    @pytest.mark.parametrize(
        "field_name",
        ["verification_id", "signature_id", "verifier_id", "nonce", "auth_fingerprint"],
    )
    def test_rejects_identifiers_longer_than_128_chars(self, field_name):
        with pytest.raises(ValidationError):
            VerificationRequest(**self.payload(**{field_name: "x" * 129}))

    @pytest.mark.parametrize("field_name", ["issued_at", "received_at", "measurements"])
    def test_rejects_missing_required_field(self, field_name):
        values = self.payload()
        values.pop(field_name)

        with pytest.raises(ValidationError):
            VerificationRequest(**values)

    def test_round_trips_through_json(self):
        request = VerificationRequest(**self.payload())

        restored = VerificationRequest.model_validate_json(request.model_dump_json())

        assert restored == request


class TestVerificationResponse:
    def payload(self, **overrides):
        values = {
            "verification_id": "ver_1",
            "decision": Decision.ACCEPT,
            "detected": False,
            "error_rate": 0.02,
        }
        values.update(overrides)
        return values

    def test_accepts_a_valid_payload(self):
        response = VerificationResponse(**self.payload())

        assert response.verification_id == "ver_1"
        assert response.decision is Decision.ACCEPT
        assert response.detected is False
        assert response.error_rate == pytest.approx(0.02)

    def test_defaults(self):
        response = VerificationResponse(**self.payload())

        assert response.threats == []
        assert response.evidence == []

    @pytest.mark.parametrize("decision", list(Decision))
    def test_accepts_every_decision(self, decision):
        assert VerificationResponse(**self.payload(decision=decision)).decision is decision

    def test_accepts_decision_as_plain_string(self):
        assert VerificationResponse(**self.payload(decision="REJECT")).decision is Decision.REJECT

    def test_rejects_unknown_decision(self):
        with pytest.raises(ValidationError):
            VerificationResponse(**self.payload(decision="MAYBE"))

    def test_parses_threats_into_the_threat_enum(self):
        response = VerificationResponse(
            **self.payload(
                decision=Decision.REJECT,
                detected=True,
                threats=["FORGERY", "REPLAY"],
            )
        )

        assert response.threats == [ThreatType.FORGERY, ThreatType.REPLAY]

    def test_rejects_unknown_threat_type(self):
        with pytest.raises(ValidationError):
            VerificationResponse(**self.payload(threats=["SPOOFING"]))

    @pytest.mark.parametrize("rate", [0.0, 0.5, 1.0])
    def test_accepts_error_rate_within_bounds(self, rate):
        assert VerificationResponse(**self.payload(error_rate=rate)).error_rate == pytest.approx(rate)

    @pytest.mark.parametrize("rate", [-0.01, 1.01, 2.0])
    def test_rejects_error_rate_outside_bounds(self, rate):
        with pytest.raises(ValidationError):
            VerificationResponse(**self.payload(error_rate=rate))

    @pytest.mark.parametrize("field_name", ["verification_id", "decision", "detected", "error_rate"])
    def test_rejects_missing_required_field(self, field_name):
        values = self.payload()
        values.pop(field_name)

        with pytest.raises(ValidationError):
            VerificationResponse(**values)

    def test_carries_evidence_entries(self):
        response = VerificationResponse(
            **self.payload(evidence=[{"type": "error_rate", "value": 0.4}])
        )

        assert response.evidence[0]["type"] == "error_rate"
