# tests/test_address_service.py
import pytest
from services.address_service import (
    create_address,
    get_address,
    update_address,
    delete_address,
    list_addresses,
)
from services.client_service import create_client  # Needed to create test clients
from db import db_connection


def test_create_address():
    """
    Test creating a new address and verify that it exists in the database.
    """
    # Create a test client first
    client_id = create_client(
        "Test Client",
        "RFC123",
        "John Doe",
        "johndoe@example.com",
        True,
        True,
        "password",
        None,
        "{}",
    )
    assert client_id is not None

    # Create an address for this client
    address_id = create_address(
        client_id, "Main Street", "123", "Apt 4", "12345", "Central", "Mexico City"
    )
    assert address_id is not None

    # Verify directly from the database
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM DIRECCION_CLIENTE WHERE id_direccion = ?", (address_id,)
        )
        row = cursor.fetchone()

    assert row is not None
    assert row["id_cliente"] == client_id
    assert row["calle"] == "Main Street"
    assert row["num_exterior"] == "123"
    assert row["num_interior"] == "Apt 4"
    assert row["codigo_postal"] == "12345"
    assert row["delegacion"] == "Central"
    assert row["estado"] == "Mexico City"


def test_get_address_not_found():
    """
    Test retrieving an address that does not exist.
    """
    address = get_address(9999)  # Nonexistent ID
    assert address is None


def test_update_address():
    """
    Test updating an address and verifying the change in the database.
    """
    client_id = create_client(
        "Another Client",
        "RFC999",
        "Jane Doe",
        "jane@example.com",
        True,
        True,
        "password",
        None,
        "{}",
    )

    address_id = create_address(
        client_id, "Old Street", "456", "Suite 3", "54321", "North", "Guadalajara"
    )

    affected_rows = update_address(
        address_id,
        client_id,
        "New Street",
        "789",
        "Floor 2",
        "67890",
        "West",
        "Monterrey",
    )
    assert affected_rows == 1

    # Verify update in database
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM DIRECCION_CLIENTE WHERE id_direccion = ?", (address_id,)
        )
        row = cursor.fetchone()

    assert row is not None
    assert row["calle"] == "New Street"
    assert row["num_exterior"] == "789"
    assert row["num_interior"] == "Floor 2"
    assert row["codigo_postal"] == "67890"
    assert row["delegacion"] == "West"
    assert row["estado"] == "Monterrey"


def test_delete_address():
    """
    Test deleting an address and confirm that it no longer exists in the database.
    """
    client_id = create_client(
        "Client to Delete",
        "RFCDEL",
        "Mark Smith",
        "mark@example.com",
        True,
        True,
        "password",
        None,
        "{}",
    )

    address_id = create_address(
        client_id, "Delete Street", "999", "B", "99999", "South", "Cancun"
    )

    affected_rows = delete_address(address_id)
    assert affected_rows == 1

    # Verify deletion in database
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM DIRECCION_CLIENTE WHERE id_direccion = ?", (address_id,)
        )
        row = cursor.fetchone()

    assert row is None  # Address should no longer exist


def test_list_addresses():
    """
    Test listing all addresses and confirm that database reflects the correct number of addresses.
    """
    client_id = create_client(
        "Listing Client",
        "RFCLST",
        "Emily Johnson",
        "emily@example.com",
        True,
        True,
        "password",
        None,
        "{}",
    )

    create_address(client_id, "Street 1", "111", None, "11111", "Zone A", "City A")
    create_address(client_id, "Street 2", "222", None, "22222", "Zone B", "City B")

    addresses = list_addresses()
    assert len(addresses) >= 2  # Check that at least 2 addresses exist

    # Verify directly from the database
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM DIRECCION_CLIENTE")
        address_count = cursor.fetchone()[0]

    assert address_count >= 2  # Ensure at least two addresses exist in the table
