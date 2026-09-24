from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Callable

import numpy as np

from .base import AttackConfigError
from .baseline import SourceFactory, default_source_factory
from .contracts import (
    AttackedSample,
    Decision,
    DetectionOutcome,
    ThreatType,
    Verifier,
)
from .registry import ATTACK_REGISTRY, create_attack
from .verifier_adapter import real_verifier_factory

VerifierFactory = Callable[[], Verifier]



@dataclass
class AttackExperimentConfig:
    attack_type: str
    parameters: dict[str, Any] = field(default_factory=dict)
    n_targets: int = 100  # legitimate transactions to attack (and to use as control)
    seed: int = 12345
    rounds: int = 200  # measurement rounds per signature
    natural_error_rate: float = 0.01

    def validate(self) -> None:
        if not 1 <= self.n_targets <= 100_000:
            raise AttackConfigError("n_targets must be in [1, 100000]")
        if self.rounds < 1:
            raise AttackConfigError("rounds must be >= 1")
        if not 0.0 <= self.natural_error_rate < 0.5:
            raise AttackConfigError("natural_error_rate must be in [0, 0.5)")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def experiment_id(self) -> str:
        blob = json.dumps(self.to_dict(), sort_keys=True, default=str)
        return "exp_" + hashlib.sha256(blob.encode()).hexdigest()[:12]


@dataclass
class SampleRecord:
    context_id: str
    role: str
    is_attack: bool
    expected_threat: ThreatType
    decision: Decision
    threats: list[ThreatType]
    detected: bool
    correctly_classified: bool
    latency_ms: float
    error: str | None = None
    error_rate: float = 0.0
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass
class AttackReport:
    config: AttackExperimentConfig
    metrics: dict[str, Any]
    attack_evidence: dict[str, Any]
    records: list[SampleRecord]

    def to_dict(self, include_records: bool = False) -> dict[str, Any]:
        out: dict[str, Any] = {
            "experiment_id": self.config.experiment_id,
            "config": self.config.to_dict(),
            "metrics": self.metrics,
            "attack_evidence": self.attack_evidence,
        }
        if include_records:
            out["records"] = [asdict(r) for r in self.records]
        return out


def _submit(verifier: Verifier, sample: AttackedSample) -> SampleRecord:
    start = time.perf_counter()
    error = None
    try:
        outcome = verifier.verify(sample.context)
    except Exception as exc:  # noqa: BLE001 - fail closed, but make it visible
        outcome = DetectionOutcome(Decision.REJECT, [], [{"error": repr(exc)}])
        error = repr(exc)
    latency_ms = (time.perf_counter() - start) * 1000.0
    return SampleRecord(
        context_id=sample.context.context_id,
        role=sample.role,
        is_attack=sample.is_attack,
        expected_threat=sample.expected_threat,
        decision=outcome.decision,
        threats=list(outcome.threats),
        detected=outcome.detected,
        correctly_classified=sample.expected_threat in outcome.threats,
        latency_ms=latency_ms,
        error=error,
        error_rate=sample.context.error_rate,
        evidence=sample.evidence,
    )


def _ratio(num: int, den: int) -> float:
    return round(num / den, 6) if den else 0.0


def _compute_metrics(records: list[SampleRecord], wall_s: float) -> dict[str, Any]:
    attacks = [r for r in records if r.is_attack]
    benign = [r for r in records if not r.is_attack]
    detected = [r for r in attacks if r.detected]
    exact = [r for r in detected if set(r.threats) == {r.expected_threat}]
    correct = [r for r in detected if r.correctly_classified]
    false_pos = [r for r in benign if r.detected]
    lat = np.array([r.latency_ms for r in records]) if records else np.array([0.0])
    decisions: dict[str, int] = {}
    for r in attacks:
        decisions[r.decision.value] = decisions.get(r.decision.value, 0) + 1

    fingerprint_src = json.dumps(
        [(r.context_id, r.decision.value, sorted(t.value for t in r.threats)) for r in records]
    )
    return {
        "attacks_total": len(attacks),
        "attacks_detected": len(detected),
        "attacks_missed": len(attacks) - len(detected),
        "detection_rate": _ratio(len(detected), len(attacks)),
        "false_negative_rate": _ratio(len(attacks) - len(detected), len(attacks)),
        "classification_rate": _ratio(len(correct), len(attacks)),
        "exact_classification_rate": _ratio(len(exact), len(attacks)),
        "attack_decisions": decisions,
        "benign_total": len(benign),
        "false_positives": len(false_pos),
        "false_positive_rate": _ratio(len(false_pos), len(benign)),
        "attack_mean_error_rate": round(float(np.mean([r.error_rate for r in attacks])), 4) if attacks else 0.0,
        "benign_mean_error_rate": round(float(np.mean([r.error_rate for r in benign])), 4) if benign else 0.0,
        "verifier_errors": sum(1 for r in records if r.error),
        "latency_mean_ms": round(float(lat.mean()), 4),
        "latency_p95_ms": round(float(np.percentile(lat, 95)), 4),
        "throughput_per_s": round(len(records) / wall_s, 1) if wall_s > 0 else 0.0,
        "result_fingerprint": hashlib.sha256(fingerprint_src.encode()).hexdigest()[:16],
    }


def run_attack_experiment(
    config: AttackExperimentConfig,
    verifier_factory: VerifierFactory | None = None,
    source_factory: SourceFactory | None = None,
) -> AttackReport:
    config.validate()
    make_verifier: VerifierFactory = verifier_factory or real_verifier_factory

    seeds = [int(s.generate_state(1)[0]) for s in np.random.SeedSequence(config.seed).spawn(3)]
    base_seed, attack_seed, control_seed = seeds

    attack = create_attack(config.attack_type, seed=attack_seed, parameters=config.parameters)
    make_source = source_factory or default_source_factory
    targets = make_source(base_seed, config.rounds, config.natural_error_rate)
    control = make_source(control_seed, config.rounds, config.natural_error_rate)

    attack_verifier = make_verifier()
    control_verifier = make_verifier()  # isolated state
    records: list[SampleRecord] = []

    t0 = time.perf_counter()
    for _ in range(config.n_targets):
        for sample in attack.execute(targets.make_legitimate()):
            records.append(_submit(attack_verifier, sample))
    for _ in range(config.n_targets):
        sample = AttackedSample(control.make_legitimate(), False, ThreatType.NONE, "control")
        records.append(_submit(control_verifier, sample))
    wall = time.perf_counter() - t0

    return AttackReport(config, _compute_metrics(records, wall), attack.collect_evidence(), records)


def run_attack_suite(
    seed: int = 12345,
    n_targets: int = 200,
    overrides: dict[str, dict[str, Any]] | None = None,
    verifier_factory: VerifierFactory | None = None,
    source_factory: SourceFactory | None = None,
) -> list[AttackReport]:
    """Run every registered attack with defaults (benchmark table, SRS 25.6)."""
    overrides = overrides or {}
    return [
        run_attack_experiment(
            AttackExperimentConfig(
                attack_type=name,
                parameters=overrides.get(name, {}),
                n_targets=n_targets,
                seed=seed,
            ),
            verifier_factory,
            source_factory,
        )
        for name in ATTACK_REGISTRY
    ]