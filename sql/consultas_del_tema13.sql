-- consultas avanzadas adaptadas a academico_db
-- ejecutar en: academico_db


-- filter: calificación total por trimestre y alumno
SELECT a.nombre || ' ' || a.apellido                                              AS alumno,
       SUM(m.calificacion) FILTER (WHERE EXTRACT(quarter FROM m.fecha_matricula) = 1) AS t1,
       SUM(m.calificacion) FILTER (WHERE EXTRACT(quarter FROM m.fecha_matricula) = 2) AS t2,
       SUM(m.calificacion) FILTER (WHERE EXTRACT(quarter FROM m.fecha_matricula) = 3) AS t3,
       SUM(m.calificacion) FILTER (WHERE EXTRACT(quarter FROM m.fecha_matricula) = 4) AS t4
FROM matriculas m
JOIN alumnos a ON a.id = m.alumno_id
WHERE m.calificacion IS NOT NULL
GROUP BY a.id, a.nombre, a.apellido
ORDER BY alumno;


-- rollup: detalle por mes y alumno con subtotales y total global
SELECT TO_CHAR(DATE_TRUNC('month', m.fecha_matricula), 'YYYY-MM') AS mes,
       a.nombre || ' ' || a.apellido                               AS alumno,
       ROUND(SUM(m.calificacion)::NUMERIC, 2)                      AS total,
       GROUPING(DATE_TRUNC('month', m.fecha_matricula))            AS g_mes,
       GROUPING(a.nombre || ' ' || a.apellido)                    AS g_alumno
FROM matriculas m
JOIN alumnos a ON a.id = m.alumno_id
WHERE m.calificacion IS NOT NULL
GROUP BY ROLLUP (DATE_TRUNC('month', m.fecha_matricula), a.nombre || ' ' || a.apellido)
ORDER BY mes NULLS LAST, alumno NULLS LAST;


-- grouping sets: detalle por mes y asignatura, subtotal por mes, total global
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
ORDER BY mes NULLS LAST, asignatura NULLS LAST;


-- row_number: top 3 asignaturas por media de calificación en cada mes
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
ORDER BY mes, puesto;
