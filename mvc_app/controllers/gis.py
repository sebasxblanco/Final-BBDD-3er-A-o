from flask import Blueprint, render_template, request, flash
import psycopg2
from models.db_postgres import query

gis_bp = Blueprint("gis", __name__, url_prefix="/gis")

_EMPTY = []


def _safe_query(sql, params=()):
    # devuelvo lista vacía si PostGIS aún no está instalado
    try:
        return query(sql, params)
    except psycopg2.Error:
        return _EMPTY


@gis_bp.route("/")
def viajar():
    alumno_id = request.args.get("alumno_id", type=int)
    asignatura_id = request.args.get("asignatura_id", type=int)

    alumnos_con_geo = _safe_query(
        "SELECT id, nombre || ' ' || apellido AS nombre "
        "FROM alumnos WHERE geom IS NOT NULL ORDER BY nombre"
    )
    asignaturas_con_geo = _safe_query(
        "SELECT id, nombre, codigo FROM asignaturas WHERE geom IS NOT NULL ORDER BY nombre"
    )
    alumnos_geo = _safe_query(
        "SELECT nombre || ' ' || apellido AS nombre, ST_AsGeoJSON(geom) AS geojson "
        "FROM alumnos WHERE geom IS NOT NULL"
    )
    aulas_geo = _safe_query(
        "SELECT nombre, codigo, ST_AsGeoJSON(geom) AS geojson "
        "FROM asignaturas WHERE geom IS NOT NULL"
    )

    postgis_listo = bool(alumnos_con_geo or asignaturas_con_geo)

    resultado = None
    if alumno_id and asignatura_id:
        rows = _safe_query("SELECT * FROM viajar(%s, %s)", (alumno_id, asignatura_id))
        resultado = rows[0] if rows else None

    return render_template(
        "gis/viajar.html",
        alumnos_con_geo=alumnos_con_geo,
        asignaturas_con_geo=asignaturas_con_geo,
        alumnos_geo=alumnos_geo,
        aulas_geo=aulas_geo,
        resultado=resultado,
        alumno_id=alumno_id,
        asignatura_id=asignatura_id,
        postgis_listo=postgis_listo,
    )
