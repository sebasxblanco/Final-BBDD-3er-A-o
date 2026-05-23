"""Configuración central: lee variables de entorno con valores por defecto para desarrollo local."""
from __future__ import annotations

import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret_tema10_ucjc")

    # PostgreSQL — datos académicos
    POSTGRES_HOST     = os.environ.get("POSTGRES_HOST",     "localhost")
    POSTGRES_PORT     = int(os.environ.get("POSTGRES_PORT", "5433"))
    POSTGRES_DB       = os.environ.get("POSTGRES_DB",       "academico_db")
    POSTGRES_USER     = os.environ.get("POSTGRES_USER",     "academico")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "academico123")

    # SQLite — autenticación (generado por dag_usuarios)
    SQLITE_PATH = os.environ.get("SQLITE_PATH", "./sqlite_data/auth.db")

    @classmethod
    def pg_dsn(cls) -> str:
        return (
            f"host={cls.POSTGRES_HOST} port={cls.POSTGRES_PORT} "
            f"dbname={cls.POSTGRES_DB} user={cls.POSTGRES_USER} "
            f"password={cls.POSTGRES_PASSWORD}"
        )
