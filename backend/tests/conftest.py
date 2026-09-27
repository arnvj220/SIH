"""Isolated in-memory MongoDB state for API tests."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# MUST run before any `app.*` import.
_BACKEND = Path(__file__).resolve().parents[1]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

os.environ["MONGODB_DATABASE"] = "qds_security_test"

import mongomock
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _isolated_mongodb():
    """Use a fresh in-memory MongoDB instance for each test."""
    from app.db import database as database_module

    database_module.client = mongomock.MongoClient()
    database_module.initialize_database()
    yield
    database_module.client.close()


@pytest.fixture()
def client():
    """TestClient bound to the app."""
    from app.main import app
    with TestClient(app) as c:
        yield c