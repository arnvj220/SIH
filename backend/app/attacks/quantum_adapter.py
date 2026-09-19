from __future__ import annotations

from typing import Any

import numpy as np

from app.attacks.baseline import BaselineConfig, BaselineFactory, RoundsProvider, SourceFactory
from app.attacks.contracts import BASES, MeasurementRound


def make_source_factory(provider: RoundsProvider) -> SourceFactory:
    """Wrap any rounds provider into a source factory the runner/benchmark accept."""

    def factory(seed: int, rounds: int, natural_error_rate: float) -> BaselineFactory:
        cfg = BaselineConfig(rounds=rounds, natural_error_rate=natural_error_rate)
        return BaselineFactory(cfg, seed, rounds_provider=provider)

    return factory


# --------------------------------------------------------------------------- #
# TODO(Arnav + Rishi): implement using the real quantum package.
# Contract, per round i in range(n_rounds):
#   basis     "X" | "Y" | "Z"   Pauli basis this round was measured in
#   expected  0 | 1             ideal (noise-free) outcome
#   observed  0 | 1             actual measured outcome; == expected except honest noise
# Requirements: use ONLY `rng` for randomness (so a seed reproduces the run), be fast
# (benchmarks call this thousands of times), and honour `natural_error_rate` if his
# noise model supports it.
# --------------------------------------------------------------------------- #
def quantum_rounds_provider(
    rng: np.random.Generator, n_rounds: int, natural_error_rate: float
) -> tuple[MeasurementRound, ...]:
    raise NotImplementedError(
        "Wire this to the quantum package. Run scripts/inspect_quantum.py and send the output."
    )


quantum_source_factory: SourceFactory = make_source_factory(quantum_rounds_provider)


# --------------------------------------------------------------------------- #
def validate_rounds_provider(
    provider: RoundsProvider, n_rounds: int = 200, natural_error_rate: float = 0.01,
    seed: int = 1, samples: int = 30, max_honest_error_rate: float = 0.05,
) -> dict[str, Any]:
    """Check a provider against the contract. Raises AssertionError with a clear message."""
    problems: list[str] = []
    rates: list[float] = []
    basis_seen: set[str] = set()

    for i in range(samples):
        rounds = tuple(provider(np.random.default_rng(seed + i), n_rounds, natural_error_rate))
        if len(rounds) != n_rounds:
            problems.append(f"returned {len(rounds)} rounds, expected {n_rounds}")
            break
        if not all(isinstance(m, MeasurementRound) for m in rounds):
            problems.append("items must be MeasurementRound instances")
            break
        if any(m.basis not in BASES for m in rounds):
            problems.append(f"basis must be one of {BASES}")
            break
        if any(m.expected not in (0, 1) or m.observed not in (0, 1) for m in rounds):
            problems.append("expected/observed must be 0 or 1 (plain int)")
            break
        basis_seen |= {m.basis for m in rounds}
        rates.append(sum(m.expected != m.observed for m in rounds) / n_rounds)

    if not problems:
        a = tuple(provider(np.random.default_rng(seed), n_rounds, natural_error_rate))
        b = tuple(provider(np.random.default_rng(seed), n_rounds, natural_error_rate))
        if a != b:
            problems.append("not reproducible: same rng seed gave different rounds "
                            "(use ONLY the rng passed in for randomness)")
        if basis_seen != set(BASES):
            problems.append(f"only bases {sorted(basis_seen)} appeared; expected all of X, Y, Z")
        mean = float(np.mean(rates))
        if mean > max_honest_error_rate:
            problems.append(f"honest mismatch rate {mean:.3f} > {max_honest_error_rate}: 'observed' must "
                            "equal 'expected' apart from small noise, otherwise every signature looks attacked")
        if mean == 0.0 and natural_error_rate > 0:
            problems.append("no noise at all: observed == expected everywhere. Fine for a first test, but "
                            "false-positive numbers will be optimistic")

    if problems:
        raise AssertionError("rounds provider violates the contract:\n  - " + "\n  - ".join(problems))
    return {"ok": True, "samples": samples, "rounds": n_rounds,
            "mean_honest_error_rate": round(float(np.mean(rates)), 5), "bases": sorted(basis_seen)}
