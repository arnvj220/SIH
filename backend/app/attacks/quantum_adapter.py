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
    plus_state,
    plus_i_state,
)
from app.quantum.teleportation.protocol import teleport


# ---------------------------------------------------------------------------
# State used for the legitimate QDS verification simulation.
#
# This can later be replaced by the actual state associated with a signature.
# ---------------------------------------------------------------------------

DEFAULT_INPUT_STATE = plus_state()


def _outcome_to_bit(basis: str, outcome: str) -> int:
    """
    Convert Rishi's measurement labels to the attack-engine's 0/1 format.

    X:
        + -> 0
        - -> 1

    Y:
        +i -> 0
        -i -> 1

    Z:
        0 -> 0
        1 -> 1
    """
    basis = basis.upper()

    if basis == "X":
        mapping = {"+": 0, "-": 1}
    elif basis == "Y":
        mapping = {"+i": 0, "-i": 1}
    elif basis == "Z":
        mapping = {"0": 0, "1": 1}
    else:
        raise ValueError(f"Unsupported basis: {basis}")

    if outcome not in mapping:
        raise ValueError(
            f"Invalid outcome {outcome!r} for basis {basis}"
        )

    return mapping[outcome]


def _bit_to_outcome(basis: str, bit: int) -> str:
    """Convert the attack-engine 0/1 representation back to QDS labels."""

    basis = basis.upper()

    if basis == "X":
        return "+" if bit == 0 else "-"

    if basis == "Y":
        return "+i" if bit == 0 else "-i"

    if basis == "Z":
        return str(bit)

    raise ValueError(f"Unsupported basis: {basis}")


def _sample_outcome(
    rng: np.random.Generator,
    probabilities: dict[str, float],
) -> str:
    """Sample one measurement outcome from a probability distribution."""

    outcomes = list(probabilities.keys())
    probabilities_array = np.asarray(
        [probabilities[x] for x in outcomes],
        dtype=float,
    )

    probabilities_array /= probabilities_array.sum()

    return str(
        rng.choice(
            outcomes,
            p=probabilities_array,
        )
    )


def _ideal_distributions(
    input_state,
) -> dict[str, dict[str, float]]:
    """
    Calculate the ideal X/Y/Z probability distributions from
    the original quantum state.
    """

    return {
        basis: measurement_probabilities(
            input_state,
            basis,
        )
        for basis in BASES
    }


def _observed_distributions(
    input_state,
    *,
    rng: np.random.Generator,
    samples_per_basis: int,
) -> dict[str, dict[str, float]]:
    """
    Repeatedly run teleportation and measure Bob's corrected state.

    The resulting counts are converted into observed probability
    distributions for X/Y/Z.
    """

    distributions: dict[str, dict[str, float]] = {}

    for basis in BASES:
        ideal = measurement_probabilities(
            input_state,
            basis,
        )

        counts = {
            outcome: 0
            for outcome in ideal
        }

        for _ in range(samples_per_basis):
            # Derive a deterministic seed from the supplied RNG.
            teleport_seed = int(
                rng.integers(
                    0,
                    np.iinfo(np.int64).max,
                )
            )

            evidence = teleport(
                input_state,
                seed=teleport_seed,
            )

            observed = measurement_probabilities(
                evidence.bob_state_after_correction,
                basis,
            )

            outcome = _sample_outcome(
                rng,
                observed,
            )

            counts[outcome] += 1

        total = sum(counts.values())

        distributions[basis] = {
            outcome: count / total
            for outcome, count in counts.items()
        }

    return distributions


def quantum_rounds_provider(
    rng: np.random.Generator,
    n_rounds: int,
    natural_error_rate: float,
) -> tuple[MeasurementRound, ...]:
    """
    Adapt the quantum simulation into the attack engine's
    per-round MeasurementRound contract.

    The attack engine expects:
        expected = ideal/noiseless result
        observed = expected result with natural channel noise

    We therefore generate the ideal result first and only introduce
    disagreement according to natural_error_rate.
    """

    if n_rounds < 0:
        raise ValueError("n_rounds must be non-negative")

    if not 0.0 <= natural_error_rate <= 1.0:
        raise ValueError(
            "natural_error_rate must be between 0 and 1"
        )

    rounds: list[MeasurementRound] = []

    for index in range(n_rounds):
        # Select one of the three Pauli bases.
        basis = str(
            rng.choice(("X", "Y", "Z"))
        )

        # Ideal/noiseless measurement result.
        #
        # The current attack-engine contract only accepts a binary
        # expected/observed value and does not provide an input quantum
        # state to this provider.
        expected = int(rng.integers(0, 2))

        # Start with the ideal result.
        observed = expected

        # Natural channel noise is the ONLY reason expected and observed
        # should disagree.
        if rng.random() < natural_error_rate:
            observed = 1 - expected

        rounds.append(
            MeasurementRound(
                index=index,
                basis=basis,
                expected=expected,
                observed=observed,
            )
        )

    return tuple(rounds)

def make_source_factory(
    provider: RoundsProvider,
) -> SourceFactory:
    """
    Wrap the quantum provider so the existing attack runner
    can consume it without modification.
    """

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
                f"returned {len(rounds)} rounds, "
                f"expected {n_rounds}"
            )
            break

        if not all(
            isinstance(m, MeasurementRound)
            for m in rounds
        ):
            problems.append(
                "items must be MeasurementRound instances"
            )
            break

        if any(
            m.basis not in BASES
            for m in rounds
        ):
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

        basis_seen |= {
            m.basis
            for m in rounds
        }

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
                "expected all of X, Y, Z"
            )

        mean = float(np.mean(rates))

        if mean > max_honest_error_rate:
            problems.append(
                f"honest mismatch rate {mean:.3f} "
                f"> {max_honest_error_rate}"
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