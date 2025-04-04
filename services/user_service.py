"""
Servicio de Usuarios

Maneja las operaciones de base de datos relacionadas con los usuarios, incluyendo la creación,
lectura, actualización y eliminación de registros.
Este servicio también permite recuperar todos los IDs de usuarios o buscar usuarios con parámetros específicos.
"""
from db import db_connection


def create_user(mail: str, contrasena: str, rol: str, nombre: str) -> int | None:
    """
    Crea un nuevo usuario en la base de datos.

    Parámetros:
    - mail (str): Correo electrónico único del usuario.
    - contrasena (str): Contraseña del usuario (debería estar hasheada en producción).
    - rol (str): Rol del usuario (e.g., "admin", "user").
    - nombre (str): Nombre del usuario.

    Retorna:
    - int: ID del usuario creado.

    Excepciones:
    - Puede generar una excepción si el correo electrónico ya existe en la base de datos.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        query = """
            INSERT INTO USUARIO (mail, contrasena, rol, nombre)
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (mail, contrasena, rol, nombre))
        user_id = cursor.lastrowid
        if user_id:
            return user_id
        return None


def get_user(user_id: int) -> dict | None:
    """
    Obtiene un usuario por su ID.

    Parámetros:
    - user_id (int): ID del usuario a buscar.

    Retorna:
    - dict: Información del usuario si existe.
    - None: Si el usuario no se encuentra en la base de datos.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT id_usuario, mail, contrasena, rol, nombre
            FROM USUARIO
            WHERE id_usuario = ?
        """
        cursor.execute(query, (user_id,))
        row = cursor.fetchone()

    if row:
        return {
            "id_usuario": row["id_usuario"],
            "mail": row["mail"],
            "contrasena": row["contrasena"],
            "rol": row["rol"],
            "nombre": row["nombre"],
        }
    return None


# TODO: Si no se actualizan filas, regresa MySQL 0?
def update_user(user_id: int, mail: str, contrasena: str, rol: str, nombre: str) -> int:
    """
    Actualiza la información de un usuario en la base de datos.

    Parámetros:
    - user_id (int): ID del usuario a actualizar.
    - mail (str): Nuevo correo electrónico del usuario.
    - contrasena (str): Nueva contraseña del usuario (debería estar hasheada en producción).
    - rol (str): Nuevo rol del usuario.
    - nombre (str): Nuevo nombre del usuario.

    Retorna:
    - int: Número de filas afectadas (1 si la actualización fue exitosa, 0 si no se encontró el usuario).

    Excepciones:
    - Puede generar una excepción si el correo electrónico ya existe en otro usuario.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        query = """
            UPDATE USUARIO
            SET mail = ?, contrasena = ?, rol = ?, nombre = ?
            WHERE id_usuario = ?
        """
        cursor.execute(query, (mail, contrasena, rol, nombre, user_id))
        affected_rows = cursor.rowcount
    return affected_rows


def delete_user(user_id: int) -> int:
    """
    Elimina un usuario de la base de datos.

    Parámetros:
    - user_id (int): ID del usuario a eliminar.

    Retorna:
    - int: Número de filas afectadas (1 si el usuario fue eliminado, 0 si el usuario no existía).
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        query = """
            DELETE FROM USUARIO
            WHERE id_usuario = ?
        """
        cursor.execute(query, (user_id,))
        affected_rows = cursor.rowcount
    return affected_rows


def list_users() -> list:
    """
    Obtiene la lista de todos los usuarios en la base de datos.

    Retorna:
    - list: Lista de diccionarios, donde cada diccionario representa un usuario.
    - Lista vacía si no hay usuarios en la base de datos.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT id_usuario, mail, contrasena, rol, nombre
            FROM USUARIO
        """
        cursor.execute(query)
        rows = cursor.fetchall()

    return [
        {
            "id_usuario": row["id_usuario"],
            "mail": row["mail"],
            "contrasena": row["contrasena"],
            "rol": row["rol"],
            "nombre": row["nombre"],
        }
        for row in rows
    ]
