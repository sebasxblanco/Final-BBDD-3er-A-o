"""
Insert a demo user into the SQLite auth database.

Run after create_sqlite_tables.py so you can log in:
    python insert_demo_user.py

Default: username 'demo', password 'demo'. Override with env or args if needed.
"""
from __future__ import annotations

import os
import sqlite3
import sys

from config import get_sqlite_db_path
from models.auth_db import get_sqlite_connection, hash_password

DEFAULT_USERNAME = os.environ.get("AUTH_DEMO_USER", "demo")
DEFAULT_PASSWORD = os.environ.get("AUTH_DEMO_PASS", "demo")


def main() -> None:
    username = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_USERNAME
    password = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_PASSWORD
    password_hash = hash_password(password)

    path = get_sqlite_db_path()
    if not path.exists():
        print("Run create_sqlite_tables.py first.")
        sys.exit(1)

    with get_sqlite_connection() as conn:
        try:
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?);",
                (username, password_hash),
            )
            print(f"Demo user created: username={username!r}. You can log in with that.")
        except sqlite3.IntegrityError:
            print(f"User {username!r} already exists. Use another username or delete the row in {path}.")
            sys.exit(1)


if __name__ == "__main__":
    main()
