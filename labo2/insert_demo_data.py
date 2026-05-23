"""
Script para insertar datos de ejemplo en vendors, parts, vendor_parts y part_drawings.

Ejecutar una vez después de create_tables.py para poder ver datos en la app:
    python insert_demo_data.py
"""
from __future__ import annotations

import psycopg

from config import load_config

# PNG 1x1 píxel (rojo), mínimo válido para mostrar un dibujo de ejemplo
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
    cfg = load_config()
    with psycopg.connect(**cfg) as conn:
        with conn.cursor() as cur:
            # Vendors
            cur.execute(
                "INSERT INTO vendors(vendor_name) VALUES (%s) RETURNING vendor_id;",
                ("ACME Corporation",),
            )
            v1 = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO vendors(vendor_name) VALUES (%s) RETURNING vendor_id;",
                ("TechSupply S.L.",),
            )
            v2 = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO vendors(vendor_name) VALUES (%s) RETURNING vendor_id;",
                ("Componentes Norte",),
            )
            v3 = cur.fetchone()[0]

            # Parts
            cur.execute(
                "INSERT INTO parts(part_name) VALUES (%s) RETURNING part_id;",
                ("Altavoz",),
            )
            p1 = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO parts(part_name) VALUES (%s) RETURNING part_id;",
                ("Amplificador",),
            )
            p2 = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO parts(part_name) VALUES (%s) RETURNING part_id;",
                ("Cable HDMI",),
            )
            p3 = cur.fetchone()[0]

            # Relación vendor_parts (qué vendor suministra qué parte)
            cur.executemany(
                "INSERT INTO vendor_parts(vendor_id, part_id) VALUES (%s, %s);",
                [(v1, p1), (v1, p2), (v2, p2), (v2, p3), (v3, p1), (v3, p3)],
            )

            # Dibujo de ejemplo para la primera parte (se muestra en /parts)
            cur.execute(
                """INSERT INTO part_drawings(part_id, file_extension, drawing_data)
                   VALUES (%s, %s, %s)
                   ON CONFLICT (part_id) DO UPDATE
                   SET file_extension = EXCLUDED.file_extension,
                       drawing_data = EXCLUDED.drawing_data;""",
                (p1, "png", DEMO_PNG_BYTES),
            )

    print("Datos de ejemplo insertados:")
    print("  Vendors: ACME Corporation, TechSupply S.L., Componentes Norte")
    print("  Parts: Altavoz, Amplificador, Cable HDMI")
    print("  Relaciones vendor_parts creadas.")
    print("  Un dibujo de ejemplo (PNG) para la primera part. Ejecuta la app y visita /vendors y /parts.")


if __name__ == "__main__":
    main()
