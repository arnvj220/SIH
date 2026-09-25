"""Session-wide test fixtures: isolated test DB + clean state between tests."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# MUST run before any `app.*` import.
_BACKEND = Path(__file__).resolve().parents[1]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

# Force test DB. Assignment, not setdefault — overrides anything .env loaded.
os.environ["DATABASE_URL"] = (
    "postgresql+psycopg://postgres:postgres@localhost:5432/qds_security_test"
)

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def _create_test_schema():
    """Drop and recreate all tables once per test session."""
    from app.db.database import Base, engine
    from app.db import models  # noqa: F401 — register all models on Base.metadata

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(autouse=True)
def _clean_tables(_create_test_schema):
    """Truncate every table before each test."""
    from app.db.database import Base, engine

    table_names = [t.name for t in Base.metadata.sorted_tables]
    with engine.begin() as conn:
        for name in reversed(table_names):
            conn.exec_driver_sql(
                f'TRUNCATE TABLE "{name}" RESTART IDENTITY CASCADE'
            )
    yield


@pytest.fixture()
def client():
    """TestClient bound to the app."""
    from app.main import app
    with TestClient(app) as c:
        yield c