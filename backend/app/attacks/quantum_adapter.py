from __future__ import annotations

from typing import Any

import numpy as np

from app.attacks.baseline import (
    BaselineConfig,
    BaselineFactory,
    RoundsProvider,
    SourceFactory,
)
from app.attacks.contracts import BASES, MeasurementRound

from app.quantum.measurements.projective import measurement_probabilities
from app.quantum.states.pauli_states import (
    zero_state,
    one_state,
    plus_state,
    minus_state,
    plus_i_state,
    minus_i_state,
)
from app.quantum.teleportation.protocol import teleport


def make_source_factory(provider: RoundsProvider) -> SourceFactory:
    """Wrap a quantum rounds provider as a source factory."""

    def factory(
        seed: int,
        rounds: int,
        natural_error_rate: float,
    ) -> BaselineFactory:
        config = BaselineConfig(
            rounds=rounds,
            natural_error_rate=natural_error_rate,
        )

        return BaselineFactory(
            config,
            seed,
            rounds_provider=provider,
        )

    return factory


def _state_for_basis(
    rng: np.random.Generator,
    basis: str,
):
    """
    Return a random eigenstate for the requested Pauli basis.

    The returned state has a deterministic measurement outcome
    in that basis.
    """

    if basis == "Z":
        if rng.integers(0, 2) == 0:
            return zero_state(), 0
        return one_state(), 1

    if basis == "X":
        if rng.integers(0, 2) == 0:
            return plus_state(), 0
        return minus_state(), 1

    if basis == "Y":
        if rng.integers(0, 2) == 0:
            return plus_i_state(), 0
        return minus_i_state(), 1

    raise ValueError(f"Unsupported basis: {basis}")


def _sample_measurement(
    rng: np.random.Generator,
    state,
    basis: str,
) -> int:
    """Measure a single qubit in the requested Pauli basis."""

    probabilities = measurement_probabilities(state, basis)

    if basis == "Z":
        zero_probability = probabilities["0"]

    elif basis == "X":
        zero_probability = probabilities["+"]

    elif basis == "Y":
        zero_probability = probabilities["+i"]

    else:
        raise ValueError(f"Unsupported basis: {basis}")

    return int(rng.random() >= zero_probability)


def quantum_rounds_provider(
    rng: np.random.Generator,
    n_rounds: int,
    natural_error_rate: float,
) -> tuple[MeasurementRound, ...]:
    """
    Generate measurement rounds using the real quantum teleportation code.

    For every round:

        basis
            Pauli basis used for verification.

        expected
            Ideal measurement result of the original eigenstate.

        observed
            Measurement result of Bob's corrected state.

    Only the RNG supplied by the attack engine is used for randomness.
    """

    if n_rounds < 0:
        raise ValueError("n_rounds must be non-negative")

    if not 0 <= natural_error_rate <= 1:
        raise ValueError("natural_error_rate must be between 0 and 1")

    rounds: list[MeasurementRound] = []

    for index in range(n_rounds):
        basis = str(rng.choice(BASES))

        input_state, expected = _state_for_basis(
            rng,
            basis,
        )

        # Derive a deterministic seed from the supplied RNG.
        # This keeps teleportation reproducible.
        teleport_seed = int(
            rng.integers(0, np.iinfo(np.int64).max)
        )

        evidence = teleport(
            input_state,
            seed=teleport_seed,
        )

        observed = _sample_measurement(
            rng,
            evidence.bob_state_after_correction,
            basis,
        )

        # Apply the configured honest-channel noise model.
        if rng.random() < natural_error_rate:
            observed = 1 - observed

        rounds.append(
            MeasurementRound(
                index=index,
                basis=basis,
                expected=expected,
                observed=observed,
            )
        )

    return tuple(rounds)


quantum_source_factory: SourceFactory = make_source_factory(
    quantum_rounds_provider
)


def validate_rounds_provider(
    provider: RoundsProvider,
    n_rounds: int = 200,
    natural_error_rate: float = 0.01,
    seed: int = 1,
    samples: int = 30,
    max_honest_error_rate: float = 0.05,
) -> dict[str, Any]:
    """Validate the quantum provider against the attack-engine contract."""

    problems: list[str] = []
    rates: list[float] = []
    basis_seen: set[str] = set()

    for i in range(samples):
        rounds = tuple(
            provider(
                np.random.default_rng(seed + i),
                n_rounds,
                natural_error_rate,
            )
        )

        if len(rounds) != n_rounds:
            problems.append(
                f"returned {len(rounds)} rounds, expected {n_rounds}"
            )
            break

        if not all(isinstance(m, MeasurementRound) for m in rounds):
            problems.append(
                "items must be MeasurementRound instances"
            )
            break

        if any(m.basis not in BASES for m in rounds):
            problems.append(
                f"basis must be one of {BASES}"
            )
            break

        if any(
            m.expected not in (0, 1)
            or m.observed not in (0, 1)
            for m in rounds
        ):
            problems.append(
                "expected/observed must be 0 or 1"
            )
            break

        basis_seen |= {m.basis for m in rounds}

        rates.append(
            sum(
                m.expected != m.observed
                for m in rounds
            )
            / n_rounds
        )

    if not problems:
        a = tuple(
            provider(
                np.random.default_rng(seed),
                n_rounds,
                natural_error_rate,
            )
        )

        b = tuple(
            provider(
                np.random.default_rng(seed),
                n_rounds,
                natural_error_rate,
            )
        )

        if a != b:
            problems.append(
                "not reproducible: same RNG seed "
                "gave different rounds"
            )

        if basis_seen != set(BASES):
            problems.append(
                f"only bases {sorted(basis_seen)} appeared; "
                "expected X, Y, Z"
            )

        mean = float(np.mean(rates))

        if mean > max_honest_error_rate:
            problems.append(
                f"honest mismatch rate {mean:.3f} > "
                f"{max_honest_error_rate}"
            )

    if problems:
        raise AssertionError(
            "rounds provider violates the contract:\n  - "
            + "\n  - ".join(problems)
        )

    return {
        "ok": True,
        "samples": samples,
        "rounds": n_rounds,
        "mean_honest_error_rate": round(
            float(np.mean(rates)),
            5,
        ),
        "bases": sorted(basis_seen),
    }