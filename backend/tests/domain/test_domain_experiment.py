"""Tests for app.models.domain.experiment."""

import dataclasses

import pytest

from app.models.domain import ExperimentConfig, ExperimentResult


class TestExperimentConfig:
    def test_defaults(self):
        config = ExperimentConfig(name="Forgery Baseline", scenario="forgery")

        assert config.seed == 0
        assert config.rounds == 200
        assert config.parameters == {}

    def test_carries_overrides(self):
        config = ExperimentConfig(
            name="Replay Sweep",
            scenario="replay",
            seed=42,
            rounds=1000,
            parameters={"window_seconds": 30},
        )

        assert config.name == "Replay Sweep"
        assert config.scenario == "replay"
        assert config.seed == 42
        assert config.rounds == 1000
        assert config.parameters == {"window_seconds": 30}

    def test_parameters_default_is_not_shared_between_instances(self):
        first = ExperimentConfig(name="a", scenario="forgery")
        second = ExperimentConfig(name="b", scenario="forgery")

        first.parameters["window_seconds"] = 30

        assert second.parameters == {}

    def test_is_frozen(self):
        config = ExperimentConfig(name="a", scenario="forgery")

        with pytest.raises(dataclasses.FrozenInstanceError):
            config.rounds = 10


class TestExperimentResult:
    def build(self, **overrides):
        values = {
            "experiment_id": "exp_1",
            "name": "Forgery Baseline",
            "scenario": "forgery",
            "total_samples": 200,
            "detected_samples": 180,
            "false_positives": 5,
            "false_negatives": 20,
            "detection_rate": 0.9,
            "false_positive_rate": 0.025,
            "false_negative_rate": 0.1,
            "duration_seconds": 12.5,
        }
        values.update(overrides)
        return ExperimentResult(**values)

    def test_carries_all_fields(self):
        result = self.build()

        assert result.experiment_id == "exp_1"
        assert result.name == "Forgery Baseline"
        assert result.scenario == "forgery"
        assert result.total_samples == 200
        assert result.detected_samples == 180
        assert result.false_positives == 5
        assert result.false_negatives == 20
        assert result.detection_rate == pytest.approx(0.9)
        assert result.false_positive_rate == pytest.approx(0.025)
        assert result.false_negative_rate == pytest.approx(0.1)
        assert result.duration_seconds == pytest.approx(12.5)

    def test_metadata_defaults_to_empty_dict(self):
        assert self.build().metadata == {}

    def test_metadata_default_is_not_shared_between_instances(self):
        first = self.build()
        second = self.build()

        first.metadata["git_sha"] = "abc123"

        assert second.metadata == {}

    def test_is_frozen(self):
        result = self.build()

        with pytest.raises(dataclasses.FrozenInstanceError):
            result.detection_rate = 0.1
