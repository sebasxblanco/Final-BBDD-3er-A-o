from flask import Blueprint, flash, redirect, render_template, request, url_for

from models.db_postgres import execute, query
from utils import build_where, pagination_args

alumnos_bp = Blueprint("alumnos", __name__, url_prefix="/alumnos")


@alumnos_bp.route("/")
def list_alumnos():
    q           = request.args.get("q", "").strip()
    fecha_desde = request.args.get("fecha_desde", "")
    fecha_hasta = request.args.get("fecha_hasta", "")
    saldo_min   = request.args.get("saldo_min", "")
    saldo_max   = request.args.get("saldo_max", "")
    page, per_page, offset = pagination_args()

    clauses, params = [], []
    if q:
        clauses.append("(a.nombre ILIKE %s OR a.apellido ILIKE %s OR a.email ILIKE %s OR a.numero_expediente ILIKE %s)")
        params += [f"%{q}%"] * 4
    if fecha_desde:
        clauses.append("a.fecha_nacimiento >= %s"); params.append(fecha_desde)
    if fecha_hasta:
        clauses.append("a.fecha_nacimiento <= %s"); params.append(fecha_hasta)
    if saldo_min:
        clauses.append("a.saldo >= %s"); params.append(float(saldo_min))
    if saldo_max:
        clauses.append("a.saldo <= %s"); params.append(float(saldo_max))

    where = build_where(clauses)
    total = query(f"SELECT COUNT(*) AS cnt FROM alumnos a {where}", tuple(params), one=True)["cnt"]
    total_pages = max(1, (total + per_page - 1) // per_page)

    rows = query(
        f"""SELECT a.id, a.nombre, a.apellido, a.email, a.numero_expediente,
                   a.saldo, COUNT(m.id) AS num_matriculas
              FROM alumnos a LEFT JOIN matriculas m ON m.alumno_id = a.id
              {where}
          GROUP BY a.id ORDER BY a.apellido, a.nombre
             LIMIT %s OFFSET %s""",
        tuple(params) + (per_page, offset),
    )
    return render_template(
        "alumnos/list.html",
        alumnos=rows, page=page, total_pages=total_pages, total=total,
        q=q, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta,
        saldo_min=saldo_min, saldo_max=saldo_max,
    )


@alumnos_bp.route("/<int:alumno_id>")
def detail_alumno(alumno_id: int):
    alumno = query("SELECT * FROM alumnos WHERE id = %s", (alumno_id,), one=True)
    matriculas = query("""
        SELECT m.id, m.fecha_matricula, m.calificacion,
               asig.nombre AS asignatura, asig.creditos, asig.precio
          FROM matriculas m
          JOIN asignaturas asig ON asig.id = m.asignatura_id
         WHERE m.alumno_id = %s ORDER BY m.fecha_matricula DESC
    """, (alumno_id,))
    return render_template("alumnos/detail.html", alumno=alumno, matriculas=matriculas)


@alumnos_bp.route("/nuevo", methods=["GET", "POST"])
def crear_alumno():
    if request.method == "POST":
        execute(
            "INSERT INTO alumnos (nombre, apellido, email, fecha_nacimiento, numero_expediente, saldo)"
            " VALUES (%s, %s, %s, %s, %s, %s)",
            (request.form["nombre"], request.form["apellido"], request.form["email"],
             request.form["fecha_nacimiento"] or None, request.form["numero_expediente"],
             float(request.form.get("saldo", 0))),
        )
        flash("Alumno creado correctamente.", "success")
        return redirect(url_for("alumnos.list_alumnos"))
    return render_template("alumnos/form.html", alumno=None)


@alumnos_bp.route("/<int:alumno_id>/editar", methods=["GET", "POST"])
def editar_alumno(alumno_id: int):
    alumno = query("SELECT * FROM alumnos WHERE id = %s", (alumno_id,), one=True)
    if request.method == "POST":
        execute(
            "UPDATE alumnos SET nombre=%s, apellido=%s, email=%s, fecha_nacimiento=%s,"
            " numero_expediente=%s, saldo=%s WHERE id=%s",
            (request.form["nombre"], request.form["apellido"], request.form["email"],
             request.form["fecha_nacimiento"] or None, request.form["numero_expediente"],
             float(request.form.get("saldo", 0)), alumno_id),
        )
        flash("Alumno actualizado.", "success")
        return redirect(url_for("alumnos.detail_alumno", alumno_id=alumno_id))
    return render_template("alumnos/form.html", alumno=alumno)


@alumnos_bp.route("/<int:alumno_id>/borrar", methods=["POST"])
def borrar_alumno(alumno_id: int):
    execute("DELETE FROM alumnos WHERE id = %s", (alumno_id,))
    flash("Alumno eliminado.", "warning")
    return redirect(url_for("alumnos.list_alumnos"))
