"""FastAPI dependency providing the shared MongoDB database handle."""
from __future__ import annotations

from collections.abc import Generator

from pymongo.database import Database

from .database import get_database


def get_db() -> Generator[Database, None, None]:
    yield get_database()