# services/user_service.py
from db import db_connection

def createUser(username, email):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email) VALUES (?, ?)",
            (username, email)
        )
        conn.commit()
        return cursor.lastrowid

def getUser(user_id):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def updateUser(user_id, new_username, new_email):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users
            SET username = ?, email = ?
            WHERE id = ?
        """, (new_username, new_email, user_id))
        conn.commit()
        return cursor.rowcount

def deleteUser(user_id):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount

def listUsers():
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

