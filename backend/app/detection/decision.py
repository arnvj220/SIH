"""
Decision combination helpers.

Maps a set of triggered rules to a final accept/reject/suspicious
decision. Kept separate from services so it's unit-testable.
"""

from __future__ import annotations

from typing import Iterable


def combine_decisions(any_triggered: bool, any_accept: bool = True) -> str:
    """
    Given the outcome of rule evaluation, produce a decision string.

    - No rules triggered         → "ACCEPT"
    - Any rule triggered         → "REJECT"
    """
    if any_triggered:
        return "REJECT"
    return "ACCEPT" if any_accept else "SUSPICIOUS"