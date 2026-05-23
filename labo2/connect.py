from __future__ import annotations

import psycopg
from psycopg import OperationalError

from config import load_config


def connect() -> None:
    """Connect to the PostgreSQL server and print a short confirmation."""
    cfg = load_config()
    try:
        with psycopg.connect(**cfg) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                ver = cur.fetchone()[0]
            print("Connected to the PostgreSQL server.")
            print(ver)
    except OperationalError as exc:
        print("Connection failed:", exc)


if __name__ == "__main__":
    connect()
