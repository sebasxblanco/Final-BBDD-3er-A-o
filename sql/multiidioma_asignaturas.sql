-- multiidioma en asignaturas con columna jsonb
-- ejecutar en: academico_db


-- añadir columna jsonb para nombres traducidos
ALTER TABLE asignaturas
    ADD COLUMN IF NOT EXISTS nombre_i18n JSONB DEFAULT '{}'::jsonb;


-- poblar traducciones en español e inglés para las 20 asignaturas
UPDATE asignaturas SET nombre_i18n = '{"es": "Programación I",          "en": "Programming I"}'::jsonb          WHERE codigo = 'INF101';
UPDATE asignaturas SET nombre_i18n = '{"es": "Programación II",         "en": "Programming II"}'::jsonb         WHERE codigo = 'INF102';
UPDATE asignaturas SET nombre_i18n = '{"es": "Bases de Datos",          "en": "Database Systems"}'::jsonb       WHERE codigo = 'INF201';
UPDATE asignaturas SET nombre_i18n = '{"es": "Redes de Computadores",   "en": "Computer Networks"}'::jsonb      WHERE codigo = 'INF301';
UPDATE asignaturas SET nombre_i18n = '{"es": "Inteligencia Artificial", "en": "Artificial Intelligence"}'::jsonb WHERE codigo = 'INF401';
UPDATE asignaturas SET nombre_i18n = '{"es": "Álgebra Lineal",          "en": "Linear Algebra"}'::jsonb         WHERE codigo = 'MAT101';
UPDATE asignaturas SET nombre_i18n = '{"es": "Cálculo I",               "en": "Calculus I"}'::jsonb             WHERE codigo = 'MAT102';
UPDATE asignaturas SET nombre_i18n = '{"es": "Estadística Aplicada",    "en": "Applied Statistics"}'::jsonb     WHERE codigo = 'MAT201';
UPDATE asignaturas SET nombre_i18n = '{"es": "Física I",                "en": "Physics I"}'::jsonb              WHERE codigo = 'FIS101';
UPDATE asignaturas SET nombre_i18n = '{"es": "Química General",         "en": "General Chemistry"}'::jsonb      WHERE codigo = 'QUI101';
UPDATE asignaturas SET nombre_i18n = '{"es": "Historia Contemporánea",  "en": "Contemporary History"}'::jsonb   WHERE codigo = 'HIS101';
UPDATE asignaturas SET nombre_i18n = '{"es": "Historia del Arte",       "en": "Art History"}'::jsonb            WHERE codigo = 'HIS201';
UPDATE asignaturas SET nombre_i18n = '{"es": "Lengua y Literatura",     "en": "Language and Literature"}'::jsonb WHERE codigo = 'LEN101';
UPDATE asignaturas SET nombre_i18n = '{"es": "Microeconomía",           "en": "Microeconomics"}'::jsonb         WHERE codigo = 'ECO101';
UPDATE asignaturas SET nombre_i18n = '{"es": "Macroeconomía",           "en": "Macroeconomics"}'::jsonb         WHERE codigo = 'ECO102';
UPDATE asignaturas SET nombre_i18n = '{"es": "Economía Digital",        "en": "Digital Economy"}'::jsonb        WHERE codigo = 'ECO201';
UPDATE asignaturas SET nombre_i18n = '{"es": "Psicología General",      "en": "General Psychology"}'::jsonb     WHERE codigo = 'PSI101';
UPDATE asignaturas SET nombre_i18n = '{"es": "Derecho Civil",           "en": "Civil Law"}'::jsonb              WHERE codigo = 'DER101';
UPDATE asignaturas SET nombre_i18n = '{"es": "Derecho Penal",           "en": "Criminal Law"}'::jsonb           WHERE codigo = 'DER102';
UPDATE asignaturas SET nombre_i18n = '{"es": "Biología Celular",        "en": "Cell Biology"}'::jsonb           WHERE codigo = 'BIO101';


-- índice gin para búsquedas dentro del jsonb
CREATE INDEX IF NOT EXISTS idx_asignaturas_nombre_i18n
    ON asignaturas USING GIN (nombre_i18n jsonb_path_ops);


-- ver todas las traducciones
SELECT codigo,
       nombre_i18n->>'es' AS nombre_es,
       nombre_i18n->>'en' AS nombre_en
FROM asignaturas
ORDER BY codigo;

-- obtener nombre en inglés con filtro
SELECT codigo, nombre_i18n->>'en' AS nombre_ingles, creditos
FROM asignaturas
WHERE nombre_i18n->>'en' ILIKE '%data%'
   OR nombre_i18n->>'en' ILIKE '%computer%';

-- listar todos los idiomas disponibles por asignatura
SELECT codigo, jsonb_object_keys(nombre_i18n) AS idioma
FROM asignaturas
ORDER BY codigo, idioma;
