"""
Servicio de Direcciones

Administra operaciones CRUD para las direcciones, incluyendo su vinculación con los registros de clientes.
Permite recuperar todos los IDs de direcciones y obtener detalles de direcciones en función de parámetros específicos.
"""

from db import db_connection


def create_address(
    id_cliente: int,
    calle: str,
    num_exterior: str,
    num_interior: str | None,
    codigo_postal: str,
    delegacion: str,
    estado: str,
) -> int:
    """
    Crea una nueva dirección asociada a un cliente en la base de datos.

    Parámetros:
    - id_cliente (int): ID del cliente al que pertenece la dirección.
    - calle (str): Nombre de la calle.
    - num_exterior (str): Número exterior de la dirección.
    - num_interior (str | None): Número interior (puede ser `None` si no aplica).
    - codigo_postal (str): Código postal de la dirección.
    - delegacion (str): Delegación o municipio de la dirección.
    - estado (str): Estado en el que se encuentra la dirección.

    Retorna:
    - int: ID de la dirección creada.
    """
    pass


def get_address(id_direccion: int) -> dict | None:
    """
    Obtiene una dirección por su ID.

    Parámetros:
    - id_direccion (int): ID de la dirección a buscar.

    Retorna:
    - dict: Información de la dirección si existe.
    - None: Si la dirección no se encuentra en la base de datos.
    """
    pass


def update_address(
    id_direccion: int,
    id_cliente: int,
    calle: str,
    num_exterior: str,
    num_interior: str | None,
    codigo_postal: str,
    delegacion: str,
    estado: str,
) -> int:
    """
    Actualiza la información de una dirección en la base de datos.

    Parámetros:
    - id_direccion (int): ID de la dirección a actualizar.
    - id_cliente (int): ID del cliente al que pertenece la dirección.
    - calle (str): Nueva calle de la dirección.
    - num_exterior (str): Nuevo número exterior.
    - num_interior (str | None): Nuevo número interior (puede ser `None` si no aplica).
    - codigo_postal (str): Nuevo código postal.
    - delegacion (str): Nueva delegación o municipio.
    - estado (str): Nuevo estado.

    Retorna:
    - int: Número de filas afectadas (1 si se actualizó, 0 si no se encontró la dirección).
    """
    pass


def delete_address(id_direccion: int) -> int:
    """
    Elimina una dirección de la base de datos.

    Parámetros:
    - id_direccion (int): ID de la dirección a eliminar.

    Retorna:
    - int: Número de filas afectadas (1 si la dirección fue eliminada, 0 si no existía).
    """
    pass


def list_addresses() -> list:
    """
    Obtiene la lista de todas las direcciones en la base de datos.

    Retorna:
    - list: Lista de diccionarios, donde cada diccionario representa una dirección.
    - Lista vacía si no hay direcciones en la base de datos.
    """
    pass
