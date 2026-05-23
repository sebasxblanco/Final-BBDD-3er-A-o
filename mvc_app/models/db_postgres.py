from __future__ import annotations

import psycopg2
import psycopg2.extras

from config import Config


def get_pg_conn():
    return psycopg2.connect(Config.pg_dsn())


def query(sql: str, params: tuple = (), *, one: bool = False):
    conn = get_pg_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql, params)
    result = cur.fetchone() if one else cur.fetchall()
    cur.close(); conn.close()
    return result


def execute(sql: str, params: tuple = ()):
    conn = get_pg_conn()
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    cur.close(); conn.close()


def matricular_transaccion(alumno_id: int, asignatura_id: int) -> tuple[bool, str]:
    # verifico duplicado, plazas y saldo antes de inscribir; todo en una transacción
    conn = get_pg_conn()
    conn.autocommit = False
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Bloquea la fila del alumno para evitar condiciones de carrera
        cur.execute("SELECT id, saldo FROM alumnos WHERE id = %s FOR UPDATE", (alumno_id,))
        alumno = cur.fetchone()
        if not alumno:
            raise ValueError("Alumno no encontrado.")

        # Bloquea la fila de la asignatura
        cur.execute("""
            SELECT id, nombre, precio, limite_alumnos,
                   (SELECT COUNT(*) FROM matriculas WHERE asignatura_id = %s) AS inscritos
              FROM asignaturas WHERE id = %s FOR UPDATE
        """, (asignatura_id, asignatura_id))
        asig = cur.fetchone()
        if not asig:
            raise ValueError("Asignatura no encontrada.")

        # Validación 1: matrícula duplicada
        cur.execute(
            "SELECT id FROM matriculas WHERE alumno_id = %s AND asignatura_id = %s",
            (alumno_id, asignatura_id)
        )
        if cur.fetchone():
            raise ValueError("El alumno ya está matriculado en esta asignatura.")

        # Validación 2: plazas disponibles
        if asig['inscritos'] >= asig['limite_alumnos']:
            raise ValueError(
                f"Asignatura completa ({asig['limite_alumnos']} plazas, "
                f"{asig['inscritos']} inscritos)."
            )

        # Validación 3: saldo suficiente
        if alumno['saldo'] < asig['precio']:
            raise ValueError(
                f"Saldo insuficiente. Disponible: {alumno['saldo']:.2f} €, "
                f"Precio: {asig['precio']:.2f} €."
            )

        # Operaciones atómicas
        cur.execute(
            "UPDATE alumnos SET saldo = saldo - %s WHERE id = %s",
            (asig['precio'], alumno_id)
        )
        cur.execute(
            "INSERT INTO matriculas (alumno_id, asignatura_id, fecha_matricula) "
            "VALUES (%s, %s, CURRENT_DATE)",
            (alumno_id, asignatura_id)
        )

        conn.commit()
        return True, f"Matrícula en «{asig['nombre']}» completada. Se descontaron {asig['precio']:.2f} €."

    except ValueError as e:
        conn.rollback()
        return False, str(e)
    except Exception as e:
        conn.rollback()
        return False, f"Error inesperado: {e}"
    finally:
        cur.close(); conn.close()


def cancelar_matricula_transaccion(matricula_id: int) -> tuple[bool, str]:
    conn = get_pg_conn()
    conn.autocommit = False
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT m.id, m.alumno_id, asig.precio, asig.nombre
              FROM matriculas m
              JOIN asignaturas asig ON asig.id = m.asignatura_id
             WHERE m.id = %s FOR UPDATE
        """, (matricula_id,))
        mat = cur.fetchone()
        if not mat:
            raise ValueError("Matrícula no encontrada.")

        cur.execute("UPDATE alumnos SET saldo = saldo + %s WHERE id = %s",
                    (mat['precio'], mat['alumno_id']))
        cur.execute("DELETE FROM matriculas WHERE id = %s", (matricula_id,))

        conn.commit()
        return True, f"Matrícula cancelada. Se reembolsaron {mat['precio']:.2f} € al alumno."
    except ValueError as e:
        conn.rollback()
        return False, str(e)
    except Exception as e:
        conn.rollback()
        return False, f"Error inesperado: {e}"
    finally:
        cur.close(); conn.close()
