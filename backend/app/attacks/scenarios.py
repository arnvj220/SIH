from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .baseline import SourceFactory
from .runner import AttackExperimentConfig, VerifierFactory, run_attack_experiment

SEED = 12345

# Mirrors the SIH demo scenarios in SRS section 24 (A = legitimate is the control
# arm of every comparison, so it is produced by side_by_side()).
DEMO_SCENARIOS: dict[str, dict[str, Any]] = {
    "B_forgery": {
        "title": "Forgery",
        "narrative": "Attacker forges a signature without knowing the quantum states; "
                     "outcomes stop correlating with what the signer would produce.",
        "config": AttackExperimentConfig("forgery", {"mode": "blind_guess"}, 200, SEED),
    },
    "C_replay": {
        "title": "Replay",
        "narrative": "A valid, already-verified transaction is captured and replayed three times.",
        "config": AttackExperimentConfig("replay", {"mode": "exact", "replay_count": 3}, 200, SEED),
    },
    "D_channel": {
        "title": "Quantum channel manipulation",
        "narrative": "An eavesdropper intercepts and resends the quantum states, disturbing the "
                     "measurement statistics.",
        "config": AttackExperimentConfig(
            "channel_manipulation", {"mode": "intercept_resend", "perturbation": 0.8}, 200, SEED),
    },
    "E_impersonation": {
        "title": "Impersonation",
        "narrative": "An attacker presents a valid-looking transaction under a stolen identity.",
        "config": AttackExperimentConfig("impersonation", {"mode": "stolen_identity"}, 200, SEED),
    },
    "F_unauthorized": {
        "title": "Unauthorized verification",
        "narrative": "A revoked verifier tries to verify a signature.",
        "config": AttackExperimentConfig("unauthorized_verification", {"mode": "revoked"}, 200, SEED),
    },
}


def list_scenarios() -> list[dict[str, Any]]:
    return [
        {"id": sid, "title": s["title"], "narrative": s["narrative"], "config": s["config"].to_dict()}
        for sid, s in DEMO_SCENARIOS.items()
    ]


def save_scenario(config: AttackExperimentConfig, path: str | Path) -> Path:
    """Persist a scenario so a judge can re-run the exact same attack."""
    path = Path(path)
    path.write_text(json.dumps({"format": "qds-attack-scenario/1", **config.to_dict()}, indent=2))
    return path


def load_scenario(path: str | Path) -> AttackExperimentConfig:
    data = json.loads(Path(path).read_text())
    if data.pop("format", None) != "qds-attack-scenario/1":
        raise ValueError("not a qds-attack-scenario/1 file")
    return AttackExperimentConfig(**data)


def side_by_side(
    config: AttackExperimentConfig,
    verifier_factory: VerifierFactory | None = None,
    source_factory: SourceFactory | None = None,
) -> dict[str, Any]:
    """Legitimate vs attack under identical parameters (FR-037)."""
    report = run_attack_experiment(config, verifier_factory, source_factory)

    def summarise(records: list) -> dict[str, Any]:
        n = len(records)
        return {
            "count": n,
            "mean_error_rate": round(sum(r.error_rate for r in records) / n, 4) if n else 0.0,
            "decisions": dict(Counter(r.decision.value for r in records)),
            "threats": dict(Counter(t.value for r in records for t in r.threats)),
            "flagged_rate": round(sum(r.detected for r in records) / n, 4) if n else 0.0,
        }

    legit = summarise([r for r in report.records if r.role == "control"])
    attack = summarise([r for r in report.records if r.is_attack])
    return {
        "experiment_id": config.experiment_id,
        "config": config.to_dict(),
        "legitimate": legit,
        "attack": attack,
        "separation": {"error_rate_delta": round(attack["mean_error_rate"] - legit["mean_error_rate"], 4)},
        "metrics": report.metrics,
    }
