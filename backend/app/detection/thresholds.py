"""
Threshold comparison primitives.

Rules use these. Keeping them separate from rules.py means
the same comparison logic is reusable and testable independently.
"""

from __future__ import annotations


def crosses(observed: float, operator: str, threshold: float) -> bool:
    """
    Evaluate `observed <op> threshold` for a supported operator.

    Supported: ">", ">=", "<", "<=", "==", "!="
    Raises ValueError for unknown operators.
    """
    if operator == ">":
        return observed > threshold
    if operator == ">=":
        return observed >= threshold
    if operator == "<":
        return observed < threshold
    if operator == "<=":
        return observed <= threshold
    if operator == "==":
        return observed == threshold
    if operator == "!=":
        return observed != threshold
    raise ValueError(f"Unsupported operator: {operator!r}")