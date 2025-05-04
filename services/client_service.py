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


def _build_config_json(use_custom: bool, form: dict, client_id: int) -> str:
    params = {}
    if not use_custom:
        path_default = os.path.join(
            os.path.dirname(__file__), "parametros_default.json"
        )
        with open(path_default, "r", encoding="utf-8") as f:
            params = json.load(f)
    else:
        for key, val in form.items():
            if key.startswith(("alveo_", "fari_")) and val.strip():
                equipo, param, bound = key.split("_", 2)
                k = f"{equipo}_{param}"
                params.setdefault(k, {})[bound] = float(val)
    params["id_cliente"] = client_id
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
        configuracion_json = _build_config_json(use_custom_params, form_data, client_id)
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


# ----------------------------------------------
# Funciones para gestionar archivos de configuración
# ----------------------------------------------

# Directorio donde se encuentra este archivo (services)
CONFIG_DIR = os.path.dirname(__file__)

# Ruta completa al archivo de parámetros por defecto
DEFAULT_CONFIG_FILE = os.path.join(CONFIG_DIR, "parametros_default.json")


def create_default_config_file():
    """
    Crea el archivo parametros_default.json con los parámetros por defecto.
    Esta función se debe llamar una sola vez al iniciar el programa para crear el archivo default.

    Parámetros:
      - client_id (int): ID del cliente.
      - config (dict): Diccionario con los parámetros de configuración del cliente.
        Se espera que siga el siguiente formato:
           {
             "farinografo": {
                "absorcion_de_agua": {"inf": <valor>, "sup": <valor>},
                "tiempo_de_desarrollo": {"inf": <valor>, "sup": <valor>},
                "estabilidad": {"inf": <valor>, "sup": <valor>},
                "indice_de_tolerancia": {"inf": <valor>, "sup": <valor>}
             },
             "alveografo": {
                "W": {"inf": <valor>, "sup": <valor>},
                "P": {"inf": <valor>, "sup": <valor>},
                "L": {"inf": <valor>, "sup": <valor>},
                "relacion_P_L": {"inf": <valor>, "sup": <valor>}
             }
           }
    """
    default_params = {
        "farinografo": {
            "absorcion_de_agua": {"inf": 55, "sup": 65},
            "tiempo_de_desarrollo": {"inf": 1.5, "sup": 3.0},
            "estabilidad": {"inf": 5, "sup": 10},
            "indice_de_tolerancia": {"inf": 70, "sup": 110},
        },
        "alveografo": {
            "W": {"inf": 180, "sup": 350},
            "P": {"inf": 70, "sup": 130},
            "L": {"inf": 90, "sup": 140},
            "relacion_P_L": {"inf": 0.5, "sup": 1.0},
        },
    }
    with open(DEFAULT_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(default_params, f, indent=4)


def save_client_specific_config(client_id: int, config: dict):
    """
    Guarda la configuración personalizada para un cliente en un archivo JSON.

    Parámetros:
      - client_id (int): ID del cliente.
      - config (dict): Diccionario con los parámetros de configuración del cliente.
        Se espera que siga el siguiente formato:
           {
             "farinografo": {
                "absorcion_de_agua": {"inf": <valor>, "sup": <valor>},
                "tiempo_de_desarrollo": {"inf": <valor>, "sup": <valor>},
                "estabilidad": {"inf": <valor>, "sup": <valor>},
                "indice_de_tolerancia": {"inf": <valor>, "sup": <valor>}
             },
             "alveografo": {
                "W": {"inf": <valor>, "sup": <valor>},
                "P": {"inf": <valor>, "sup": <valor>},
                "L": {"inf": <valor>, "sup": <valor>},
                "relacion_P_L": {"inf": <valor>, "sup": <valor>}
             }
           }

    Se crea o sobrescribe el archivo {id_cliente}.json en el mismo directorio.
    """

    file_path = os.path.join(CONFIG_DIR, f"{client_id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

    """
    Referencias parametros (tomar 2 de las siguientes) 
    American Association of Cereal Chemists International. (2010). AACC International Approved Methods of Analysis. AACC International. Recuperado de http://www.aaccnet.org/

    Corsini, D., & Gujral, H. S. (2005). Calidad y evaluación de la harina de trigo. Journal of Cereal Science, 41(2), 128–137.

    Rodríguez, F. G., Martínez, A., & López, G. (2012). Normas internacionales para la calidad de la harina de trigo. Revista de Tecnología de Cereales, 15(3), 45–57.
    
    Molinos del Norte. (2020). Ficha técnica: Análisis reológico de la harina de trigo. Recuperado de http://www.molinosdelnorte.com/analisis_reologico

    Organización de las Naciones Unidas para la Agricultura y la Alimentación. (2019). Normas internacionales para la harina de trigo: Métodos reológicos. FAO. Recuperado de http://www.fao.org/standards

    Pérez, M. (2021). Evaluación reológica de la harina de trigo: Un estudio aplicado [Tesis de maestría, Universidad Nacional Agraria La Molina]. Repositorio Digital UNALM.
    
    """
