"""
Run the full attack suite against Shubh's real DetectionEngine and print
per-attack detection / false-positive / classification rates.

This is the proof script for Shubh §15 DoD items 4 and 5:
    - synthetic benchmark shows 100% detection, 0 FP (via ReferenceVerifier
      path is not exercised here; this script exercises the real engine)
    - real engine detects all 5 attacks with 0 false positives

Usage (from backend/):
    python scripts/run_real_attack_suite.py
    python scripts/run_real_attack_suite.py --n-targets 500 --seed 12345
    python scripts/run_real_attack_suite.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow running as a plain script from backend/ without installing the package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.attacks.runner import run_attack_suite
from app.attacks.verifier_adapter import real_verifier_factory


def _pct(x: float) -> str:
    return f"{x * 100:6.2f}%"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-targets", type=int, default=200,
                        help="legitimate transactions per attack (default: 200)")
    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument("--json", action="store_true",
                        help="emit raw JSON instead of a table")
    args = parser.parse_args()

    reports = run_attack_suite(
        seed=args.seed,
        n_targets=args.n_targets,
        verifier_factory=real_verifier_factory,
    )

    if args.json:
        print(json.dumps([r.to_dict() for r in reports], indent=2, default=str))
        return 0

    header = (
        f"{'attack':<26} {'total':>7} {'detect':>8} {'miss':>6} "
        f"{'FP':>5} {'FP rate':>9} {'class':>8} {'mean ms':>10}"
    )
    print("Attack suite vs. DetectionEngine (real verifier)")
    print(f"n_targets={args.n_targets}  seed={args.seed}")
    print("-" * len(header))
    print(header)
    print("-" * len(header))

    all_detected = True
    total_fp = 0
    for rep in reports:
        m = rep.metrics
        det = m["detection_rate"]
        fp = m["false_positive_rate"]
        cls = m["classification_rate"]
        if m["attacks_total"] and det < 1.0:
            all_detected = False
        total_fp += m["false_positives"]
        print(
            f"{rep.config.attack_type:<26} "
            f"{m['attacks_total']:>7} "
            f"{m['attacks_detected']:>8} "
            f"{m['attacks_missed']:>6} "
            f"{m['false_positives']:>5} "
            f"{_pct(fp):>9} "
            f"{_pct(cls):>8} "
            f"{m['latency_mean_ms']:>10.4f}"
        )

    print("-" * len(header))

    if all_detected and total_fp == 0:
        print("PASS: all attacks detected at 100%, 0 false positives.")
        return 0

    if not all_detected:
        print("FAIL: at least one attack was not fully detected.")
    if total_fp:
        print(f"FAIL: {total_fp} false positives across the suite.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())