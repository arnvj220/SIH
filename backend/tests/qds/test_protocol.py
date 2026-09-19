import hashlib

import numpy as np

from app.qds.protocol import (
    PROTOCOL_VERSION,
    compute_message_digest,
    execute_protocol,
)
from app.quantum.states.pauli_states import plus_state


def test_message_digest_is_deterministic():
    digest_1 = compute_message_digest("hello")
    digest_2 = compute_message_digest("hello")

    assert digest_1 == digest_2


def test_different_messages_have_different_digests():
    digest_1 = compute_message_digest("hello")
    digest_2 = compute_message_digest("goodbye")

    assert digest_1 != digest_2


def test_digest_matches_sha256():
    message = "hello quantum world"

    expected = hashlib.sha256(
        message.encode("utf-8")
    ).hexdigest()

    assert compute_message_digest(message) == expected


def test_protocol_version_exists():
    assert PROTOCOL_VERSION == "qds-v1"


def test_execute_protocol_returns_quantum_evidence():
    digest, evidence = execute_protocol(
        message="hello",
        input_state=plus_state(),
        seed=42,
    )

    assert len(digest) == 64
    assert evidence.measurement_bits in {
        "00",
        "01",
        "10",
        "11",
    }


def test_execute_protocol_is_reproducible():
    kwargs = {
        "message": "hello",
        "input_state": plus_state(),
        "seed": 123,
    }

    digest_1, evidence_1 = execute_protocol(**kwargs)
    digest_2, evidence_2 = execute_protocol(**kwargs)

    assert digest_1 == digest_2
    assert evidence_1.measurement_bits == evidence_2.measurement_bits

    assert np.allclose(
        evidence_1.bob_state_after_correction,
        evidence_2.bob_state_after_correction,
    )