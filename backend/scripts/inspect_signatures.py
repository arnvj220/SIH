"""Print an example document shape from the signatures collection."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.database import get_database


def main() -> None:
    database = get_database()
    document = database["signatures"].find_one({}, {"_id": 0})
    print("signatures document fields:")
    if document is None:
        print("  Collection is empty.")
        return
    for key, value in sorted(document.items()):
        print(f"  {key:<24} {type(value).__name__}")


if __name__ == "__main__":
    main()