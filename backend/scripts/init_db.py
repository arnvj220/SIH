"""Create MongoDB indexes used by the API."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.db.database import get_database, initialize_database


def main() -> None:
    database = get_database()
    initialize_database(database)
    print(f"MongoDB database: {settings.MONGODB_DATABASE}")
    print("Collections:")
    for name in sorted(database.list_collection_names()):
        print(f"  - {name}")
    print("Indexes initialized.")


if __name__ == "__main__":
    main()