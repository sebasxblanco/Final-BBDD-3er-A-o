# Práctica Final — Bases de Datos Avanzadas
**UCJC · 3er año**

---

## Resumen

Esta práctica implementa un sistema académico completo que combina PostgreSQL, SQLite, Apache Airflow y una aplicación web Flask siguiendo el patrón MVC. Todo el entorno corre en contenedores Docker y no requiere ninguna instalación local más allá de Docker Desktop.

El sistema gestiona profesores, alumnos, asignaturas y matrículas, con autenticación de usuarios, auditoría automática de cambios mediante triggers, extensiones avanzadas de PostgreSQL, capacidades geoespaciales con PostGIS y estadísticas con funciones de ventana.

---

## Lo que se implementó

**Base de datos académica (PostgreSQL)**

Se construyó un esquema con cuatro tablas principales: `profesores`, `alumnos`, `asignaturas` y `matriculas`, pobladas con 10 profesores, 100 alumnos, 20 asignaturas y 200 matrículas generadas con Faker y semilla fija para reproducibilidad.

**Extensiones PostgreSQL**

Se instalaron y utilizaron `pg_trgm` para búsqueda por similitud, `unaccent` para normalización de acentos, `fuzzystrmatch` para distancia de Levenshtein, `citext` para comparaciones sin distinción de mayúsculas y `btree_gin` para índices combinados.

**Auditoría con triggers**

Se crearon tablas de auditoría para profesores, alumnos y asignaturas. Cada INSERT, UPDATE y DELETE queda registrado automáticamente con los datos anteriores y nuevos en formato JSONB.

**Multiidioma JSONB**

La columna `nombre_i18n` en `asignaturas` almacena traducciones en español e inglés mediante JSONB, con índice GIN para búsquedas eficientes por clave.

**Transacciones y saldo**

La matriculación es transaccional: verifica plazas disponibles, saldo del alumno y matrícula duplicada antes de ejecutar el descuento. Todo en una única transacción con bloqueo por filas para evitar condiciones de carrera.

**Vista SQL**

La vista `vista_alumno_profesor_asignatura` cruza las cuatro tablas y expone la relación completa entre alumnos, profesores, asignaturas y calificaciones.

**Estadísticas avanzadas**

Se implementaron consultas con `ROW_NUMBER`, `GROUPING SETS`, `ROLLUP`, `FILTER` y funciones de ventana para análisis de rendimiento académico.

**PostGIS (geoespacial)**

Se activó la extensión PostGIS sobre PostgreSQL. Se asignaron posiciones reales en el campus (EPSG:4326) a 4 alumnos como puntos y se delimitaron 4 aulas como polígonos. La función `viajar(alumno_id, asignatura_id)` calcula la distancia en metros, detecta si el alumno ya está dentro del aula y devuelve los GeoJSON para el mapa. Los datos se visualizan en un mapa interactivo con Leaflet.js.

**Autenticación SQLite**

La gestión de sesiones de usuario usa una base de datos SQLite separada con contraseñas cifradas con pbkdf2:sha256.

**Apache Airflow**

Todo el proceso de creación de esquema, inserción de datos y configuración avanzada está automatizado en DAGs de Airflow. No existe ningún dato creado manualmente fuera de los DAGs.

---

## Requisitos

- Docker Desktop 24.x o superior (incluye Docker Compose v2)
- Git

No se requiere Python, PostgreSQL ni ninguna otra herramienta instalada localmente.

---

## Cómo reproducirlo

**1. Clonar el repositorio**

```bash
git clone https://github.com/sebasxblanco/BBDD_sistema_academico.git
cd BBDD_sistema_academico.git
```

**2. Levantar todos los contenedores**

```bash
docker compose up -d --build
```

Esto arranca seis servicios: dos instancias de PostgreSQL, tres componentes de Airflow (init, webserver, scheduler) y la aplicación Flask. Esperar aproximadamente 60-90 segundos a que todos estén en estado `healthy`.

```bash
docker ps
```

**3. Abrir Airflow y ejecutar los DAGs en orden**

Acceder a http://localhost:8080 con usuario `admin` y contraseña `admin123`.

Ejecutar los DAGs en este orden (botón de play en cada uno, esperar a que todas las tareas estén en verde antes de pasar al siguiente):

1. `dag_academico` — crea las tablas y pobla 10 profesores, 100 alumnos, 20 asignaturas y 200 matrículas
2. `dag_usuarios` — crea la base de datos SQLite con 3 usuarios de prueba
3. `dag_extensiones` — instala extensiones, auditoría, vista, índices y multiidioma JSONB
4. `dag_postgis` — activa PostGIS, añade geometrías a alumnos y aulas, crea índices GiST y la función `viajar()`

**4. Acceder a la aplicación**

Abrir http://localhost:5000

Credenciales disponibles:

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| admin | admin123 | admin |
| profesor1 | prof123 | profesor |
| alumno1 | alum123 | alumno |

**5. Verificar los datos desde terminal**

```bash
docker exec -it pg_academico psql -U academico -d academico_db -c \
"SELECT 'profesores' AS tabla, COUNT(*) FROM profesores
 UNION ALL SELECT 'alumnos', COUNT(*) FROM alumnos
 UNION ALL SELECT 'asignaturas', COUNT(*) FROM asignaturas
 UNION ALL SELECT 'matriculas', COUNT(*) FROM matriculas;"
```

Resultado esperado: 10, 100, 20, 200.

```bash
docker exec -it pg_academico psql -U academico -d academico_db -c \
"SELECT extname FROM pg_extension WHERE extname IN ('postgis','pg_trgm','unaccent','citext','fuzzystrmatch','btree_gin');"
```

**6. Parar el sistema**

```bash
# conserva los datos en volúmenes
docker compose down

# reinicio total, borra todos los datos
docker compose down -v
```

---

## Estructura del proyecto

```
tema10/
├── docker-compose.yml
├── dags/
│   ├── dag_academico.py       
│   ├── dag_usuarios.py        
│   ├── dag_extensiones.py     
│   └── dag_postgis.py         
├── sql/
│   ├── indices.sql
│   ├── vista_academica.sql
│   ├── multiidioma_asignaturas.sql
│   └── postgis_academico.sql
└── mvc_app/
    ├── Dockerfile
    ├── requirements.txt
    ├── app.py
    ├── config.py
    ├── models/
    │   ├── db_postgres.py
    │   ├── db_sqlite.py
    │   └── user.py
    ├── controllers/
    │   ├── auth.py
    │   ├── main.py
    │   ├── profesores.py
    │   ├── alumnos.py
    │   ├── asignaturas.py
    │   ├── matriculas.py
    │   ├── auditoria.py
    │   ├── vista.py
    │   └── gis.py
    └── templates/
```
