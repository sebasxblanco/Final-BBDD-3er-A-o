from __future__ import annotations

import psycopg

from config import load_config


DDL = (
    """CREATE TABLE IF NOT EXISTS vendors (
    vendor_id SERIAL PRIMARY KEY,
    vendor_name VARCHAR(255) NOT NULL
);""",
    """CREATE TABLE IF NOT EXISTS parts (
    part_id SERIAL PRIMARY KEY,
    part_name VARCHAR(255) NOT NULL
);""",
    """CREATE TABLE IF NOT EXISTS part_drawings (
    part_id INTEGER PRIMARY KEY,
    file_extension VARCHAR(5) NOT NULL,
    drawing_data BYTEA NOT NULL,
    FOREIGN KEY (part_id)
        REFERENCES parts (part_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);""",
    """CREATE TABLE IF NOT EXISTS vendor_parts (
    vendor_id INTEGER NOT NULL,
    part_id INTEGER NOT NULL,
    PRIMARY KEY (vendor_id, part_id),
    FOREIGN KEY (vendor_id)
        REFERENCES vendors (vendor_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (part_id)
        REFERENCES parts (part_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);""",
)


def create_tables() -> None:
    """Create demo tables for the lab (idempotent)."""
    cfg = load_config()
    with psycopg.connect(**cfg) as conn:
        with conn.cursor() as cur:
            for stmt in DDL:
                cur.execute(stmt)
    print("Tables created (or already existed).")


if __name__ == "__main__":
    create_tables()
