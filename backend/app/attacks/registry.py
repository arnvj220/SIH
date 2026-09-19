from __future__ import annotations

from typing import Any

from .base import AttackScenario
from .channel_manipulation import ChannelManipulationAttack
from .forgery import ForgeryAttack
from .impersonation import ImpersonationAttack
from .replay import ReplayAttack
from .unauthorized import UnauthorizedVerificationAttack


class UnknownAttackError(KeyError):
    """Requested attack type is not registered."""


ATTACK_REGISTRY: dict[str, type[AttackScenario]] = {
    cls.name: cls
    for cls in (
        ForgeryAttack,
        ImpersonationAttack,
        ReplayAttack,
        UnauthorizedVerificationAttack,
        ChannelManipulationAttack,
    )
}


def create_attack(
    name: str, seed: int = 0, parameters: dict[str, Any] | None = None
) -> AttackScenario:
    try:
        cls = ATTACK_REGISTRY[name]
    except KeyError:
        raise UnknownAttackError(
            f"Unknown attack '{name}'. Available: {sorted(ATTACK_REGISTRY)}"
        ) from None
    return cls(seed=seed, parameters=parameters)


def describe_attacks() -> list[dict[str, Any]]:
    """Metadata for the Attack Lab UI (scenario selection, FR-035/FR-036)."""
    return [
        {
            "name": cls.name,
            "threat_type": cls.attack_type.value,
            "description": cls.description,
            "modes": list(getattr(cls, "MODES", ())),
            "default_parameters": {
                k: list(v) if isinstance(v, tuple) else v for k, v in cls.defaults.items()
            },
        }
        for cls in ATTACK_REGISTRY.values()
    ]
