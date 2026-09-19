import pytest

from app.models.domain import (
    AlertSeverity,
    AlertStatus,
    AttackRequest,
    AttackType,
    ExperimentConfig,
    Measurement,
    SecurityAlert,
    Signature,
    VerificationDecision,
    VerificationRequest,
    VerificationResult,
)


def test_measurement_valid():
    measurement = Measurement(
        index=0,
        basis="X",
        expected=1,
        observed=0,
    )

    assert measurement.basis == "X"
    assert measurement.is_error is True


def test_measurement_valid_no_error():
    measurement = Measurement(
        index=1,
        basis="Z",
        expected=1,
        observed=1,
    )

    assert measurement.is_error is False


def test_measurement_rejects_invalid_basis():
    with pytest.raises(ValueError):
        Measurement(
            index=0,
            basis="A",
            expected=0,
            observed=0,
        )


def test_signature():
    signature = Signature(
        signature_id="sig_1",
        signer_id="usr_alice",
        message_id="msg_1",
        message_digest="abc123",
        protocol_version="qds-v1",
        session_id="sess_1",
    )

    assert signature.signature_id == "sig_1"
    assert signature.protocol_version == "qds-v1"


def test_signature_rejects_empty_id():
    with pytest.raises(ValueError):
        Signature(
            signature_id="",
            signer_id="usr_alice",
            message_id="msg_1",
            message_digest="abc",
            protocol_version="qds-v1",
            session_id="sess_1",
        )


def test_verification_result():
    result = VerificationResult(
        verification_id="ver_1",
        signature_id="sig_1",
        decision=VerificationDecision.REJECT,
        threats=("FORGERY",),
    )

    assert result.accepted is False
    assert result.detected is True
    assert result.threats == ("FORGERY",)


def test_verification_accept():
    result = VerificationResult(
        verification_id="ver_1",
        signature_id="sig_1",
        decision=VerificationDecision.ACCEPT,
    )

    assert result.accepted is True
    assert result.detected is False


def test_attack_request():
    request = AttackRequest(
        attack_type=AttackType.FORGERY,
        parameters={"mode": "signature_alter"},
        seed=42,
    )

    assert request.attack_type == AttackType.FORGERY
    assert request.seed == 42


def test_security_alert():
    alert = SecurityAlert(
        alert_id="alert_1",
        verification_id="ver_1",
        threat_type="FORGERY",
        severity=AlertSeverity.HIGH,
        title="Signature forgery detected",
        description="Measurement evidence indicates a forged signature.",
    )

    assert alert.status == AlertStatus.OPEN
    assert alert.severity == AlertSeverity.HIGH


def test_experiment_config():
    config = ExperimentConfig(
        name="Forgery Baseline",
        scenario="forgery",
        seed=42,
        rounds=1000,
    )

    assert config.scenario == "forgery"
    assert config.rounds == 1000