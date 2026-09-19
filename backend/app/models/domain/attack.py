"""
Domain models for attack simulation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AttackType(str, Enum):
    FORGERY = "FORGERY"
    REPLAY = "REPLAY"
    IMPERSONATION = "IMPERSONATION"
    CHANNEL_MANIPULATION = "CHANNEL_MANIPULATION"


@dataclass(frozen=True)
class AttackRequest:
    """Request to execute an attack scenario."""

    attack_type: AttackType
    parameters: dict[str, Any] = field(default_factory=dict)
    seed: int = 0


@dataclass(frozen=True)
class AttackResult:
    """Application-level representation of an attack execution."""

    attack_id: str
    attack_type: AttackType
    is_attack: bool

    expected_threat: str

    role: str = "attack"

    evidence: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)