"""
Password Hashing and Verification
Uses bcrypt for secure password hashing
"""

import bcrypt
import logging

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    logger.debug("Password hashed successfully")
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception as exc:
        logger.error(f"Error verifying password: {exc}")
        return False


def needs_rehash(hashed_password: str) -> bool:
    """Check if password hash needs to be updated."""
    try:
        cost_str = hashed_password.split("$")[2]
        cost = int(cost_str)
    except (IndexError, ValueError):
        return True
    return cost < 12
