# tests/conftest.py
import pytest
import db


@pytest.fixture(scope="session", autouse=True)
def configure_test_db(tmp_path_factory):
    # Create a temporary directory and database file.
    temp_db = tmp_path_factory.mktemp("data") / "test.db"
    db.DB_PATH = str(
        temp_db
    )  # Override the DB_PATH used by db_connection() and init_db()


@pytest.fixture(scope="function", autouse=True)
def fresh_db():
    """
    This fixture runs before each test function.
    It creates a new in-memory database schema so each test is isolated.
    """
    with db.db_connection() as conn:
        db.init_db()
        # Test runs here
        yield conn
