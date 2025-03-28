# tests/test_inspection_service.py
import pytest
from services.inspection_service import (
    create_inspection,
    get_inspection,
    update_inspection,
    delete_inspection,
    list_inspections,
)
from services.equipment_service import (
    create_equipment,
)  # Needed to create test equipment
from services.user_service import create_user  # Needed to create an inspector
from db import db_connection


def test_create_inspection():
    """
    Test creating a new inspection and verify that it exists in the database.
    """
    # Create a test user (laboratorista)
    inspector_id = create_user(
        "inspector@example.com", "securepass", "technician", "Lab Inspector"
    )
    assert inspector_id is not None

    # Create test equipment
    equipment_id = create_equipment(
        "Spectrometer",
        "SPEC-123",
        "Agilent",
        "Cary 5000",
        "SN123456",
        "High-end spectrometer",
        "Spectrometer",
        "Lab Supplier",
        "2023-06-15",
        "5 years",
        "2028-06-15",
        "Lab A",
        inspector_id,
        "Operational",
        None,
    )
    assert equipment_id is not None

    # Create an inspection record
    inspection_id = create_inspection(
        "LOT-001",
        "2024-03-25",
        equipment_id,
        "SEQ001",
        "pH, Conductivity",
        "Routine",
        inspector_id,
    )
    assert inspection_id is not None

    # Verify directly from the database
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM INSPECCION WHERE id_inspeccion = ?", (inspection_id,)
        )
        row = cursor.fetchone()

    assert row is not None
    assert row["numero_lote"] == "LOT-001"
    assert row["id_equipo"] == equipment_id
    assert row["id_laboratorista"] == inspector_id
    assert row["tipo_inspeccion"] == "Routine"


def test_get_inspection_not_found():
    """
    Test retrieving an inspection that does not exist.
    """
    inspection = get_inspection(9999)  # Nonexistent ID
    assert inspection is None


def test_update_inspection():
    """
    Test updating an inspection record and verifying the change in the database.
    """
    inspector_id = create_user(
        "updateinspector@example.com", "securepass", "technician", "Update Inspector"
    )

    equipment_id = create_equipment(
        "Old Balance",
        "BAL-987",
        "Mettler",
        "XPE205",
        "SN987654",
        "Precision balance",
        "Balance",
        "Tech Supplier",
        "2022-09-20",
        "4 years",
        "2026-09-20",
        "Lab B",
        inspector_id,
        "Operational",
        None,
    )

    inspection_id = create_inspection(
        "LOT-002",
        "2024-04-10",
        equipment_id,
        "SEQ002",
        "Mass Calibration",
        "Initial",
        inspector_id,
    )

    affected_rows = update_inspection(
        inspection_id,
        "LOT-003",
        "2024-04-15",
        equipment_id,
        "SEQ003",
        "Density, Temperature",
        "Final",
        inspector_id,
    )
    assert affected_rows == 1

    # Verify update in database
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM INSPECCION WHERE id_inspeccion = ?", (inspection_id,)
        )
        row = cursor.fetchone()

    assert row is not None
    assert row["numero_lote"] == "LOT-003"
    assert row["fecha"] == "2024-04-15"
    assert row["secuencia"] == "SEQ003"
    assert row["parametros_analizados"] == "Density, Temperature"
    assert row["tipo_inspeccion"] == "Final"


def test_delete_inspection():
    """
    Test deleting an inspection and confirm that it no longer exists in the database.
    """
    inspector_id = create_user(
        "deleteinspector@example.com", "securepass", "technician", "Delete Inspector"
    )

    equipment_id = create_equipment(
        "pH Meter",
        "PHM-555",
        "Metrohm",
        "781",
        "SN555111",
        "pH measuring device",
        "pH Meter",
        "Lab Vendor",
        "2020-07-10",
        "3 years",
        "2023-07-10",
        "Lab C",
        inspector_id,
        "Operational",
        None,
    )

    inspection_id = create_inspection(
        "LOT-004",
        "2024-05-05",
        equipment_id,
        "SEQ004",
        "pH Measurement",
        "Routine",
        inspector_id,
    )

    affected_rows = delete_inspection(inspection_id)
    assert affected_rows == 1

    # Verify deletion in database
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM INSPECCION WHERE id_inspeccion = ?", (inspection_id,)
        )
        row = cursor.fetchone()

    assert row is None  # Inspection should no longer exist


def test_list_inspections():
    """
    Test listing all inspections and confirm that the count matches the database.
    """
    inspector_id = create_user(
        "listinspector@example.com", "securepass", "technician", "List Inspector"
    )

    equipment_id = create_equipment(
        "Titrator",
        "TIT-789",
        "Hanna",
        "HI902C",
        "SN789000",
        "Automatic titrator",
        "Titrator",
        "Titration Systems",
        "2021-11-11",
        "3 years",
        "2024-11-11",
        "Lab D",
        inspector_id,
        "Operational",
        None,
    )

    create_inspection(
        "LOT-005",
        "2024-06-01",
        equipment_id,
        "SEQ005",
        "Acid-Base Titration",
        "Initial",
        inspector_id,
    )
    create_inspection(
        "LOT-006",
        "2024-06-10",
        equipment_id,
        "SEQ006",
        "Conductivity Check",
        "Routine",
        inspector_id,
    )

    inspections = list_inspections()
    assert len(inspections) >= 2  # Ensuring at least two inspection records exist

    # Verify directly from the database
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM INSPECCION")
        inspection_count = cursor.fetchone()[0]

    assert inspection_count >= 2  # Ensure at least two inspections exist in the table
