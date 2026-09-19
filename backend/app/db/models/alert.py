"""
Security alert persistence model.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class AlertModel(Base):
    __tablename__ = "security_alerts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    alert_id: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        index=True,
    )

    alert_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    severity: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="OPEN",
    )

    verification_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True,
    )

    attack_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
    )

    evidence: Mapped[list] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )