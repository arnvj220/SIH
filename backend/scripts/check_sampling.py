"""
Standalone sanity check for real measurement sampling.

Run from backend/:
    python scripts/check_sampling.py
"""

import sys
from pathlib import Path

# Ensure `backend/` is on sys.path so `app.*` imports resolve.
_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from collections import Counter

from app.detection.measurement_builder import BuilderConfig, build_measurements
from app.quantum.states.pauli_states import zero_state, plus_state, one_state
from app.quantum.teleportation.protocol import teleport


def summarize(label: str, state, seed: int, shots: int = 100) -> None:
    evidence = teleport(state, seed=seed)
    rounds = build_measurements(
        evidence,
        BuilderConfig(shots_per_basis=shots, seed=seed),
    )

    total = len(rounds)
    errors = sum(1 for r in rounds if r.is_error)

    by_basis_total = Counter()
    by_basis_errors = Counter()
    for r in rounds:
        by_basis_total[r.basis] += 1
        if r.is_error:
            by_basis_errors[r.basis] += 1

    print(f"\n=== {label} ===")
    print(f"  rounds={total}, errors={errors}, error_rate={errors/total:.4f}")
    for basis in ("X", "Y", "Z"):
        t = by_basis_total[basis]
        e = by_basis_errors[basis]
        rate = e / t if t else 0.0
        print(f"  {basis}: {e}/{t} = {rate:.4f}")


if __name__ == "__main__":
    summarize("zero_state", zero_state(), seed=42)
    summarize("one_state", one_state(), seed=42)
    summarize("plus_state", plus_state(), seed=42)