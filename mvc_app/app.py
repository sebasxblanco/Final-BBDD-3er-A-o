"""Punto de entrada — Application Factory."""
from __future__ import annotations

from flask import Flask, redirect, request, session, url_for

from config import Config
from controllers.auth        import auth_bp
from controllers.main        import main_bp
from controllers.profesores  import profesores_bp
from controllers.alumnos     import alumnos_bp
from controllers.asignaturas import asignaturas_bp
from controllers.matriculas  import matriculas_bp
from controllers.auditoria   import auditoria_bp
from controllers.vista       import vista_bp
from controllers.estadisticas import estadisticas_bp
from controllers.gis import gis_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Config.SECRET_KEY

    for bp in (auth_bp, main_bp, profesores_bp, alumnos_bp,
               asignaturas_bp, matriculas_bp, auditoria_bp, vista_bp, estadisticas_bp, gis_bp):
        app.register_blueprint(bp)

    @app.before_request
    def require_login():
        public = {"auth.login", "auth.logout", "static"}
        if request.endpoint in public or (request.endpoint or "").startswith("auth."):
            return None
        if "username" not in session:
            return redirect(url_for("auth.login"))
        return None

    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template("errors/404.html"), 404

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
