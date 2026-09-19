"""
Database model for verification attempts.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class VerificationModel(Base):
    __tablename__ = "verifications"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    verification_id: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        index=True,
    )

    signature_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )

    signer_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )

    verifier_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )

    message_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )

    decision: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
    )

    error_rate: Mapped[float] = mapped_column(
        nullable=False,
        default=0.0,
    )

    threats: Mapped[list] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
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