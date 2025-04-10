"""
Servicio de Inspecciones

Maneja las operaciones de base de datos relacionadas con las inspecciones de equipos.
Admite operaciones CRUD, recuperación de todos los IDs de inspecciones y filtrado de inspecciones según diferentes parámetros.
"""

from db import db_connection


def create_inspection(
    numero_lote: str,
    fecha: str,
    id_equipo: int | None,
    secuencia: str | None,
    parametros_analizados: str | None,
    tipo_inspeccion: str,
    id_laboratorista: int | None,
) -> int | None:
    """
    Crea una nueva inspección en la base de datos.

    Parámetros:
    - numero_lote (str): Número de lote de la inspección.
    - fecha (str): Fecha de la inspección (Formato: YYYY-MM-DD).
    - id_equipo (int | None): ID del equipo inspeccionado (puede ser None si no aplica).
    - secuencia (str | None): Código de secuencia del proceso (puede ser None si no aplica).
    - parametros_analizados (str | None): Parámetros que fueron analizados (puede ser None si no aplica).
    - tipo_inspeccion (str): Tipo de inspección (e.g., "Inicial", "Rutina", "Final").
    - id_laboratorista (int | None): ID del usuario que realizó la inspección (puede ser None si no aplica).

    Retorna:
    - int: ID de la inspección creada, o None si no se pudo crear.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        query = """
            INSERT INTO INSPECCION (
                numero_lote, fecha, id_equipo, secuencia, 
                parametros_analizados, tipo_inspeccion, id_laboratorista
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (
            numero_lote,
            fecha,
            id_equipo,
            secuencia,
            parametros_analizados,
            tipo_inspeccion,
            id_laboratorista
        ))
        inspection_id = cursor.lastrowid

    if inspection_id:
        return inspection_id
    return None


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
        cursor.execute(query, (
            numero_lote,
            fecha,
            id_equipo,
            secuencia,
            parametros_analizados,
            tipo_inspeccion,
            id_laboratorista,
            id_inspeccion
        ))
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


def list_inspections() -> list:
    """
    Obtiene la lista de todas las inspecciones en la base de datos.

    Retorna:
    - list: Lista de diccionarios, donde cada diccionario representa una inspección.
    - Lista vacía si no hay inspecciones en la base de datos.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT id_inspeccion, numero_lote, fecha, id_equipo, secuencia, 
                   parametros_analizados, tipo_inspeccion, id_laboratorista
            FROM INSPECCION
        """
        cursor.execute(query)
        rows = cursor.fetchall()

    return [dict(row) for row in rows]
