"""
Servicio de Certificados

Proporciona operaciones CRUD para la gestión de registros de certificación en el sistema.
Este servicio permite recuperar todos los IDs de certificados y obtener información según parámetros específicos.
"""

from db import db_connection
import sqlite3
import os, json   # ← añade esto

# --------------------------------------------------------------------
#  Helpers para comparar resultados vs. especificaciones de cliente
# --------------------------------------------------------------------
SPEC_PATH = os.path.join(os.path.dirname(__file__), "specs.json")
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "parametros_default.json")

def _load_refs_json(client_id: int) -> dict:
    """Load client-specific or default parameters"""
    try:
        # First try to load client-specific parameters from specs.json
        with open(SPEC_PATH, "r", encoding="utf-8") as fh:
            specs = json.load(fh)
        
        client_specs = specs.get(str(client_id), {})
        
        # If no client-specific parameters found, load defaults
        if not client_specs:
            with open(DEFAULT_PATH, "r", encoding="utf-8") as f:
                defaults = json.load(f)
            return defaults
        
        return client_specs
    except Exception as e:
        print(f"Error loading references: {str(e)}")
        return {}

def _detect_devs(resultados: dict, refs: dict) -> list:
    """Detect deviations between results and reference values"""
    devs = []

    print(f"DEBUG - Resultados: {resultados}")
    print(f"DEBUG - Referencias: {refs}")

    # Known parameters mapped to their category
    known_params = {
        "W": "alveografo",
        "P": "alveografo",
        "L": "alveografo",
        "relacion_P_L": "alveografo",
        "absorcion_de_agua": "farinografo",
        "tiempo_de_desarrollo": "farinografo",
        "estabilidad": "farinografo",
        "indice_de_tolerancia": "farinografo"
    }

    # Flatten if wrapped inside a category key (e.g., {'farinografo': {...}})
    if any(k in resultados for k in ["farinografo", "alveografo"]):
        flat_resultados = {}
        for cat in ["farinografo", "alveografo"]:
            if cat in resultados and isinstance(resultados[cat], dict):
                flat_resultados.update(resultados[cat])
        resultados = flat_resultados

    print("DEBUG - Normalized resultados:", resultados)

    for param_name, category in known_params.items():
        if param_name not in resultados:
            continue

        try:
            param_value = float(resultados[param_name])
        except (ValueError, TypeError):
            print(f"DEBUG - Skipping invalid value for {param_name}: {resultados[param_name]}")
            continue

        ref = refs.get(category, {}).get(param_name, {})
        min_val = ref.get("inf")
        max_val = ref.get("sup")

        print(f"DEBUG - Checking {param_name}: value={param_value}, min={min_val}, max={max_val}")

        if min_val is not None and param_value < min_val:
            devs.append(f"{param_name} bajo ({param_value} < {min_val})")
        elif max_val is not None and param_value > max_val:
            devs.append(f"{param_name} alto ({param_value} > {max_val})")

    print(f"DEBUG - Detected deviations: {devs}")
    return devs

def build_desviaciones(id_cliente: int, resultados: dict, user_text: str) -> tuple:
    """Build deviations list based on client parameters"""
    print(f"Cliente: {id_cliente}")
    print(f"Resultados crudos: {resultados}")
    try:
        # Parse resultados if it's a string
        if isinstance(resultados, str):
            try:
                resultados = json.loads(resultados)
            except json.JSONDecodeError:
                print("DEBUG - JSON decode error on resultados")
                resultados = {}
        
        # Handle null/None case
        if resultados is None:
            resultados = {}
            
        # Get reference parameters for this client
        refs = _load_refs_json(id_cliente)
        
        # Detect deviations
        auto_devs = _detect_devs(resultados, refs)
        
        if auto_devs:
            return (True, ", ".join(auto_devs))
        return (False, user_text.strip())
    except Exception as e:
        print(f"DEBUG - Error in build_desviaciones: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return original text if there's an error
        return (False, user_text.strip())


def create_certificate(
    id_cliente: int,
    id_inspeccion: int,
    secuencia_inspeccion: str,
    orden_compra: str,
    cantidad_solicitada: float,
    cantidad_entregada: float,
    numero_factura: str,
    fecha_envio: str,
    fecha_caducidad: str,
    resultados_analisis: str,
    compara_referencias: str,
    desviaciones: str,
    destinatario_correo: str,
) -> int:
    """
    Inserta un nuevo registro de certificado de calidad en la base de datos.

    Retorna:
    - ID del nuevo certificado insertado.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO CERTIFICADO_CALIDAD (
                id_cliente,
                id_inspeccion,
                secuencia_inspeccion,
                orden_compra,
                cantidad_solicitada,
                cantidad_entregada,
                numero_factura,
                fecha_envio,
                fecha_caducidad,
                resultados_analisis,
                compara_referencias,
                desviaciones,
                destinatario_correo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_cliente,
            id_inspeccion,
            secuencia_inspeccion,
            orden_compra,
            cantidad_solicitada,
            cantidad_entregada,
            numero_factura,
            fecha_envio,
            fecha_caducidad,
            resultados_analisis,
            compara_referencias,
            desviaciones,
            destinatario_correo
        ))
        return cursor.lastrowid


def get_certificate(id_certificado: int) -> dict | None:
    """
    Recupera un certificado de calidad por su ID.

    Retorna:
    - dict con los campos del certificado si existe.
    - None si no se encuentra.
    """
    with db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT *
            FROM CERTIFICADO_CALIDAD
            WHERE id_certificado = ?
        """, (id_certificado,))
        row = cursor.fetchone()

    if row:
        return dict(row)
    return None

def update_certificate(
    id_certificado: int,
    id_cliente: int,
    id_inspeccion: int,
    secuencia_inspeccion: str,
    orden_compra: str,
    cantidad_solicitada: float,
    cantidad_entregada: float,
    numero_factura: str,
    fecha_envio: str,
    fecha_caducidad: str,
    resultados_analisis: str,
    compara_referencias: str,
    desviaciones: str,
    destinatario_correo: str,
) -> int:
    """
    Actualiza un certificado de calidad existente en la base de datos.

    Retorna:
    - Número de filas afectadas (1 si se actualizó, 0 si no se encontró).
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE CERTIFICADO_CALIDAD
            SET id_cliente = ?,
                id_inspeccion = ?,
                secuencia_inspeccion = ?,
                orden_compra = ?,
                cantidad_solicitada = ?,
                cantidad_entregada = ?,
                numero_factura = ?,
                fecha_envio = ?,
                fecha_caducidad = ?,
                resultados_analisis = ?,
                compara_referencias = ?,
                desviaciones = ?,
                destinatario_correo = ?
            WHERE id_certificado = ?
        """, (
            id_cliente,
            id_inspeccion,
            secuencia_inspeccion,
            orden_compra,
            cantidad_solicitada,
            cantidad_entregada,
            numero_factura,
            fecha_envio,
            fecha_caducidad,
            resultados_analisis,
            compara_referencias,
            desviaciones,
            destinatario_correo,
            id_certificado
        ))
        return cursor.rowcount


def delete_certificate(id_certificado: int) -> int:
    """
    Elimina un certificado de calidad por su ID.

    Retorna:
    - Número de filas afectadas (1 si se eliminó, 0 si no existía).
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM CERTIFICADO_CALIDAD
            WHERE id_certificado = ?
        """, (id_certificado,))
        return cursor.rowcount


def list_certificates() -> list[dict]:
    """
    Devuelve todos los certificados registrados en la base de datos.

    Retorna:
    - Lista de diccionarios, cada uno representando un certificado.
    - Lista vacía si no hay certificados.
    """
    with db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT *
            FROM CERTIFICADO_CALIDAD
            ORDER BY id_certificado DESC
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]