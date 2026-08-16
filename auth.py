"""
auth.py
Handles user registration and login, including secure password hashing.

Uses hashlib's PBKDF2-HMAC-SHA256 (stdlib, no external dependency) with a
random per-user salt, which is a NIST-recommended approach for password
storage when a dedicated library like bcrypt isn't available.
"""

import hashlib
import hmac
import os
import binascii

# Number of PBKDF2 iterations. Higher = slower to brute-force.
# 200,000 is a reasonable modern default (OWASP recommends 210,000+ as of 2023).
PBKDF2_ITERATIONS = 200_000


def hash_password(password: str) -> str:
    """
    Hashes a password with a random salt.
    Returns a single string of the form: "<salt_hex>$<hash_hex>"
    so it can be stored in a single database column.
    """
    salt = os.urandom(16)
    pw_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return f"{binascii.hexlify(salt).decode()}${binascii.hexlify(pw_hash).decode()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verifies a plaintext password against a stored '<salt_hex>$<hash_hex>' string."""
    try:
        salt_hex, hash_hex = stored_hash.split("$")
    except ValueError:
        return False

    salt = binascii.unhexlify(salt_hex)
    expected_hash = binascii.unhexlify(hash_hex)

    new_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    # Constant-time comparison to avoid timing attacks
    return hmac.compare_digest(new_hash, expected_hash)


class AuthManager:
    """Wraps the Database class with register/login business logic."""

    def __init__(self, database):
        self.db = database

    def register(self, name: str, email: str, password: str):
        """Returns (success: bool, message: str)."""
        if not name.strip() or not email.strip() or not password:
            return False, "Name, email, and password cannot be empty."

        if self.db.email_exists(email):
            return False, "Email already registered."

        password_hash = hash_password(password)
        self.db.add_user(email, name, password_hash)
        return True, "Registration successful. You can now log in."

    def login(self, email: str, password: str):
        """Returns (success: bool, message: str, name: str | None)."""
        user = self.db.get_user(email)
        if user is None:
            return False, "This email is not registered.", None

        name, stored_hash = user
        if verify_password(password, stored_hash):
            return True, "Login successful.", name
        else:
            return False, "Incorrect password.", None