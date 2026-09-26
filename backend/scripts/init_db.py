"""
Create all database tables.

Run once after cloning the repo, or any time you add a new model:

    cd backend
    python scripts/init_db.py

Safe to re-run — create_all only creates missing tables.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.database import Base, engine, create_tables


def main() -> None:
    print("Creating tables on:", engine.url)
    create_tables()
    tables = sorted(Base.metadata.tables.keys())
    print(f"Registered tables ({len(tables)}):")
    for t in tables:
        print(f"  - {t}")
    print("Done.")


if __name__ == "__main__":
    main()