# tests/test_parameters_service.py
import pytest
from services.parameters_service import (
    create_parameter,
    get_parameter,
    update_parameter,
    delete_parameter,
    list_parameters,
)
from services.inspection_service import (
    create_inspection,
)  # Needed to create test inspections
from services.equipment_service import (
    create_equipment,
)  # Needed to create test equipment


def test_create_parameter(fresh_db):
    """
    Test creating a new parameter and verify that it exists in the database.
    """
    # Create a test inspection
    inspection_id = create_inspection(
        "LOT-100", "2024-04-15", None, "SEQ100", "pH, Conductivity", "Routine", None
    )
    assert inspection_id is not None

    # Create a test equipment
    equipment_id = create_equipment(
        "Spectrometer",
        "SPEC-001",
        "Agilent",
        "Cary 60",
        "SN100001",
        "UV-Vis Spectrometer",
        "Spectrometer",
        "Tech Supplier",
        "2023-01-10",
        "3 years",
        "2026-01-10",
        "Lab A",
        None,
        "Operational",
        None,
    )
    assert equipment_id is not None

    # Create a parameter entry
    parameter_id = create_parameter(inspection_id, equipment_id, "Absorbance", 1.23)
    assert parameter_id is not None

    # Verify directly from the database
    cursor = fresh_db.cursor()
    cursor.execute(
        "SELECT * FROM PARAMETRO_ANALISIS WHERE id_parametro = ?", (parameter_id,)
    )
    row = cursor.fetchone()

    assert row is not None
    assert row["id_inspeccion"] == inspection_id
    assert row["id_equipo_laboratorio"] == equipment_id
    assert row["parametro_analizado"] == "Absorbance"
    assert row["valor"] == 1.23


def test_get_parameter_not_found():
    """
    Test retrieving a parameter that does not exist.
    """
    parameter = get_parameter(9999)  # Nonexistent ID
    assert parameter is None


def test_update_parameter(fresh_db):
    """
    Test updating a parameter and verifying the change in the database.
    """
    inspection_id = create_inspection(
        "LOT-101", "2024-05-01", None, "SEQ101", "pH, Conductivity", "Routine", None
    )
    equipment_id = create_equipment(
        "pH Meter",
        "PHM-002",
        "Metrohm",
        "781",
        "SN200002",
        "pH Measuring Device",
        "pH Meter",
        "Tech Supplier",
        "2022-08-15",
        "2 years",
        "2024-08-15",
        "Lab B",
        None,
        "Operational",
        None,
    )

    parameter_id = create_parameter(inspection_id, equipment_id, "Conductivity", 5.67)

    affected_rows = update_parameter(
        parameter_id, inspection_id, equipment_id, "Salinity", 8.90
    )
    assert affected_rows == 1

    # Verify update in database
    cursor = fresh_db.cursor()
    cursor.execute(
        "SELECT * FROM PARAMETRO_ANALISIS WHERE id_parametro = ?", (parameter_id,)
    )
    row = cursor.fetchone()

    assert row is not None
    assert row["parametro_analizado"] == "Salinity"
    assert row["valor"] == 8.90


def test_delete_parameter(fresh_db):
    """
    Test deleting a parameter and confirming that it no longer exists in the database.
    """
    inspection_id = create_inspection(
        "LOT-102", "2024-06-01", None, "SEQ102", "pH, Conductivity", "Routine", None
    )
    equipment_id = create_equipment(
        "Titrator",
        "TIT-003",
        "Hanna",
        "HI902C",
        "SN300003",
        "Automatic Titrator",
        "Titrator",
        "Chemical Supplier",
        "2021-10-10",
        "4 years",
        "2025-10-10",
        "Lab C",
        None,
        "Operational",
        None,
    )

    parameter_id = create_parameter(inspection_id, equipment_id, "pH", 7.00)

    affected_rows = delete_parameter(parameter_id)
    assert affected_rows == 1

    # Verify deletion in database
    cursor = fresh_db.cursor()
    cursor.execute(
        "SELECT * FROM PARAMETRO_ANALISIS WHERE id_parametro = ?", (parameter_id,)
    )
    row = cursor.fetchone()

    assert row is None  # Parameter should no longer exist


def test_list_parameters(fresh_db):
    """
    Test listing all parameters and confirm that the count matches the database.
    """
    inspection_id = create_inspection(
        "LOT-103", "2024-07-01", None, "SEQ103", "Viscosity, Hardness", "Routine", None
    )
    equipment_id = create_equipment(
        "Balance",
        "BAL-004",
        "Mettler",
        "XPE205",
        "SN400004",
        "Precision Balance",
        "Balance",
        "Lab Supplier",
        "2022-04-20",
        "3 years",
        "2025-04-20",
        "Lab D",
        None,
        "Operational",
        None,
    )

    create_parameter(inspection_id, equipment_id, "Density", 2.45)
    create_parameter(inspection_id, equipment_id, "Hardness", 6.78)

    parameters = list_parameters()
    assert len(parameters) >= 2  # Ensuring at least two parameter records exist

    # Verify directly from the database
    cursor = fresh_db.cursor()
    cursor.execute("SELECT COUNT(*) FROM PARAMETRO_ANALISIS")
    parameter_count = cursor.fetchone()[0]

    assert parameter_count >= 2  # Ensure at least two parameters exist in the table
