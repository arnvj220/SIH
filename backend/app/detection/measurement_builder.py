"""
Build MeasurementRound objects from QuantumEvidence.

Uses projective/sampling APIs to produce realistic
per-shot expected/observed pairs across all three Pauli bases.

Design:
    expected: sampled from the ORIGINAL input state
    observed: sampled from Bob's CORRECTED state

Under legitimate teleportation these agree statistically; under
attack, they diverge.

Basis-to-bit mapping:
    0 / +  / +i  ->  0
    1 / -  / -i  ->  1
"""

from __future__ import annotations

from dataclasses import dataclass

from app.attacks.contracts import MeasurementRound
from app.quantum.measurements.evidence import QuantumEvidence
from app.quantum.measurements.outcomes import sample_measurements


BASIS_OUTCOME_MAP: dict[str, dict[str, int]] = {
    "Z": {"0": 0, "1": 1},
    "X": {"+": 0, "-": 1},
    "Y": {"+i": 0, "-i": 1},
}


# Deterministic per-basis offsets so each basis gets a distinct
# sampling stream — avoids correlating expected and observed draws.
_BASIS_OFFSET = {"X": 0, "Y": 1, "Z": 2}


@dataclass(frozen=True)
class BuilderConfig:
    """Configuration for measurement construction."""

    shots_per_basis: int = 100
    seed: int | None = None


def build_measurements(
    evidence: QuantumEvidence,
    config: BuilderConfig | None = None,
) -> tuple[MeasurementRound, ...]:
    """
    Produce MeasurementRound objects from teleportation evidence.

    For each Pauli basis:
      - expected outcomes sampled from evidence.input_state
      - observed outcomes sampled from evidence.bob_state_after_correction

    Returns rounds grouped by basis:
        (shots_per_basis X rounds, shots_per_basis Y, shots_per_basis Z)
    """
    if config is None:
        config = BuilderConfig()

    rounds: list[MeasurementRound] = []
    index = 0

    for basis in ("X", "Y", "Z"):
        expected_seed, observed_seed = _seeds_for_basis(
            basis, config.seed
        )

        expected_counts = sample_measurements(
            evidence.input_state,
            basis,
            shots=config.shots_per_basis,
            seed=expected_seed,
        )
        observed_counts = sample_measurements(
            evidence.bob_state_after_correction,
            basis,
            shots=config.shots_per_basis,
            seed=observed_seed,
        )

        expected_seq = _expand(expected_counts)
        observed_seq = _expand(observed_counts)

        for e_key, o_key in zip(expected_seq, observed_seq):
            rounds.append(
                MeasurementRound(
                    index=index,
                    basis=basis,
                    expected=BASIS_OUTCOME_MAP[basis][e_key],
                    observed=BASIS_OUTCOME_MAP[basis][o_key],
                )
            )
            index += 1

    return tuple(rounds)


def _seeds_for_basis(
    basis: str, base_seed: int | None
) -> tuple[int | None, int | None]:
    """Derive distinct seeds for expected/observed sampling."""
    if base_seed is None:
        return None, None
    offset = _BASIS_OFFSET[basis]
    expected_seed = base_seed + offset * 2
    observed_seed = base_seed + offset * 2 + 1000
    return expected_seed, observed_seed


def _expand(counts: dict[str, int]) -> list[str]:
    """Expand {'0': 3, '1': 2} → ['0','0','0','1','1'].

    Iteration order is deterministic because Python dicts preserve
    insertion order and the sample_measurements returns keys in
    a stable order.
    """
    out: list[str] = []
    for key, count in counts.items():
        out.extend([key] * count)
    return out