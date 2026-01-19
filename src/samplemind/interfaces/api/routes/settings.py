"""
Settings and User Preferences API Routes
User configuration, API key management, preferences
"""

import logging
import secrets
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from samplemind.interfaces.api.schemas.settings import (
    APIKeyCreate,
    APIKeyResponse,
    APIKeyWithSecret,
    UserSettingsResponse,
    UserSettingsUpdate,
    PreferencesResponse,
    UserPreferences,
    AnalysisPreferences,
    UIPreferences,
    NotificationPreferences,
    CloudSyncSettings,
    PrivacySettings,
    StorageStatsResponse,
    ApiKeysListResponse,
    MessageResponse,
)
from samplemind.core.auth import get_current_active_user
from samplemind.core.database.repositories import UserRepository, APIKeyRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/user", response_model=UserSettingsResponse)
async def get_user_settings(current_user=Depends(get_current_active_user)):
    """
    Get current user settings and preferences

    Requires authentication (Bearer token)
    """
    logger.info(f"Fetching settings for user: {current_user.user_id}")

    try:
        # Get user settings from database (or use defaults)
        user_data = await UserRepository.get_by_user_id(current_user.user_id)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Get API keys count
        api_keys = await APIKeyRepository.get_by_user_id(current_user.user_id)
        api_keys_count = len(api_keys) if api_keys else 0

        # Get preferences (from database or defaults)
        preferences = UserPreferences()
        if hasattr(user_data, 'preferences') and user_data.preferences:
            preferences = UserPreferences(**user_data.preferences)

        return UserSettingsResponse(
            user_id=current_user.user_id,
            username=user_data.username,
            email=user_data.email,
            avatar_url=getattr(user_data, 'avatar_url', None),
            bio=getattr(user_data, 'bio', None),
            preferences=preferences,
            api_keys_count=api_keys_count,
            storage_used_mb=getattr(user_data, 'storage_used_mb', 0),
            total_uploads=getattr(user_data, 'total_uploads', 0),
            total_analyses=getattr(user_data, 'total_analyses', 0),
            created_at=user_data.created_at,
            updated_at=getattr(user_data, 'updated_at', datetime.utcnow())
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch user settings: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user settings"
        )


@router.put("/user", response_model=UserSettingsResponse)
async def update_user_settings(
    settings_update: UserSettingsUpdate,
    current_user=Depends(get_current_active_user)
):
    """
    Update current user settings and preferences

    - **username**: New username (optional)
    - **avatar_url**: Avatar image URL (optional)
    - **bio**: User biography (optional)
    - **preferences**: User preferences including analysis, UI, notifications, cloud sync (optional)
    """
    logger.info(f"Updating settings for user: {current_user.user_id}")

    try:
        update_data = {}

        # Update username if provided
        if settings_update.username:
            existing = await UserRepository.get_by_username(settings_update.username)
            if existing and existing.user_id != current_user.user_id:
                logger.warning(f"Username already taken: {settings_update.username}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            update_data['username'] = settings_update.username

        # Update other fields
        if settings_update.avatar_url:
            update_data['avatar_url'] = settings_update.avatar_url
        if settings_update.bio:
            update_data['bio'] = settings_update.bio

        # Update preferences
        if settings_update.preferences:
            update_data['preferences'] = settings_update.preferences.dict()

        update_data['updated_at'] = datetime.utcnow()

        # Save to database
        updated_user = await UserRepository.update(current_user.user_id, **update_data)

        # Get API keys count
        api_keys = await APIKeyRepository.get_by_user_id(current_user.user_id)
        api_keys_count = len(api_keys) if api_keys else 0

        # Get preferences
        preferences = UserPreferences()
        if hasattr(updated_user, 'preferences') and updated_user.preferences:
            preferences = UserPreferences(**updated_user.preferences)

        logger.info(f"✅ Settings updated for user: {current_user.user_id}")

        return UserSettingsResponse(
            user_id=updated_user.user_id,
            username=updated_user.username,
            email=updated_user.email,
            avatar_url=getattr(updated_user, 'avatar_url', None),
            bio=getattr(updated_user, 'bio', None),
            preferences=preferences,
            api_keys_count=api_keys_count,
            storage_used_mb=getattr(updated_user, 'storage_used_mb', 0),
            total_uploads=getattr(updated_user, 'total_uploads', 0),
            total_analyses=getattr(updated_user, 'total_analyses', 0),
            created_at=updated_user.created_at,
            updated_at=getattr(updated_user, 'updated_at', datetime.utcnow())
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user settings: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user settings"
        )


@router.get("/preferences", response_model=PreferencesResponse)
async def get_preferences(current_user=Depends(get_current_active_user)):
    """
    Get user preferences

    Returns analysis, UI, notification, cloud sync, and custom preferences
    """
    logger.info(f"Fetching preferences for user: {current_user.user_id}")

    try:
        user_data = await UserRepository.get_by_user_id(current_user.user_id)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        preferences = UserPreferences()
        if hasattr(user_data, 'preferences') and user_data.preferences:
            preferences = UserPreferences(**user_data.preferences)

        return PreferencesResponse(
            preferences=preferences,
            updated_at=getattr(user_data, 'updated_at', datetime.utcnow())
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch preferences: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch preferences"
        )


@router.put("/preferences", response_model=PreferencesResponse)
async def update_preferences(
    preferences: UserPreferences,
    current_user=Depends(get_current_active_user)
):
    """
    Update user preferences

    Update analysis settings, UI preferences, notifications, cloud sync, and custom settings
    """
    logger.info(f"Updating preferences for user: {current_user.user_id}")

    try:
        update_data = {
            'preferences': preferences.dict(),
            'updated_at': datetime.utcnow()
        }

        updated_user = await UserRepository.update(current_user.user_id, **update_data)

        logger.info(f"✅ Preferences updated for user: {current_user.user_id}")

        return PreferencesResponse(
            preferences=preferences,
            updated_at=update_data['updated_at']
        )

    except Exception as e:
        logger.error(f"Failed to update preferences: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences"
        )


# ============================================================================
# API Key Management
# ============================================================================

@router.post("/api-keys", response_model=APIKeyWithSecret, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    request: APIKeyCreate,
    current_user=Depends(get_current_active_user)
):
    """
    Create a new API key for the current user

    - **name**: Descriptive name for the API key
    - **provider**: Provider name (e.g., 'custom', 'plugin')
    - **permissions**: List of permissions (e.g., ['read', 'write'])

    Returns the API key secret (shown only once!)
    """
    logger.info(f"Creating API key for user: {current_user.user_id}")

    try:
        # Generate secure key
        key_secret = secrets.token_urlsafe(32)
        key_id = str(uuid.uuid4())

        # Store API key in database
        api_key = await APIKeyRepository.create(
            key_id=key_id,
            user_id=current_user.user_id,
            name=request.name,
            provider=request.provider,
            key_hash=hash(key_secret),  # Store hash, not secret
            permissions=request.permissions,
            created_at=datetime.utcnow(),
            is_active=True
        )

        logger.info(f"✅ API key created for user: {current_user.user_id} (name: {request.name})")

        return APIKeyWithSecret(
            key_id=api_key.key_id,
            name=api_key.name,
            provider=api_key.provider,
            permissions=api_key.permissions,
            secret=key_secret,
            created_at=api_key.created_at,
            is_active=api_key.is_active
        )

    except Exception as e:
        logger.error(f"Failed to create API key: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create API key"
        )


@router.get("/api-keys", response_model=ApiKeysListResponse)
async def list_api_keys(
    current_user=Depends(get_current_active_user),
    limit: int = 50,
    offset: int = 0
):
    """
    List all API keys for the current user

    Returns API keys without secrets (secrets are shown only on creation)
    """
    logger.info(f"Listing API keys for user: {current_user.user_id}")

    try:
        api_keys = await APIKeyRepository.get_by_user_id(
            current_user.user_id,
            limit=limit,
            offset=offset
        )

        if not api_keys:
            api_keys = []

        keys_response = [
            APIKeyResponse(
                key_id=key.key_id,
                name=key.name,
                provider=key.provider,
                permissions=getattr(key, 'permissions', []),
                created_at=key.created_at,
                last_used=getattr(key, 'last_used', None),
                is_active=getattr(key, 'is_active', True)
            )
            for key in api_keys
        ]

        return ApiKeysListResponse(
            keys=keys_response,
            total=len(api_keys)
        )

    except Exception as e:
        logger.error(f"Failed to list API keys: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list API keys"
        )


@router.delete("/api-keys/{key_id}", response_model=MessageResponse)
async def delete_api_key(
    key_id: str,
    current_user=Depends(get_current_active_user)
):
    """
    Delete an API key

    - **key_id**: API key ID to delete
    """
    logger.info(f"Deleting API key for user: {current_user.user_id}")

    try:
        # Verify the key belongs to the user
        api_key = await APIKeyRepository.get_by_id(key_id)
        if not api_key or api_key.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )

        # Delete the key
        await APIKeyRepository.delete(key_id)

        logger.info(f"✅ API key deleted for user: {current_user.user_id}")

        return MessageResponse(message="API key successfully deleted")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete API key: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete API key"
        )


@router.put("/api-keys/{key_id}/toggle", response_model=APIKeyResponse)
async def toggle_api_key(
    key_id: str,
    current_user=Depends(get_current_active_user)
):
    """
    Toggle an API key's active status

    Deactivated keys cannot be used for authentication
    """
    logger.info(f"Toggling API key for user: {current_user.user_id}")

    try:
        # Verify the key belongs to the user
        api_key = await APIKeyRepository.get_by_id(key_id)
        if not api_key or api_key.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )

        # Toggle active status
        new_status = not getattr(api_key, 'is_active', True)
        updated_key = await APIKeyRepository.update(
            key_id,
            is_active=new_status,
            updated_at=datetime.utcnow()
        )

        logger.info(f"✅ API key toggled for user: {current_user.user_id}")

        return APIKeyResponse(
            key_id=updated_key.key_id,
            name=updated_key.name,
            provider=updated_key.provider,
            permissions=getattr(updated_key, 'permissions', []),
            created_at=updated_key.created_at,
            last_used=getattr(updated_key, 'last_used', None),
            is_active=getattr(updated_key, 'is_active', True)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to toggle API key: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle API key"
        )


# ============================================================================
# Storage and Statistics
# ============================================================================

@router.get("/storage", response_model=StorageStatsResponse)
async def get_storage_stats(current_user=Depends(get_current_active_user)):
    """
    Get storage usage and statistics for the current user
    """
    logger.info(f"Fetching storage stats for user: {current_user.user_id}")

    try:
        user_data = await UserRepository.get_by_user_id(current_user.user_id)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        storage_used = getattr(user_data, 'storage_used_mb', 0)
        storage_quota = getattr(user_data, 'storage_quota_mb', 1000)  # Default 1GB

        percent_used = (storage_used / storage_quota * 100) if storage_quota > 0 else 0

        return StorageStatsResponse(
            storage_used_mb=storage_used,
            storage_quota_mb=storage_quota,
            storage_percent_used=percent_used,
            total_files=getattr(user_data, 'total_uploads', 0),
            total_analyses=getattr(user_data, 'total_analyses', 0),
            last_cleanup=getattr(user_data, 'last_cleanup', None)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch storage stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch storage stats"
        )
