"""
Database model for attack simulations.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class AttackModel(Base):
    __tablename__ = "attacks"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    attack_id: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        index=True,
    )

    attack_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    scenario_name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    seed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    parameters: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )

    target_context_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True,
    )

    generated_samples: Mapped[list] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )

    evidence: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )