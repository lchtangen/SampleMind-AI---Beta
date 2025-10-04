"""
Password Hashing and Verification
Uses bcrypt for secure password hashing
"""

from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)

# Bcrypt context for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    hashed = pwd_context.hash(password)
    logger.debug("Password hashed successfully")
    return hashed


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
        is_valid = pwd_context.verify(plain_password, hashed_password)
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
    return pwd_context.needs_update(hashed_password)
