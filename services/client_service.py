"""
Servicio de Clientes

Proporciona operaciones CRUD para gestionar registros de clientes en el sistema.
Este servicio permite recuperar todos los IDs de clientes, obtener registros con parámetros específicos
y generar salidas en formato JSON para ciertos datos de clientes.
También incluye funcionalidades para desactivar o eliminar clientes según reglas personalizadas.
"""

from db import db_connection
import os
import json


def build_config_json(use_custom: bool, form: dict, client_id: int) -> str:
    # Si no usa parámetros a la carta, cargo los defaults (ya vienen anidados)
    if not use_custom:
        path_default = os.path.join(
            os.path.dirname(__file__), "parametros_default.json"
        )
        with open(path_default, "r", encoding="utf-8") as f:
            params = json.load(f)

    # Si usa parámetros personalizados, construyo dos dicts separados
    else:
        alveo = {}
        fari = {}

        for key, val in form.items():
            val = val.strip()
            if not val:
                continue

            parts = key.split("_")
            equipo = parts[0]  # "alveo" o "fari"
            bound = parts[-1]  # "inf" o "sup"
            # todo lo que queda en medio es el nombre del parámetro
            param = "_".join(parts[1:-1])

            if equipo == "alveo":
                # ejemplo: param == "W" o "relacion_P_L"
                alveo.setdefault(param, {})[bound] = float(val)
            elif equipo == "fari":
                # ejemplo: param == "absorcion_de_agua"
                fari.setdefault(param, {})[bound] = float(val)

        params = {"alveografo": alveo, "farinografo": fari}

    # Siempre incluyo el id del cliente
    params["id_cliente"] = client_id  # type: ignore
    return json.dumps(params, ensure_ascii=False)


def create_client(
    nombre: str,
    rfc: str,
    nombre_contacto: str,
    correo_contacto: str,
    requiere_certificado: bool,
    activo: bool,
    contrasena: str,
    motivo_baja: str | None,
    use_custom_params: bool,
    form_data: dict,
) -> int | None:
    """
    Crea un nuevo cliente en la base de datos.

    Parámetros:
    - nombre (str): Nombre de la empresa o cliente.
    - rfc (str): Registro Federal de Contribuyentes del cliente.
    - nombre_contacto (str): Nombre del contacto principal del cliente.
    - correo_contacto (str): Correo electrónico del contacto.
    - requiere_certificado (bool): Indica si el cliente necesita certificado (1 = sí, 0 = no).
    - activo (bool): Indica si el cliente está activo (1) o inactivo (0).
    - contrasena (str): Contraseña del cliente (debería estar hasheada en producción).
    - motivo_baja (str | None): Razón de baja si el cliente ha sido inactivado.
    - use_custom_params (bool): Indica si se usan parámetros personalizados.
    - form_data (dict): Datos crudos del formulario para construir configuracion_json.

    Retorna:
    - int: ID del cliente creado, o None si no se pudo crear.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO CLIENTE(
                nombre, rfc, nombre_contacto, correo_contacto, 
                requiere_certificado, activo, contrasena, motivo_baja, configuracion_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                nombre,
                rfc,
                nombre_contacto,
                correo_contacto,
                1 if requiere_certificado else 0,
                1 if activo else 0,
                contrasena,
                motivo_baja,
                "{}",  # JSON vacío provisional
            ),
        )
        client_id = cursor.lastrowid

        if client_id is None:
            conn.rollback()
            return None

        # Construir y actualizar JSON con ID incluido
        configuracion_json = build_config_json(use_custom_params, form_data, client_id)
        cursor.execute(
            "UPDATE CLIENTE SET configuracion_json = ? WHERE id_cliente = ?",
            (configuracion_json, client_id),
        )
        conn.commit()

    return client_id


def get_client(client_id: int) -> dict | None:
    """
    Obtiene un cliente por su ID.

    Parámetros:
    - client_id (int): ID del cliente a buscar.

    Retorna:
    - dict: Información del cliente si existe.
    - None: Si el cliente no se encuentra en la base de datos.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM CLIENTE WHERE id_cliente = ?"
        cursor.execute(query, (client_id,))
        row = cursor.fetchone()

    if row:
        return dict(row)
    return None


def update_client(
    client_id: int,
    nombre: str,
    rfc: str,
    nombre_contacto: str,
    correo_contacto: str,
    requiere_certificado: bool,
    activo: bool,
    motivo_baja: str | None,
    configuracion_json: str,
) -> int:
    """
    Actualiza la información de un cliente en la base de datos.

    Parámetros:
    - client_id (int): ID del cliente a actualizar.
    - nombre (str): Nuevo nombre del cliente.
    - rfc (str): Nuevo RFC del cliente.
    - nombre_contacto (str): Nuevo nombre del contacto.
    - correo_contacto (str): Nuevo correo del contacto.
    - requiere_certificado (bool): Indica si el cliente requiere certificado.
    - activo (bool): Indica si el cliente está activo o inactivo.
    - motivo_baja (str | None): Razón de baja si aplica.
    - configuracion_json (str): Nueva configuración en formato JSON.

    Retorna:
    - int: Número de filas afectadas (1 si se actualizó, 0 si no se encontró el cliente).
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        query = """
            UPDATE CLIENTE 
            SET nombre = ?, 
                rfc = ?, 
                nombre_contacto = ?, 
                correo_contacto = ?,
                requiere_certificado = ?, 
                activo = ?, 
                motivo_baja = ?, 
                configuracion_json = ?
            WHERE id_cliente = ?
        """
        cursor.execute(
            query,
            (
                nombre,
                rfc,
                nombre_contacto,
                correo_contacto,
                1 if requiere_certificado else 0,
                1 if activo else 0,
                motivo_baja,
                configuracion_json,
                client_id,
            ),
        )
        affected_rows = cursor.rowcount

    return affected_rows


def deactivate_client(client_id: int, motivo_baja: str) -> int:
    """
    Desactiva un cliente en la base de datos y almacena la razón de baja.

    Parámetros:
    - client_id (int): ID del cliente a desactivar.
    - motivo_baja (str): Razón de la desactivación.

    Retorna:
    - int: Número de filas afectadas (1 si se desactivó, 0 si el cliente no existía).
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        query = "UPDATE CLIENTE SET activo = 0, motivo_baja = ? WHERE id_cliente = ?"
        cursor.execute(query, (motivo_baja, client_id))
        affected_rows = cursor.rowcount

    return affected_rows


def delete_client(client_id: int) -> int:
    """
    Elimina un cliente de la base de datos.

    Parámetros:
    - client_id (int): ID del cliente a eliminar.

    Retorna:
    - int: Número de filas afectadas (1 si el cliente fue eliminado, 0 si no existía).
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        query = "DELETE FROM CLIENTE WHERE id_cliente = ?"
        cursor.execute(query, (client_id,))
        affected_rows = cursor.rowcount

    return affected_rows


def list_clients() -> list:
    """
    Obtiene la lista de todos los clientes en la base de datos.

    Retorna:
    - list: Lista de diccionarios, donde cada diccionario representa un cliente.
    - Lista vacía si no hay clientes en la base de datos.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM CLIENTE"
        cursor.execute(query)
        rows = cursor.fetchall()

    return [dict(row) for row in rows]
