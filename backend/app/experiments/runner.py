"""
Experiment runner.

Programmatic and CLI entry point for reproducible benchmark runs.

Usage:
    from app.experiments.runner import run_experiment

    metrics = run_experiment(iterations=100, seed=12345)

CLI:
    python -m app.experiments.runner --iterations 100 --seed 12345
    python -m app.experiments.runner --mode real --iterations 50
    python -m app.experiments.runner --mode both --format markdown
"""

from __future__ import annotations

import argparse
import sys

from app.experiments.benchmark import BenchmarkMetrics, run_benchmark
from app.experiments.config import ExperimentConfig
from app.experiments.report import to_json, to_markdown
from app.experiments.real_benchmark import RealBenchmarkMetrics, run_real_benchmark
from app.experiments.real_report import (
    to_json as real_to_json,
    to_markdown as real_to_markdown,
)


def run_experiment(
    *,
    iterations: int = 100,
    seed: int = 12345,
    include_replay: bool = True,
) -> BenchmarkMetrics:
    """Run a synthetic benchmark. Thin alias for run_benchmark."""
    return run_benchmark(
        iterations=iterations,
        seed=seed,
        include_replay=include_replay,
    )


def run_from_config(config: ExperimentConfig) -> BenchmarkMetrics:
    """
    Run a synthetic benchmark configured by an ExperimentConfig.

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


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _emit(
    synthetic: BenchmarkMetrics | None,
    real: RealBenchmarkMetrics | None,
    fmt: str,
) -> None:
    """Print one or both benchmarks in the requested format."""
    chunks: list[str] = []

    if synthetic is not None:
        if fmt == "json":
            chunks.append(to_json(synthetic))
        else:
            chunks.append(to_markdown(synthetic, title="Detection Benchmark (synthetic)"))

    if real is not None:
        if fmt == "json":
            chunks.append(real_to_json(real))
        else:
            chunks.append(real_to_markdown(real, title="Detection Benchmark (real pipeline)"))

    print("\n\n".join(chunks))


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
        help="Skip replay scenarios (synthetic only)",
    )
    parser.add_argument(
        "--mode", choices=("synthetic", "real", "both"),
        default="synthetic",
        help="Which benchmark to run (default: synthetic)",
    )
    parser.add_argument(
        "--shots-per-basis", type=int, default=100,
        help="Shots per Pauli basis for real pipeline (default: 100)",
    )
    args = parser.parse_args()

    synthetic: BenchmarkMetrics | None = None
    real: RealBenchmarkMetrics | None = None

    if args.mode in ("synthetic", "both"):
        synthetic = run_benchmark(
            iterations=args.iterations,
            seed=args.seed,
            include_replay=not args.no_replay,
        )

    if args.mode in ("real", "both"):
        real = run_real_benchmark(
            iterations=args.iterations,
            seed=args.seed,
            shots_per_basis=args.shots_per_basis,
        )

    _emit(synthetic, real, args.format)
    return 0


if __name__ == "__main__":
    sys.exit(_cli())