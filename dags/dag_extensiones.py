from __future__ import annotations

from datetime import datetime
import psycopg2
from airflow import DAG
from airflow.operators.python import PythonOperator

_PG = dict(
    host="postgres_academico", port=5432,
    dbname="academico_db", user="academico", password="academico123",
)


def _conn():
    return psycopg2.connect(**_PG)


# instalo las extensiones y creo índices de trigramas
def instalar_extensiones(**_):
    conn = _conn()
    cur = conn.cursor()
    for ext in ('unaccent', 'citext', 'fuzzystrmatch', 'pg_trgm', 'btree_gin'):
        cur.execute(f"CREATE EXTENSION IF NOT EXISTS {ext}")
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_asignaturas_nombre_trgm
            ON asignaturas USING GIN (nombre gin_trgm_ops)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_alumnos_apellido_trgm
            ON alumnos USING GIN (apellido gin_trgm_ops)
    """)
    conn.commit(); cur.close(); conn.close()
    print("[OK] Extensiones y GIN trigram indexes instalados")


# añado columnas nuevas al esquema base
def ampliar_esquema(**_):
    conn = _conn()
    cur = conn.cursor()
    cur.execute("ALTER TABLE alumnos     ADD COLUMN IF NOT EXISTS saldo          NUMERIC(10,2) DEFAULT 1000.00")
    cur.execute("ALTER TABLE asignaturas ADD COLUMN IF NOT EXISTS precio         NUMERIC(8,2)  DEFAULT 150.00")
    cur.execute("ALTER TABLE asignaturas ADD COLUMN IF NOT EXISTS limite_alumnos INTEGER       DEFAULT 30")
    conn.commit(); cur.close(); conn.close()
    print("[OK] Columnas saldo, precio, limite_alumnos añadidas")


# actualizo los datos con valores más realistas
def actualizar_datos(**_):
    conn = _conn()
    cur = conn.cursor()
    # saldo aleatorio entre 200 y 2500 €
    cur.execute("""
        UPDATE alumnos
           SET saldo = ROUND((RANDOM() * 2300 + 200)::NUMERIC, 2)
    """)
    # precio según créditos
    cur.execute("""
        UPDATE asignaturas
           SET precio = CASE
               WHEN creditos = 3 THEN 120.00
               WHEN creditos = 4 THEN 160.00
               WHEN creditos = 6 THEN 240.00
               ELSE 150.00
           END
    """)
    # límite entre 8 y 25 alumnos
    cur.execute("""
        UPDATE asignaturas
           SET limite_alumnos = 8 + (RANDOM() * 17)::INTEGER
    """)
    conn.commit(); cur.close(); conn.close()
    print("[OK] Datos actualizados: saldo, precio, limite_alumnos")


# creo las tablas de auditoría y los triggers asociados
def crear_auditoria(**_):
    conn = _conn()
    cur = conn.cursor()

    for tabla in ('profesores', 'alumnos', 'asignaturas'):
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS auditoria_{tabla} (
                id               SERIAL PRIMARY KEY,
                operacion        VARCHAR(10) NOT NULL,
                registro_id      INTEGER,
                datos_anteriores JSONB,
                datos_nuevos     JSONB,
                fecha_hora       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    for tabla in ('profesores', 'alumnos', 'asignaturas'):
        cur.execute(f"""
            CREATE OR REPLACE FUNCTION fn_auditoria_{tabla}()
            RETURNS TRIGGER LANGUAGE plpgsql AS $$
            BEGIN
                IF TG_OP = 'INSERT' THEN
                    INSERT INTO auditoria_{tabla}(operacion, registro_id, datos_nuevos)
                    VALUES ('INSERT', NEW.id, to_jsonb(NEW));
                    RETURN NEW;
                ELSIF TG_OP = 'UPDATE' THEN
                    INSERT INTO auditoria_{tabla}(operacion, registro_id, datos_anteriores, datos_nuevos)
                    VALUES ('UPDATE', NEW.id, to_jsonb(OLD), to_jsonb(NEW));
                    RETURN NEW;
                ELSIF TG_OP = 'DELETE' THEN
                    INSERT INTO auditoria_{tabla}(operacion, registro_id, datos_anteriores)
                    VALUES ('DELETE', OLD.id, to_jsonb(OLD));
                    RETURN OLD;
                END IF;
            END;
            $$
        """)
        cur.execute(f"DROP TRIGGER IF EXISTS trg_auditoria_{tabla} ON {tabla}")
        cur.execute(f"""
            CREATE TRIGGER trg_auditoria_{tabla}
            AFTER INSERT OR UPDATE OR DELETE ON {tabla}
            FOR EACH ROW EXECUTE FUNCTION fn_auditoria_{tabla}()
        """)

    conn.commit(); cur.close(); conn.close()
    print("[OK] Tablas de auditoría y triggers creados para profesores, alumnos, asignaturas")


# vista que cruza alumnos, profesores y asignaturas
def crear_vista(**_):
    conn = _conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE OR REPLACE VIEW vista_alumno_profesor_asignatura AS
        SELECT
            a.id                                    AS alumno_id,
            a.nombre  || ' ' || a.apellido          AS nombre_alumno,
            a.numero_expediente,
            p.id                                    AS profesor_id,
            p.nombre  || ' ' || p.apellido          AS nombre_profesor,
            p.departamento,
            asig.id                                 AS asignatura_id,
            asig.nombre                             AS nombre_asignatura,
            asig.codigo,
            asig.creditos,
            m.calificacion,
            m.fecha_matricula
        FROM matriculas m
        JOIN alumnos     a    ON a.id    = m.alumno_id
        JOIN asignaturas asig ON asig.id = m.asignatura_id
        LEFT JOIN profesores  p    ON p.id    = asig.profesor_id
        ORDER BY a.apellido, p.apellido, asig.nombre
    """)
    conn.commit(); cur.close(); conn.close()
    print("[OK] Vista 'vista_alumno_profesor_asignatura' creada")


# índices B-tree sobre columnas de búsqueda frecuente
def crear_indices(**_):
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_alumnos_apellido       ON alumnos(apellido)",
        "CREATE INDEX IF NOT EXISTS idx_alumnos_email          ON alumnos(email)",
        "CREATE INDEX IF NOT EXISTS idx_alumnos_saldo          ON alumnos(saldo)",
        "CREATE INDEX IF NOT EXISTS idx_alumnos_expediente     ON alumnos(numero_expediente)",
        "CREATE INDEX IF NOT EXISTS idx_profesores_apellido    ON profesores(apellido)",
        "CREATE INDEX IF NOT EXISTS idx_profesores_dpto        ON profesores(departamento)",
        "CREATE INDEX IF NOT EXISTS idx_asignaturas_nombre     ON asignaturas(nombre)",
        "CREATE INDEX IF NOT EXISTS idx_asignaturas_codigo     ON asignaturas(codigo)",
        "CREATE INDEX IF NOT EXISTS idx_matriculas_fecha       ON matriculas(fecha_matricula)",
        "CREATE INDEX IF NOT EXISTS idx_matriculas_cal         ON matriculas(calificacion)",
        "CREATE INDEX IF NOT EXISTS idx_auditoria_prof_fecha   ON auditoria_profesores(fecha_hora)",
        "CREATE INDEX IF NOT EXISTS idx_auditoria_alum_fecha   ON auditoria_alumnos(fecha_hora)",
        "CREATE INDEX IF NOT EXISTS idx_auditoria_asig_fecha   ON auditoria_asignaturas(fecha_hora)",
    ]
    conn = _conn()
    cur = conn.cursor()
    for idx in indices:
        cur.execute(idx)
    conn.commit(); cur.close(); conn.close()
    print(f"[OK] {len(indices)} índices creados")


# columna JSONB para traducciones es/en de cada asignatura
def multiidioma(**_):
    conn = _conn()
    cur = conn.cursor()
    cur.execute("""
        ALTER TABLE asignaturas
            ADD COLUMN IF NOT EXISTS nombre_i18n JSONB DEFAULT '{}'::jsonb
    """)
    traducciones = [
        ('{"es": "Programación I",          "en": "Programming I"}',          'INF101'),
        ('{"es": "Programación II",         "en": "Programming II"}',         'INF102'),
        ('{"es": "Bases de Datos",          "en": "Database Systems"}',       'INF201'),
        ('{"es": "Redes de Computadores",   "en": "Computer Networks"}',      'INF301'),
        ('{"es": "Inteligencia Artificial", "en": "Artificial Intelligence"}','INF401'),
        ('{"es": "Álgebra Lineal",          "en": "Linear Algebra"}',         'MAT101'),
        ('{"es": "Cálculo I",               "en": "Calculus I"}',             'MAT102'),
        ('{"es": "Estadística Aplicada",    "en": "Applied Statistics"}',     'MAT201'),
        ('{"es": "Física I",                "en": "Physics I"}',              'FIS101'),
        ('{"es": "Química General",         "en": "General Chemistry"}',      'QUI101'),
        ('{"es": "Historia Contemporánea",  "en": "Contemporary History"}',   'HIS101'),
        ('{"es": "Historia del Arte",       "en": "Art History"}',            'HIS201'),
        ('{"es": "Lengua y Literatura",     "en": "Language and Literature"}','LEN101'),
        ('{"es": "Microeconomía",           "en": "Microeconomics"}',         'ECO101'),
        ('{"es": "Macroeconomía",           "en": "Macroeconomics"}',         'ECO102'),
        ('{"es": "Economía Digital",        "en": "Digital Economy"}',        'ECO201'),
        ('{"es": "Psicología General",      "en": "General Psychology"}',     'PSI101'),
        ('{"es": "Derecho Civil",           "en": "Civil Law"}',              'DER101'),
        ('{"es": "Derecho Penal",           "en": "Criminal Law"}',           'DER102'),
        ('{"es": "Biología Celular",        "en": "Cell Biology"}',           'BIO101'),
    ]
    for json_val, codigo in traducciones:
        cur.execute(
            "UPDATE asignaturas SET nombre_i18n = %s::jsonb WHERE codigo = %s",
            (json_val, codigo),
        )
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_asignaturas_nombre_i18n
            ON asignaturas USING GIN (nombre_i18n jsonb_path_ops)
    """)
    conn.commit(); cur.close(); conn.close()
    print("[OK] Columna nombre_i18n JSONB poblada para 20 asignaturas")


default_args = {"owner": "ucjc", "start_date": datetime(2024, 1, 1), "retries": 1}

with DAG(
    dag_id="dag_extensiones",
    default_args=default_args,
    description="Amplía esquema: auditoría, saldo, precios, límites, vista, índices",
    schedule_interval=None,
    catchup=False,
    tags=["extensiones", "auditoria", "transacciones", "tema10"],
) as dag:

    t0 = PythonOperator(task_id="instalar_extensiones", python_callable=instalar_extensiones)
    t1 = PythonOperator(task_id="ampliar_esquema",      python_callable=ampliar_esquema)
    t2 = PythonOperator(task_id="actualizar_datos",     python_callable=actualizar_datos)
    t3 = PythonOperator(task_id="crear_auditoria",      python_callable=crear_auditoria)
    t4 = PythonOperator(task_id="crear_vista",          python_callable=crear_vista)
    t5 = PythonOperator(task_id="crear_indices",        python_callable=crear_indices)
    t6 = PythonOperator(task_id="multiidioma",          python_callable=multiidioma)

    t0 >> t1 >> t2 >> t3 >> t4 >> t5 >> t6
