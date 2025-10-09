"""
FastAPI Authentication Dependencies
OAuth2 password bearer and user retrieval
"""

import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .jwt_handler import decode_token, verify_token

logger = logging.getLogger(__name__)

# OAuth2 password bearer for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", scheme_name="JWT")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get current authenticated user from JWT token

    Args:
        token: JWT token from Authorization header

    Returns:
        User document from database

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    from samplemind.core.database.repositories import UserRepository

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify token
    if not verify_token(token, token_type="access"):
        logger.warning("Invalid token provided")
        raise credentials_exception

    payload = decode_token(token)
    if not payload or "sub" not in payload:
        logger.warning("Token missing user_id")
        raise credentials_exception

    user_id = payload["sub"]

    # Get user from database
    try:
        user = await UserRepository.get_by_user_id(user_id)
        if not user:
            logger.warning(f"User {user_id} not found in database")
            raise credentials_exception

        logger.debug(f"Authenticated user: {user.email}")
        return user

    except Exception as e:
        logger.error(f"Error retrieving user: {e}")
        raise credentials_exception


async def get_current_active_user(user=Depends(get_current_user)):
    """
    Get current active user (must be active and verified)

    Args:
        user: Current user from get_current_user dependency

    Returns:
        Active user document

    Raises:
        HTTPException: 403 if user is inactive or not verified
    """
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user account"
        )

    # Optional: require email verification
    # if not user.is_verified:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Email not verified"
    #     )

    return user


async def get_optional_user(token: str | None = Depends(oauth2_scheme)):
    """
    Get current user if authenticated, None otherwise
    Useful for endpoints that work both authenticated and unauthenticated

    Args:
        token: JWT token from Authorization header (optional)

    Returns:
        User document or None
    """
    if not token:
        return None

    try:
        return await get_current_user(token)
    except HTTPException:
        return None
