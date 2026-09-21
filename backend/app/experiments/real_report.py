"""
Benchmark report formatting for the real-pipeline benchmark.

Renders RealBenchmarkMetrics as human-readable markdown and JSON.
Mirrors report.py; kept separate because the two metrics classes have
different field sets (real pipeline has classification_accuracy and
per-attack naming that matches scenario names, not fabricated ones).
"""

from __future__ import annotations

import json

from app.experiments.real_benchmark import RealBenchmarkMetrics


def to_markdown(metrics: RealBenchmarkMetrics, *, title: str = "Real Benchmark") -> str:
    lines: list[str] = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    lines.append(f"| Total samples | {metrics.total} |")
    lines.append(f"| Correct decisions | {metrics.correct} |")
    lines.append(f"| Accuracy | {metrics.accuracy:.4f} |")
    lines.append(f"| Classification accuracy | {metrics.classification_accuracy:.4f} |")
    lines.append(f"| True positives | {metrics.true_positives} |")
    lines.append(f"| True negatives | {metrics.true_negatives} |")
    lines.append(f"| False positives | {metrics.false_positives} |")
    lines.append(f"| False negatives | {metrics.false_negatives} |")
    lines.append(f"| Detection rate | {metrics.detection_rate:.4f} |")
    lines.append(f"| False positive rate | {metrics.false_positive_rate:.4f} |")
    lines.append(f"| False negative rate | {metrics.false_negative_rate:.4f} |")
    lines.append(f"| Mean latency (ms) | {metrics.mean_latency_ms:.4f} |")
    lines.append(f"| P95 latency (ms) | {metrics.p95_latency_ms:.4f} |")
    lines.append("")
    lines.append("## Per-attack breakdown")
    lines.append("")
    lines.append("| Scenario | Total | Detected | Missed |")
    lines.append("|---|---:|---:|---:|")
    for name, stats in sorted(metrics.per_attack.items()):
        lines.append(
            f"| {name} | {stats['total']} | "
            f"{stats['detected']} | {stats['missed']} |"
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- Real pipeline: SignatureService -> VerificationService -> DetectionService")
    lines.append("- Channel manipulation is excluded (requires quantum-state corruption)")
    lines.append("- See docs/architecture.md Sections 8-9 for measurement construction details")
    lines.append("")
    return "\n".join(lines)


def to_json(metrics: RealBenchmarkMetrics) -> str:
    return json.dumps(
        {
            "summary": {
                "total": metrics.total,
                "correct": metrics.correct,
                "accuracy": metrics.accuracy,
                "classification_accuracy": metrics.classification_accuracy,
                "true_positives": metrics.true_positives,
                "true_negatives": metrics.true_negatives,
                "false_positives": metrics.false_positives,
                "false_negatives": metrics.false_negatives,
                "detection_rate": metrics.detection_rate,
                "false_positive_rate": metrics.false_positive_rate,
                "false_negative_rate": metrics.false_negative_rate,
                "mean_latency_ms": metrics.mean_latency_ms,
                "p95_latency_ms": metrics.p95_latency_ms,
            },
            "per_attack": metrics.per_attack,
        },
        indent=2,
    )