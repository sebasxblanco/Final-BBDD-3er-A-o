from flask import Blueprint, flash, redirect, render_template, request, url_for

from models.db_postgres import cancelar_matricula_transaccion, matricular_transaccion, query
from utils import build_where, pagination_args

matriculas_bp = Blueprint("matriculas", __name__, url_prefix="/matriculas")


@matriculas_bp.route("/")
def list_matriculas():
    q           = request.args.get("q", "").strip()
    fecha_desde = request.args.get("fecha_desde", "")
    fecha_hasta = request.args.get("fecha_hasta", "")
    cal_min     = request.args.get("cal_min", "")
    cal_max     = request.args.get("cal_max", "")
    page, per_page, offset = pagination_args()

    clauses, params = [], []
    if q:
        clauses.append("(a.nombre ILIKE %s OR a.apellido ILIKE %s OR asig.nombre ILIKE %s OR asig.codigo ILIKE %s)")
        params += [f"%{q}%"] * 4
    if fecha_desde:
        clauses.append("m.fecha_matricula >= %s"); params.append(fecha_desde)
    if fecha_hasta:
        clauses.append("m.fecha_matricula <= %s"); params.append(fecha_hasta)
    if cal_min:
        clauses.append("m.calificacion >= %s"); params.append(float(cal_min))
    if cal_max:
        clauses.append("m.calificacion <= %s"); params.append(float(cal_max))

    where = build_where(clauses)
    total = query(
        f"""SELECT COUNT(*) AS cnt FROM matriculas m
             JOIN alumnos a ON a.id = m.alumno_id
             JOIN asignaturas asig ON asig.id = m.asignatura_id {where}""",
        tuple(params), one=True,
    )["cnt"]
    total_pages = max(1, (total + per_page - 1) // per_page)

    rows = query(
        f"""SELECT m.id, m.fecha_matricula, m.calificacion,
                   a.nombre || ' ' || a.apellido AS alumno, a.numero_expediente,
                   asig.nombre AS asignatura, asig.codigo, asig.precio
              FROM matriculas m
              JOIN alumnos a ON a.id = m.alumno_id
              JOIN asignaturas asig ON asig.id = m.asignatura_id
              {where}
             ORDER BY m.fecha_matricula DESC
             LIMIT %s OFFSET %s""",
        tuple(params) + (per_page, offset),
    )
    return render_template(
        "matriculas/list.html",
        matriculas=rows, page=page, total_pages=total_pages, total=total,
        q=q, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta,
        cal_min=cal_min, cal_max=cal_max,
    )


@matriculas_bp.route("/<int:mat_id>")
def detail_matricula(mat_id: int):
    matricula = query("""
        SELECT m.id, m.fecha_matricula, m.calificacion,
               a.id AS alumno_id, a.nombre || ' ' || a.apellido AS alumno,
               a.numero_expediente, a.email AS alumno_email, a.saldo,
               asig.id AS asignatura_id, asig.nombre AS asignatura,
               asig.codigo, asig.creditos, asig.precio,
               p.nombre || ' ' || p.apellido AS profesor
          FROM matriculas m
          JOIN alumnos a ON a.id = m.alumno_id
          JOIN asignaturas asig ON asig.id = m.asignatura_id
     LEFT JOIN profesores p ON p.id = asig.profesor_id
         WHERE m.id = %s
    """, (mat_id,), one=True)
    return render_template("matriculas/detail.html", matricula=matricula)


@matriculas_bp.route("/nueva", methods=["GET", "POST"])
def nueva_matricula():
    alumnos     = query("SELECT id, nombre || ' ' || apellido AS nombre, saldo FROM alumnos ORDER BY apellido")
    asignaturas = query("""
        SELECT asig.id, asig.nombre, asig.codigo, asig.precio, asig.limite_alumnos,
               (SELECT COUNT(*) FROM matriculas WHERE asignatura_id = asig.id) AS inscritos
          FROM asignaturas asig ORDER BY asig.nombre
    """)

    if request.method == "POST":
        alumno_id    = int(request.form["alumno_id"])
        asignatura_id = int(request.form["asignatura_id"])
        ok, msg = matricular_transaccion(alumno_id, asignatura_id)
        flash(msg, "success" if ok else "danger")
        if ok:
            return redirect(url_for("matriculas.list_matriculas"))

    return render_template("matriculas/form.html", alumnos=alumnos, asignaturas=asignaturas)


@matriculas_bp.route("/<int:mat_id>/cancelar", methods=["POST"])
def cancelar_matricula(mat_id: int):
    ok, msg = cancelar_matricula_transaccion(mat_id)
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("matriculas.list_matriculas"))
