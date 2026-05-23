"""Rutas principales: índice y navegación."""
from __future__ import annotations

from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Página de inicio con enlaces a listados."""
    return render_template("index.html")
