# Tema 10 — Airflow + MVC Flask (PostgreSQL + SQLite)
**UCJC · Práctica de Sistemas Reproducibles**

---

## Arquitectura

```
┌──────────────────────────────────────────────────────────┐
│                     Docker Compose                       │
│                                                          │
│  ┌─────────────┐   ┌──────────────────────────────────┐  │
│  │  Airflow    │   │           DAGs                   │  │
│  │  :8080      │──▶│  dag_academico  → PostgreSQL :5433│  │
│  │  admin/     │   │  dag_usuarios   → SQLite (volumen)│  │
│  │  admin123   │   └──────────────────────────────────┘  │
│  └─────────────┘                                         │
│                                                          │
│  ┌─────────────┐   ┌──────────────────────────────────┐  │
│  │ Flask MVC   │   │  PostgreSQL academico_db          │  │
│  │  :5000      │──▶│  profesores / alumnos /           │  │
│  │             │   │  asignaturas / matriculas         │  │
│  │             │──▶│  SQLite auth.db (usuarios)        │  │
│  └─────────────┘   └──────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

## Requisitos

| Herramienta | Versión mínima |
|-------------|----------------|
| Docker Desktop | 24.x |
| Docker Compose | v2.x (incluido en Docker Desktop) |
| Git | cualquiera |

> **Importante:** No se requiere Python, PostgreSQL ni ninguna otra herramienta instalada localmente. Todo corre en contenedores Docker.

---

## Ejecución paso a paso

### Paso 1 — Clonar / posicionarse en el proyecto

```bash
cd Desktop/tema10
```

### Paso 2 — Levantar todos los contenedores

```bash
docker compose up -d --build
```

Esto arranca:
- `pg_airflow` — PostgreSQL para metadatos de Airflow
- `pg_academico` — PostgreSQL para datos académicos (puerto 5433)
- `airflow_init` — inicializa la BD de Airflow y crea el usuario admin
- `airflow_webserver` — UI de Airflow (puerto 8080)
- `airflow_scheduler` — scheduler de Airflow
- `flask_mvc` — aplicación Flask (puerto 5000)

Esperar ~60-90 segundos a que todos los servicios estén `healthy`.

### Paso 3 — Verificar que todos los contenedores están activos

```bash
docker ps
```

Todos deben aparecer con estado **Up** (y los que tienen healthcheck, como **healthy**).

### Paso 4 — Abrir Airflow y ejecutar los DAGs

1. Abrir **http://localhost:8080**
2. Login: `admin` / `admin123`
3. En la lista de DAGs verás: `dag_academico` y `dag_usuarios`

**Ejecutar `dag_academico`:**
- Clic en `dag_academico` → botón ▶ (Trigger DAG) → Trigger
- Esperar a que todas las tareas estén en verde ✓

**Ejecutar `dag_usuarios`:**
- Clic en `dag_usuarios` → botón ▶ → Trigger
- Esperar a que todas las tareas estén en verde ✓

> **Orden:** Los DAGs son independientes; pueden ejecutarse en cualquier orden o en paralelo. Sin embargo, Flask-MVC solo mostrará datos cuando ambos DAGs hayan completado.

### Paso 5 — Verificar datos en PostgreSQL (opcional)

```bash
docker exec -it pg_academico psql -U academico -d academico_db -c "\dt"
docker exec -it pg_academico psql -U academico -d academico_db -c "SELECT COUNT(*) FROM profesores;"
docker exec -it pg_academico psql -U academico -d academico_db -c "SELECT COUNT(*) FROM alumnos;"
docker exec -it pg_academico psql -U academico -d academico_db -c "SELECT COUNT(*) FROM asignaturas;"
docker exec -it pg_academico psql -U academico -d academico_db -c "SELECT COUNT(*) FROM matriculas;"
```

Resultados esperados: 10, 100, 20, 200 respectivamente.

### Paso 6 — Verificar datos en SQLite (opcional)

```bash
docker exec -it flask_mvc python -c "
import sqlite3
conn = sqlite3.connect('/app/sqlite_data/auth.db')
for row in conn.execute('SELECT id, username, role, nombre FROM users'):
    print(dict(zip([\"id\",\"username\",\"role\",\"nombre\"], row)))
conn.close()
"
```

### Paso 7 — Usar la aplicación Flask MVC

1. Abrir **http://localhost:5000**
2. Login con cualquiera de las credenciales:

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| `admin` | `admin123` | admin |
| `profesor1` | `prof123` | profesor |
| `alumno1` | `alum123` | alumno |

3. Navegar por los módulos:
   - `/profesores` — listado y detalle
   - `/alumnos` — listado y detalle
   - `/asignaturas` — listado y detalle
   - `/matriculas` — listado y detalle

---

## Estructura del proyecto

```
tema10/
├── docker-compose.yml          # Orquestación de todos los servicios
├── README.md                   # Este archivo
│
├── dags/                       # DAGs de Apache Airflow
│   ├── dag_academico.py        # PostgreSQL: 10 prof, 100 alum, 20 asig, 200 mat
│   └── dag_usuarios.py         # SQLite: 3 usuarios con contraseñas cifradas
│
├── sqlite_data/                # Volumen compartido (auth.db generado por DAG)
│
└── mvc_app/                    # Aplicación Flask (patrón MVC)
    ├── Dockerfile
    ├── requirements.txt
    ├── app.py                  # Application Factory
    ├── config.py               # Configuración (ENV vars)
    ├── models/
    │   ├── db_postgres.py      # Acceso a PostgreSQL
    │   ├── db_sqlite.py        # Acceso a SQLite
    │   └── user.py             # Entidad User + autenticación
    ├── controllers/
    │   ├── auth.py             # Login / Logout (SQLite)
    │   ├── main.py             # Dashboard
    │   ├── profesores.py       # /profesores (PostgreSQL)
    │   ├── alumnos.py          # /alumnos (PostgreSQL)
    │   ├── asignaturas.py      # /asignaturas (PostgreSQL)
    │   └── matriculas.py       # /matriculas (PostgreSQL)
    └── templates/
        ├── base.html
        ├── index.html
        ├── auth/login.html
        ├── profesores/{list,detail}.html
        ├── alumnos/{list,detail}.html
        ├── asignaturas/{list,detail}.html
        └── matriculas/{list,detail}.html
```

---

## Reproducibilidad

El sistema es **100% reproducible**:

1. `docker compose down -v` elimina todos los contenedores y volúmenes
2. `docker compose up -d --build` reconstruye todo desde cero
3. Ejecutar ambos DAGs recrea exactamente los mismos datos (semilla fija `random.seed(42)`)

No existe ningún dato creado manualmente fuera de los DAGs.

---

## Orden obligatorio de ejecución de DAGs

```
1. dag_academico    → crea tablas base + 10 prof, 100 alum, 20 asig, 200 mat
2. dag_usuarios     → crea auth.db en SQLite con 3 usuarios cifrados
3. dag_extensiones  → extensiones, auditoría, saldo, vista, índices, multiidioma
```

Los DAGs 1 y 2 pueden ejecutarse en paralelo. El DAG 3 requiere que el DAG 1 haya completado (depende del esquema base).

---

## Guión de screenshots — prueba de entrega

### BLOQUE A — Infraestructura

**Screenshot A-1:** `docker ps` mostrando los 6 contenedores activos
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

**Screenshot A-2:** Airflow UI en http://localhost:8080 — lista de los 3 DAGs (`dag_academico`, `dag_usuarios`, `dag_extensiones`)

---

### BLOQUE B — DAG Académico (datos base)

**Screenshot B-1:** `dag_academico` ejecutado correctamente — las 6 tareas en verde en el Graph View de Airflow

**Screenshot B-2:** Recuentos de tablas base en PostgreSQL
```bash
docker exec -it pg_academico psql -U academico -d academico_db -c \
"SELECT 'profesores' t, COUNT(*) FROM profesores
 UNION ALL SELECT 'alumnos', COUNT(*) FROM alumnos
 UNION ALL SELECT 'asignaturas', COUNT(*) FROM asignaturas
 UNION ALL SELECT 'matriculas', COUNT(*) FROM matriculas;"
```
Resultados esperados: 10, 100, 20, 200

---

### BLOQUE C — DAG Usuarios (autenticación SQLite)

**Screenshot C-1:** `dag_usuarios` ejecutado correctamente — las 2 tareas en verde

**Screenshot C-2:** Contenido de auth.db mostrando hash de contraseñas
```bash
docker exec -it flask_mvc python -c "
import sqlite3
conn = sqlite3.connect('/app/sqlite_data/auth.db')
for row in conn.execute('SELECT username, role, password_hash FROM users'):
    print(row)
conn.close()
"
```
Debe aparecer el prefijo `pbkdf2:sha256:600000$...` en cada contraseña

**Screenshot C-3:** Login en http://localhost:5000 con `admin` / `admin123` → dashboard visible

---

### BLOQUE D — DAG Extensiones (auditoría, saldo, vista, índices, extensiones, multiidioma)

**Screenshot D-1:** `dag_extensiones` ejecutado correctamente — las 7 tareas en verde  
(instalar_extensiones → ampliar_esquema → actualizar_datos → crear_auditoria → crear_vista → crear_indices → multiidioma)

**Screenshot D-2:** Extensiones instaladas
```bash
docker exec -it pg_academico psql -U academico -d academico_db -c \
"SELECT name, installed_version FROM pg_available_extensions
 WHERE name IN ('unaccent','citext','fuzzystrmatch','pg_trgm','btree_gin')
 ORDER BY name;"
```

**Screenshot D-3:** Tablas de auditoría y triggers existentes
```bash
docker exec -it pg_academico psql -U academico -d academico_db -c \
"SELECT tablename FROM pg_tables WHERE tablename LIKE 'auditoria_%' ORDER BY tablename;"
```

**Screenshot D-4:** Registro de auditoría generado automáticamente  
En la app Flask, edita cualquier alumno (cambia el email por ejemplo) y luego ejecuta:
```bash
docker exec -it pg_academico psql -U academico -d academico_db -c \
"SELECT operacion, registro_id, fecha_hora FROM auditoria_alumnos ORDER BY fecha_hora DESC LIMIT 5;"
```

**Screenshot D-5:** Vista PostgreSQL funcionando
```bash
docker exec -it pg_academico psql -U academico -d academico_db -c \
"SELECT nombre_alumno, nombre_profesor, nombre_asignatura FROM vista_alumno_profesor_asignatura LIMIT 5;"
```

**Screenshot D-6:** Índices creados
```bash
docker exec -it pg_academico psql -U academico -d academico_db -c \
"SELECT indexname, tablename FROM pg_indexes
 WHERE schemaname='public' AND indexname LIKE 'idx_%'
 ORDER BY tablename, indexname;"
```

**Screenshot D-7:** Multiidioma JSONB — traducciones es/en
```bash
docker exec -it pg_academico psql -U academico -d academico_db -c \
"SELECT codigo, nombre_i18n->>'es' AS es, nombre_i18n->>'en' AS en
 FROM asignaturas ORDER BY codigo LIMIT 10;"
```

---

### BLOQUE E — Flask MVC funcional

**Screenshot E-1:** http://localhost:5000/profesores — listado con filtros (busca algo, ej: "informática")

**Screenshot E-2:** http://localhost:5000/alumnos — listado con paginación visible (página 2)

**Screenshot E-3:** http://localhost:5000/asignaturas — listado mostrando precio y límite de alumnos

**Screenshot E-4:** http://localhost:5000/matriculas — realizar una matrícula nueva (formulario) y confirmar éxito

**Screenshot E-5:** http://localhost:5000/vista — Vista Académica con filtros aplicados (fecha o calificación)

**Screenshot E-6:** http://localhost:5000/auditoria/alumnos — log de auditoría tras la edición del screenshot D-4

---

### BLOQUE F — Saldo y transacciones

**Screenshot F-1:** Detalle de un alumno en Flask mostrando su saldo antes de matricularse

**Screenshot F-2:** Formulario de nueva matrícula mostrando precio de asignatura y plazas disponibles

**Screenshot F-3:** Detalle del mismo alumno después de la matrícula — saldo reducido en el precio

**Screenshot F-4:** Intento de matrícula en asignatura sin plazas → mensaje de error de la transacción

---

### BLOQUE G — Extensiones avanzadas (psql directo)

**Screenshot G-1:** Búsqueda con `unaccent` — "Garcia" encuentra "García"
```bash
docker exec -it pg_academico psql -U academico -d academico_db -c \
"SELECT id, nombre, apellido FROM alumnos
 WHERE unaccent(lower(apellido)) = unaccent(lower('garcia')) LIMIT 5;"
```

**Screenshot G-2:** Levenshtein — distancia de edición entre códigos de asignatura
```bash
docker exec -it pg_academico psql -U academico -d academico_db -c \
"SELECT codigo, nombre, levenshtein(codigo, 'INF201') AS distancia
 FROM asignaturas WHERE levenshtein(codigo, 'INF201') <= 2
 ORDER BY distancia;"
```

**Screenshot G-3:** Similaridad por trigramas — búsqueda tolerante a errores
```bash
docker exec -it pg_academico psql -U academico -d academico_db -c \
"SELECT codigo, nombre, similarity(nombre, 'Programacion') AS sim
 FROM asignaturas WHERE nombre % 'Programacion'
 ORDER BY sim DESC;"
```

---

## Parar el sistema

```bash
# Para los contenedores (conserva datos en volúmenes)
docker compose down

# Para los contenedores Y borra todos los datos (reinicio total)
docker compose down -v
```
