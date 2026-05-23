from flask import Blueprint, render_template
from models.db_postgres import query

estadisticas_bp = Blueprint("estadisticas", __name__, url_prefix="/estadisticas")


@estadisticas_bp.route("/")
def list_estadisticas():
    filter_rows = query("""
        SELECT a.nombre || ' ' || a.apellido AS alumno,
               ROUND(SUM(m.calificacion) FILTER (WHERE EXTRACT(quarter FROM m.fecha_matricula) = 1)::NUMERIC, 2) AS t1,
               ROUND(SUM(m.calificacion) FILTER (WHERE EXTRACT(quarter FROM m.fecha_matricula) = 2)::NUMERIC, 2) AS t2,
               ROUND(SUM(m.calificacion) FILTER (WHERE EXTRACT(quarter FROM m.fecha_matricula) = 3)::NUMERIC, 2) AS t3,
               ROUND(SUM(m.calificacion) FILTER (WHERE EXTRACT(quarter FROM m.fecha_matricula) = 4)::NUMERIC, 2) AS t4
        FROM matriculas m
        JOIN alumnos a ON a.id = m.alumno_id
        WHERE m.calificacion IS NOT NULL
        GROUP BY a.id, a.nombre, a.apellido
        ORDER BY alumno
        LIMIT 20
    """)

    rollup_rows = query("""
        SELECT TO_CHAR(DATE_TRUNC('month', m.fecha_matricula), 'YYYY-MM') AS mes,
               a.nombre || ' ' || a.apellido                               AS alumno,
               ROUND(SUM(m.calificacion)::NUMERIC, 2)                      AS total,
               GROUPING(DATE_TRUNC('month', m.fecha_matricula))            AS g_mes,
               GROUPING(a.nombre || ' ' || a.apellido)                    AS g_alumno
        FROM matriculas m
        JOIN alumnos a ON a.id = m.alumno_id
        WHERE m.calificacion IS NOT NULL
        GROUP BY ROLLUP (DATE_TRUNC('month', m.fecha_matricula), a.nombre || ' ' || a.apellido)
        ORDER BY mes NULLS LAST, alumno NULLS LAST
        LIMIT 50
    """)

    gsets_rows = query("""
        SELECT TO_CHAR(DATE_TRUNC('month', m.fecha_matricula), 'YYYY-MM') AS mes,
               asig.nombre                                                  AS asignatura,
               ROUND(SUM(m.calificacion)::NUMERIC, 2)                      AS total,
               GROUPING(DATE_TRUNC('month', m.fecha_matricula))            AS g_mes,
               GROUPING(asig.nombre)                                       AS g_asig
        FROM matriculas m
        JOIN asignaturas asig ON asig.id = m.asignatura_id
        WHERE m.calificacion IS NOT NULL
        GROUP BY GROUPING SETS (
            (DATE_TRUNC('month', m.fecha_matricula), asig.nombre),
            (DATE_TRUNC('month', m.fecha_matricula)),
            ()
        )
        ORDER BY mes NULLS LAST, asignatura NULLS LAST
        LIMIT 50
    """)

    rn_rows = query("""
        WITH por_mes AS (
            SELECT DATE_TRUNC('month', m.fecha_matricula) AS mes,
                   asig.nombre                             AS asignatura,
                   ROUND(AVG(m.calificacion)::NUMERIC, 2)  AS media
            FROM matriculas m
            JOIN asignaturas asig ON asig.id = m.asignatura_id
            WHERE m.calificacion IS NOT NULL
            GROUP BY 1, 2
        )
        SELECT TO_CHAR(mes, 'YYYY-MM') AS mes, asignatura, media, puesto
        FROM (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY mes ORDER BY media DESC) AS puesto
            FROM por_mes
        ) ranked
        WHERE puesto <= 3
        ORDER BY mes, puesto
    """)

    return render_template("estadisticas/list.html",
                           filter_rows=filter_rows,
                           rollup_rows=rollup_rows,
                           gsets_rows=gsets_rows,
                           rn_rows=rn_rows)
