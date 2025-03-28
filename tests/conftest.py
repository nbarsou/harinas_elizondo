# tests/conftest.py
import pytest
from db import db_connection, init_db


@pytest.fixture(scope="function", autouse=True)
def fresh_db():
    """
    This fixture runs before each test function.
    It creates a new in-memory database schema so each test is isolated.
    """
    with db_connection() as conn:
        init_db()
        # Test runs here
        yield conn
        # Teardown (in memory DB goes away when connection closes, so nothing else needed)
        conn.close()
