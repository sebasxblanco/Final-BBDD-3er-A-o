"""Rutas del recurso parts (listado y dibujo binario)."""
from __future__ import annotations

from flask import Blueprint, Response, abort, render_template

from models.db import get_drawing, get_part_ids_with_drawing, get_parts

# MIME types seguros para imágenes servidas por la app
DRAWING_MIMETYPES = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
}
DEFAULT_MIMETYPE = "application/octet-stream"

parts_bp = Blueprint("parts", __name__, url_prefix="/parts")


@parts_bp.route("")
def list_():
    """Lista de parts. Incluye indicador de cuáles tienen dibujo."""
    parts = get_parts()
    parts_with_drawing = get_part_ids_with_drawing()
    return render_template(
        "parts.html",
        parts=parts,
        parts_with_drawing=parts_with_drawing,
    )


@parts_bp.route("/<int:part_id>/drawing")
def drawing(part_id: int):
    """Sirve el dibujo (imagen) de una parte. 404 si no existe."""
    drawing_data = get_drawing(part_id)
    if not drawing_data:
        abort(404)
    ext, data = drawing_data
    mimetype = DRAWING_MIMETYPES.get(ext.lower(), DEFAULT_MIMETYPE)
    return Response(data, mimetype=mimetype)
