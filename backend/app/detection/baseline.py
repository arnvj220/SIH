"""
Expected statistical behaviour of a legitimate verification event.

The baseline is what makes "deviation" meaningful. Values here are
placeholders until confirmed against the quantum engine's ideal
output for the selected QDS protocol.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BaselineProfile:
    """Expected statistics for legitimate verification events."""

    expected_error_rate: float = 0.0
    expected_p0_by_basis: dict[str, float] = field(
        default_factory=lambda: {"X": 0.5, "Y": 0.5, "Z": 0.5}
    )

    def expected_p0(self, basis: str) -> float:
        return self.expected_p0_by_basis.get(basis.upper(), 0.5)


DEFAULT_BASELINE = BaselineProfile()