from flask import Blueprint, flash, redirect, render_template, request, url_for

from models.db_postgres import execute, query
from utils import build_where, pagination_args

asignaturas_bp = Blueprint("asignaturas", __name__, url_prefix="/asignaturas")


@asignaturas_bp.route("/")
def list_asignaturas():
    q          = request.args.get("q", "").strip()
    creditos   = request.args.get("creditos", "")
    precio_max = request.args.get("precio_max", "")
    page, per_page, offset = pagination_args()

    clauses, params = [], []
    if q:
        clauses.append("(asig.nombre ILIKE %s OR asig.codigo ILIKE %s)")
        params += [f"%{q}%", f"%{q}%"]
    if creditos:
        clauses.append("asig.creditos = %s"); params.append(int(creditos))
    if precio_max:
        clauses.append("asig.precio <= %s"); params.append(float(precio_max))

    where = build_where(clauses)
    total = query(f"SELECT COUNT(*) AS cnt FROM asignaturas asig {where}", tuple(params), one=True)["cnt"]
    total_pages = max(1, (total + per_page - 1) // per_page)

    rows = query(
        f"""SELECT asig.id, asig.nombre, asig.codigo, asig.creditos,
                   asig.precio, asig.limite_alumnos,
                   p.nombre || ' ' || p.apellido AS profesor,
                   COUNT(m.id) AS num_alumnos
              FROM asignaturas asig
         LEFT JOIN profesores p ON p.id = asig.profesor_id
         LEFT JOIN matriculas m ON m.asignatura_id = asig.id
              {where}
          GROUP BY asig.id, p.nombre, p.apellido
          ORDER BY asig.nombre
             LIMIT %s OFFSET %s""",
        tuple(params) + (per_page, offset),
    )
    return render_template(
        "asignaturas/list.html",
        asignaturas=rows, page=page, total_pages=total_pages, total=total,
        q=q, creditos=creditos, precio_max=precio_max,
    )


@asignaturas_bp.route("/<int:asig_id>")
def detail_asignatura(asig_id: int):
    asignatura = query("""
        SELECT asig.*, p.nombre || ' ' || p.apellido AS profesor_nombre,
               (SELECT COUNT(*) FROM matriculas WHERE asignatura_id = asig.id) AS inscritos
          FROM asignaturas asig LEFT JOIN profesores p ON p.id = asig.profesor_id
         WHERE asig.id = %s
    """, (asig_id,), one=True)
    alumnos = query("""
        SELECT a.nombre, a.apellido, a.numero_expediente, m.calificacion, m.fecha_matricula
          FROM matriculas m JOIN alumnos a ON a.id = m.alumno_id
         WHERE m.asignatura_id = %s ORDER BY a.apellido, a.nombre
    """, (asig_id,))
    return render_template("asignaturas/detail.html", asignatura=asignatura, alumnos=alumnos)


@asignaturas_bp.route("/nueva", methods=["GET", "POST"])
def crear_asignatura():
    profesores = query("SELECT id, nombre || ' ' || apellido AS nombre FROM profesores ORDER BY apellido")
    if request.method == "POST":
        execute(
            "INSERT INTO asignaturas (nombre, codigo, creditos, profesor_id, precio, limite_alumnos)"
            " VALUES (%s, %s, %s, %s, %s, %s)",
            (request.form["nombre"], request.form["codigo"], int(request.form["creditos"]),
             request.form["profesor_id"] or None,
             float(request.form.get("precio", 150)),
             int(request.form.get("limite_alumnos", 30))),
        )
        flash("Asignatura creada correctamente.", "success")
        return redirect(url_for("asignaturas.list_asignaturas"))
    return render_template("asignaturas/form.html", asignatura=None, profesores=profesores)


@asignaturas_bp.route("/<int:asig_id>/editar", methods=["GET", "POST"])
def editar_asignatura(asig_id: int):
    asignatura = query("SELECT * FROM asignaturas WHERE id = %s", (asig_id,), one=True)
    profesores = query("SELECT id, nombre || ' ' || apellido AS nombre FROM profesores ORDER BY apellido")
    if request.method == "POST":
        execute(
            "UPDATE asignaturas SET nombre=%s, codigo=%s, creditos=%s, profesor_id=%s,"
            " precio=%s, limite_alumnos=%s WHERE id=%s",
            (request.form["nombre"], request.form["codigo"], int(request.form["creditos"]),
             request.form["profesor_id"] or None,
             float(request.form.get("precio", 150)),
             int(request.form.get("limite_alumnos", 30)), asig_id),
        )
        flash("Asignatura actualizada.", "success")
        return redirect(url_for("asignaturas.detail_asignatura", asig_id=asig_id))
    return render_template("asignaturas/form.html", asignatura=asignatura, profesores=profesores)


@asignaturas_bp.route("/<int:asig_id>/borrar", methods=["POST"])
def borrar_asignatura(asig_id: int):
    execute("DELETE FROM asignaturas WHERE id = %s", (asig_id,))
    flash("Asignatura eliminada.", "warning")
    return redirect(url_for("asignaturas.list_asignaturas"))
