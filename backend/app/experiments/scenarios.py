"""
Deterministic scenario generation for benchmarking.

Every scenario is built from a seed, so the same seed produces the
same test set — this is what makes benchmarks reproducible (SR-002).
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from app.attacks.contracts import (
    MeasurementRound,
    ThreatType,
    VerificationContext,
)


@dataclass(frozen=True)
class Scenario:
    """One benchmark sample: a context plus its ground truth."""

    name: str
    context: VerificationContext
    expected_threat: ThreatType  # ThreatType.NONE for legitimate
    is_attack: bool


# ---------- helpers ----------

def _clean_measurements(
    rng: random.Random, rounds: int = 20
) -> tuple[MeasurementRound, ...]:
    """Legit: observed always equals expected."""
    out: list[MeasurementRound] = []
    for i in range(rounds):
        bit = rng.randint(0, 1)
        out.append(
            MeasurementRound(index=i, basis="Z", expected=bit, observed=bit)
        )
    return tuple(out)


def _noisy_measurements(
    rng: random.Random,
    rounds: int = 21,                    # ← multiple of 3 for even distribution
    error_rate: float = 0.6,
    target_basis: str = "Z",
) -> tuple[MeasurementRound, ...]:
    """
    Channel-manipulation attack: corrupt exactly error_rate fraction
    of the rounds measured in the target basis. Other bases stay clean.

    Uses rounds that is a multiple of 3 so each basis gets an equal share.
    """
    bases = ["X", "Y", "Z"]

    # Which rounds belong to the target basis?
    target_indices = [i for i in range(rounds) if bases[i % 3] == target_basis]

    # Choose exactly N of them to flip
    n_flip = int(round(len(target_indices) * error_rate))
    flip_set = set(rng.sample(target_indices, n_flip))

    out: list[MeasurementRound] = []
    for i in range(rounds):
        basis = bases[i % 3]
        bit = rng.randint(0, 1)
        observed = (1 - bit) if i in flip_set else bit
        out.append(
            MeasurementRound(index=i, basis=basis, expected=bit, observed=observed)
        )
    return tuple(out)


def _base_context(
    *,
    sample_id: str,
    measurements: tuple[MeasurementRound, ...],
    signer_id: str = "alice",
    expected_signer_id: str = "alice",
    verifier_id: str = "bob",
    message_digest: str = "abc",
    signed_digest: str = "abc",
    nonce: str | None = None,
) -> VerificationContext:
    return VerificationContext(
        context_id=f"ctx_{sample_id}",
        signature_id=f"sig_{sample_id}",
        signer_id=signer_id,
        expected_signer_id=expected_signer_id,
        verifier_id=verifier_id,
        message_id=f"msg_{sample_id}",
        message_digest=message_digest,
        signed_digest=signed_digest,
        session_id=f"sess_{sample_id}",
        nonce=nonce if nonce is not None else f"n_{sample_id}",
        issued_at=0.0,
        received_at=1.0,
        auth_fingerprint="fp_alice",
        measurements=measurements,
    )


# ---------- scenario builders ----------

def legit_scenario(seed: int, sample_id: str) -> Scenario:
    rng = random.Random(seed)
    ctx = _base_context(
        sample_id=sample_id,
        measurements=_clean_measurements(rng),
    )
    return Scenario(
        name="legit",
        context=ctx,
        expected_threat=ThreatType.NONE,
        is_attack=False,
    )


def forgery_scenario(seed: int, sample_id: str) -> Scenario:
    rng = random.Random(seed)
    ctx = _base_context(
        sample_id=sample_id,
        measurements=_clean_measurements(rng),
        message_digest="tampered",
        signed_digest="abc",
    )
    return Scenario(
        name="forgery",
        context=ctx,
        expected_threat=ThreatType.FORGERY,
        is_attack=True,
    )


def impersonation_scenario(seed: int, sample_id: str) -> Scenario:
    rng = random.Random(seed)
    ctx = _base_context(
        sample_id=sample_id,
        measurements=_clean_measurements(rng),
        signer_id="mallory",
        expected_signer_id="alice",
    )
    return Scenario(
        name="impersonation",
        context=ctx,
        expected_threat=ThreatType.IMPERSONATION,
        is_attack=True,
    )


def channel_manipulation_scenario(seed: int, sample_id: str) -> Scenario:
    rng = random.Random(seed)
    ctx = _base_context(
        sample_id=sample_id,
        measurements=_noisy_measurements(rng, rounds=20, error_rate=0.6),
    )
    return Scenario(
        name="channel_manipulation",
        context=ctx,
        expected_threat=ThreatType.CHANNEL_MANIPULATION,
        is_attack=True,
    )


def unauthorized_scenario(seed: int, sample_id: str) -> Scenario:
    rng = random.Random(seed)
    ctx = _base_context(
        sample_id=sample_id,
        measurements=_clean_measurements(rng),
        verifier_id="mallory",
    )
    return Scenario(
        name="unauthorized",
        context=ctx,
        expected_threat=ThreatType.UNAUTHORIZED_VERIFICATION,
        is_attack=True,
    )