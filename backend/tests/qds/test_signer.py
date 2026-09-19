import hashlib

import numpy as np

from app.qds.signature import QDSSignature
from app.qds.signer import sign
from app.quantum.states.pauli_states import plus_i_state


def test_sign_returns_qds_signature():
    signature = sign(
        signature_id="sig-1",
        signer_id="alice",
        message_id="msg-1",
        session_id="session-1",
        message="hello",
        input_state=plus_i_state(),
        seed=42,
    )

    assert isinstance(signature, QDSSignature)


def test_sign_preserves_metadata():
    signature = sign(
        signature_id="sig-123",
        signer_id="alice",
        message_id="msg-456",
        session_id="session-789",
        message="hello",
        input_state=plus_i_state(),
        seed=42,
    )

    assert signature.signature_id == "sig-123"
    assert signature.signer_id == "alice"
    assert signature.message_id == "msg-456"
    assert signature.session_id == "session-789"
    assert signature.protocol_version == "qds-v1"


def test_sign_binds_message_digest():
    message = "hello"

    signature = sign(
        signature_id="sig-1",
        signer_id="alice",
        message_id="msg-1",
        session_id="session-1",
        message=message,
        input_state=plus_i_state(),
        seed=42,
    )

    expected = hashlib.sha256(
        message.encode("utf-8")
    ).hexdigest()

    assert signature.message_digest == expected


def test_sign_contains_quantum_evidence():
    signature = sign(
        signature_id="sig-1",
        signer_id="alice",
        message_id="msg-1",
        session_id="session-1",
        message="hello",
        input_state=plus_i_state(),
        seed=42,
    )

    evidence = signature.quantum_evidence

    assert evidence.measurement_bits in {
        "00",
        "01",
        "10",
        "11",
    }

    assert evidence.correction_operator in {
        "I",
        "X",
        "Z",
        "XZ",
    }


def test_sign_is_reproducible():
    kwargs = {
        "signature_id": "sig-1",
        "signer_id": "alice",
        "message_id": "msg-1",
        "session_id": "session-1",
        "message": "hello",
        "input_state": plus_i_state(),
        "seed": 123,
    }

    sig_1 = sign(**kwargs)
    sig_2 = sign(**kwargs)

    assert sig_1.message_digest == sig_2.message_digest

    assert (
        sig_1.quantum_evidence.measurement_bits
        == sig_2.quantum_evidence.measurement_bits
    )

    assert np.allclose(
        sig_1.quantum_evidence.bob_state_after_correction,
        sig_2.quantum_evidence.bob_state_after_correction,
    )