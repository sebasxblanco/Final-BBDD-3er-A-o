"""Rutas del recurso vendors."""
from __future__ import annotations

from flask import Blueprint, render_template

from models.db import get_vendors

vendors_bp = Blueprint("vendors", __name__, url_prefix="/vendors")


@vendors_bp.route("")
def list_():
    """Lista de vendors. Datos desde el Model, presentación en la View."""
    vendors = get_vendors()
    return render_template("vendors.html", vendors=vendors)
