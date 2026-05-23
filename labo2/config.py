from __future__ import annotations

from configparser import ConfigParser
from pathlib import Path

# SQLite DB for auth: separate from PostgreSQL, lives in instance/
_SQLITE_DIR = Path(__file__).resolve().parent / "instance"


def get_sqlite_db_path() -> Path:
    """Path to the SQLite database used for authentication (users/passwords)."""
    _SQLITE_DIR.mkdir(parents=True, exist_ok=True)
    return _SQLITE_DIR / "auth.db"


def load_config(filename: str = "database.ini", section: str = "postgresql") -> dict[str, str]:
    """Load DB connection parameters from an INI file.

    Expected keys in [postgresql]:
      host, port, dbname, user, password
    """
    parser = ConfigParser()
    parser.read(filename)

    if not parser.has_section(section):
        raise RuntimeError(f"Section [{section}] not found in {filename}")

    return {k: v for k, v in parser.items(section)}
