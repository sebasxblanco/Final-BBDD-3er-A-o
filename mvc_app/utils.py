"""Utilidades compartidas: paginación, construcción de filtros SQL."""
from __future__ import annotations

from flask import request


PER_PAGE = 20


def pagination_args() -> tuple[int, int, int]:
    """Devuelve (page, per_page, offset)."""
    page = max(1, int(request.args.get("page", 1)))
    per_page = PER_PAGE
    return page, per_page, (page - 1) * per_page


def build_where(clauses: list[str]) -> str:
    return ("WHERE " + " AND ".join(clauses)) if clauses else ""
