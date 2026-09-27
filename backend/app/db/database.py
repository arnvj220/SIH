"""MongoDB client and collection index configuration."""
from __future__ import annotations

from pymongo import MongoClient
from pymongo.database import Database

from ..core.config import settings


client = MongoClient(
    settings.MONGODB_URI,
    connectTimeoutMS=5_000,
    serverSelectionTimeoutMS=5_000,
)


def get_database() -> Database:
    return client[settings.MONGODB_DATABASE]


def initialize_database(database: Database | None = None) -> None:
    db = database if database is not None else get_database()
    db["alerts"].create_index("alert_id", unique=True)
    db["alerts"].create_index("created_at")
    db["attacks"].create_index("attack_id", unique=True)
    db["events"].create_index("event_id", unique=True)
    db["events"].create_index("created_at")
    db["experiment_runs"].create_index("experiment_id", unique=True)
    db["experiment_runs"].create_index([("created_at", -1)])
    db["signatures"].create_index("signature_id", unique=True)
    db["signatures"].create_index([("created_at", -1)])
    db["verifications"].create_index("verification_id", unique=True)
    db["verifications"].create_index([("created_at", -1)])