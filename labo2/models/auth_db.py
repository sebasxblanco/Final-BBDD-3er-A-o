"""
Authentication model: SQLite database for users and password hashes.

- Independent from PostgreSQL; used only for login.
- Passwords are stored hashed (Werkzeug); never plain text.
- Code in English.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

from werkzeug.security import check_password_hash, generate_password_hash

from config import get_sqlite_db_path


@contextmanager
def get_sqlite_connection():
    """Yield a connection to the auth SQLite database."""
    path = get_sqlite_db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def get_user_by_username(username: str) -> sqlite3.Row | None:
    """Return the user row for the given username, or None if not found."""
    with get_sqlite_connection() as conn:
        cur = conn.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?;",
            (username.strip(),),
        )
        return cur.fetchone()


def verify_password(username: str, password: str) -> bool:
    """Check that the given password matches the stored hash for the username."""
    row = get_user_by_username(username)
    if not row:
        return False
    return check_password_hash(row["password_hash"], password)


def hash_password(password: str) -> str:
    """Return a secure hash of the password (for storage)."""
    return generate_password_hash(password, method="pbkdf2:sha256")
