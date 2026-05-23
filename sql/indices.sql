-- índices para optimización de consultas
-- base de datos: academico_db


-- tabla alumnos
CREATE INDEX IF NOT EXISTS idx_alumnos_apellido
    ON alumnos(apellido);                        -- filtros sobre apellido

CREATE INDEX IF NOT EXISTS idx_alumnos_email
    ON alumnos(email);                           -- filtros sobre email

CREATE INDEX IF NOT EXISTS idx_alumnos_expediente
    ON alumnos(numero_expediente);               -- filtros sobre expediente

CREATE INDEX IF NOT EXISTS idx_alumnos_saldo
    ON alumnos(saldo);                           -- filtros sobre saldo

-- tabla profesores
CREATE INDEX IF NOT EXISTS idx_profesores_apellido
    ON profesores(apellido);                     -- filtros sobre apellido

CREATE INDEX IF NOT EXISTS idx_profesores_dpto
    ON profesores(departamento);                 -- filtros sobre departamento

CREATE INDEX IF NOT EXISTS idx_profesores_fecha
    ON profesores(fecha_contratacion);           -- filtros sobre fecha de contratación

-- tabla asignaturas
CREATE INDEX IF NOT EXISTS idx_asignaturas_nombre
    ON asignaturas(nombre);                      -- filtros sobre nombre

CREATE INDEX IF NOT EXISTS idx_asignaturas_codigo
    ON asignaturas(codigo);                      -- filtros sobre código

CREATE INDEX IF NOT EXISTS idx_asignaturas_creditos
    ON asignaturas(creditos);                    -- filtros sobre créditos

CREATE INDEX IF NOT EXISTS idx_asignaturas_precio
    ON asignaturas(precio);                      -- filtros sobre precio

-- tabla matriculas
CREATE INDEX IF NOT EXISTS idx_matriculas_fecha
    ON matriculas(fecha_matricula);              -- filtros sobre fecha de matrícula

CREATE INDEX IF NOT EXISTS idx_matriculas_calificacion
    ON matriculas(calificacion);                 -- filtros sobre calificación

-- verificación: ver todos los índices creados
SELECT
    indexname   AS nombre_indice,
    tablename   AS tabla,
    indexdef    AS definicion
FROM pg_indexes
WHERE schemaname = 'public'
  AND indexname LIKE 'idx_%'
ORDER BY tablename, indexname;
