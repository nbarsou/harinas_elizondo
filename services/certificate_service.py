"""
Servicio de Certificados

Proporciona operaciones CRUD para la gestión de registros de certificación en el sistema.
Este servicio permite recuperar todos los IDs de certificados y obtener información según parámetros específicos.
"""

from db import db_connection
import sqlite3



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
