"""
JWT Token Handler
Creates, validates, and decodes JWT tokens for authentication
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt

logger = logging.getLogger(__name__)


class JWTConfig:
    """JWT Configuration - should be set from API config"""

    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


def configure_jwt(
    secret_key: str,
    algorithm: str = "HS256",
    access_expire: int = 30,
    refresh_expire: int = 7,
):
    """Configure JWT settings from application config"""
    JWTConfig.SECRET_KEY = secret_key
    JWTConfig.ALGORITHM = algorithm
    JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES = access_expire
    JWTConfig.REFRESH_TOKEN_EXPIRE_DAYS = refresh_expire


def create_access_token(
    data: dict[str, Any] | str,
    email: str | None = None,
    additional_claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a new JWT access token

    Args:
        data: Either a dict with token data (legacy API) or user_id string
        email: User email address (required if data is a string)
        additional_claims: Extra claims to include in token
        expires_delta: Custom expiration time

    Returns:
        Encoded JWT token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    if isinstance(data, dict):
        to_encode = data.copy()
        to_encode.update(
            {
                "exp": expire,
                "type": "access",
                "iat": datetime.utcnow(),
            }
        )
        user_id = data.get("sub", data.get("user_id", "unknown"))
    else:
        user_id = data
        to_encode = {
            "sub": user_id,
            "email": email,
            "exp": expire,
            "type": "access",
            "iat": datetime.utcnow(),
        }

    if additional_claims:
        to_encode.update(additional_claims)

    encoded_jwt = jwt.encode(
        to_encode, JWTConfig.SECRET_KEY, algorithm=JWTConfig.ALGORITHM
    )

    logger.debug(f"Created access token for user {user_id}")
    return encoded_jwt


def create_refresh_token(
    data: dict[str, Any] | str, expires_delta: timedelta | None = None
) -> str:
    """
    Create a new JWT refresh token

    Args:
        data: Either a dict with token data (legacy API) or user_id string
        expires_delta: Custom expiration time

    Returns:
        Encoded JWT refresh token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=JWTConfig.REFRESH_TOKEN_EXPIRE_DAYS)

    if isinstance(data, dict):
        to_encode = data.copy()
        to_encode.update(
            {
                "exp": expire,
                "type": "refresh",
                "iat": datetime.utcnow(),
            }
        )
        user_id = data.get("sub", data.get("user_id", "unknown"))
    else:
        user_id = data
        to_encode = {
            "sub": user_id,
            "exp": expire,
            "type": "refresh",
            "iat": datetime.utcnow(),
        }

    encoded_jwt = jwt.encode(
        to_encode, JWTConfig.SECRET_KEY, algorithm=JWTConfig.ALGORITHM
    )

    logger.debug(f"Created refresh token for user {user_id}")
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any] | None:
    """
    Decode JWT token without verification

    Args:
        token: JWT token string

    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            JWTConfig.SECRET_KEY,
            algorithms=[JWTConfig.ALGORITHM],
            options={"verify_signature": True},
        )
        return payload
    except JWTError as e:
        logger.warning(f"Failed to decode token: {e}")
        return None


def verify_token(token: str, token_type: str = "access") -> bool:
    """
    Verify JWT token and return True if valid

    Args:
        token: JWT token string
        token_type: Expected token type ("access" or "refresh")

    Returns:
        True if token is valid, False otherwise
    """
    try:
        payload = jwt.decode(
            token, JWTConfig.SECRET_KEY, algorithms=[JWTConfig.ALGORITHM]
        )

        user_id: str = payload.get("sub")
        exp: int = payload.get("exp")
        token_type_claim: str = payload.get("type")

        if not user_id:
            logger.warning("Token missing user_id (sub)")
            return False

        if not exp:
            logger.warning("Token missing expiration")
            return False

        if token_type_claim != token_type:
            logger.warning(
                f"Token type mismatch: expected {token_type}, got {token_type_claim}"
            )
            return False

        if datetime.utcnow() > datetime.fromtimestamp(exp):
            logger.warning("Token has expired")
            return False

        logger.debug(f"Token verified for user {user_id}")
        return True

    except JWTError as e:
        logger.warning(f"Token verification failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error verifying token: {e}")
        return False


def get_token_expiration(token: str) -> datetime | None:
    """
    Get expiration datetime from token

    Args:
        token: JWT token string

    Returns:
        Expiration datetime or None
    """
    payload = decode_token(token)
    if not payload or "exp" not in payload:
        return None

    return datetime.fromtimestamp(payload["exp"])


def is_token_expired(token: str) -> bool:
    """
    Check if token is expired

    Args:
        token: JWT token string

    Returns:
        True if expired or invalid, False if still valid
    """
    exp = get_token_expiration(token)
    if not exp:
        return True

    return datetime.utcnow() > exp
