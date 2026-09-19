from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.api.alerts import _alerts
from app.api.events import service as event_service


client = TestClient(app)


def setup_function() -> None:
    _alerts.clear()
    event_service.clear()


# ---------------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------------


def test_create_alert():
    response = client.post(
        "/alerts",
        json={
            "alert_id": "alert_1",
            "alert_type": "forgery",
            "severity": "high",
            "title": "Forgery detected",
            "description": "Message digest mismatch.",
            "evidence": [
                {
                    "type": "message_digest_mismatch",
                }
            ],
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["alert_id"] == "alert_1"
    assert data["alert_type"] == "forgery"
    assert data["severity"] == "high"
    assert data["status"] == "open"
    assert data["created_at"] is not None


def test_create_duplicate_alert_is_rejected():
    payload = {
        "alert_id": "alert_duplicate",
        "alert_type": "forgery",
        "severity": "high",
        "title": "Duplicate test",
    }

    first = client.post("/alerts", json=payload)
    second = client.post("/alerts", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409


def test_list_alerts():
    client.post(
        "/alerts",
        json={
            "alert_id": "alert_a",
            "alert_type": "forgery",
            "severity": "high",
            "title": "Alert A",
        },
    )

    client.post(
        "/alerts",
        json={
            "alert_id": "alert_b",
            "alert_type": "impersonation",
            "severity": "critical",
            "title": "Alert B",
        },
    )

    response = client.get("/alerts")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2


def test_get_alert():
    client.post(
        "/alerts",
        json={
            "alert_id": "alert_get",
            "alert_type": "forgery",
            "severity": "medium",
            "title": "Get me",
        },
    )

    response = client.get("/alerts/alert_get")

    assert response.status_code == 200
    assert response.json()["alert_id"] == "alert_get"


def test_missing_alert_returns_404():
    response = client.get("/alerts/does_not_exist")

    assert response.status_code == 404


def test_resolve_alert():
    client.post(
        "/alerts",
        json={
            "alert_id": "alert_resolve",
            "alert_type": "forgery",
            "severity": "high",
            "title": "Resolve me",
        },
    )

    response = client.post("/alerts/alert_resolve/resolve")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "resolved"
    assert data["resolved_at"] is not None


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------


def test_create_event():
    response = client.post(
        "/events",
        json={
            "event_type": "signature_created",
            "context_id": "ctx_123",
            "details": {
                "signature_id": "sig_123",
            },
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["event_type"] == "signature_created"
    assert data["context_id"] == "ctx_123"
    assert data["details"]["signature_id"] == "sig_123"


def test_list_events():
    client.post(
        "/events",
        json={
            "event_type": "test_event",
            "context_id": "ctx_1",
        },
    )

    response = client.get("/events")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["event_type"] == "test_event"


def test_clear_events():
    client.post(
        "/events",
        json={
            "event_type": "event_to_clear",
        },
    )

    response = client.delete("/events")

    assert response.status_code == 204

    response = client.get("/events")

    assert response.status_code == 200
    assert response.json() == []


# ---------------------------------------------------------------------------
# Experiments
# ---------------------------------------------------------------------------


def test_create_experiment():
    response = client.post(
        "/experiments",
        json={
            "experiment_id": "exp_1",
            "name": "Forgery baseline",
            "scenario": "forgery",
            "seed": 42,
            "parameters": {
                "samples": 100,
            },
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["experiment_id"] == "exp_1"
    assert data["name"] == "Forgery baseline"
    assert data["scenario"] == "forgery"
    assert data["seed"] == 42
    assert data["parameters"]["samples"] == 100


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def test_verification_metrics():
    context = {
        "context_id": "ctx_metrics",
        "signature_id": "sig_1",
        "signer_id": "alice",
        "expected_signer_id": "alice",
        "verifier_id": "bob",
        "message_id": "msg_1",
        "message_digest": "a" * 64,
        "signed_digest": "a" * 64,
        "session_id": "session_1",
        "nonce": "nonce",
        "issued_at": 1.0,
        "received_at": 2.0,
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
                "basis": "Z",
                "expected": 1,
                "observed": 0,
            },
            {
                "index": 2,
                "basis": "X",
                "expected": 1,
                "observed": 1,
            },
        ],
        "protocol_version": "qds-v1",
        "metadata": {},
    }

    response = client.post(
        "/metrics/verification",
        json=context,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["context_id"] == "ctx_metrics"
    assert data["total_measurements"] == 3
    assert data["errors"] == 1
    assert data["error_rate"] == 1 / 3
    assert data["protocol_version"] == "qds-v1"