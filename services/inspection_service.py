"""
Servicio de Inspecciones

Maneja las operaciones de base de datos relacionadas con las inspecciones de equipos.
Admite operaciones CRUD, recuperación de todos los IDs de inspecciones y filtrado de inspecciones según diferentes parámetros.
"""

from db import db_connection
import json
import sqlite3


def create_inspection(
    numero_lote,
    fecha,
    id_equipo,
    secuencia,
    tipo_inspeccion,
    parametros_analizados,
    id_laboratorista,
):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
    INSERT INTO inspeccion (
        numero_lote, fecha, id_equipo, secuencia, tipo_inspeccion, parametros_analizados, id_laboratorista
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
""",
            (
                numero_lote,
                fecha,
                id_equipo,
                secuencia,
                tipo_inspeccion,
                json.dumps(parametros_analizados),
                id_laboratorista,
            ),
        )


def list_inspections():
    with db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 
                i.id_inspeccion,
                i.numero_lote,
                i.secuencia,
                i.tipo_inspeccion,
                i.fecha,
                e.descripcion_corta AS equipo_nombre,
                e.modelo AS equipo_modelo, 
                e.serie AS equipo_serie,
                i.id_laboratorista
            FROM INSPECCION i
            JOIN EQUIPO_LABORATORIO e
              ON i.id_equipo = e.id_equipo
            ORDER BY i.id_inspeccion DESC
        """
        )
        rows = cursor.fetchall()

    return [dict(row) for row in rows]


def get_inspection(id_inspeccion: int) -> dict | None:
    """
    Obtiene una inspección por su ID.

    Parámetros:
    - id_inspeccion (int): ID de la inspección a buscar.

    Retorna:
    - dict: Información de la inspección si existe.
    - None: Si la inspección no se encuentra en la base de datos.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT id_inspeccion, numero_lote, fecha, id_equipo, secuencia, 
                   parametros_analizados, tipo_inspeccion, id_laboratorista
            FROM INSPECCION
            WHERE id_inspeccion = ?
        """
        cursor.execute(query, (id_inspeccion,))
        row = cursor.fetchone()

    if row:
        return dict(row)
    return None


def update_inspection(
    id_inspeccion: int,
    numero_lote: str,
    fecha: str,
    id_equipo: int | None,
    secuencia: str | None,
    parametros_analizados: str | None,
    tipo_inspeccion: str,
    id_laboratorista: int | None,
) -> int:
    """
    Actualiza la información de una inspección en la base de datos.

    Parámetros:
    - id_inspeccion (int): ID de la inspección a actualizar.
    - numero_lote (str): Nuevo número de lote de la inspección.
    - fecha (str): Nueva fecha de la inspección.
    - id_equipo (int | None): Nuevo ID del equipo inspeccionado.
    - secuencia (str | None): Nueva secuencia del proceso.
    - parametros_analizados (str | None): Nuevos parámetros analizados.
    - tipo_inspeccion (str): Nuevo tipo de inspección.
    - id_laboratorista (int | None): Nuevo ID del usuario que realizó la inspección.

    Retorna:
    - int: Número de filas afectadas (1 si se actualizó, 0 si no se encontró la inspección).
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        query = """
            UPDATE INSPECCION
            SET numero_lote = ?, fecha = ?, id_equipo = ?, secuencia = ?,
                parametros_analizados = ?, tipo_inspeccion = ?, id_laboratorista = ?
            WHERE id_inspeccion = ?
        """
        cursor.execute(
            query,
            (
                numero_lote,
                fecha,
                id_equipo,
                secuencia,
                parametros_analizados,
                tipo_inspeccion,
                id_laboratorista,
                id_inspeccion,
            ),
        )
        affected_rows = cursor.rowcount

    return affected_rows


def delete_inspection(id_inspeccion: int) -> int:
    """
    Elimina una inspección de la base de datos.

    Parámetros:
    - id_inspeccion (int): ID de la inspección a eliminar.

    Retorna:
    - int: Número de filas afectadas (1 si la inspección fue eliminada, 0 si no existía).
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        query = "DELETE FROM INSPECCION WHERE id_inspeccion = ?"
        cursor.execute(query, (id_inspeccion,))
        affected_rows = cursor.rowcount

    return affected_rows


def get_all_inspections() -> list[dict]:
    with db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id_inspeccion, numero_lote, secuencia
            FROM INSPECCION
            ORDER BY id_inspeccion DESC
        """
        )
        return cursor.fetchall()
