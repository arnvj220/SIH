from __future__ import annotations

from typing import Any

from .base import AttackScenario
from .forgery import ForgeryAttack


class UnknownAttackError(KeyError):
    """Requested attack type is not registered."""


ATTACK_REGISTRY: dict[str, type[AttackScenario]] = {
    ForgeryAttack.name: ForgeryAttack,
}


def create_attack(
    name: str,
    seed: int = 0,
    parameters: dict[str, Any] | None = None,
) -> AttackScenario:
    try:
        cls = ATTACK_REGISTRY[name]
    except KeyError:
        raise UnknownAttackError(
            f"Unknown attack '{name}'. Available: {sorted(ATTACK_REGISTRY)}"
        ) from None

    return cls(seed=seed, parameters=parameters)


def describe_attacks() -> list[dict[str, Any]]:
    return [
        {
            "name": cls.name,
            "threat_type": cls.attack_type.value,
            "description": cls.description,
            "modes": list(getattr(cls, "MODES", ())),
            "default_parameters": {
                k: list(v) if isinstance(v, tuple) else v
                for k, v in cls.defaults.items()
            },
        }
        for cls in ATTACK_REGISTRY.values()
    ]