-- vista que muestra la relación completa entre alumnos, profesores y asignaturas


CREATE OR REPLACE VIEW vista_alumno_profesor_asignatura AS
SELECT
    a.id                               AS alumno_id,
    a.nombre  || ' ' || a.apellido     AS nombre_alumno,
    a.numero_expediente,
    p.id                               AS profesor_id,
    p.nombre  || ' ' || p.apellido     AS nombre_profesor,
    p.departamento,
    asig.id                            AS asignatura_id,
    asig.nombre                        AS nombre_asignatura,
    asig.codigo,
    asig.creditos,
    m.calificacion,
    m.fecha_matricula
FROM matriculas m
JOIN alumnos     a    ON a.id    = m.alumno_id
JOIN asignaturas asig ON asig.id = m.asignatura_id
LEFT JOIN profesores  p    ON p.id    = asig.profesor_id
ORDER BY a.apellido, p.apellido, asig.nombre;


-- verificación: consultar la vista
SELECT
    nombre_alumno,
    nombre_profesor,
    nombre_asignatura
FROM vista_alumno_profesor_asignatura
LIMIT 10;
