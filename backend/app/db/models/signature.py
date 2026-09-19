"""
Database model for QDS signatures.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class SignatureModel(Base):
    __tablename__ = "signatures"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    signature_id: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        index=True,
    )

    signer_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )

    message_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )

    message_digest: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    protocol_version: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    session_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )

    # Serialized QuantumEvidence.
    quantum_evidence: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    metadata_json: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )