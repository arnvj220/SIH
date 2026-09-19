"""Tests for app.models.domain.alert."""

import dataclasses

import pytest

from app.models.domain import AlertSeverity, AlertStatus, SecurityAlert


def build_alert(**overrides):
    values = {
        "alert_id": "alert_1",
        "verification_id": "ver_1",
        "threat_type": "FORGERY",
        "severity": AlertSeverity.HIGH,
        "title": "Signature forgery detected",
        "description": "Measurement evidence indicates a forged signature.",
    }
    values.update(overrides)
    return SecurityAlert(**values)


class TestAlertEnums:
    def test_severity_has_exactly_the_expected_members(self):
        assert {member.value for member in AlertSeverity} == {
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL",
        }

    def test_status_has_exactly_the_expected_members(self):
        assert {member.value for member in AlertStatus} == {
            "OPEN",
            "ACKNOWLEDGED",
            "RESOLVED",
        }

    def test_enums_are_string_enums(self):
        assert AlertSeverity.CRITICAL == "CRITICAL"
        assert AlertStatus.OPEN == "OPEN"
        assert isinstance(AlertSeverity.LOW, str)
        assert isinstance(AlertStatus.RESOLVED, str)


class TestSecurityAlert:
    def test_carries_required_fields(self):
        alert = build_alert()

        assert alert.alert_id == "alert_1"
        assert alert.verification_id == "ver_1"
        assert alert.threat_type == "FORGERY"
        assert alert.severity is AlertSeverity.HIGH
        assert alert.title == "Signature forgery detected"

    def test_defaults(self):
        alert = build_alert()

        assert alert.status is AlertStatus.OPEN
        assert alert.evidence == ()
        assert alert.metadata == {}

    def test_metadata_default_is_not_shared_between_instances(self):
        first = build_alert()
        second = build_alert()

        first.metadata["notified"] = True

        assert second.metadata == {}

    @pytest.mark.parametrize("status", list(AlertStatus))
    def test_accepts_every_status(self, status):
        assert build_alert(status=status).status is status

    @pytest.mark.parametrize("severity", list(AlertSeverity))
    def test_accepts_every_severity(self, severity):
        assert build_alert(severity=severity).severity is severity

    def test_carries_evidence_entries(self):
        alert = build_alert(
            evidence=({"type": "error_rate", "value": 0.4}, {"type": "digest"}),
        )

        assert len(alert.evidence) == 2
        assert alert.evidence[0]["value"] == pytest.approx(0.4)

    def test_is_frozen(self):
        alert = build_alert()

        with pytest.raises(dataclasses.FrozenInstanceError):
            alert.status = AlertStatus.RESOLVED
