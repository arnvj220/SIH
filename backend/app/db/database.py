"""
SQLAlchemy database configuration.
"""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

from ..core.config import settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)


def create_tables() -> None:
    """
    Create all database tables.

    Intended mainly for local development and smoke tests.
    Production schema changes should be handled through Alembic.
    """
    # Import models so SQLAlchemy knows about them before create_all.
    from .models import (  # noqa: F401
        AlertModel,
        AttackModel,
        EventModel,
        SignatureModel,
        VerificationModel,
    )

    Base.metadata.create_all(bind=engine)