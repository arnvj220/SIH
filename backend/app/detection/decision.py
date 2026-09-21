"""
Decision combination helpers.

Maps a set of triggered rules to a final accept/reject/suspicious
decision. Kept separate from services so it's unit-testable.
"""

from __future__ import annotations

from app.attacks.contracts import Decision


def combine_decisions(any_triggered: bool) -> Decision:
    """Map rule outcomes to a final decision."""
    return Decision.REJECT if any_triggered else Decision.ACCEPT