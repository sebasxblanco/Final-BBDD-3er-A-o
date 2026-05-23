# labo2 — MVC (Flask + PostgreSQL)

## Autenticación (SQLite, independiente de PostgreSQL)

La primera pantalla es **login**. Los usuarios y contraseñas se guardan en una base SQLite aparte; las contraseñas están hasheadas (pbkdf2:sha256).

1. Crear tabla de usuarios: `python create_sqlite_tables.py`
2. Crear usuario de prueba: `python insert_demo_user.py` (por defecto usuario `demo`, contraseña `demo`)

La base SQLite se crea en `instance/auth.db` y no interfiere con PostgreSQL.

## Conectarse y preparar la BD (PostgreSQL)

1. Configurar `database.ini` (user, password).
2. Probar conexión: `python connect.py`
3. Crear tablas: `python create_tables.py`
4. (Opcional) Insertar datos de ejemplo: `python insert_demo_data.py`

## Aplicación web (prototipo MVC)

- Ver **MVC.md** para la descripción de la arquitectura (Model, View, Controller).
- Arrancar la app:
  ```bash
  export FLASK_APP=app.py
  flask run
  ```
- Abrir en el navegador: `http://127.0.0.1:5000/` → redirige a **login**. Tras iniciar sesión se accede a inicio, /vendors y /parts (PostgreSQL).

## Estructura actual

- `config.py` — Carga de credenciales desde `database.ini`.
- `connect.py` — Script para comprobar la conexión.
- `create_tables.py` — Crea las tablas del laboratorio (idempotente).
- `app.py` — Controller (rutas Flask).
- `models/db.py` — Model (conexión y SELECTs).
- `templates/` — View (plantillas Jinja2).

Los scripts de CRUD, transacciones, funciones/procedimientos y BLOB se eliminaron; la práctica se centra en el prototipo MVC con listados (SELECT). Se pueden reintroducir en fases posteriores si se desea.
