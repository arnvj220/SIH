"""Tests for the benchmark runner and report formatter."""

import json

import pytest

from app.experiments.benchmark import run_benchmark
from app.experiments.config import ExperimentConfig
from app.experiments.report import to_json, to_markdown
from app.experiments.runner import run_experiment, run_from_config
from app.experiments.scenarios import (
    channel_manipulation_scenario,
    forgery_scenario,
    impersonation_scenario,
    legit_scenario,
    unauthorized_scenario,
)


class TestScenarios:
    def test_legit_scenario_is_marked_non_attack(self):
        s = legit_scenario(seed=1, sample_id="t1")
        assert s.is_attack is False

    def test_all_attack_scenarios_are_marked_attack(self):
        for build in (
            forgery_scenario,
            impersonation_scenario,
            channel_manipulation_scenario,
            unauthorized_scenario,
        ):
            s = build(seed=1, sample_id="t1")
            assert s.is_attack is True

    def test_scenarios_are_deterministic(self):
        a = forgery_scenario(seed=42, sample_id="x")
        b = forgery_scenario(seed=42, sample_id="x")
        assert a.context == b.context


class TestBenchmarkMetrics:
    def test_small_benchmark_runs(self):
        metrics = run_benchmark(iterations=5, seed=7)
        # 5 iterations × (5 scenarios + 1 replay) = 30 samples
        assert metrics.total == 30

    def test_detection_rate_is_high(self):
        metrics = run_benchmark(iterations=20, seed=42)
        assert metrics.detection_rate >= 0.9

    def test_false_positive_rate_is_near_zero(self):
        metrics = run_benchmark(iterations=20, seed=42)
        assert metrics.false_positive_rate <= 0.05

    def test_latencies_recorded(self):
        metrics = run_benchmark(iterations=5, seed=1)
        assert len(metrics.latencies_ms) == metrics.total

    def test_deterministic_metrics_with_same_seed(self):
        a = run_benchmark(iterations=10, seed=99)
        b = run_benchmark(iterations=10, seed=99)
        assert a.total == b.total
        assert a.true_positives == b.true_positives
        assert a.false_positives == b.false_positives


class TestRunner:
    def test_run_experiment_returns_metrics(self):
        metrics = run_experiment(iterations=3, seed=1)
        assert metrics.total > 0

    def test_run_from_config(self):
        config = ExperimentConfig(
            name="test",
            attack="all",
            seed=42,
            parameters={"iterations": 3},
        )
        metrics = run_from_config(config)
        assert metrics.total > 0

    def test_run_from_config_default_iterations(self):
        config = ExperimentConfig(name="test", attack="all", seed=1)
        metrics = run_from_config(config)
        # Default 100 iterations × 6 = 600
        assert metrics.total == 600


class TestReport:
    def test_markdown_contains_summary(self):
        metrics = run_benchmark(iterations=3, seed=1)
        md = to_markdown(metrics, title="Test Run")
        assert "# Test Run" in md
        assert "Detection rate" in md
        assert "Per-attack breakdown" in md

    def test_json_is_valid(self):
        metrics = run_benchmark(iterations=3, seed=1)
        parsed = json.loads(to_json(metrics))
        assert "summary" in parsed
        assert "per_attack" in parsed
        assert parsed["summary"]["total"] == metrics.total