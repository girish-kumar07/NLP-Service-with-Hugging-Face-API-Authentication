"""
database.py
Handles all SQLite database operations for the NLP App's user system.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")


class Database:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._create_table()

    def _get_connection(self):
        # A new connection per operation keeps this simple and thread-safe enough
        # for a CLI app (avoids sharing a single connection across calls).
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    email TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    password_hash TEXT NOT NULL
                )
            """)
            conn.commit()

    def email_exists(self, email: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT 1 FROM users WHERE email = ?", (email,))
            return cursor.fetchone() is not None

    def add_user(self, email: str, name: str, password_hash: str) -> None:
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?)",
                (email, name, password_hash),
            )
            conn.commit()

    def get_user(self, email: str):
        """Returns (name, password_hash) tuple, or None if not found."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT name, password_hash FROM users WHERE email = ?", (email,)
            )
            return cursor.fetchone()