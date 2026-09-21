from __future__ import annotations

import numpy as np
import pytest

from app.attacks.contracts import Decision, ThreatType
from app.quantum.states.pauli_states import plus_state
from app.services.audit_service import AuditService
from app.services.attack_service import AttackService
from app.services.detection_service import DetectionService
from app.services.signature_service import (
    SignatureRequest,
    SignatureService,
)
from app.services.verification_service import VerificationService


# ---------------------------------------------------------------------------
# Signature service
# ---------------------------------------------------------------------------

def test_signature_service_creates_signature():
    service = SignatureService()

    signature = service.create_signature(
        SignatureRequest(
            signature_id="sig_test_001",
            signer_id="usr_alice",
            message_id="msg_001",
            session_id="sess_001",
            message="hello quantum world",
            input_state=plus_state(),
            seed=42,
        )
    )

    assert signature.signature_id == "sig_test_001"
    assert signature.signer_id == "usr_alice"
    assert signature.message_id == "msg_001"
    assert signature.session_id == "sess_001"
    assert signature.protocol_version == "qds-v1"

    assert len(signature.message_digest) == 64
    assert signature.quantum_evidence.measurement_bits in {
        "00",
        "01",
        "10",
        "11",
    }


def test_signature_generation_is_reproducible():
    service = SignatureService()

    request = SignatureRequest(
        signature_id="sig_test",
        signer_id="usr_alice",
        message_id="msg_001",
        session_id="sess_001",
        message="same message",
        input_state=plus_state(),
        seed=123,
    )

    first = service.create_signature(request)
    second = service.create_signature(request)

    assert first.message_digest == second.message_digest
    assert (
        first.quantum_evidence.measurement_bits
        == second.quantum_evidence.measurement_bits
    )


# ---------------------------------------------------------------------------
# Verification service
# ---------------------------------------------------------------------------

def test_verification_service_builds_context():
    signature_service = SignatureService()
    verification_service = VerificationService()

    signature = signature_service.create_signature(
        SignatureRequest(
            signature_id="sig_verify",
            signer_id="usr_alice",
            message_id="msg_verify",
            session_id="sess_verify",
            message="verify me",
            input_state=plus_state(),
            seed=42,
        )
    )

    context = verification_service.build_context(
        signature,
        verifier_id="ver_bob",
        message="verify me",
        nonce="nonce-123",
    )

    assert context.signature_id == signature.signature_id
    assert context.signer_id == "usr_alice"
    assert context.expected_signer_id == "usr_alice"
    assert context.verifier_id == "ver_bob"
    assert context.message_digest == signature.message_digest
    assert context.signed_digest == signature.message_digest
    assert context.nonce == "nonce-123"
    expected_rounds = 100 * 3  # default shots_per_basis × 3 Pauli bases
    assert len(context.measurements) == expected_rounds


# ---------------------------------------------------------------------------
# Detection service
# ---------------------------------------------------------------------------

def test_detection_accepts_valid_context():
    signature_service = SignatureService()
    verification_service = VerificationService()
    detection_service = DetectionService()

    signature = signature_service.create_signature(
        SignatureRequest(
            signature_id="sig_detection",
            signer_id="usr_alice",
            message_id="msg_detection",
            session_id="sess_detection",
            message="valid message",
            input_state=plus_state(),
            seed=1,
        )
    )

    context = verification_service.build_context(
        signature,
        verifier_id="ver_bob",
        message="valid message",
    )

    result = detection_service.detect(context)

    assert result.decision == Decision.ACCEPT
    assert result.threats == []
    assert result.detected is False


def test_detection_rejects_message_tampering():
    signature_service = SignatureService()
    verification_service = VerificationService()
    detection_service = DetectionService()

    signature = signature_service.create_signature(
        SignatureRequest(
            signature_id="sig_forgery",
            signer_id="usr_alice",
            message_id="msg_forgery",
            session_id="sess_forgery",
            message="original message",
            input_state=plus_state(),
            seed=1,
        )
    )

    context = verification_service.build_context(
        signature,
        verifier_id="ver_bob",
        message="tampered message",
    )

    result = detection_service.detect(context)

    assert result.decision == Decision.REJECT
    assert ThreatType.FORGERY in result.threats
    assert result.detected is True


def test_detection_rejects_impersonation():
    signature_service = SignatureService()
    verification_service = VerificationService()
    detection_service = DetectionService()

    signature = signature_service.create_signature(
        SignatureRequest(
            signature_id="sig_impersonation",
            signer_id="usr_evil",
            message_id="msg_impersonation",
            session_id="sess_impersonation",
            message="message",
            input_state=plus_state(),
            seed=1,
        )
    )

    context = verification_service.build_context(
        signature,
        verifier_id="ver_bob",
        message="message",
        expected_signer_id="usr_alice",
    )

    result = detection_service.detect(context)

    assert result.decision == Decision.REJECT
    assert ThreatType.IMPERSONATION in result.threats


# ---------------------------------------------------------------------------
# Attack service
# ---------------------------------------------------------------------------

def test_attack_service_lists_registered_attacks():
    service = AttackService()

    attacks = service.list_attacks()

    assert isinstance(attacks, list)
    assert any(attack["name"] == "forgery" for attack in attacks)


def test_attack_service_executes_forgery():
    signature_service = SignatureService()
    verification_service = VerificationService()
    attack_service = AttackService()

    signature = signature_service.create_signature(
        SignatureRequest(
            signature_id="sig_attack",
            signer_id="usr_alice",
            message_id="msg_attack",
            session_id="sess_attack",
            message="attack target",
            input_state=plus_state(),
            seed=42,
        )
    )

    context = verification_service.build_context(
        signature,
        verifier_id="ver_bob",
        message="attack target",
    )

    samples = attack_service.execute(
        "forgery",
        context,
        seed=42,
        parameters={
            "mode": "message_tamper",
            "modified_fraction": 0.5,
        },
    )

    assert len(samples) == 1

    sample = samples[0]

    assert sample.is_attack is True
    assert sample.expected_threat == ThreatType.FORGERY
    assert sample.role == "attack"
    assert sample.context.context_id != context.context_id


# ---------------------------------------------------------------------------
# Audit service
# ---------------------------------------------------------------------------

def test_audit_service_records_events():
    service = AuditService()

    event = service.record(
        "signature_created",
        context_id="ctx_001",
        details={
            "signature_id": "sig_001",
        },
    )

    assert event["event_type"] == "signature_created"
    assert event["context_id"] == "ctx_001"
    assert event["details"]["signature_id"] == "sig_001"

    events = service.list_events()

    assert len(events) == 1
    assert events[0] == event


def test_audit_service_clear():
    service = AuditService()

    service.record("event_1")
    service.record("event_2")

    assert len(service.list_events()) == 2

    service.clear()

    assert service.list_events() == []