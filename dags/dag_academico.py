from __future__ import annotations

import random
from datetime import date, datetime

import psycopg2
from airflow import DAG
from airflow.operators.python import PythonOperator

_PG = dict(
    host="postgres_academico",
    port=5432,
    dbname="academico_db",
    user="academico",
    password="academico123",
)


def _conn():
    return psycopg2.connect(**_PG)


def verificar_conexion(**_):
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()[0]
    cur.close()
    conn.close()
    print(f"[OK] Conexión exitosa a PostgreSQL: {version}")


def crear_esquema(**_):
    ddl = [
        """
        CREATE TABLE IF NOT EXISTS profesores (
            id               SERIAL PRIMARY KEY,
            nombre           VARCHAR(100) NOT NULL,
            apellido         VARCHAR(100) NOT NULL,
            email            VARCHAR(150) UNIQUE NOT NULL,
            departamento     VARCHAR(100),
            fecha_contratacion DATE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS alumnos (
            id                  SERIAL PRIMARY KEY,
            nombre              VARCHAR(100) NOT NULL,
            apellido            VARCHAR(100) NOT NULL,
            email               VARCHAR(150) UNIQUE NOT NULL,
            fecha_nacimiento    DATE,
            numero_expediente   VARCHAR(20) UNIQUE NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS asignaturas (
            id          SERIAL PRIMARY KEY,
            nombre      VARCHAR(150) NOT NULL,
            codigo      VARCHAR(20)  UNIQUE NOT NULL,
            creditos    INTEGER      NOT NULL,
            profesor_id INTEGER REFERENCES profesores(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS matriculas (
            id              SERIAL PRIMARY KEY,
            alumno_id       INTEGER REFERENCES alumnos(id),
            asignatura_id   INTEGER REFERENCES asignaturas(id),
            fecha_matricula DATE NOT NULL,
            calificacion    NUMERIC(4,2),
            UNIQUE (alumno_id, asignatura_id)
        )
        """,
    ]
    conn = _conn()
    cur = conn.cursor()
    for stmt in ddl:
        cur.execute(stmt)
    conn.commit()
    cur.close()
    conn.close()
    print("[OK] Esquema creado: profesores, alumnos, asignaturas, matriculas")


def insertar_profesores(**_):
    from faker import Faker

    fake = Faker("es_ES")
    departamentos = [
        "Informática", "Matemáticas", "Física", "Química",
        "Historia", "Lengua", "Economía", "Psicología",
        "Derecho", "Biología",
    ]

    conn = _conn()
    cur = conn.cursor()
    # limpio para garantizar reproducibilidad
    cur.execute(
        "TRUNCATE TABLE matriculas, asignaturas, alumnos, profesores RESTART IDENTITY CASCADE"
    )

    Faker.seed(0)
    for i, dept in enumerate(departamentos):
        nombre = fake.first_name()
        apellido = fake.last_name()
        email = f"prof{i+1:02d}.{nombre.lower()[:4]}{apellido.lower()[:4]}@ucjc.edu"
        fecha = fake.date_between(start_date="-15y", end_date="-1y")
        cur.execute(
            "INSERT INTO profesores (nombre, apellido, email, departamento, fecha_contratacion)"
            " VALUES (%s, %s, %s, %s, %s)",
            (nombre, apellido, email, dept, fecha),
        )

    conn.commit()
    cur.close()
    conn.close()
    print("[OK] 10 profesores insertados")


def insertar_alumnos(**_):
    from faker import Faker

    fake = Faker("es_ES")
    Faker.seed(1)

    conn = _conn()
    cur = conn.cursor()

    for i in range(1, 101):
        nombre = fake.first_name()
        apellido = fake.last_name()
        email = f"alumno{i:03d}@ucjc.edu"
        fecha_nac = fake.date_of_birth(minimum_age=18, maximum_age=30)
        expediente = f"UCJC-{2020 + (i % 5)}-{i:04d}"
        cur.execute(
            "INSERT INTO alumnos (nombre, apellido, email, fecha_nacimiento, numero_expediente)"
            " VALUES (%s, %s, %s, %s, %s)",
            (nombre, apellido, email, fecha_nac, expediente),
        )

    conn.commit()
    cur.close()
    conn.close()
    print("[OK] 100 alumnos insertados")


def insertar_asignaturas(**_):
    asignaturas = [
        ("Programación I",          "INF101", 6, 1),
        ("Programación II",         "INF102", 6, 1),
        ("Bases de Datos",          "INF201", 6, 1),
        ("Redes de Computadores",   "INF301", 6, 1),
        ("Inteligencia Artificial", "INF401", 6, 1),
        ("Álgebra Lineal",          "MAT101", 6, 2),
        ("Cálculo I",               "MAT102", 6, 2),
        ("Estadística Aplicada",    "MAT201", 4, 2),
        ("Física I",                "FIS101", 6, 3),
        ("Química General",         "QUI101", 6, 4),
        ("Historia Contemporánea",  "HIS101", 4, 5),
        ("Historia del Arte",       "HIS201", 4, 5),
        ("Lengua y Literatura",     "LEN101", 4, 6),
        ("Microeconomía",           "ECO101", 6, 7),
        ("Macroeconomía",           "ECO102", 6, 7),
        ("Economía Digital",        "ECO201", 4, 7),
        ("Psicología General",      "PSI101", 4, 8),
        ("Derecho Civil",           "DER101", 6, 9),
        ("Derecho Penal",           "DER102", 6, 9),
        ("Biología Celular",        "BIO101", 6, 10),
    ]

    conn = _conn()
    cur = conn.cursor()
    for nombre, codigo, creditos, prof_id in asignaturas:
        cur.execute(
            "INSERT INTO asignaturas (nombre, codigo, creditos, profesor_id)"
            " VALUES (%s, %s, %s, %s)",
            (nombre, codigo, creditos, prof_id),
        )
    conn.commit()
    cur.close()
    conn.close()
    print("[OK] 20 asignaturas insertadas")


def insertar_matriculas(**_):
    conn = _conn()
    cur = conn.cursor()

    cur.execute("SELECT id FROM alumnos ORDER BY id")
    alumno_ids = [r[0] for r in cur.fetchall()]

    cur.execute("SELECT id FROM asignaturas ORDER BY id")
    asig_ids = [r[0] for r in cur.fetchall()]

    random.seed(42)  # semilla fija para reproducibilidad
    insertadas: set[tuple[int, int]] = set()
    count = 0

    while count < 200:
        aid = random.choice(alumno_ids)
        sid = random.choice(asig_ids)
        if (aid, sid) in insertadas:
            continue
        fecha = date(2024, random.randint(1, 9), random.randint(1, 28))
        cal = round(random.uniform(0, 10), 2) if random.random() > 0.3 else None
        cur.execute(
            "INSERT INTO matriculas (alumno_id, asignatura_id, fecha_matricula, calificacion)"
            " VALUES (%s, %s, %s, %s)",
            (aid, sid, fecha, cal),
        )
        insertadas.add((aid, sid))
        count += 1

    conn.commit()
    cur.close()
    conn.close()
    print(f"[OK] 200 matrículas insertadas")


default_args = {
    "owner": "ucjc",
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
}

with DAG(
    dag_id="dag_academico",
    default_args=default_args,
    description="Crea y pobla el esquema académico en PostgreSQL",
    schedule_interval=None,
    catchup=False,
    tags=["academico", "postgresql", "tema10"],
) as dag:

    t1 = PythonOperator(task_id="verificar_conexion",  python_callable=verificar_conexion)
    t2 = PythonOperator(task_id="crear_esquema",       python_callable=crear_esquema)
    t3 = PythonOperator(task_id="insertar_profesores", python_callable=insertar_profesores)
    t4 = PythonOperator(task_id="insertar_alumnos",    python_callable=insertar_alumnos)
    t5 = PythonOperator(task_id="insertar_asignaturas",python_callable=insertar_asignaturas)
    t6 = PythonOperator(task_id="insertar_matriculas", python_callable=insertar_matriculas)

    t1 >> t2 >> t3 >> t4 >> t5 >> t6
