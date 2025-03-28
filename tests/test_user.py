# tests/test_user_service.py
import pytest
from services.user_service import (
    create_user,
    get_user,
    update_user,
    delete_user,
    list_users,
)


def test_create_user(fresh_db):
    """
    Test creating a new user and verify that it exists in the database.
    """
    user_id = create_user("test@example.com", "securepassword", "admin", "Test User")
    assert user_id is not None

    # Query database directly
    cursor = fresh_db.cursor()
    cursor.execute("SELECT * FROM USUARIO WHERE id_usuario = ?", (user_id,))
    row = cursor.fetchone()

    assert row is not None
    assert row["mail"] == "test@example.com"
    assert row["rol"] == "admin"
    assert row["nombre"] == "Test User"


def test_get_user_not_found():
    """
    Test retrieving a user that does not exist.
    """
    user = get_user(9999)  # Nonexistent ID
    assert user is None


def test_update_user(fresh_db):
    """
    Test updating a user's information and verifying the change in the database.
    """
    user_id = create_user("update@example.com", "oldpassword", "user", "Old Name")

    affected_rows = update_user(
        user_id, "update@example.com", "newpassword", "admin", "New Name"
    )
    assert affected_rows == 1

    # Verify update in database
    cursor = fresh_db.cursor()
    cursor.execute("SELECT * FROM USUARIO WHERE id_usuario = ?", (user_id,))
    row = cursor.fetchone()

    assert row["nombre"] == "New Name"
    assert row["rol"] == "admin"


def test_delete_user(fresh_db):
    """
    Test deleting a user and confirm that it no longer exists in the database.
    """
    user_id = create_user("delete@example.com", "password123", "user", "Delete Me")

    affected_rows = delete_user(user_id)
    assert affected_rows == 1

    # Verify deletion in database
    cursor = fresh_db.cursor()
    cursor.execute("SELECT * FROM USUARIO WHERE id_usuario = ?", (user_id,))
    row = cursor.fetchone()

    assert row is None  # User should no longer exist


def test_list_users(fresh_db):
    """
    Test listing all users and confirm that database reflects the correct number of users.
    """
    create_user("user1@example.com", "pass1", "user", "User One")
    create_user("user2@example.com", "pass2", "admin", "User Two")

    users = list_users()
    assert len(users) >= 2  # Check that at least 2 users exist

    # Verify directly from the database
    cursor = fresh_db.cursor()
    cursor.execute("SELECT COUNT(*) FROM USUARIO")
    user_count = cursor.fetchone()[0]  # Fetch count

    assert user_count >= 2  # Ensure at least two users exist in the table
