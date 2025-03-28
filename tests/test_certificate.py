# tests/test_certificate_service.py
import pytest
from services.certificate_service import (
    create_certificate,
    get_certificate,
    update_certificate,
    delete_certificate,
    list_certificates,
)
from services.client_service import create_client  # Needed to create test clients
from services.inspection_service import (
    create_inspection,
)  # Needed to create test inspections


def test_create_certificate(fresh_db):
    """
    Test creating a new certification record and verify that it exists in the database.
    """
    # Create a test client
    client_id = create_client(
        "Client S.A.",
        "RFC123456",
        "John Smith",
        "john@example.com",
        True,
        True,
        "securepass",
        None,
        "{}",
    )
    assert client_id is not None

    # Create a test inspection
    inspection_id = create_inspection(
        "LOT-001", "2024-03-25", None, "SEQ001", "pH, Conductivity", "Routine", None
    )
    assert inspection_id is not None

    # Create a certification record
    certificate_id = create_certificate(
        client_id,
        inspection_id,
        "SEQ001",
        "PO-1001",
        500.0,
        495.0,
        "INV-2024001",
        "2024-03-30",
        "2025-03-30",
        "Pass",
        "Yes",
        "None",
        "qa@example.com",
    )
    assert certificate_id is not None

    # Verify directly from the database
    cursor = fresh_db.cursor()
    cursor.execute(
        "SELECT * FROM CERTIFICADO_CALIDAD WHERE id_certificado = ?",
        (certificate_id,),
    )
    row = cursor.fetchone()

    assert row is not None
    assert row["id_cliente"] == client_id
    assert row["id_inspeccion"] == inspection_id
    assert row["orden_compra"] == "PO-1001"
    assert row["cantidad_solicitada"] == 500.0
    assert row["cantidad_entregada"] == 495.0


def test_get_certificate_not_found():
    """
    Test retrieving a certificate that does not exist.
    """
    certificate = get_certificate(9999)  # Nonexistent ID
    assert certificate is None


def test_update_certificate(fresh_db):
    """
    Test updating a certification record and verifying the change in the database.
    """
    client_id = create_client(
        "Updated Client S.A.",
        "RFC654321",
        "Alice Brown",
        "alice@example.com",
        True,
        True,
        "securepass",
        None,
        "{}",
    )
    inspection_id = create_inspection(
        "LOT-002", "2024-04-10", None, "SEQ002", "Density, Temperature", "Initial", None
    )

    certificate_id = create_certificate(
        client_id,
        inspection_id,
        "SEQ002",
        "PO-2002",
        600.0,
        590.0,
        "INV-2024002",
        "2024-04-15",
        "2025-04-15",
        "Pass",
        "No",
        "Minor deviation",
        "qa@company.com",
    )

    affected_rows = update_certificate(
        certificate_id,
        client_id,
        inspection_id,
        "SEQ003",
        "PO-3003",
        700.0,
        680.0,
        "INV-2024003",
        "2024-05-01",
        "2025-05-01",
        "Pass",
        "Yes",
        "No deviation",
        "quality@example.com",
    )
    assert affected_rows == 1

    # Verify update in database
    cursor = fresh_db.cursor()
    cursor.execute(
        "SELECT * FROM CERTIFICADO_CALIDAD WHERE id_certificado = ?",
        (certificate_id,),
    )
    row = cursor.fetchone()

    assert row is not None
    assert row["orden_compra"] == "PO-3003"
    assert row["cantidad_solicitada"] == 700.0
    assert row["cantidad_entregada"] == 680.0
    assert row["destinatario_correo"] == "quality@example.com"


def test_delete_certificate(fresh_db):
    """
    Test deleting a certification record and confirm that it no longer exists in the database.
    """
    client_id = create_client(
        "Delete Client S.A.",
        "RFC000111",
        "Emma Wilson",
        "emma@example.com",
        True,
        True,
        "securepass",
        None,
        "{}",
    )
    inspection_id = create_inspection(
        "LOT-003", "2024-06-05", None, "SEQ004", "Acid-Base Titration", "Final", None
    )

    certificate_id = create_certificate(
        client_id,
        inspection_id,
        "SEQ004",
        "PO-4004",
        300.0,
        290.0,
        "INV-2024004",
        "2024-06-10",
        "2025-06-10",
        "Fail",
        "No",
        "Major deviation",
        "compliance@example.com",
    )

    affected_rows = delete_certificate(certificate_id)
    assert affected_rows == 1

    # Verify deletion in database
    cursor = fresh_db.cursor()
    cursor.execute(
        "SELECT * FROM CERTIFICADO_CALIDAD WHERE id_certificado = ?",
        (certificate_id,),
    )
    row = cursor.fetchone()

    assert row is None  # Certificate should no longer exist


def test_list_certificates(fresh_db):
    """
    Test listing all certificates and confirm that the count matches the database.
    """
    client_id = create_client(
        "Listing Client S.A.",
        "RFC789654",
        "Robert Johnson",
        "robert@example.com",
        True,
        True,
        "securepass",
        None,
        "{}",
    )
    inspection_id = create_inspection(
        "LOT-005", "2024-07-01", None, "SEQ005", "Viscosity, Hardness", "Routine", None
    )

    create_certificate(
        client_id,
        inspection_id,
        "SEQ005",
        "PO-5005",
        200.0,
        195.0,
        "INV-2024005",
        "2024-07-05",
        "2025-07-05",
        "Pass",
        "Yes",
        "No deviation",
        "qa@example.com",
    )
    create_certificate(
        client_id,
        inspection_id,
        "SEQ006",
        "PO-6006",
        100.0,
        99.5,
        "INV-2024006",
        "2024-07-10",
        "2025-07-10",
        "Pass",
        "Yes",
        "Minor deviation",
        "quality@example.com",
    )

    certificates = list_certificates()
    assert len(certificates) >= 2  # Ensuring at least two certification records exist

    # Verify directly from the database
    cursor = fresh_db.cursor()
    cursor.execute("SELECT COUNT(*) FROM CERTIFICADO_CALIDAD")
    certificate_count = cursor.fetchone()[0]

    assert certificate_count >= 2  # Ensure at least two certificates exist in the table
