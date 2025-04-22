"""
Servicio de Equipos

Este servicio proporciona operaciones CRUD para gestionar registros de equipos en la base de datos.
Permite recuperar todos los equipos, obtener un equipo por ID, actualizar su información, eliminarlo,
así como marcar un equipo como inactivo (dar de baja) asignándole una causa de baja.
"""

from db import db_connection


def create_equipment(
    tipo: str,
    clave: str | None,
    marca: str | None,
    modelo: str | None,
    serie: str | None,
    descripcion_larga: str | None,
    descripcion_corta: str | None,
    proveedor: str | None,
    fecha_adquisicion: str | None,
    garantia: str | None,
    vigencia_garantia: str | None,
    ubicacion: str | None,
    encargado: int | None,
    estado: str,
    causa_baja: str | None,
) -> int | None:
    """
    Crea un nuevo equipo en la base de datos.

    Parámetros:
    - tipo (str): Tipo de equipo.
    - clave (str | None): Clave única del equipo (puede ser None si no aplica).
    - marca (str | None): Marca del equipo.
    - modelo (str | None): Modelo del equipo.
    - serie (str | None): Número de serie del equipo.
    - descripcion_larga (str | None): Descripción detallada del equipo.
    - descripcion_corta (str | None): Descripción corta o alias del equipo.
    - proveedor (str | None): Nombre del proveedor del equipo.
    - fecha_adquisicion (str | None): Fecha de adquisición del equipo.
    - garantia (str | None): Información de la garantía.
    - vigencia_garantia (str | None): Fecha de vigencia de la garantía.
    - ubicacion (str | None): Ubicación del equipo dentro del laboratorio.
    - encargado (int | None): ID del usuario responsable del equipo.
    - estado (str): Estado actual del equipo (e.g., "Operativo", "Mantenimiento", "Inactivo").
    - causa_baja (str | None): Motivo de baja del equipo (si aplica).

    Retorna:
    - int: ID del equipo creado, o None si no se pudo crear.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        query = """
            INSERT INTO EQUIPO_LABORATORIO (
                tipo, clave, marca, modelo, serie,
                descripcion_larga, descripcion_corta, proveedor,
                fecha_adquisicion, garantia, vigencia_garantia,
                ubicacion, encargado, estado, causa_baja
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (
            tipo,
            clave,
            marca,
            modelo,
            serie,
            descripcion_larga,
            descripcion_corta,
            proveedor,
            fecha_adquisicion,
            garantia,
            vigencia_garantia,
            ubicacion,
            encargado,
            estado,
            causa_baja
        ))
        equipment_id = cursor.lastrowid

    if equipment_id:
        return equipment_id
    return None


def get_equipment(id_equipo: int) -> dict | None:
    """
    Obtiene un equipo por su ID.

    Parámetros:
    - id_equipo (int): ID del equipo a buscar.

    Retorna:
    - dict: Información del equipo si existe.
    - None: Si el equipo no se encuentra en la base de datos.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM EQUIPO_LABORATORIO WHERE id_equipo = ?"
        cursor.execute(query, (id_equipo,))
        row = cursor.fetchone()

    if row:
        return dict(row)
    return None


def update_equipment(
    id_equipo: int,
    tipo: str,
    clave: str | None,
    marca: str | None,
    modelo: str | None,
    serie: str | None,
    descripcion_larga: str | None,
    descripcion_corta: str | None,
    proveedor: str | None,
    fecha_adquisicion: str | None,
    garantia: str | None,
    vigencia_garantia: str | None,
    ubicacion: str | None,
    encargado: int | None,
    estado: str,
    causa_baja: str | None,
) -> int:
    """
    Actualiza la información de un equipo en la base de datos.

    Parámetros:
    - id_equipo (int): ID del equipo a actualizar.
    - tipo (str): Nuevo tipo de equipo.
    - clave (str | None): Nueva clave única del equipo.
    - marca (str | None): Nueva marca del equipo.
    - modelo (str | None): Nuevo modelo del equipo.
    - serie (str | None): Nuevo número de serie.
    - descripcion_larga (str | None): Nueva descripción larga.
    - descripcion_corta (str | None): Nueva descripción corta.
    - proveedor (str | None): Nuevo proveedor del equipo.
    - fecha_adquisicion (str | None): Nueva fecha de adquisición.
    - garantia (str | None): Nueva información de la garantía.
    - vigencia_garantia (str | None): Nueva vigencia de la garantía.
    - ubicacion (str | None): Nueva ubicación del equipo.
    - encargado (int | None): Nuevo ID del usuario encargado del equipo.
    - estado (str): Nuevo estado del equipo.
    - causa_baja (str | None): Nueva causa de baja del equipo (si aplica).

    Retorna:
    - int: Número de filas afectadas (1 si se actualizó, 0 si no se encontró el equipo).
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        query = """
            UPDATE EQUIPO_LABORATORIO
            SET tipo = ?, clave = ?, marca = ?, modelo = ?, serie = ?,
                descripcion_larga = ?, descripcion_corta = ?, proveedor = ?,
                fecha_adquisicion = ?, garantia = ?, vigencia_garantia = ?,
                ubicacion = ?, encargado = ?, estado = ?, causa_baja = ?
            WHERE id_equipo = ?
        """
        cursor.execute(query, (
            tipo,
            clave,
            marca,
            modelo,
            serie,
            descripcion_larga,
            descripcion_corta,
            proveedor,
            fecha_adquisicion,
            garantia,
            vigencia_garantia,
            ubicacion,
            encargado,
            estado,
            causa_baja,
            id_equipo
        ))
        affected_rows = cursor.rowcount

    return affected_rows


def delete_equipment(id_equipo: int) -> int:
    """
    Elimina un equipo de la base de datos.

    Parámetros:
    - id_equipo (int): ID del equipo a eliminar.

    Retorna:
    - int: Número de filas afectadas (1 si el equipo fue eliminado, 0 si no existía).
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        query = "DELETE FROM EQUIPO_LABORATORIO WHERE id_equipo = ?"
        cursor.execute(query, (id_equipo,))
        affected_rows = cursor.rowcount

    return affected_rows


def list_equipment() -> list:
    """
    Obtiene la lista de todos los equipos en la base de datos.

    Retorna:
    - list: Lista de diccionarios, donde cada diccionario representa un equipo.
    - Lista vacía si no hay equipos en la base de datos.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM EQUIPO_LABORATORIO"
        cursor.execute(query)
        rows = cursor.fetchall()

    return [dict(row) for row in rows]


def deactivate_equipment(id_equipo: int, causa_baja: str) -> int:
    """
    Marca un equipo como inactivo en la base de datos y almacena la razón de baja.

    Parámetros:
    - id_equipo (int): ID del equipo a desactivar.
    - causa_baja (str): Razón de la desactivación.

    Retorna:
    - int: Número de filas afectadas (1 si se desactivó, 0 si el equipo no existía).
    """
    # Actualizamos el estado a "Inactive" y asignamos la causa de baja
    with db_connection() as conn:
        cursor = conn.cursor()
        query = """
            UPDATE EQUIPO_LABORATORIO 
            SET estado = 'Inactive', causa_baja = ? 
            WHERE id_equipo = ?
        """
        cursor.execute(query, (causa_baja, id_equipo))
        affected_rows = cursor.rowcount

    return affected_rows
