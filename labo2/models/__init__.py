# Capa Model del MVC: acceso a datos (PostgreSQL) y entidades de dominio.

from models.db import (
    get_connection,
    get_drawing,
    get_part_ids_with_drawing,
    get_parts,
    get_vendors,
)
from models.entities import Part, Vendor

__all__ = [
    "Part",
    "Vendor",
    "get_connection",
    "get_drawing",
    "get_part_ids_with_drawing",
    "get_parts",
    "get_vendors",
]
