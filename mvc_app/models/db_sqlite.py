from __future__ import annotations

import sqlite3
from contextlib import contextmanager

from config import Config


@contextmanager
def get_sqlite_conn():
    conn = sqlite3.connect(Config.SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def query_sqlite(sql: str, params: tuple = (), *, one: bool = False):
    with get_sqlite_conn() as conn:
        cur = conn.execute(sql, params)
        return cur.fetchone() if one else cur.fetchall()
