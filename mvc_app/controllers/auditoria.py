from flask import Blueprint, render_template, request

from models.db_postgres import query
from utils import build_where, pagination_args

auditoria_bp = Blueprint("auditoria", __name__, url_prefix="/auditoria")

_TABLAS_VALIDAS = {"profesores", "alumnos", "asignaturas"}


@auditoria_bp.route("/<tabla>")
def list_auditoria(tabla: str):
    if tabla not in _TABLAS_VALIDAS:
        return "Tabla no válida", 404

    operacion   = request.args.get("operacion", "")
    fecha_desde = request.args.get("fecha_desde", "")
    fecha_hasta = request.args.get("fecha_hasta", "")
    page, per_page, offset = pagination_args()

    clauses, params = [], []
    if operacion:
        clauses.append("operacion = %s"); params.append(operacion)
    if fecha_desde:
        clauses.append("fecha_hora >= %s"); params.append(fecha_desde)
    if fecha_hasta:
        clauses.append("fecha_hora < (%s::date + interval '1 day')"); params.append(fecha_hasta)

    where = build_where(clauses)
    total = query(
        f"SELECT COUNT(*) AS cnt FROM auditoria_{tabla} {where}", tuple(params), one=True
    )["cnt"]
    total_pages = max(1, (total + per_page - 1) // per_page)

    rows = query(
        f"""SELECT id, operacion, registro_id, datos_anteriores, datos_nuevos, fecha_hora
              FROM auditoria_{tabla} {where}
             ORDER BY fecha_hora DESC LIMIT %s OFFSET %s""",
        tuple(params) + (per_page, offset),
    )
    return render_template(
        "auditoria/list.html",
        rows=rows, tabla=tabla, page=page, total_pages=total_pages, total=total,
        operacion=operacion, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta,
    )
