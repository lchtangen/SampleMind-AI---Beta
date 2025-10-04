"""
Authentication Routes
User registration, login, token refresh, and profile management
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
import uuid
import logging

from samplemind.interfaces.api.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    ChangePasswordRequest,
    UserResponse,
    UserProfileUpdate,
    MessageResponse,
)
from samplemind.core.auth import (
    create_access_token,
    create_refresh_token,
    verify_token,
    hash_password,
    verify_password,
    get_current_user,
    get_current_active_user,
)
from samplemind.core.database.repositories import UserRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(request: UserRegisterRequest):
    """
    Register a new user
    
    - **email**: Valid email address (unique)
    - **username**: Alphanumeric username (unique, 3-50 chars)
    - **password**: Strong password (min 8 chars, uppercase, lowercase, digit)
    """
    # Check if email already exists
    logger.info(f"Registration attempt for email: {request.email}")
    existing_user = await UserRepository.get_by_email(request.email)
    if existing_user:
        logger.warning(f"Registration failed: Email already exists - {request.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = await UserRepository.get_by_username(request.username)
    if existing_username:
        logger.warning(f"Registration failed: Username already taken - {request.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Hash password
    hashed_password = hash_password(request.password)
    
    # Create user
    user = await UserRepository.create(
        user_id=str(uuid.uuid4()),
        email=request.email,
        username=request.username,
        hashed_password=hashed_password,
        is_active=True,
        is_verified=False,
        created_at=datetime.utcnow()
    )
    
    logger.info(f"✅ New user registered successfully: {user.email} (username: {user.username})")
    return UserResponse.from_orm(user)


@router.post("/login", response_model=TokenResponse)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login with username/email and password
    
    Returns access and refresh JWT tokens
    OAuth2 compatible endpoint (can be used with OAuth2PasswordBearer)
    """
    # Try to find user by email or username
    logger.info(f"Login attempt for: {form_data.username}")
    user = await UserRepository.get_by_email(form_data.username)
    if not user:
        user = await UserRepository.get_by_username(form_data.username)
    
    if not user:
        logger.warning(f"Login failed: User not found - {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Login failed: Invalid password for user - {user.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        logger.warning(f"Login failed: Account inactive - {user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Update last login
    await UserRepository.update(user.user_id, last_login=datetime.utcnow())
    
    # Create tokens
    access_token = create_access_token(
        user_id=user.user_id,
        email=user.email
    )
    refresh_token = create_refresh_token(user_id=user.user_id)
    
    logger.info(f"✅ User logged in successfully: {user.email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=30 * 60  # 30 minutes in seconds
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    
    - **refresh_token**: Valid refresh token
    """
    # Verify refresh token
    logger.info("Token refresh attempt")
    user_id = verify_token(request.refresh_token, token_type="refresh")
    if not user_id:
        logger.warning("Token refresh failed: Invalid refresh token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = await UserRepository.get_by_user_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Create new tokens
    access_token = create_access_token(
        user_id=user.user_id,
        email=user.email
    )
    refresh_token = create_refresh_token(user_id=user.user_id)
    
    logger.info(f"✅ Token refreshed successfully for user: {user.email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=30 * 60
    )


@router.post("/logout", response_model=MessageResponse)
async def logout_user(current_user = Depends(get_current_active_user)):
    """
    Logout current user
    
    Note: With JWT, logout is primarily client-side (delete tokens)
    This endpoint is provided for completeness and future enhancements
    (e.g., token blacklisting)
    """
    logger.info(f"✅ User logged out: {current_user.email}")
    return MessageResponse(message="Successfully logged out")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_active_user)):
    """
    Get current user information
    
    Requires authentication (Bearer token)
    """
    return UserResponse.from_orm(current_user)


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    profile: UserProfileUpdate,
    current_user = Depends(get_current_active_user)
):
    """
    Update current user profile
    
    - **username**: New username (optional)
    """
    update_data = {}
    
    if profile.username:
        # Check if username is already taken by another user
        logger.info(f"Profile update attempt for user: {current_user.email}")
        existing_user = await UserRepository.get_by_username(profile.username)
        if existing_user and existing_user.user_id != current_user.user_id:
            logger.warning(f"Profile update failed: Username taken - {profile.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        update_data["username"] = profile.username
    
    if update_data:
        updated_user = await UserRepository.update(current_user.user_id, **update_data)
        logger.info(f"✅ User profile updated successfully: {current_user.email}")
        return UserResponse.from_orm(updated_user)
    
    return UserResponse.from_orm(current_user)


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user = Depends(get_current_active_user)
):
    """
    Change user password
    
    - **current_password**: Current password
    - **new_password**: New strong password
    """
    # Verify current password
    logger.info(f"Password change attempt for user: {current_user.email}")
    if not verify_password(request.current_password, current_user.hashed_password):
        logger.warning(f"Password change failed: Incorrect current password - {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Hash new password
    new_hashed_password = hash_password(request.new_password)
    
    # Update password
    await UserRepository.update(
        current_user.user_id,
        hashed_password=new_hashed_password
    )
    
    logger.info(f"✅ Password changed successfully for user: {current_user.email}")
    return MessageResponse(message="Password successfully changed")
