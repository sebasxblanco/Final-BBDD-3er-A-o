-- unaccent: elimina tildes y diacríticos en búsquedas
CREATE EXTENSION IF NOT EXISTS unaccent;

-- ejemplo: "garcia" encuentra "garcía"
SELECT id, nombre, apellido
FROM profesores
WHERE unaccent(lower(apellido)) = unaccent(lower('Garcia'));

-- búsqueda insensible a tildes en asignaturas
SELECT id, codigo, nombre
FROM asignaturas
WHERE unaccent(lower(nombre)) ILIKE unaccent(lower('%matematicas%'));


-- citext: comparaciones de texto insensibles a mayúsculas
CREATE EXTENSION IF NOT EXISTS citext;

-- ejemplo con email de alumnos
SELECT id, nombre, apellido, email
FROM alumnos
WHERE email::citext = 'alumno001@ucjc.edu';


-- fuzzystrmatch: distancia de edición con levenshtein
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;

-- distancia entre dos códigos de asignatura
SELECT levenshtein('INF101', 'INF102') AS distancia;

-- asignaturas cuyo código esté a distancia ≤ 2 del buscado
SELECT id, codigo, nombre
FROM asignaturas
WHERE levenshtein(codigo, 'INF201') <= 2
ORDER BY levenshtein(codigo, 'INF201');

-- alumnos con apellido parecido, tolerancia a errores tipográficos
SELECT id, nombre, apellido
FROM alumnos
WHERE levenshtein_less_equal(lower(apellido), lower('Garcia'), 2) <= 2
ORDER BY levenshtein(lower(apellido), lower('Garcia'));


-- pg_trgm: similitud por trigramas
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- índice gin de trigramas sobre nombre de asignatura
CREATE INDEX IF NOT EXISTS idx_asignaturas_nombre_trgm
    ON asignaturas USING GIN (nombre gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_alumnos_apellido_trgm
    ON alumnos USING GIN (apellido gin_trgm_ops);

-- búsqueda por similitud aunque el usuario escriba mal
SELECT id, codigo, nombre,
       similarity(nombre, 'Programacion') AS sim
FROM asignaturas
WHERE nombre % 'Programacion'
ORDER BY sim DESC;

-- ver trigramas de una palabra
SELECT show_trgm('bases de datos');


-- btree_gin: permite indexar escalares en índices gin
CREATE EXTENSION IF NOT EXISTS btree_gin;

-- índice gin compuesto sobre créditos y nombre
CREATE INDEX IF NOT EXISTS idx_asignaturas_gin_creditos_nombre
    ON asignaturas USING GIN (creditos, nombre gin_trgm_ops);

-- consulta que usa el índice compuesto
SELECT id, codigo, nombre, creditos
FROM asignaturas
WHERE creditos = 6
  AND nombre % 'datos';


-- verificar extensiones instaladas
SELECT name, default_version, installed_version
FROM pg_available_extensions
WHERE name IN ('unaccent','citext','fuzzystrmatch','pg_trgm','btree_gin')
ORDER BY name;
