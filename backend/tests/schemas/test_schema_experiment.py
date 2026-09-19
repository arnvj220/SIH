"""Tests for app.models.schemas.experiment."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.models.schemas.experiment import ExperimentCreate, ExperimentResult

RATE_FIELDS = ("detection_rate", "false_positive_rate", "false_negative_rate")


class TestExperimentCreate:
    def payload(self, **overrides):
        values = {
            "experiment_id": "exp_1",
            "name": "Forgery Baseline",
            "scenario": "forgery",
            "seed": 42,
            "parameters": {"rounds": 1000},
        }
        values.update(overrides)
        return values

    def test_accepts_a_valid_payload(self):
        experiment = ExperimentCreate(**self.payload())

        assert experiment.experiment_id == "exp_1"
        assert experiment.name == "Forgery Baseline"
        assert experiment.scenario == "forgery"
        assert experiment.seed == 42
        assert experiment.parameters == {"rounds": 1000}

    def test_defaults(self):
        experiment = ExperimentCreate(
            experiment_id="exp_1",
            name="Forgery Baseline",
            scenario="forgery",
        )

        assert experiment.seed == 0
        assert experiment.parameters == {}

    @pytest.mark.parametrize("field_name", ["experiment_id", "name", "scenario"])
    def test_rejects_empty_required_field(self, field_name):
        with pytest.raises(ValidationError):
            ExperimentCreate(**self.payload(**{field_name: ""}))

    @pytest.mark.parametrize("field_name", ["experiment_id", "name", "scenario"])
    def test_rejects_missing_required_field(self, field_name):
        values = self.payload()
        values.pop(field_name)

        with pytest.raises(ValidationError):
            ExperimentCreate(**values)

    @pytest.mark.parametrize(
        ("field_name", "max_length"),
        [("experiment_id", 128), ("name", 256), ("scenario", 128)],
    )
    def test_enforces_max_length(self, field_name, max_length):
        assert ExperimentCreate(**self.payload(**{field_name: "x" * max_length}))

        with pytest.raises(ValidationError):
            ExperimentCreate(**self.payload(**{field_name: "x" * (max_length + 1)}))


class TestExperimentResult:
    def payload(self, **overrides):
        values = {
            "experiment_id": "exp_1",
            "name": "Forgery Baseline",
            "scenario": "forgery",
            "seed": 42,
            "parameters": {"rounds": 1000},
            "total_samples": 1000,
            "detected_samples": 900,
            "detection_rate": 0.9,
            "false_positive_rate": 0.02,
            "false_negative_rate": 0.1,
        }
        values.update(overrides)
        return values

    def test_accepts_a_valid_payload(self):
        result = ExperimentResult(**self.payload())

        assert result.experiment_id == "exp_1"
        assert result.total_samples == 1000
        assert result.detected_samples == 900
        assert result.detection_rate == pytest.approx(0.9)

    def test_optional_fields_default_to_none_or_empty(self):
        result = ExperimentResult(**self.payload())

        assert result.verification_latency_ms is None
        assert result.simulation_throughput is None
        assert result.metrics == {}
        assert result.created_at is None

    def test_carries_optional_performance_fields(self):
        result = ExperimentResult(
            **self.payload(verification_latency_ms=12.5, simulation_throughput=850.0)
        )

        assert result.verification_latency_ms == pytest.approx(12.5)
        assert result.simulation_throughput == pytest.approx(850.0)

    @pytest.mark.parametrize("field_name", ["total_samples", "detected_samples"])
    def test_counts_must_be_non_negative(self, field_name):
        assert ExperimentResult(**self.payload(**{field_name: 0}))

        with pytest.raises(ValidationError):
            ExperimentResult(**self.payload(**{field_name: -1}))

    @pytest.mark.parametrize("field_name", RATE_FIELDS)
    @pytest.mark.parametrize("rate", [0.0, 0.5, 1.0])
    def test_rates_accept_values_within_bounds(self, field_name, rate):
        result = ExperimentResult(**self.payload(**{field_name: rate}))

        assert getattr(result, field_name) == pytest.approx(rate)

    @pytest.mark.parametrize("field_name", RATE_FIELDS)
    @pytest.mark.parametrize("rate", [-0.01, 1.01, 5.0])
    def test_rates_reject_values_outside_bounds(self, field_name, rate):
        with pytest.raises(ValidationError):
            ExperimentResult(**self.payload(**{field_name: rate}))

    @pytest.mark.parametrize("field_name", ["verification_latency_ms", "simulation_throughput"])
    def test_optional_performance_fields_must_be_non_negative(self, field_name):
        assert ExperimentResult(**self.payload(**{field_name: 0.0}))

        with pytest.raises(ValidationError):
            ExperimentResult(**self.payload(**{field_name: -1.0}))

    @pytest.mark.parametrize(
        "field_name",
        [
            "experiment_id",
            "name",
            "scenario",
            "seed",
            "parameters",
            "total_samples",
            "detected_samples",
            *RATE_FIELDS,
        ],
    )
    def test_rejects_missing_required_field(self, field_name):
        values = self.payload()
        values.pop(field_name)

        with pytest.raises(ValidationError):
            ExperimentResult(**values)

    def test_accepts_created_at(self):
        moment = datetime(2026, 1, 1, 12, 0, 0)

        assert ExperimentResult(**self.payload(created_at=moment)).created_at == moment

    def test_round_trips_through_json(self):
        result = ExperimentResult(**self.payload())

        restored = ExperimentResult.model_validate_json(result.model_dump_json())

        assert restored == result
