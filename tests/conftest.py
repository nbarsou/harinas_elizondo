# tests/conftest.py
import pytest
from db import get_connection, init_db


@pytest.fixture(scope="function", autouse=True)
def fresh_db():
    """
    This fixture runs before each test function.
    It creates a new in-memory database schema so each test is isolated.
    """
    conn = get_connection()
    init_db()
    # Test runs here
    yield conn
    # Teardown (in memory DB goes away when connection closes, so nothing else needed)
    conn.close()
