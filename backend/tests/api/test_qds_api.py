from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.db.database import get_database


client = TestClient(app)


def test_get_signature_details_returns_persisted_signing_evidence():
    get_database()["signatures"].insert_one(
        {
            "signature_id": "sig_details",
            "signer_id": "usr_alice",
            "message_id": "msg_details",
            "message_digest": "a" * 64,
            "session_id": "sess_details",
            "protocol_version": "qds-v1",
            "created_at": "2026-01-01T00:00:00Z",
            "quantum_evidence": {
                "measurement_bits": "01",
                "correction_bits": "01",
                "correction_operator": "X",
                "seed": 42,
            },
        }
    )

    response = client.get("/api/signatures/sig_details")

    assert response.status_code == 200
    data = response.json()
    assert data["message_digest"] == "a" * 64
    assert data["quantum_evidence"]["correction_operator"] == "X"


def test_create_signature():
    response = client.post(
        "/api/signatures",
        json={
            "signature_id": "sig_api_1",
            "signer_id": "usr_alice",
            "message_id": "msg_api_1",
            "session_id": "sess_api_1",
            "message": "hello qds",
            "input_state": [
                [0.7071067811865475, 0.0],
                [0.7071067811865475, 0.0],
            ],
            "seed": 42,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["signature_id"] == "sig_api_1"
    assert data["signer_id"] == "usr_alice"
    assert data["message_id"] == "msg_api_1"
    assert data["protocol_version"] == "qds-v1"

    evidence = data["quantum_evidence"]

    assert len(evidence["input_state"]) == 2
    assert evidence["measurement_bits"] in {
        "00",
        "01",
        "10",
        "11",
    }
    assert evidence["correction_bits"] == evidence["measurement_bits"]
    assert evidence["correction_operator"] in {
        "I",
        "X",
        "Z",
        "XZ",
    }


def test_create_signature_rejects_invalid_measurement_state():
    response = client.post(
        "/api/signatures",
        json={
            "signature_id": "sig_invalid",
            "signer_id": "usr_alice",
            "message_id": "msg_invalid",
            "session_id": "sess_invalid",
            "message": "hello",
            "input_state": [
                [1.0, 0.0],
                [1.0, 0.0],
            ],
        },
    )

    assert response.status_code == 400


def test_verification_accepts_valid_context():
    response = client.post(
        "/api/verification",
        json={
            "verification_id": "verify_api_1",
            "signature_id": "sig_api_1",
            "signer_id": "usr_alice",
            "expected_signer_id": "usr_alice",
            "verifier_id": "ver_bob",
            "message_id": "msg_api_1",
            "message_digest": "a" * 64,
            "signed_digest": "a" * 64,
            "session_id": "sess_api_1",
            "nonce": "nonce-123",
            "issued_at": 1700000000.0,
            "received_at": 1700000001.0,
            "auth_fingerprint": "fingerprint",
            "measurements": [
                {
                    "index": 0,
                    "basis": "Z",
                    "expected": 0,
                    "observed": 0,
                },
                {
                    "index": 1,
                    "basis": "X",
                    "expected": 1,
                    "observed": 1,
                },
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["verification_id"] == "verify_api_1"
    assert data["decision"] == "ACCEPT"
    assert data["detected"] is False
    assert data["threats"] == []
    assert data["error_rate"] == 0.0


def test_verification_rejects_impersonation():
    response = client.post(
        "/api/verification",
        json={
            "verification_id": "verify_impersonation",
            "signature_id": "sig_impersonation",
            "signer_id": "usr_evil",
            "expected_signer_id": "usr_alice",
            "verifier_id": "ver_bob",
            "message_id": "msg_1",
            "message_digest": "a" * 64,
            "signed_digest": "a" * 64,
            "session_id": "sess_1",
            "nonce": "nonce-123",
            "issued_at": 1700000000.0,
            "received_at": 1700000001.0,
            "auth_fingerprint": "fingerprint",
            "measurements": [
                {
                    "index": 0,
                    "basis": "Z",
                    "expected": 0,
                    "observed": 0,
                }
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["decision"] == "REJECT"
    assert data["detected"] is True
    assert "IMPERSONATION" in data["threats"]


def test_verification_rejects_message_tampering():
    response = client.post(
        "/api/verification",
        json={
            "verification_id": "verify_forgery",
            "signature_id": "sig_forgery",
            "signer_id": "usr_alice",
            "expected_signer_id": "usr_alice",
            "verifier_id": "ver_bob",
            "message_id": "msg_1",
            "message_digest": "b" * 64,
            "signed_digest": "a" * 64,
            "session_id": "sess_1",
            "nonce": "nonce-123",
            "issued_at": 1700000000.0,
            "received_at": 1700000001.0,
            "auth_fingerprint": "fingerprint",
            "measurements": [
                {
                    "index": 0,
                    "basis": "Z",
                    "expected": 0,
                    "observed": 0,
                }
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["decision"] == "REJECT"
    assert data["detected"] is True
    assert "FORGERY" in data["threats"]


def test_verification_rejects_high_measurement_error():
    response = client.post(
        "/api/verification",
        json={
            "verification_id": "verify_channel",
            "signature_id": "sig_channel",
            "signer_id": "usr_alice",
            "expected_signer_id": "usr_alice",
            "verifier_id": "ver_bob",
            "message_id": "msg_1",
            "message_digest": "a" * 64,
            "signed_digest": "a" * 64,
            "session_id": "sess_1",
            "nonce": "nonce-123",
            "issued_at": 1700000000.0,
            "received_at": 1700000001.0,
            "auth_fingerprint": "fingerprint",
            "measurements": [
                {"index": 0, "basis": "Z", "expected": 0, "observed": 1},   # flipped
                {"index": 1, "basis": "Z", "expected": 1, "observed": 0},   # flipped
                {"index": 2, "basis": "Z", "expected": 0, "observed": 1},   # flipped
                {"index": 3, "basis": "X", "expected": 0, "observed": 0},   # clean
                {"index": 4, "basis": "X", "expected": 1, "observed": 1},   # clean
                {"index": 5, "basis": "Y", "expected": 0, "observed": 0},   # clean
                {"index": 6, "basis": "Y", "expected": 1, "observed": 1},   # clean
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["decision"] == "REJECT"
    assert data["detected"] is True
    assert "CHANNEL_MANIPULATION" in data["threats"]
    assert abs(data["error_rate"] - (3 / 7)) < 1e-9
