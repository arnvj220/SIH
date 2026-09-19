"""Attack simulation & security-scenario engine (owner: Arnav)."""
from .base import AttackConfigError, AttackScenario
from .contracts import (
    AttackedSample,
    Decision,
    DetectionOutcome,
    MeasurementRound,
    ThreatType,
    VerificationContext,
    Verifier,
)
from .registry import ATTACK_REGISTRY, UnknownAttackError, create_attack, describe_attacks
from .runner import (
    AttackExperimentConfig,
    AttackReport,
    run_attack_experiment,
    run_attack_suite,
)

__all__ = [
    "ATTACK_REGISTRY",
    "AttackConfigError",
    "AttackExperimentConfig",
    "AttackReport",
    "AttackScenario",
    "AttackedSample",
    "Decision",
    "DetectionOutcome",
    "MeasurementRound",
    "ThreatType",
    "UnknownAttackError",
    "VerificationContext",
    "Verifier",
    "create_attack",
    "describe_attacks",
    "run_attack_experiment",
    "run_attack_suite",
]
