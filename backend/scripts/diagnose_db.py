"""Check the configured MongoDB database, collections, and document counts."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.db.database import get_database, initialize_database


def main() -> None:
    print("MongoDB diagnostics")
    print(f"Database name: {settings.MONGODB_DATABASE}")
    database = get_database()
    initialize_database(database)

    collections = sorted(database.list_collection_names())
    print(f"Collections ({len(collections)}):")
    for name in collections:
        print(f"  {name:<24} {database[name].count_documents({})} documents")


if __name__ == "__main__":
    main()