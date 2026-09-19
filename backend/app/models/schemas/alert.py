"""
API schemas for security alerts.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AlertCreate(BaseModel):
    """Create a security alert."""

    alert_id: str = Field(
        min_length=1,
        max_length=128,
    )

    alert_type: str = Field(
        min_length=1,
        max_length=64,
    )

    severity: str = Field(
        min_length=1,
        max_length=32,
    )

    title: str = Field(
        min_length=1,
        max_length=256,
    )

    description: str | None = Field(
        default=None,
        max_length=2048,
    )

    verification_id: str | None = None

    attack_id: str | None = None

    evidence: list[dict] = Field(
        default_factory=list,
    )


class AlertResponse(AlertCreate):
    """API representation of a security alert."""

    status: str

    created_at: datetime | None = None

    resolved_at: datetime | None = None