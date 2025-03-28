# tests/test_equipment_service.py
import pytest
from services.equipment_service import (
    create_equipment,
    get_equipment,
    update_equipment,
    delete_equipment,
    list_equipment,
    deactivate_equipment,
)
from services.user_service import create_user  # Needed to create an equipment manager
from db import db_connection


def test_create_equipment():
    """
    Test creating a new equipment record and verify that it exists in the database.
    """
    # Create a test user to be assigned as the manager of the equipment
    user_id = create_user(
        "manager@example.com", "password123", "admin", "Equipment Manager"
    )
    assert user_id is not None

    # Create equipment
    equipment_id = create_equipment(
        "Microscope",
        "MIC-123",
        "Nikon",
        "Eclipse E100",
        "SN123456",
        "High-end optical microscope",
        "Optical Microscope",
        "Tech Supplier",
        "2024-01-10",
        "3 years",
        "2027-01-10",
        "Lab A",
        user_id,
        "Operational",
        None,
    )
    assert equipment_id is not None

    # Verify directly from the database
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM EQUIPO_LABORATORIO WHERE id_equipo = ?", (equipment_id,)
        )
        row = cursor.fetchone()

    assert row is not None
    assert row["tipo"] == "Microscope"
    assert row["marca"] == "Nikon"
    assert row["modelo"] == "Eclipse E100"
    assert row["serie"] == "SN123456"
    assert row["estado"] == "Operational"


def test_get_equipment_not_found():
    """
    Test retrieving equipment that does not exist.
    """
    equipment = get_equipment(9999)  # Nonexistent ID
    assert equipment is None


def test_update_equipment():
    """
    Test updating an equipment record and verifying the change in the database.
    """
    user_id = create_user("labtech@example.com", "securepass", "technician", "Lab Tech")

    equipment_id = create_equipment(
        "Old Microscope",
        "OLD-456",
        "Zeiss",
        "Axio Lab",
        "SN987654",
        "Entry-level microscope",
        "Basic Microscope",
        "Old Supplier",
        "2020-05-15",
        "2 years",
        "2022-05-15",
        "Lab B",
        user_id,
        "Operational",
        None,
    )

    affected_rows = update_equipment(
        equipment_id,
        "Advanced Microscope",
        "ADV-789",
        "Leica",
        "DM750",
        "SN456789",
        "High-performance microscope",
        "Advanced Microscope",
        "Modern Supplier",
        "2023-07-20",
        "4 years",
        "2027-07-20",
        "Lab C",
        user_id,
        "Under Maintenance",
        None,
    )
    assert affected_rows == 1

    # Verify update in database
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM EQUIPO_LABORATORIO WHERE id_equipo = ?", (equipment_id,)
        )
        row = cursor.fetchone()

    assert row is not None
    assert row["tipo"] == "Advanced Microscope"
    assert row["marca"] == "Leica"
    assert row["modelo"] == "DM750"
    assert row["estado"] == "Under Maintenance"


def test_deactivate_equipment():
    """
    Test marking an equipment as inactive and storing a reason for deactivation.
    """
    user_id = create_user(
        "deactmgr@example.com", "pass", "manager", "Deactivation Manager"
    )

    equipment_id = create_equipment(
        "Old Centrifuge",
        "CENT-555",
        "Thermo",
        "Megafuge",
        "SN555111",
        "Old model centrifuge",
        "Basic Centrifuge",
        "Lab Supplier",
        "2018-06-01",
        "5 years",
        "2023-06-01",
        "Storage",
        user_id,
        "Operational",
        None,
    )

    affected_rows = deactivate_equipment(
        equipment_id, "Outdated and replaced with a newer model"
    )
    assert affected_rows == 1

    # Verify deactivation in database
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT estado, causa_baja FROM EQUIPO_LABORATORIO WHERE id_equipo = ?",
            (equipment_id,),
        )
        row = cursor.fetchone()

    assert row is not None
    assert row["estado"] == "Inactive"
    assert row["causa_baja"] == "Outdated and replaced with a newer model"


def test_delete_equipment():
    """
    Test deleting an equipment record and confirming that it no longer exists in the database.
    """
    user_id = create_user("deletemgr@example.com", "pass123", "admin", "Delete Manager")

    equipment_id = create_equipment(
        "Obsolete Oscilloscope",
        "OSC-999",
        "Tektronix",
        "TBS1104",
        "SN999000",
        "Old oscilloscope model",
        "Oscilloscope",
        "Lab Vendor",
        "2015-08-15",
        "5 years",
        "2020-08-15",
        "Storage",
        user_id,
        "Decommissioned",
        "No longer functional",
    )

    affected_rows = delete_equipment(equipment_id)
    assert affected_rows == 1

    # Verify deletion in database
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM EQUIPO_LABORATORIO WHERE id_equipo = ?", (equipment_id,)
        )
        row = cursor.fetchone()

    assert row is None  # Equipment should no longer exist


def test_list_equipment():
    """
    Test listing all equipment and confirm that the count matches the database.
    """
    user_id = create_user("listmgr@example.com", "pass456", "manager", "List Manager")

    create_equipment(
        "Spectrometer",
        "SPEC-100",
        "Agilent",
        "Cary 60",
        "SN100001",
        "UV-Vis Spectrometer",
        "Spectrometer",
        "Spectro Supplier",
        "2022-03-01",
        "3 years",
        "2025-03-01",
        "Lab D",
        user_id,
        "Operational",
        None,
    )
    create_equipment(
        "Autoclave",
        "AUTO-200",
        "Tuttnauer",
        "Elara 11",
        "SN200002",
        "Sterilization unit",
        "Autoclave",
        "Medical Supplier",
        "2021-10-10",
        "4 years",
        "2025-10-10",
        "Lab E",
        user_id,
        "Operational",
        None,
    )

    equipment = list_equipment()
    assert len(equipment) >= 2  # Ensuring at least two equipment records exist

    # Verify directly from the database
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM EQUIPO_LABORATORIO")
        equipment_count = cursor.fetchone()[0]

    assert equipment_count >= 2  # Ensure at least two equipment exist in the table
