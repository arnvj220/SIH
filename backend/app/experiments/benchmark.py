"""
Benchmark runner.

Runs a configured set of legitimate and attack scenarios through
the detection engine and reports security and performance metrics.
"""

from __future__ import annotations

import statistics
import time
from dataclasses import dataclass, field

from app.attacks.contracts import Decision, ThreatType
from app.detection.engine import DetectionEngine
from app.detection.stores import AuthorizationStore, ReplayStore
from app.experiments.scenarios import (
    Scenario,
    channel_manipulation_scenario,
    forgery_scenario,
    impersonation_scenario,
    legit_scenario,
    unauthorized_scenario,
)


@dataclass
class BenchmarkMetrics:
    """Aggregate results of one benchmark run."""

    total: int = 0
    correct: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    true_positives: int = 0
    true_negatives: int = 0

    classified_correctly: int = 0
    classified_wrongly: int = 0

    latencies_ms: list[float] = field(default_factory=list)
    per_attack: dict[str, dict] = field(default_factory=dict)

    @property
    def classification_accuracy(self) -> float:
        denom = self.classified_correctly + self.classified_wrongly
        return self.classified_correctly / denom if denom else 0.0

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 0.0

    @property
    def detection_rate(self) -> float:
        denom = self.true_positives + self.false_negatives
        return self.true_positives / denom if denom else 0.0

    @property
    def false_positive_rate(self) -> float:
        denom = self.false_positives + self.true_negatives
        return self.false_positives / denom if denom else 0.0

    @property
    def false_negative_rate(self) -> float:
        denom = self.false_negatives + self.true_positives
        return self.false_negatives / denom if denom else 0.0

    @property
    def mean_latency_ms(self) -> float:
        return statistics.mean(self.latencies_ms) if self.latencies_ms else 0.0

    @property
    def p95_latency_ms(self) -> float:
        if not self.latencies_ms:
            return 0.0
        sorted_lat = sorted(self.latencies_ms)
        idx = int(0.95 * (len(sorted_lat) - 1))
        return sorted_lat[idx]


def _evaluate(metrics, scenario, outcome_decision, threats):
    flagged = outcome_decision != Decision.ACCEPT
    is_attack = scenario.is_attack
    correct_threat = scenario.expected_threat in threats

    if is_attack and flagged and correct_threat:
        metrics.true_positives += 1
        metrics.correct += 1
        metrics.classified_correctly += 1
    elif is_attack and flagged:
        metrics.true_positives += 1
        metrics.classified_wrongly += 1
    elif is_attack and not flagged:
        metrics.false_negatives += 1
        metrics.classified_wrongly += 1
    elif not is_attack and flagged:
        metrics.false_positives += 1
    else:
        metrics.true_negatives += 1
        metrics.correct += 1
        metrics.classified_correctly += 1

    name = scenario.name
    metrics.per_attack.setdefault(
        name, {"total": 0, "detected": 0, "missed": 0}
    )
    metrics.per_attack[name]["total"] += 1
    if is_attack:
        if scenario.expected_threat in threats:
            metrics.per_attack[name]["detected"] += 1
        else:
            metrics.per_attack[name]["missed"] += 1


def run_benchmark(
    *,
    iterations: int = 100,
    seed: int = 12345,
    include_replay: bool = True,
) -> BenchmarkMetrics:
    """Run a full benchmark suite."""
    metrics = BenchmarkMetrics()

    replay_store = ReplayStore()
    auth_store = AuthorizationStore()
    auth_store.allow("alice", "bob")  # restrict so unauthorized fires

    engine = DetectionEngine(
        replay_store=replay_store,
        authorization_store=auth_store,
    )

    builders = [
        legit_scenario,
        forgery_scenario,
        impersonation_scenario,
        channel_manipulation_scenario,
        unauthorized_scenario,
    ]

    for i in range(iterations):
        for build in builders:
            scenario = build(seed + i, sample_id=f"{build.__name__}_{i}")
            t0 = time.perf_counter()
            outcome = engine.verify(scenario.context)
            t1 = time.perf_counter()

            metrics.total += 1
            metrics.latencies_ms.append((t1 - t0) * 1000.0)
            _evaluate(metrics, scenario, outcome.decision, list(outcome.threats))

        if include_replay:
            base_ctx = legit_scenario(seed + i, sample_id=f"replay_{i}").context
            engine.verify(base_ctx)
            t0 = time.perf_counter()
            second = engine.verify(base_ctx)
            t1 = time.perf_counter()

            metrics.total += 1
            metrics.latencies_ms.append((t1 - t0) * 1000.0)

            replay_scenario_obj = Scenario(
                name="replay",
                context=base_ctx,
                expected_threat=ThreatType.REPLAY,
                is_attack=True,
            )
            _evaluate(
                metrics,
                replay_scenario_obj,
                second.decision,
                list(second.threats),
            )

    return metrics