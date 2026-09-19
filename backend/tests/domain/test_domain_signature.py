"""Tests for app.models.domain.signature."""

import dataclasses

import pytest

from app.models.domain import Signature

REQUIRED_FIELDS = (
    "signature_id",
    "signer_id",
    "message_id",
    "message_digest",
    "protocol_version",
    "session_id",
)


def build_signature(**overrides):
    values = {
        "signature_id": "sig_1",
        "signer_id": "usr_alice",
        "message_id": "msg_1",
        "message_digest": "a" * 64,
        "protocol_version": "qds-v1",
        "session_id": "sess_1",
    }
    values.update(overrides)
    return Signature(**values)


def test_builds_with_all_required_fields():
    signature = build_signature()

    assert signature.signature_id == "sig_1"
    assert signature.signer_id == "usr_alice"
    assert signature.message_id == "msg_1"
    assert signature.message_digest == "a" * 64
    assert signature.protocol_version == "qds-v1"
    assert signature.session_id == "sess_1"


def test_quantum_evidence_defaults_to_empty_dict():
    assert build_signature().quantum_evidence == {}


def test_quantum_evidence_default_is_not_shared_between_instances():
    first = build_signature()
    second = build_signature()

    first.quantum_evidence["seed"] = 42

    assert second.quantum_evidence == {}


def test_quantum_evidence_is_stored_as_given():
    evidence = {"measurement_bits": "01", "seed": 7}

    assert build_signature(quantum_evidence=evidence).quantum_evidence == evidence


@pytest.mark.parametrize("field_name", REQUIRED_FIELDS)
def test_rejects_empty_required_field(field_name):
    with pytest.raises(ValueError, match=field_name):
        build_signature(**{field_name: ""})


@pytest.mark.parametrize("field_name", REQUIRED_FIELDS)
def test_rejects_none_required_field(field_name):
    with pytest.raises(ValueError, match=field_name):
        build_signature(**{field_name: None})


def test_is_frozen():
    signature = build_signature()

    with pytest.raises(dataclasses.FrozenInstanceError):
        signature.signer_id = "usr_mallory"


def test_equality_is_by_value():
    assert build_signature() == build_signature()
    assert build_signature() != build_signature(signature_id="sig_2")
