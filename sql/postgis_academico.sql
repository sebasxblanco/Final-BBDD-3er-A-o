-- postgis sobre academico_db
-- requiere imagen postgis/postgis:15-3.4 en docker-compose


-- instalar la extensión
CREATE EXTENSION IF NOT EXISTS postgis;


-- añadir columna de punto a alumnos
ALTER TABLE alumnos
    ADD COLUMN IF NOT EXISTS geom GEOMETRY(Point, 4326);

-- añadir columna de polígono a asignaturas
ALTER TABLE asignaturas
    ADD COLUMN IF NOT EXISTS geom GEOMETRY(Polygon, 4326);


-- posiciones de 4 alumnos en el campus ucjc (lon, lat en wgs84)
UPDATE alumnos SET geom = ST_SetSRID(ST_MakePoint(-4.0060, 40.4515), 4326)
WHERE id = (SELECT id FROM alumnos ORDER BY id LIMIT 1 OFFSET 0);

UPDATE alumnos SET geom = ST_SetSRID(ST_MakePoint(-4.0030, 40.4525), 4326)
WHERE id = (SELECT id FROM alumnos ORDER BY id LIMIT 1 OFFSET 1);

UPDATE alumnos SET geom = ST_SetSRID(ST_MakePoint(-4.0055, 40.4495), 4326)
WHERE id = (SELECT id FROM alumnos ORDER BY id LIMIT 1 OFFSET 2);

UPDATE alumnos SET geom = ST_SetSRID(ST_MakePoint(-4.0043, 40.4508), 4326)
WHERE id = (SELECT id FROM alumnos ORDER BY id LIMIT 1 OFFSET 3);


-- polígonos de aulas en el campus (edificios de ~50 x 40 m)
UPDATE asignaturas
    SET geom = ST_GeomFromText('POLYGON((-4.0053 40.4510, -4.0047 40.4510, -4.0047 40.4514, -4.0053 40.4514, -4.0053 40.4510))', 4326)
WHERE codigo = 'INF201';

UPDATE asignaturas
    SET geom = ST_GeomFromText('POLYGON((-4.0038 40.4516, -4.0032 40.4516, -4.0032 40.4520, -4.0038 40.4520, -4.0038 40.4516))', 4326)
WHERE codigo = 'MAT101';

UPDATE asignaturas
    SET geom = ST_GeomFromText('POLYGON((-4.0068 40.4503, -4.0062 40.4503, -4.0062 40.4507, -4.0068 40.4507, -4.0068 40.4503))', 4326)
WHERE codigo = 'FIS101';

UPDATE asignaturas
    SET geom = ST_GeomFromText('POLYGON((-4.0045 40.4498, -4.0039 40.4498, -4.0039 40.4502, -4.0045 40.4502, -4.0045 40.4498))', 4326)
WHERE codigo = 'HIS101';


-- índices gist para consultas espaciales
CREATE INDEX IF NOT EXISTS idx_alumnos_geom
    ON alumnos USING GIST (geom);

CREATE INDEX IF NOT EXISTS idx_asignaturas_geom
    ON asignaturas USING GIST (geom);


-- función viajar: calcula ruta y distancia de un alumno a un aula
CREATE OR REPLACE FUNCTION viajar(p_alumno_id INTEGER, p_asignatura_id INTEGER)
RETURNS TABLE(
    alumno_nombre       TEXT,
    asignatura_nombre   TEXT,
    asignatura_codigo   VARCHAR,
    distancia_metros    NUMERIC,
    ya_llego            BOOLEAN,
    alumno_geojson      TEXT,
    aula_geojson        TEXT,
    ruta_geojson        TEXT
) LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        al.nombre || ' ' || al.apellido                                                    AS alumno_nombre,
        asig.nombre                                                                         AS asignatura_nombre,
        asig.codigo                                                                         AS asignatura_codigo,
        ROUND(ST_Distance(al.geom::geography, ST_Centroid(asig.geom)::geography)::NUMERIC, 1) AS distancia_metros,
        ST_Contains(asig.geom, al.geom)                                                    AS ya_llego,
        ST_AsGeoJSON(al.geom)                                                              AS alumno_geojson,
        ST_AsGeoJSON(asig.geom)                                                            AS aula_geojson,
        ST_AsGeoJSON(ST_MakeLine(al.geom, ST_Centroid(asig.geom)))                        AS ruta_geojson
    FROM alumnos al
    JOIN asignaturas asig ON asig.id = p_asignatura_id
    WHERE al.id = p_alumno_id
      AND al.geom IS NOT NULL
      AND asig.geom IS NOT NULL;
END;
$$;


-- verificación: ver alumnos con posición
SELECT id, nombre, apellido, ST_AsText(geom) AS posicion_wkt
FROM alumnos
WHERE geom IS NOT NULL
ORDER BY id;

-- verificación: ver aulas con polígono
SELECT codigo, nombre, ST_AsText(geom) AS poligono_wkt
FROM asignaturas
WHERE geom IS NOT NULL
ORDER BY codigo;

-- ejemplo de uso de la función viajar
-- SELECT * FROM viajar(1, (SELECT id FROM asignaturas WHERE codigo = 'INF201'));

-- distancias entre todos los alumnos geolocalizados y todas las aulas
SELECT
    al.nombre || ' ' || al.apellido         AS alumno,
    asig.codigo                              AS aula,
    ROUND(ST_Distance(
        al.geom::geography,
        ST_Centroid(asig.geom)::geography
    )::NUMERIC, 1)                           AS distancia_metros,
    ST_Contains(asig.geom, al.geom)         AS dentro_del_aula
FROM alumnos al
CROSS JOIN asignaturas asig
WHERE al.geom IS NOT NULL
  AND asig.geom IS NOT NULL
ORDER BY al.nombre, distancia_metros;
