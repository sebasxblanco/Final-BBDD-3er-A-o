"""
Auth routes: login and logout against SQLite (users/passwords).

- Login is the entry point; after success, session is set and user uses PostgreSQL app.
- Code in English.
"""
from __future__ import annotations

from flask import Blueprint, redirect, render_template, request, session, url_for

from models.auth_db import verify_password

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Show login form (GET) or validate credentials and redirect (POST)."""
    if request.method == "GET":
        return render_template("auth/login.html")

    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""

    if not username or not password:
        return render_template(
            "auth/login.html",
            error="Usuario y contraseña son obligatorios.",
            username=username,
        ), 400

    if not verify_password(username, password):
        return render_template(
            "auth/login.html",
            error="Usuario o contraseña incorrectos.",
            username=username,
        ), 401

    session["username"] = username
    session.permanent = True
    return redirect(url_for("main.index"))


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Clear session and redirect to login."""
    session.clear()
    return redirect(url_for("auth.login"))
