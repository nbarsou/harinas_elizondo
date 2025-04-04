# db.py
import sqlite3
import os
from contextlib import contextmanager

# Default to a persistent file-based database.
# When testing/developing, you can override this via an environment variable.
DB_PATH = os.environ.get("DB_PATH", "data.db")

# Path to the SQL schema file
SQL_FILE_PATH = "./harina.sql"


@contextmanager
def db_connection():
    """
    Context manager to handle database connections automatically.
    Usage:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SQL_QUERY")
            result = cursor.fetchall()
    """
    conn = sqlite3.connect(DB_PATH, uri=DB_PATH.startswith("file:"))
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    try:
        yield conn  # Return the connection for use
        conn.commit()  # Commit changes automatically
    finally:
        conn.close()  # Close connection automatically


def init_db():
    """
    Reads the SQL schema from `harina.sql` and executes it.
    Ensures tables are created in the database.
    Uses `db_connection()` to automatically handle connection management.
    """
    if not os.path.exists(SQL_FILE_PATH):
        print(
            f"⚠️ WARNING: SQL file '{SQL_FILE_PATH}' not found. Skipping database initialization."
        )
        return

    with db_connection() as conn:  # Automatically handles open/close
        with open(SQL_FILE_PATH, "r", encoding="utf-8") as sql_file:
            sql_script = sql_file.read()

        conn.executescript(sql_script)  # Execute the entire SQL script
