"""
Adapter between the attack engine and the real detection engine.

The runner needs exactly one thing: an object with

    verify(context: VerificationContext) -> DetectionOutcome

DetectionEngine (Shubh's engine, app/detection/engine.py) implements that
protocol directly, so no wrapper class is needed.

What this module is responsible for:
    1. Constructing a DetectionEngine with FRESH stores per instance.
       Using the module-level DEFAULT_REPLAY_STORE / DEFAULT_AUTHORIZATION_STORE
       singletons would share replay and auth state across the attack arm and
       the control arm, violating SR-005 (attack isolation) and SR-002
       (deterministic decisions).
    2. Pre-registering every (signer, verifier) pair the baseline can produce,
       so legitimate traffic stays authorized while the revoked/rogue verifiers
       used by UnauthorizedVerificationAttack are rejected. Without this,
       AuthorizationStore runs in open mode and the unauthorized attack is
       never detected.

Usage:
    from app.attacks.verifier_adapter import real_verifier_factory
    from app.attacks.runner import run_attack_suite

    reports = run_attack_suite(verifier_factory=real_verifier_factory)

Validation:
    from app.attacks.verifier_adapter import validate_verifier, real_verifier_factory
    assert validate_verifier(real_verifier_factory)["ok"]
"""
from __future__ import annotations

from typing import Any, Callable

from app.attacks.baseline import BaselineConfig, BaselineFactory
from app.attacks.contracts import (
    Decision,
    DetectionOutcome,
    ThreatType,
    VerificationContext,
    Verifier,
)

VerifierFactory = Callable[[], Verifier]


def real_verifier_factory() -> Verifier:
    """
    Build a fresh DetectionEngine wired for the attack suite.

    Lazy import keeps this module importable even when the detection package
    is not on the path (e.g. attack-only unit tests, CI on a partial checkout).
    """
    from app.detection import DetectionEngine
    from app.detection.stores import AuthorizationStore, ReplayStore

    config = BaselineConfig()

    auth_store = AuthorizationStore()
    for signer in config.signers:
        for verifier in config.authorized_verifiers:
            auth_store.allow(signer, verifier)

    return DetectionEngine(
        replay_store=ReplayStore(),
        authorization_store=auth_store,
    )


def validate_verifier(factory: VerifierFactory, samples: int = 20) -> dict[str, Any]:
    """
    Check a verifier factory against the contract.

    Raises AssertionError with a clear message on any violation; never
    silently accepts a broken integration.
    """
    problems: list[str] = []

    try:
        verifier = factory()
    except Exception as exc:  # noqa: BLE001
        raise AssertionError(
            f"verifier_factory() raised: {type(exc).__name__}: {exc}"
        ) from None

    if not hasattr(verifier, "verify") or not callable(verifier.verify):
        raise AssertionError("verifier has no callable .verify(context) method")

    src = BaselineFactory(seed=1)
    legit_ctx = src.make_legitimate()

    try:
        out = verifier.verify(legit_ctx)
    except Exception as exc:  # noqa: BLE001
        raise AssertionError(
            f"verify() raised on a legitimate context: {type(exc).__name__}: {exc}"
        ) from None

    if not isinstance(out, DetectionOutcome):
        problems.append(
            f"verify() must return a DetectionOutcome, got {type(out).__name__}. "
            "If your real class returns something else, wrap it."
        )
    else:
        if not isinstance(out.decision, Decision):
            problems.append(
                f"outcome.decision must be a Decision enum, got {out.decision!r}"
            )
        if not isinstance(out.threats, list) or not all(
            isinstance(t, ThreatType) for t in out.threats
        ):
            problems.append(
                f"outcome.threats must be a list[ThreatType], got {out.threats!r}"
            )

    if not problems:
        legit_flags = 0
        for i in range(samples):
            ctx = BaselineFactory(seed=100 + i).make_legitimate()
            # Fresh instance each time: proves no cross-instance state leakage.
            legit_flags += factory().verify(ctx).detected
        if legit_flags > 0:
            problems.append(
                f"{legit_flags}/{samples} FRESH legitimate signatures were flagged "
                "as attacks - check thresholds/config, or that replay/session "
                "state isn't shared across instances"
            )

        v = factory()
        r1 = v.verify(legit_ctx)
        r2 = v.verify(legit_ctx)
        if (
            r1.decision,
            tuple(r1.threats),
        ) == (
            r2.decision,
            tuple(r2.threats),
        ) and r1.decision == Decision.ACCEPT:
            problems.append(
                "verifying the SAME context twice returned ACCEPT both times - "
                "replay protection looks inactive (a real verifier should "
                "reject the second attempt)"
            )

    if problems:
        raise AssertionError(
            "verifier violates the contract:\n  - " + "\n  - ".join(problems)
        )
    return {"ok": True, "samples": samples, "false_positives_on_fresh_legit": 0}