"""
Model (capa de acceso a datos).

- Centraliza la conexión a PostgreSQL usando config.load_config().
- Expone funciones de solo lectura (SELECT); devuelve objetos de dominio.
- No contiene HTML ni lógica de rutas; solo datos.

Si se cambia el motor o el esquema, solo se modifica este módulo.
"""
from __future__ import annotations

import psycopg

from config import load_config

from models.entities import Part, Vendor


def get_connection():
    """
    Devuelve una conexión a PostgreSQL.

    Usa database.ini vía load_config(). La conexión debe usarse con
    context manager (with ... as conn) para cerrar correctamente.
    """
    cfg = load_config()
    return psycopg.connect(**cfg)


def get_vendors() -> list[Vendor]:
    """Lista todos los vendors. Devuelve objetos Vendor."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT vendor_id, vendor_name FROM vendors ORDER BY vendor_id;"
            )
            return [Vendor(id=r[0], name=r[1]) for r in cur.fetchall()]


def get_parts() -> list[Part]:
    """Lista todas las partes. Devuelve objetos Part."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT part_id, part_name FROM parts ORDER BY part_id;"
            )
            return [Part(id=r[0], name=r[1]) for r in cur.fetchall()]


def get_drawing(part_id: int) -> tuple[str, bytes] | None:
    """
    Devuelve el dibujo de una parte si existe.

    Returns:
        (file_extension, drawing_data) o None si no hay dibujo.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT file_extension, drawing_data FROM part_drawings WHERE part_id = %s;",
                (part_id,),
            )
            row = cur.fetchone()
    return (row[0], bytes(row[1])) if row else None


def get_part_ids_with_drawing() -> set[int]:
    """Ids de partes que tienen dibujo asociado (para mostrar imagen en la lista)."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT part_id FROM part_drawings;")
            return {r[0] for r in cur.fetchall()}
