"""
API schemas for attack simulation.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from ...attacks.contracts import ThreatType


class AttackRequest(BaseModel):
    """Request to execute an attack scenario."""

    attack_id: str = Field(
        min_length=1,
        max_length=128,
    )

    attack_type: str = Field(
        min_length=1,
        max_length=64,
    )

    seed: int = 0

    parameters: dict = Field(
        default_factory=dict,
    )


class AttackSampleResponse(BaseModel):
    """Summary of an attack-generated verification sample."""

    context_id: str

    is_attack: bool

    expected_threat: ThreatType

    role: str

    evidence: dict = Field(
        default_factory=dict,
    )


class AttackResponse(BaseModel):
    """Result of an attack simulation."""

    attack_id: str

    attack_type: ThreatType

    scenario_name: str

    seed: int

    parameters: dict

    samples: list[AttackSampleResponse]

    evidence: dict = Field(
        default_factory=dict,
    )


class AttackDescription(BaseModel):
    """Metadata describing an available attack."""

    name: str

    threat_type: ThreatType

    description: str

    modes: list[str] = Field(
        default_factory=list,
    )

    default_parameters: dict = Field(
        default_factory=dict,
    )