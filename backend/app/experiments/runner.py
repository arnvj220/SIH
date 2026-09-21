"""
Experiment runner.

Programmatic and CLI entry point for reproducible benchmark runs.

Usage:
    from app.experiments.runner import run_experiment

    metrics = run_experiment(iterations=100, seed=12345)

CLI:
    python -m app.experiments.runner --iterations 100 --seed 12345
"""

from __future__ import annotations

import argparse
import sys

from app.experiments.benchmark import BenchmarkMetrics, run_benchmark
from app.experiments.config import ExperimentConfig
from app.experiments.report import to_json, to_markdown


def run_experiment(
    *,
    iterations: int = 100,
    seed: int = 12345,
    include_replay: bool = True,
) -> BenchmarkMetrics:
    """Run a benchmark and return metrics. Thin alias for run_benchmark."""
    return run_benchmark(
        iterations=iterations,
        seed=seed,
        include_replay=include_replay,
    )


def run_from_config(config: ExperimentConfig) -> BenchmarkMetrics:
    """
    Run a benchmark configured by an ExperimentConfig.

    Recognized parameters:
        iterations (int, default 100)
        include_replay (bool, default True)
    """
    iterations = int(config.parameters.get("iterations", 100))
    include_replay = bool(config.parameters.get("include_replay", True))
    return run_benchmark(
        iterations=iterations,
        seed=config.seed,
        include_replay=include_replay,
    )


def _cli() -> int:
    parser = argparse.ArgumentParser(
        description="Run the QDS detection benchmark.",
    )
    parser.add_argument(
        "--iterations", type=int, default=100,
        help="Iterations per attack type (default: 100)",
    )
    parser.add_argument(
        "--seed", type=int, default=12345,
        help="Random seed (default: 12345)",
    )
    parser.add_argument(
        "--format", choices=("markdown", "json"), default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "--no-replay", action="store_true",
        help="Skip replay scenarios",
    )
    args = parser.parse_args()

    metrics = run_benchmark(
        iterations=args.iterations,
        seed=args.seed,
        include_replay=not args.no_replay,
    )

    if args.format == "json":
        print(to_json(metrics))
    else:
        print(to_markdown(metrics, title="Detection Benchmark"))
    return 0


if __name__ == "__main__":
    sys.exit(_cli())