from flask import Blueprint, flash, redirect, render_template, request, url_for

from models.db_postgres import execute, query
from utils import build_where, pagination_args

profesores_bp = Blueprint("profesores", __name__, url_prefix="/profesores")


@profesores_bp.route("/")
def list_profesores():
    q           = request.args.get("q", "").strip()
    fecha_desde = request.args.get("fecha_desde", "")
    fecha_hasta = request.args.get("fecha_hasta", "")
    dpto        = request.args.get("dpto", "").strip()
    page, per_page, offset = pagination_args()

    clauses, params = [], []
    if q:
        clauses.append("(p.nombre ILIKE %s OR p.apellido ILIKE %s OR p.email ILIKE %s)")
        params += [f"%{q}%", f"%{q}%", f"%{q}%"]
    if dpto:
        clauses.append("p.departamento ILIKE %s")
        params.append(f"%{dpto}%")
    if fecha_desde:
        clauses.append("p.fecha_contratacion >= %s"); params.append(fecha_desde)
    if fecha_hasta:
        clauses.append("p.fecha_contratacion <= %s"); params.append(fecha_hasta)

    where = build_where(clauses)
    total = query(f"SELECT COUNT(*) AS cnt FROM profesores p {where}", tuple(params), one=True)["cnt"]
    total_pages = max(1, (total + per_page - 1) // per_page)

    rows = query(
        f"""SELECT p.id, p.nombre, p.apellido, p.email, p.departamento,
                   p.fecha_contratacion, COUNT(a.id) AS num_asignaturas
              FROM profesores p LEFT JOIN asignaturas a ON a.profesor_id = p.id
              {where}
          GROUP BY p.id ORDER BY p.apellido, p.nombre
             LIMIT %s OFFSET %s""",
        tuple(params) + (per_page, offset),
    )
    dptos = query("SELECT DISTINCT departamento FROM profesores ORDER BY departamento")
    return render_template(
        "profesores/list.html",
        profesores=rows, page=page, total_pages=total_pages, total=total,
        q=q, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta, dpto=dpto, dptos=dptos,
    )


@profesores_bp.route("/<int:prof_id>")
def detail_profesor(prof_id: int):
    profesor    = query("SELECT * FROM profesores WHERE id = %s", (prof_id,), one=True)
    asignaturas = query("SELECT * FROM asignaturas WHERE profesor_id = %s ORDER BY nombre", (prof_id,))
    return render_template("profesores/detail.html", profesor=profesor, asignaturas=asignaturas)


@profesores_bp.route("/nuevo", methods=["GET", "POST"])
def crear_profesor():
    if request.method == "POST":
        execute(
            "INSERT INTO profesores (nombre, apellido, email, departamento, fecha_contratacion)"
            " VALUES (%s, %s, %s, %s, %s)",
            (request.form["nombre"], request.form["apellido"], request.form["email"],
             request.form["departamento"], request.form["fecha_contratacion"] or None),
        )
        flash("Profesor creado correctamente.", "success")
        return redirect(url_for("profesores.list_profesores"))
    return render_template("profesores/form.html", profesor=None)


@profesores_bp.route("/<int:prof_id>/editar", methods=["GET", "POST"])
def editar_profesor(prof_id: int):
    profesor = query("SELECT * FROM profesores WHERE id = %s", (prof_id,), one=True)
    if request.method == "POST":
        execute(
            "UPDATE profesores SET nombre=%s, apellido=%s, email=%s, departamento=%s,"
            " fecha_contratacion=%s WHERE id=%s",
            (request.form["nombre"], request.form["apellido"], request.form["email"],
             request.form["departamento"], request.form["fecha_contratacion"] or None, prof_id),
        )
        flash("Profesor actualizado.", "success")
        return redirect(url_for("profesores.detail_profesor", prof_id=prof_id))
    return render_template("profesores/form.html", profesor=profesor)


@profesores_bp.route("/<int:prof_id>/borrar", methods=["POST"])
def borrar_profesor(prof_id: int):
    execute("DELETE FROM profesores WHERE id = %s", (prof_id,))
    flash("Profesor eliminado.", "warning")
    return redirect(url_for("profesores.list_profesores"))
