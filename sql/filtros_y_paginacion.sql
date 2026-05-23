-- filtros de búsqueda y paginación con limit / offset
-- base de datos: academico_db


-- filtros sobre strings con ilike

-- alumnos cuyo nombre o apellido contenga "mar"
SELECT id, nombre, apellido, email, numero_expediente
FROM alumnos
WHERE nombre  ILIKE '%mar%'
   OR apellido ILIKE '%mar%'
ORDER BY apellido, nombre;

-- profesores del departamento de informática
SELECT id, nombre, apellido, departamento, fecha_contratacion
FROM profesores
WHERE departamento ILIKE '%informática%'
ORDER BY apellido;

-- asignaturas cuyo código empiece por inf
SELECT id, codigo, nombre, creditos, precio
FROM asignaturas
WHERE codigo ILIKE 'INF%'
ORDER BY codigo;


-- filtros sobre fechas

-- matrículas del primer semestre de 2024
SELECT m.id, a.nombre || ' ' || a.apellido AS alumno,
       asig.nombre AS asignatura, m.fecha_matricula
FROM matriculas m
JOIN alumnos     a    ON a.id    = m.alumno_id
JOIN asignaturas asig ON asig.id = m.asignatura_id
WHERE m.fecha_matricula BETWEEN '2024-01-01' AND '2024-06-30'
ORDER BY m.fecha_matricula;

-- profesores contratados en los últimos 5 años
SELECT id, nombre, apellido, departamento, fecha_contratacion
FROM profesores
WHERE fecha_contratacion >= CURRENT_DATE - INTERVAL '5 years'
ORDER BY fecha_contratacion DESC;

-- alumnos nacidos entre 1995 y 2000
SELECT id, nombre, apellido, fecha_nacimiento
FROM alumnos
WHERE fecha_nacimiento BETWEEN '1995-01-01' AND '2000-12-31'
ORDER BY fecha_nacimiento;


-- filtros sobre enteros y float

-- asignaturas de 6 créditos con precio mayor de 200 €
SELECT id, codigo, nombre, creditos, precio, limite_alumnos
FROM asignaturas
WHERE creditos = 6
  AND precio > 200.00
ORDER BY precio DESC;

-- alumnos con saldo entre 500 € y 1500 €
SELECT id, nombre, apellido, saldo
FROM alumnos
WHERE saldo BETWEEN 500.00 AND 1500.00
ORDER BY saldo DESC;

-- matrículas aprobadas
SELECT m.id, a.nombre || ' ' || a.apellido AS alumno,
       asig.nombre AS asignatura, m.calificacion
FROM matriculas m
JOIN alumnos     a    ON a.id    = m.alumno_id
JOIN asignaturas asig ON asig.id = m.asignatura_id
WHERE m.calificacion >= 5.00
ORDER BY m.calificacion DESC;

-- matrículas suspensas
SELECT m.id, a.nombre || ' ' || a.apellido AS alumno,
       asig.nombre AS asignatura, m.calificacion
FROM matriculas m
JOIN alumnos     a    ON a.id    = m.alumno_id
JOIN asignaturas asig ON asig.id = m.asignatura_id
WHERE m.calificacion < 5.00
ORDER BY m.calificacion;


-- paginación con limit y offset

-- página 1
SELECT id, nombre, apellido, email, saldo
FROM alumnos
ORDER BY apellido, nombre
LIMIT 20 OFFSET 0;

-- página 2
SELECT id, nombre, apellido, email, saldo
FROM alumnos
ORDER BY apellido, nombre
LIMIT 20 OFFSET 20;

-- página 3
SELECT id, nombre, apellido, email, saldo
FROM alumnos
ORDER BY apellido, nombre
LIMIT 20 OFFSET 40;

-- fórmula general: offset = (página - 1) * registros_por_página
SELECT id, nombre, apellido, email, saldo
FROM alumnos
ORDER BY apellido, nombre
LIMIT 10 OFFSET 40;


-- filtros combinados con paginación

-- matrículas aprobadas del segundo semestre 2024, página 1
SELECT m.id, a.nombre || ' ' || a.apellido AS alumno,
       asig.nombre AS asignatura,
       m.calificacion, m.fecha_matricula
FROM matriculas m
JOIN alumnos     a    ON a.id    = m.alumno_id
JOIN asignaturas asig ON asig.id = m.asignatura_id
WHERE m.fecha_matricula BETWEEN '2024-07-01' AND '2024-12-31'
  AND m.calificacion >= 5.00
ORDER BY m.calificacion DESC
LIMIT 20 OFFSET 0;


-- explain analyze para verificar uso de índices

EXPLAIN ANALYZE
SELECT id, nombre, apellido
FROM alumnos
WHERE apellido ILIKE 'garcia%'
ORDER BY apellido;

EXPLAIN ANALYZE
SELECT id, alumno_id, fecha_matricula
FROM matriculas
WHERE fecha_matricula BETWEEN '2024-01-01' AND '2024-06-30';
