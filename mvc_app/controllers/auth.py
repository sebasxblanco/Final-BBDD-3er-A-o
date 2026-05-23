from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user = User.authenticate(username, password)
        if user:
            session["user_id"]   = user.id
            session["username"]  = user.username
            session["role"]      = user.role
            session["nombre"]    = user.nombre
            return redirect(url_for("main.index"))
        flash("Usuario o contraseña incorrectos.", "danger")
    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
