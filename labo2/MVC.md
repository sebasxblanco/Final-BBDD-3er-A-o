# Prototipo MVC en labo2 (buenas prácticas)

Arquitectura **Model — View — Controller** con Flask y PostgreSQL: aplicación factory, blueprints, objetos de dominio y plantilla base.

## Dónde está cada capa

| Capa        | Ubicación                 | Responsabilidad |
|-------------|----------------------------|-----------------|
| **Model**   | `models/db.py`, `entities.py` | Conexión y SELECT; devuelve `Vendor` y `Part` (dataclasses). Sin HTML, sin rutas. |
| **View**    | `templates/*.html`, `static/style.css` | Presentación (Jinja2 + CSS). Extienden `base.html`. Sin SQL. |
| **Controller** | `app.py` + `routes/*.py` | Factory `create_app()`, blueprints por recurso. Pide datos al Model y pasa a la View. |

## Estructura del proyecto

```
labo2/
  app.py              # create_app() + registro de blueprints y errores
  config.py           # load_config() para BD (usado por Model y scripts)
  database.ini
  models/
    entities.py       # Part, Vendor (dataclasses)
    db.py             # get_connection, get_vendors, get_parts, get_drawing, ...
  routes/
    main.py           # blueprint "/" (índice)
    vendors.py        # blueprint "/vendors"
    parts.py          # blueprint "/parts", "/parts/<id>/drawing"
  templates/
    base.html         # layout común + bloque content
    index.html, vendors.html, parts.html
    errors/404.html, 500.html
  static/
    style.css
```

## Buenas prácticas aplicadas

- **Application factory:** `create_app()` para poder testear y tener varias instancias.
- **Blueprints:** Rutas agrupadas por recurso (main, vendors, parts).
- **Objetos de dominio:** La vista usa `part.id`, `part.name` y `vendor.id`, `vendor.name` en lugar de tuplas.
- **Plantilla base:** Un solo layout; las páginas definen `{% block content %}`.
- **Errores centralizados:** 404 y 500 con plantillas propias.
- **Constantes:** MIME types para imágenes en un diccionario en el blueprint de parts.
- **Configuración:** Credenciales en `database.ini`; nada hardcodeado en el código.

## Uso

1. **Configurar BD:** editar `database.ini` (user, password).
2. **Crear tablas:** `python create_tables.py`
3. **Datos de ejemplo:** `python insert_demo_data.py`
4. **Arrancar:** `export FLASK_APP=app.py && flask run`
5. Abrir: `http://127.0.0.1:5000/`

## Rutas

- `GET /` — Inicio (enlaces a vendors y parts).
- `GET /vendors` — Lista de vendors.
- `GET /parts` — Lista de parts (con miniatura si hay dibujo).
- `GET /parts/<id>/drawing` — Imagen del dibujo de la parte (404 si no existe).

## Flujo de una petición

1. El navegador pide una URL (p. ej. `/vendors`).
2. Flask enruta al blueprint correspondiente.
3. La vista del controlador llama al Model (`get_vendors()`) y recibe `list[Vendor]`.
4. Pasa los datos a la plantilla (View); la plantilla usa `vendor.id`, `vendor.name`.
5. El navegador recibe HTML (y CSS desde `static/`).

La base de datos no sirve páginas; la aplicación sí.
