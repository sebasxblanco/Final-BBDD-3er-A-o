from __future__ import annotations

import os
import sqlite3
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

SQLITE_PATH = "/opt/airflow/sqlite_data/auth.db"


def crear_tabla_usuarios(**_):
    os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)
    conn = sqlite3.connect(SQLITE_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role          TEXT NOT NULL CHECK(role IN ('admin','profesor','alumno')),
            email         TEXT,
            nombre        TEXT,
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()
    print(f"[OK] Tabla 'users' creada en {SQLITE_PATH}")


def insertar_usuarios(**_):
    from werkzeug.security import generate_password_hash

    usuarios = [
        ("admin",     "admin123", "admin",    "admin@ucjc.edu",       "Administrador"),
        ("profesor1", "prof123",  "profesor", "prof.titular@ucjc.edu","Profesor Titular"),
        ("alumno1",   "alum123",  "alumno",   "alumno001@ucjc.edu",   "Alumno Ejemplo"),
    ]

    conn = sqlite3.connect(SQLITE_PATH)
    # limpio para garantizar reproducibilidad
    conn.execute("DELETE FROM users")
    conn.commit()

    for username, password, role, email, nombre in usuarios:
        hashed = generate_password_hash(password, method="pbkdf2:sha256")
        conn.execute(
            "INSERT INTO users (username, password_hash, role, email, nombre)"
            " VALUES (?, ?, ?, ?, ?)",
            (username, hashed, role, email, nombre),
        )
        print(f"  [+] Usuario '{username}' (rol={role}) — hash generado")

    conn.commit()
    conn.close()
    print("[OK] 3 usuarios insertados con contraseñas cifradas")


default_args = {
    "owner": "ucjc",
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
}

with DAG(
    dag_id="dag_usuarios",
    default_args=default_args,
    description="Crea tabla users en SQLite con contraseñas cifradas (pbkdf2:sha256)",
    schedule_interval=None,
    catchup=False,
    tags=["usuarios", "sqlite", "autenticacion", "tema10"],
) as dag:

    t1 = PythonOperator(task_id="crear_tabla_usuarios", python_callable=crear_tabla_usuarios)
    t2 = PythonOperator(task_id="insertar_usuarios",    python_callable=insertar_usuarios)

    t1 >> t2
