"""Tests for app.models.domain.verification."""

import dataclasses

import pytest

from app.models.domain import (
    VerificationDecision,
    VerificationRequest,
    VerificationResult,
)


def build_result(**overrides):
    values = {
        "verification_id": "ver_1",
        "signature_id": "sig_1",
        "decision": VerificationDecision.ACCEPT,
    }
    values.update(overrides)
    return VerificationResult(**values)


class TestVerificationDecision:
    def test_has_exactly_the_expected_members(self):
        assert {member.value for member in VerificationDecision} == {
            "ACCEPT",
            "REJECT",
            "SUSPICIOUS",
        }

    def test_is_a_string_enum(self):
        assert VerificationDecision.ACCEPT == "ACCEPT"
        assert isinstance(VerificationDecision.REJECT, str)


class TestVerificationRequest:
    def test_builds_with_required_fields(self):
        request = VerificationRequest(
            signature_id="sig_1",
            message_id="msg_1",
            message="hello",
            verifier_id="usr_bob",
        )

        assert request.signature_id == "sig_1"
        assert request.message == "hello"
        assert request.verifier_id == "usr_bob"

    def test_nonce_defaults_to_none(self):
        request = VerificationRequest(
            signature_id="sig_1",
            message_id="msg_1",
            message="hello",
            verifier_id="usr_bob",
        )

        assert request.nonce is None

    def test_accepts_explicit_nonce(self):
        request = VerificationRequest(
            signature_id="sig_1",
            message_id="msg_1",
            message="hello",
            verifier_id="usr_bob",
            nonce="nonce_abc",
        )

        assert request.nonce == "nonce_abc"

    def test_is_frozen(self):
        request = VerificationRequest(
            signature_id="sig_1",
            message_id="msg_1",
            message="hello",
            verifier_id="usr_bob",
        )

        with pytest.raises(dataclasses.FrozenInstanceError):
            request.verifier_id = "usr_mallory"


class TestVerificationResult:
    def test_defaults_are_empty(self):
        result = build_result()

        assert result.threats == ()
        assert result.evidence == ()
        assert result.error_rate is None
        assert result.metadata == {}

    def test_metadata_default_is_not_shared_between_instances(self):
        first = build_result()
        second = build_result()

        first.metadata["source"] = "test"

        assert second.metadata == {}

    def test_accept_is_accepted_and_not_detected(self):
        result = build_result(decision=VerificationDecision.ACCEPT)

        assert result.accepted is True
        assert result.detected is False

    @pytest.mark.parametrize(
        "decision",
        [VerificationDecision.REJECT, VerificationDecision.SUSPICIOUS],
    )
    def test_non_accept_decisions_are_detected(self, decision):
        result = build_result(decision=decision)

        assert result.accepted is False
        assert result.detected is True

    def test_carries_threats_and_evidence(self):
        result = build_result(
            decision=VerificationDecision.REJECT,
            threats=("FORGERY", "REPLAY"),
            evidence=({"type": "error_rate", "value": 0.42},),
            error_rate=0.42,
        )

        assert result.threats == ("FORGERY", "REPLAY")
        assert result.evidence[0]["type"] == "error_rate"
        assert result.error_rate == pytest.approx(0.42)

    def test_is_frozen(self):
        result = build_result()

        with pytest.raises(dataclasses.FrozenInstanceError):
            result.decision = VerificationDecision.REJECT
