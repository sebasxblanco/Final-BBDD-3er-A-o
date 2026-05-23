"""
Inserta un dibujo de ejemplo (PNG 1x1) para una part existente.

Uso:
    python insert_demo_drawing.py           # part_id = 1
    python insert_demo_drawing.py 2         # part_id = 2
"""
from __future__ import annotations

import sys

import psycopg

from config import load_config

DEMO_PNG_BYTES = bytes(
    [
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, 0x00, 0x00, 0x00, 0x0D,
        0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
        0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53, 0xDE, 0x00, 0x00, 0x00,
        0x0C, 0x49, 0x44, 0x41, 0x54, 0x08, 0xD7, 0x63, 0xF8, 0xFF, 0xFF, 0x3F,
        0x00, 0x05, 0xFE, 0x02, 0xFE, 0xDC, 0xCC, 0x59, 0xE7, 0x00, 0x00, 0x00,
        0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82,
    ]
)


def main() -> None:
    part_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    cfg = load_config()
    with psycopg.connect(**cfg) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO part_drawings(part_id, file_extension, drawing_data)
                   VALUES (%s, %s, %s)
                   ON CONFLICT (part_id) DO UPDATE
                   SET file_extension = EXCLUDED.file_extension,
                       drawing_data = EXCLUDED.drawing_data;""",
                (part_id, "png", DEMO_PNG_BYTES),
            )
    print(f"Dibujo de ejemplo insertado para part_id={part_id}. Recarga /parts.")


if __name__ == "__main__":
    main()
