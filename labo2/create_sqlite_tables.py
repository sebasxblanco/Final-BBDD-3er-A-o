"""
Create the SQLite auth database and users table.

Run once before using the app:
    python create_sqlite_tables.py

Does not touch PostgreSQL.
"""
from __future__ import annotations

import sqlite3

from config import get_sqlite_db_path

DDL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);
"""


def create_tables() -> None:
    """Create the users table in the auth SQLite DB (idempotent)."""
    path = get_sqlite_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.execute(DDL)
    print("SQLite auth table 'users' created (or already existed).")


if __name__ == "__main__":
    create_tables()
