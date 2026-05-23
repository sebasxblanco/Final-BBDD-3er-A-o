"""
Objetos de dominio: tipos claros para la capa de presentación.

La vista y el controlador trabajan con Part y Vendor, no con tuplas.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Vendor:
    """Proveedor (vendor)."""
    id: int
    name: str


@dataclass(frozen=True)
class Part:
    """Pieza (part)."""
    id: int
    name: str
