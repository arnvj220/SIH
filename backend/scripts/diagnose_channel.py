# backend/scripts/diagnose_channel.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from app.detection.measurement_builder import BuilderConfig, build_measurements
from app.quantum.states.pauli_states import plus_state
from app.quantum.teleportation.protocol import teleport


def per_basis_error_rates(rounds):
    out = {}
    for basis in ("X", "Y", "Z"):
        subset = [m for m in rounds if m.basis == basis]
        if not subset:
            out[basis] = 0.0
            continue
        errs = sum(m.is_error for m in subset)
        out[basis] = errs / len(subset)
    return out


def skew(rates):
    return max(rates.values()) - min(rates.values())


def main() -> None:
    state = plus_state()
    shots = 100

    print(f"{'seed':>5} {'X':>7} {'Y':>7} {'Z':>7} {'skew':>7}")
    print("-" * 40)

    hits = []
    for seed in range(200):
        ev = teleport(state, seed=seed)
        rounds = build_measurements(
            ev,
            BuilderConfig(shots_per_basis=shots, seed=ev.seed),
        )
        rates = per_basis_error_rates(rounds)
        s = skew(rates)
        flag = "  <-- skew > 0.15" if s > 0.15 else ""
        if s > 0.10:
            print(f"{seed:>5} {rates['X']:>7.3f} {rates['Y']:>7.3f} "
                  f"{rates['Z']:>7.3f} {s:>7.3f}{flag}")
        if s > 0.15:
            hits.append((seed, rates, s))

    print()
    print(f"{len(hits)} seeds with skew > 0.15 out of 200")
    for seed, rates, s in hits:
        print(f"  seed={seed}  X={rates['X']:.3f} Y={rates['Y']:.3f} "
              f"Z={rates['Z']:.3f} skew={s:.3f}")


if __name__ == "__main__":
    main()