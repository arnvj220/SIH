"""Tests for app.models.schemas.alert."""

from datetime import datetime

import pytest 
from pydantic import ValidationError

from app.models.schemas.alert import AlertCreate, AlertResponse


def create_payload(**overrides):
    values = {
        "alert_id": "alert_1",
        "alert_type": "FORGERY",
        "severity": "HIGH",
        "title": "Signature forgery detected",
        "description": "Measurement evidence indicates a forged signature.",
        "verification_id": "ver_1",
        "attack_id": "atk_1",
        "evidence": [{"type": "error_rate", "value": 0.42}],
    }
    values.update(overrides)
    return values


class TestAlertCreate:
    def test_accepts_a_valid_payload(self):
        alert = AlertCreate(**create_payload())

        assert alert.alert_id == "alert_1"
        assert alert.alert_type == "FORGERY"
        assert alert.severity == "HIGH"
        assert alert.title == "Signature forgery detected"

    def test_defaults(self):
        alert = AlertCreate(
            alert_id="alert_1",
            alert_type="FORGERY",
            severity="HIGH",
            title="Signature forgery detected",
        )

        assert alert.description is None
        assert alert.verification_id is None
        assert alert.attack_id is None
        assert alert.evidence == []

    def test_evidence_default_is_not_shared_between_instances(self):
        first = AlertCreate(alert_id="a", alert_type="FORGERY", severity="HIGH", title="t")
        second = AlertCreate(alert_id="b", alert_type="FORGERY", severity="HIGH", title="t")

        first.evidence.append({"type": "error_rate"})

        assert second.evidence == []

    def test_carries_evidence_entries(self):
        alert = AlertCreate(**create_payload())

        assert alert.evidence[0]["value"] == pytest.approx(0.42)

    @pytest.mark.parametrize("field_name", ["alert_id", "alert_type", "severity", "title"])
    def test_rejects_empty_required_field(self, field_name):
        with pytest.raises(ValidationError):
            AlertCreate(**create_payload(**{field_name: ""}))

    @pytest.mark.parametrize("field_name", ["alert_id", "alert_type", "severity", "title"])
    def test_rejects_missing_required_field(self, field_name):
        values = create_payload()
        values.pop(field_name)

        with pytest.raises(ValidationError):
            AlertCreate(**values)

    @pytest.mark.parametrize(
        ("field_name", "max_length"),
        [
            ("alert_id", 128),
            ("alert_type", 64),
            ("severity", 32),
            ("title", 256),
            ("description", 2048),
        ],
    )
    def test_enforces_max_length(self, field_name, max_length):
        assert AlertCreate(**create_payload(**{field_name: "x" * max_length}))

        with pytest.raises(ValidationError):
            AlertCreate(**create_payload(**{field_name: "x" * (max_length + 1)}))

    def test_severity_is_a_free_form_string_here(self):
        """The schema does not constrain severity to the domain enum."""
        assert AlertCreate(**create_payload(severity="INFORMATIONAL")).severity == "INFORMATIONAL"


class TestAlertResponse:
    def payload(self, **overrides):
        values = create_payload(status="OPEN")
        values.update(overrides)
        return values

    def test_accepts_a_valid_payload(self):
        response = AlertResponse(**self.payload())

        assert response.status == "OPEN"
        assert response.alert_id == "alert_1"

    def test_inherits_the_create_fields(self):
        response = AlertResponse(**self.payload())

        assert isinstance(response, AlertCreate)
        assert response.alert_type == "FORGERY"
        assert response.evidence[0]["type"] == "error_rate"

    def test_status_is_required(self):
        values = self.payload()
        values.pop("status")

        with pytest.raises(ValidationError):
            AlertResponse(**values)

    def test_timestamps_default_to_none(self):
        response = AlertResponse(**self.payload())

        assert response.created_at is None
        assert response.resolved_at is None

    def test_accepts_timestamps(self):
        created = datetime(2026, 1, 1, 12, 0, 0)
        resolved = datetime(2026, 1, 2, 9, 30, 0)

        response = AlertResponse(**self.payload(created_at=created, resolved_at=resolved))

        assert response.created_at == created
        assert response.resolved_at == resolved

    def test_parses_iso_timestamp_strings(self):
        response = AlertResponse(**self.payload(created_at="2026-01-01T12:00:00"))

        assert response.created_at == datetime(2026, 1, 1, 12, 0, 0)

    def test_rejects_invalid_timestamp(self):
        with pytest.raises(ValidationError):
            AlertResponse(**self.payload(created_at="not-a-date"))

    def test_round_trips_through_json(self):
        response = AlertResponse(**self.payload())

        restored = AlertResponse.model_validate_json(response.model_dump_json())

        assert restored == response
