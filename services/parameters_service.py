"""
Servicio de Parámetros

Gestiona los parámetros que vinculan certificados y registros de equipos.
Proporciona operaciones CRUD para insertar, recuperar, actualizar y eliminar registros
de parámetros asociados a certificados y equipos.
"""

from db import db_connection


def create_parameter(
    id_inspeccion: int,
    id_equipo_laboratorio: int,
    parametro_analizado: str,
    valor: float | None,
) -> int | None:
    """
    Crea un nuevo registro de parámetro de análisis en la base de datos.

    Parámetros:
    - id_inspeccion (int): ID de la inspección asociada al parámetro.
    - id_equipo_laboratorio (int): ID del equipo de laboratorio donde se realizó la medición.
    - parametro_analizado (str): Nombre del parámetro analizado (e.g., "pH", "Conductividad").
    - valor (float | None): Valor numérico del parámetro analizado (puede ser None si no aplica).

    Retorna:
    - int: ID del parámetro creado, o None si no se pudo crear.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        query = """
            INSERT INTO PARAMETRO_ANALISIS (
                id_inspeccion, id_equipo_laboratorio, parametro_analizado, valor
            )
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (
            id_inspeccion,
            id_equipo_laboratorio,
            parametro_analizado,
            valor
        ))
        param_id = cursor.lastrowid

    if param_id:
        return param_id
    return None


def get_parameter(id_parametro: int) -> dict | None:
    """
    Obtiene un parámetro de análisis por su ID.

    Parámetros:
    - id_parametro (int): ID del parámetro a buscar.

    Retorna:
    - dict: Información del parámetro si existe.
    - None: Si el parámetro no se encuentra en la base de datos.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM PARAMETRO_ANALISIS WHERE id_parametro = ?"
        cursor.execute(query, (id_parametro,))
        row = cursor.fetchone()

    if row:
        return dict(row)
    return None


def update_parameter(
    id_parametro: int,
    id_inspeccion: int,
    id_equipo_laboratorio: int,
    parametro_analizado: str,
    valor: float | None,
) -> int:
    """
    Actualiza la información de un parámetro de análisis en la base de datos.

    Parámetros:
    - id_parametro (int): ID del parámetro a actualizar.
    - id_inspeccion (int): Nuevo ID de la inspección asociada.
    - id_equipo_laboratorio (int): Nuevo ID del equipo de laboratorio asociado.
    - parametro_analizado (str): Nuevo nombre del parámetro analizado.
    - valor (float | None): Nuevo valor del parámetro analizado.

    Retorna:
    - int: Número de filas afectadas (1 si se actualizó, 0 si no se encontró el parámetro).
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        query = """
            UPDATE PARAMETRO_ANALISIS
            SET id_inspeccion = ?, id_equipo_laboratorio = ?, parametro_analizado = ?, valor = ?
            WHERE id_parametro = ?
        """
        cursor.execute(query, (
            id_inspeccion,
            id_equipo_laboratorio,
            parametro_analizado,
            valor,
            id_parametro
        ))
        affected_rows = cursor.rowcount

    return affected_rows


def delete_parameter(id_parametro: int) -> int:
    """
    Elimina un parámetro de análisis de la base de datos.

    Parámetros:
    - id_parametro (int): ID del parámetro a eliminar.

    Retorna:
    - int: Número de filas afectadas (1 si el parámetro fue eliminado, 0 si no existía).
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        query = "DELETE FROM PARAMETRO_ANALISIS WHERE id_parametro = ?"
        cursor.execute(query, (id_parametro,))
        affected_rows = cursor.rowcount

    return affected_rows


def list_parameters() -> list:
    """
    Obtiene la lista de todos los parámetros analizados en la base de datos.

    Retorna:
    - list: Lista de diccionarios, donde cada diccionario representa un parámetro analizado.
    - Lista vacía si no hay parámetros en la base de datos.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM PARAMETRO_ANALISIS"
        cursor.execute(query)
        rows = cursor.fetchall()

    return [dict(row) for row in rows]
