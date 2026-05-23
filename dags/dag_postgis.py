"""
DAG PostGIS
"""
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


# instalar extensión postgis
def instalar_postgis(**_):
    conn = _conn()
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    conn.commit(); cur.close(); conn.close()
    print("[OK] extensión postgis instalada")


# añadir columnas de geometría a alumnos y asignaturas
def agregar_geometrias(**_):
    conn = _conn()
    cur = conn.cursor()
    cur.execute("""
        ALTER TABLE alumnos
            ADD COLUMN IF NOT EXISTS geom GEOMETRY(Point, 4326)
    """)
    cur.execute("""
        ALTER TABLE asignaturas
            ADD COLUMN IF NOT EXISTS geom GEOMETRY(Polygon, 4326)
    """)
    conn.commit(); cur.close(); conn.close()
    print("[OK] columnas geom añadidas a alumnos y asignaturas")


# poblar coordenadas para los primeros 4 alumnos y 4 asignaturas concretas
def poblar_geometrias(**_):
    conn = _conn()
    cur = conn.cursor()

    # coordenadas de 4 alumnos en el campus (EPSG 4326)
    # se asignan a los 4 primeros registros ordenados por id
    puntos_alumnos = [
        (-4.0060, 40.4515),   # puerta de entrada
        (-4.0030, 40.4525),   # zona de aparcamiento
        (-4.0055, 40.4495),   # cafetería
        (-4.0043, 40.4508),   # biblioteca
    ]
    cur.execute("SELECT id FROM alumnos ORDER BY id LIMIT 4")
    ids_alumnos = [row[0] for row in cur.fetchall()]
    for alumno_id, (lon, lat) in zip(ids_alumnos, puntos_alumnos):
        cur.execute(
            "UPDATE alumnos SET geom = ST_SetSRID(ST_MakePoint(%s, %s), 4326) WHERE id = %s",
            (lon, lat, alumno_id),
        )

    # polígonos de 4 aulas en el campus (edificios de ~50 × 40 m)
    poligonos_aulas = {
        'INF201': 'POLYGON((-4.0053 40.4510, -4.0047 40.4510, -4.0047 40.4514, -4.0053 40.4514, -4.0053 40.4510))',
        'MAT101': 'POLYGON((-4.0038 40.4516, -4.0032 40.4516, -4.0032 40.4520, -4.0038 40.4520, -4.0038 40.4516))',
        'FIS101': 'POLYGON((-4.0068 40.4503, -4.0062 40.4503, -4.0062 40.4507, -4.0068 40.4507, -4.0068 40.4503))',
        'HIS101': 'POLYGON((-4.0045 40.4498, -4.0039 40.4498, -4.0039 40.4502, -4.0045 40.4502, -4.0045 40.4498))',
    }
    for codigo, wkt in poligonos_aulas.items():
        cur.execute(
            "UPDATE asignaturas SET geom = ST_GeomFromText(%s, 4326) WHERE codigo = %s",
            (wkt, codigo),
        )

    conn.commit(); cur.close(); conn.close()
    print("[OK] geometrías pobladas: 4 puntos de alumnos, 4 polígonos de aulas")


# índices GiST para consultas espaciales eficientes
def crear_indices_gis(**_):
    conn = _conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_alumnos_geom
            ON alumnos USING GIST (geom)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_asignaturas_geom
            ON asignaturas USING GIST (geom)
    """)
    conn.commit(); cur.close(); conn.close()
    print("[OK] índices GiST creados en alumnos.geom y asignaturas.geom")


# función SQL viajar(): calcula ruta y distancia de un alumno a un aula
def crear_funcion_viajar(**_):
    conn = _conn()
    cur = conn.cursor()
    cur.execute("""
        DROP FUNCTION IF EXISTS viajar(INTEGER, INTEGER);
        CREATE FUNCTION viajar(p_alumno_id INTEGER, p_asignatura_id INTEGER)
        RETURNS TABLE(
            alumno_nombre       TEXT,
            asignatura_nombre   TEXT,
            asignatura_codigo   TEXT,
            distancia_metros    NUMERIC,
            ya_llego            BOOLEAN,
            alumno_geojson      TEXT,
            aula_geojson        TEXT,
            ruta_geojson        TEXT
        ) LANGUAGE plpgsql AS $$
        BEGIN
            RETURN QUERY
            SELECT
                (al.nombre || ' ' || al.apellido)::TEXT,
                asig.nombre::TEXT,
                asig.codigo::TEXT,
                ROUND(ST_Distance(al.geom::geography, ST_Centroid(asig.geom)::geography)::NUMERIC, 1),
                ST_Contains(asig.geom, al.geom),
                ST_AsGeoJSON(al.geom)::TEXT,
                ST_AsGeoJSON(asig.geom)::TEXT,
                ST_AsGeoJSON(ST_MakeLine(al.geom, ST_Centroid(asig.geom)))::TEXT
            FROM alumnos al
            JOIN asignaturas asig ON asig.id = p_asignatura_id
            WHERE al.id = p_alumno_id
              AND al.geom IS NOT NULL
              AND asig.geom IS NOT NULL;
        END;
        $$
    """)
    conn.commit(); cur.close(); conn.close()
    print("[OK] función viajar() creada")


# definición del DAG
default_args = {"owner": "ucjc", "start_date": datetime(2024, 1, 1), "retries": 1}

with DAG(
    dag_id="dag_postgis",
    default_args=default_args,
    description="PostGIS: geometrías de alumnos y aulas, índices GiST, función viajar()",
    schedule_interval=None,
    catchup=False,
    tags=["postgis", "gis", "geometria", "tema10"],
) as dag:

    t1 = PythonOperator(task_id="instalar_postgis",    python_callable=instalar_postgis)
    t2 = PythonOperator(task_id="agregar_geometrias",  python_callable=agregar_geometrias)
    t3 = PythonOperator(task_id="poblar_geometrias",   python_callable=poblar_geometrias)
    t4 = PythonOperator(task_id="crear_indices_gis",   python_callable=crear_indices_gis)
    t5 = PythonOperator(task_id="crear_funcion_viajar", python_callable=crear_funcion_viajar)

    t1 >> t2 >> t3 >> t4 >> t5
