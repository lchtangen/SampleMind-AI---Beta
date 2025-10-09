"""
Password Hashing and Verification
Uses bcrypt for secure password hashing
"""

import logging

import bcrypt

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    logger.debug("Password hashed successfully")
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to check against

    Returns:
        True if password matches, False otherwise
    """
    try:
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        is_valid = bcrypt.checkpw(password_bytes, hashed_bytes)
        if is_valid:
            logger.debug("Password verification successful")
        else:
            logger.debug("Password verification failed")
        return is_valid
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False


def needs_rehash(hashed_password: str) -> bool:
    """
    Check if password hash needs to be updated
    (e.g., if bcrypt rounds have changed)

    Args:
        hashed_password: Hashed password to check

    Returns:
        True if rehash is needed, False otherwise
    """
    try:
        current_cost = bcrypt.gensalt()
        hash_cost = int(hashed_password.split('$')[2])
        default_cost = int(current_cost.decode('utf-8').split('$')[2])
        return hash_cost < default_cost
    except Exception:
        return False
