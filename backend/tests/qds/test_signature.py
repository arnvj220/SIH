import pytest

from app.qds.signature import QDSSignature
from app.qds.protocol import execute_protocol
from app.quantum.states.pauli_states import zero_state


def test_signature_stores_protocol_data():
    _, evidence = execute_protocol(
        message="hello",
        input_state=zero_state(),
        seed=42,
    )

    signature = QDSSignature(
        signature_id="sig-1",
        signer_id="alice",
        message_id="msg-1",
        protocol_version="qds-v1",
        session_id="session-1",
        message_digest="abc123",
        quantum_evidence=evidence,
    )

    assert signature.signature_id == "sig-1"
    assert signature.signer_id == "alice"
    assert signature.message_id == "msg-1"
    assert signature.protocol_version == "qds-v1"
    assert signature.session_id == "session-1"
    assert signature.message_digest == "abc123"


def test_signature_contains_quantum_evidence():
    _, evidence = execute_protocol(
        message="hello",
        input_state=zero_state(),
        seed=42,
    )

    signature = QDSSignature(
        signature_id="sig-1",
        signer_id="alice",
        message_id="msg-1",
        protocol_version="qds-v1",
        session_id="session-1",
        message_digest="abc123",
        quantum_evidence=evidence,
    )

    assert signature.quantum_evidence is evidence


def test_signature_is_immutable():
    _, evidence = execute_protocol(
        message="hello",
        input_state=zero_state(),
        seed=42,
    )

    signature = QDSSignature(
        signature_id="sig-1",
        signer_id="alice",
        message_id="msg-1",
        protocol_version="qds-v1",
        session_id="session-1",
        message_digest="abc123",
        quantum_evidence=evidence,
    )

    with pytest.raises(AttributeError):
        signature.signer_id = "bob"