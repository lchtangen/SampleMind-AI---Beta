"""API Key repository"""

from typing import Optional, List
from datetime import datetime
from samplemind.core.database.mongo import APIKey


class APIKeyRepository:
    """Repository for API key CRUD operations"""

    @staticmethod
    async def create(
        key_id: str,
        user_id: str,
        name: str,
        provider: str,
        key_hash: str,
        permissions: List[str],
        created_at: Optional[datetime] = None,
        is_active: bool = True
    ) -> APIKey:
        """Create new API key"""
        api_key = APIKey(
            key_id=key_id,
            user_id=user_id,
            name=name,
            provider=provider,
            key_hash=key_hash,
            permissions=permissions,
            is_active=is_active,
            created_at=created_at or datetime.utcnow()
        )
        await api_key.insert()
        return api_key

    @staticmethod
    async def get_by_id(key_id: str) -> Optional[APIKey]:
        """Get API key by ID"""
        return await APIKey.find_one(APIKey.key_id == key_id)

    @staticmethod
    async def get_by_user_id(
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> Optional[List[APIKey]]:
        """Get all API keys for a user"""
        return await APIKey.find(APIKey.user_id == user_id).skip(offset).limit(limit).to_list()

    @staticmethod
    async def get_by_hash(key_hash: str) -> Optional[APIKey]:
        """Get API key by hash"""
        return await APIKey.find_one(APIKey.key_hash == key_hash)

    @staticmethod
    async def update(key_id: str, **kwargs) -> Optional[APIKey]:
        """Update API key fields"""
        api_key = await APIKey.find_one(APIKey.key_id == key_id)
        if api_key:
            # Update all provided fields
            for key, value in kwargs.items():
                if hasattr(api_key, key):
                    setattr(api_key, key, value)
            # Always update the updated_at timestamp
            api_key.updated_at = datetime.utcnow()
            await api_key.save()
        return api_key

    @staticmethod
    async def delete(key_id: str) -> bool:
        """Delete API key"""
        api_key = await APIKey.find_one(APIKey.key_id == key_id)
        if api_key:
            await api_key.delete()
            return True
        return False

    @staticmethod
    async def toggle_active(key_id: str) -> Optional[APIKey]:
        """Toggle API key active status"""
        api_key = await APIKey.find_one(APIKey.key_id == key_id)
        if api_key:
            api_key.is_active = not api_key.is_active
            api_key.updated_at = datetime.utcnow()
            await api_key.save()
        return api_key

    @staticmethod
    async def update_last_used(key_id: str) -> Optional[APIKey]:
        """Update last used timestamp"""
        api_key = await APIKey.find_one(APIKey.key_id == key_id)
        if api_key:
            api_key.last_used = datetime.utcnow()
            api_key.updated_at = datetime.utcnow()
            await api_key.save()
        return api_key
