from flask import Blueprint, render_template, request

from models.db_postgres import query
from utils import build_where, pagination_args

vista_bp = Blueprint("vista", __name__, url_prefix="/vista-academica")


@vista_bp.route("/")
def list_vista():
    q           = request.args.get("q", "").strip()
    fecha_desde = request.args.get("fecha_desde", "")
    fecha_hasta = request.args.get("fecha_hasta", "")
    cal_min     = request.args.get("cal_min", "")
    cal_max     = request.args.get("cal_max", "")
    page, per_page, offset = pagination_args()

    clauses, params = [], []
    if q:
        clauses.append("(nombre_alumno ILIKE %s OR nombre_profesor ILIKE %s OR nombre_asignatura ILIKE %s)")
        params += [f"%{q}%"] * 3
    if fecha_desde:
        clauses.append("fecha_matricula >= %s"); params.append(fecha_desde)
    if fecha_hasta:
        clauses.append("fecha_matricula <= %s"); params.append(fecha_hasta)
    if cal_min:
        clauses.append("calificacion >= %s"); params.append(float(cal_min))
    if cal_max:
        clauses.append("calificacion <= %s"); params.append(float(cal_max))

    where = build_where(clauses)
    total = query(
        f"SELECT COUNT(*) AS cnt FROM vista_alumno_profesor_asignatura {where}",
        tuple(params), one=True,
    )["cnt"]
    total_pages = max(1, (total + per_page - 1) // per_page)

    rows = query(
        f"""SELECT nombre_alumno, numero_expediente, nombre_profesor,
                   departamento, nombre_asignatura, codigo, creditos,
                   calificacion, fecha_matricula
              FROM vista_alumno_profesor_asignatura
              {where}
             LIMIT %s OFFSET %s""",
        tuple(params) + (per_page, offset),
    )
    return render_template(
        "vista/list.html",
        rows=rows, page=page, total_pages=total_pages, total=total,
        q=q, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta,
        cal_min=cal_min, cal_max=cal_max,
    )
