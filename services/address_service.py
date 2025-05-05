"""
Servicio de Direcciones del Cliente
-----------------------------------

Proporciona operaciones CRUD para la tabla DIRECCION_CLIENTE.
Todas las funciones utilizan el helper `db_connection()` (definido en db.py)
como context manager para manejar la conexión y commit/rollback automáticos.

Funciones disponibles
~~~~~~~~~~~~~~~~~~~~~
- list_addresses(id_cliente):   Lista todas las direcciones de un cliente.
- get_address(id_direccion):    Devuelve una sola dirección por su id.
- create_address(...):          Inserta una nueva dirección y regresa su id.
- update_address(...):          Actualiza los datos de una dirección existente.
- delete_address(id_direccion): Elimina la dirección (DELETE físico).

Cada función lanza excepciones estándar de sqlite3 (o del driver que uses)
cuando ocurre algún error de integridad o conexión, por lo que el código que
las invoque deberá capturarlas y reaccionar adecuadamente (flash, logging, etc.).
"""

from db import db_connection  # type: ignore
from typing import Any, Dict, List, Optional

__all__ = [
    "list_addresses",
    "get_address",
    "create_address",
    "update_address",
    "delete_address",
]


def _row_to_dict(cursor, row) -> Dict[str, Any]:
    """Convierte una tupla devuelta por cursor.fetchall() en un dict
    usando los nombres de columna del cursor.
    """
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


# ---------------------------------------------------------------------------
# LECTURA
# ---------------------------------------------------------------------------

def list_addresses(id_cliente: int) -> List[Dict[str, Any]]:
    """Devuelve todas las direcciones asociadas a *id_cliente* ordenadas por id."""
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id_direccion, id_cliente, calle, num_exterior, num_interior,
                   codigo_postal, delegacion, estado
            FROM DIRECCION_CLIENTE
            WHERE id_cliente = ?
            ORDER BY id_direccion;
            """,
            (id_cliente,),
        )
        rows = cursor.fetchall()
        return [_row_to_dict(cursor, r) for r in rows]


def get_address(id_direccion: int) -> Optional[Dict[str, Any]]:
    """Devuelve un dict con la dirección indicada o **None** si no existe."""
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id_direccion, id_cliente, calle, num_exterior, num_interior,
                   codigo_postal, delegacion, estado
            FROM DIRECCION_CLIENTE
            WHERE id_direccion = ?;
            """,
            (id_direccion,),
        )
        row = cursor.fetchone()
        return _row_to_dict(cursor, row) if row else None


# ---------------------------------------------------------------------------
# ESCRITURA
# ---------------------------------------------------------------------------

def create_address(
    id_cliente: int,
    calle: str,
    num_exterior: str | None,
    num_interior: str | None,
    codigo_postal: str,
    delegacion: str,
    estado: str,
) -> int:
    """Crea una nueva dirección y devuelve el *id_direccion* generado."""
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO DIRECCION_CLIENTE (
                id_cliente, calle, num_exterior, num_interior,
                codigo_postal, delegacion, estado
            ) VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (
                id_cliente,
                calle.strip(),
                (num_exterior or "").strip(),
                (num_interior or "").strip(),
                codigo_postal.strip(),
                delegacion.strip(),
                estado.strip(),
            ),
        )
        return cursor.lastrowid  # type: ignore


def update_address(
    id_direccion: int,
    calle: str,
    num_exterior: str | None,
    num_interior: str | None,
    codigo_postal: str,
    delegacion: str,
    estado: str,
) -> int:
    """Actualiza la dirección indicada. Devuelve el número de filas afectadas (0 ó 1)."""
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE DIRECCION_CLIENTE SET
                calle          = ?,
                num_exterior   = ?,
                num_interior   = ?,
                codigo_postal  = ?,
                delegacion     = ?,
                estado         = ?
            WHERE id_direccion = ?;
            """,
            (
                calle.strip(),
                (num_exterior or "").strip(),
                (num_interior or "").strip(),
                codigo_postal.strip(),
                delegacion.strip(),
                estado.strip(),
                id_direccion,
            ),
        )
        return cursor.rowcount  # type: ignore


def delete_address(id_direccion: int) -> int:
    """Elimina la dirección. Devuelve el número de filas afectadas (0 ó 1)."""
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM DIRECCION_CLIENTE WHERE id_direccion = ?;",
            (id_direccion,),
        )
        return cursor.rowcount  # type: ignore
