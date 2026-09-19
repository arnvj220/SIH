from __future__ import annotations

from typing import Any

from ..attacks.registry import create_attack, describe_attacks
from ..attacks.contracts import (
    AttackedSample,
    VerificationContext,
)


class AttackService:
    """Application service for attack simulation."""

    def list_attacks(self) -> list[dict[str, Any]]:
        return describe_attacks()

    def execute(
        self,
        attack_name: str,
        target: VerificationContext,
        *,
        seed: int = 0,
        parameters: dict[str, Any] | None = None,
    ) -> list[AttackedSample]:
        attack = create_attack(
            name=attack_name,
            seed=seed,
            parameters=parameters,
        )

        return attack.execute(target)