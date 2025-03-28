# tests/test_client_service.py
import pytest
from services.client_service import (
    create_client,
    get_client,
    update_client,
    deactivate_client,
    delete_client,
    list_clients,
)


def test_create_client(fresh_db):
    """
    Test creating a new client and verify that it exists in the database.
    """
    client_id = create_client(
        "Empresa S.A.",
        "RFC123456",
        "Juan Pérez",
        "juan@example.com",
        True,
        True,
        "securepass",
        None,
        "{}",
    )
    assert client_id is not None

    # Query database directly
    cursor = fresh_db.cursor()
    cursor.execute("SELECT * FROM CLIENTE WHERE id_cliente = ?", (client_id,))
    row = cursor.fetchone()

    assert row is not None
    assert row["nombre"] == "Empresa S.A."
    assert row["rfc"] == "RFC123456"
    assert row["nombre_contacto"] == "Juan Pérez"
    assert row["correo_contacto"] == "juan@example.com"
    assert row["requiere_certificado"] == 1
    assert row["activo"] == 1


def test_get_client_not_found():
    """
    Test retrieving a client that does not exist.
    """
    client = get_client(9999)  # Nonexistent ID
    assert client is None


def test_update_client(fresh_db):
    """
    Test updating a client's information and verifying the change in the database.
    """
    client_id = create_client(
        "Cliente Viejo",
        "RFC987654",
        "Pedro López",
        "pedro@example.com",
        False,
        True,
        "securepass",
        None,
        "{}",
    )

    affected_rows = update_client(
        client_id,
        "Cliente Nuevo",
        "RFC111111",
        "Luis Gómez",
        "luis@example.com",
        True,
        False,
        None,
        "{}",
    )
    assert affected_rows == 1

    # Verify update in database
    cursor = fresh_db.cursor()
    cursor.execute("SELECT * FROM CLIENTE WHERE id_cliente = ?", (client_id,))
    row = cursor.fetchone()

    assert row["nombre"] == "Cliente Nuevo"
    assert row["rfc"] == "RFC111111"
    assert row["nombre_contacto"] == "Luis Gómez"
    assert row["correo_contacto"] == "luis@example.com"
    assert row["requiere_certificado"] == 1
    assert row["activo"] == 0  # Confirm deactivation


def test_delete_client(fresh_db):
    """
    Test deleting a client and confirm that it no longer exists in the database.
    """
    client_id = create_client(
        "Cliente Eliminado",
        "RFC543210",
        "Ana Torres",
        "ana@example.com",
        False,
        True,
        "securepass",
        None,
        "{}",
    )

    affected_rows = delete_client(client_id)
    assert affected_rows == 1

    # Verify deletion in database
    cursor = fresh_db.cursor()
    cursor.execute("SELECT * FROM CLIENTE WHERE id_cliente = ?", (client_id,))
    row = cursor.fetchone()

    assert row is None  # Client should no longer exist


def test_list_clients(fresh_db):
    """
    Test listing all clients and confirm that database reflects the correct number of clients.
    """
    create_client(
        "Cliente Uno",
        "RFCUNO123",
        "Carlos Pérez",
        "carlos@example.com",
        True,
        True,
        "pass1",
        None,
        "{}",
    )
    create_client(
        "Cliente Dos",
        "RFCDOS456",
        "María López",
        "maria@example.com",
        False,
        True,
        "pass2",
        None,
        "{}",
    )

    clients = list_clients()
    assert len(clients) >= 2  # Check that at least 2 clients exist

    # Verify directly from the database
    cursor = fresh_db.cursor()
    cursor.execute("SELECT COUNT(*) FROM CLIENTE")
    client_count = cursor.fetchone()[0]  # Fetch count

    assert client_count >= 2  # Ensure at least two clients exist in the table


def test_deactivate_client(fresh_db):
    """
    Test deactivating a client and verifying that 'activo' is set to 0 and 'motivo_baja' is stored.
    """
    client_id = create_client(
        "Cliente Inactivo",
        "RFC999",
        "Jose Martinez",
        "jose@example.com",
        True,
        True,
        "pass123",
        None,
        "{}",
    )

    affected_rows = deactivate_client(client_id, "Cliente ya no requiere servicio")
    assert affected_rows == 1

    # Verify in database
    cursor = fresh_db.cursor()
    cursor.execute(
        "SELECT activo, motivo_baja FROM CLIENTE WHERE id_cliente = ?", (client_id,)
    )
    row = cursor.fetchone()

    assert row is not None
    assert row["activo"] == 0
    assert row["motivo_baja"] == "Cliente ya no requiere servicio"
