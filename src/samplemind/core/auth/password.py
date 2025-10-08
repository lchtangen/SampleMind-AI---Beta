"""
Password Hashing and Verification
Uses bcrypt for secure password hashing
"""

from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)

# Bcrypt context for password hashing with 72-byte truncation
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__ident="2b",
    bcrypt__truncate_error=False
)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    # Bcrypt has a 72-byte password limit, truncate if necessary
    password_bytes = password.encode('utf-8')[:72]
    hashed = pwd_context.hash(password_bytes)
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
        # Bcrypt has a 72-byte password limit, truncate if necessary
        password_bytes = plain_password.encode('utf-8')[:72]
        is_valid = pwd_context.verify(password_bytes, hashed_password)
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
