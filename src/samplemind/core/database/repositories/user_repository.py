"""User repository"""

from typing import Optional, Any
from datetime import datetime
from samplemind.core.database.mongo import User


class UserRepository:
    """Repository for user CRUD operations (for future auth)"""

    @staticmethod
    async def create(
        user_id: str,
        email: str,
        username: str,
        hashed_password: str,
        is_active: bool = True,
        is_verified: bool = False,
        created_at: Optional[datetime] = None
    ) -> User:
        """Create new user"""
        user = User(
            user_id=user_id,
            email=email,
            username=username,
            hashed_password=hashed_password,
            is_active=is_active,
            is_verified=is_verified,
            created_at=created_at or datetime.utcnow()
        )
        await user.insert()
        return user

    @staticmethod
    async def get_by_id(user_id: str) -> Optional[User]:
        """Get user by ID"""
        return await User.find_one(User.user_id == user_id)

    @staticmethod
    async def get_by_user_id(user_id: str) -> Optional[User]:
        """Get user by user ID (alias for get_by_id)"""
        return await User.find_one(User.user_id == user_id)

    @staticmethod
    async def get_by_email(email: str) -> Optional[User]:
        """Get user by email"""
        return await User.find_one(User.email == email)

    @staticmethod
    async def get_by_username(username: str) -> Optional[User]:
        """Get user by username"""
        return await User.find_one(User.username == username)

    @staticmethod
    async def update(user_id: str, **kwargs) -> Optional[User]:
        """Update user fields"""
        user = await User.find_one(User.user_id == user_id)
        if user:
            # Update all provided fields
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            # Always update the updated_at timestamp
            user.updated_at = datetime.utcnow()
            await user.save()
        return user

    @staticmethod
    async def update_last_login(user_id: str) -> Optional[User]:
        """Update user last login timestamp"""
        user = await User.find_one(User.user_id == user_id)
        if user:
            user.last_login = datetime.utcnow()
            user.updated_at = datetime.utcnow()
            await user.save()
        return user

    @staticmethod
    async def increment_usage(user_id: str, analyses: int = 0, uploads: int = 0) -> Optional[User]:
        """Increment user usage counters"""
        user = await User.find_one(User.user_id == user_id)
        if user:
            user.total_analyses += analyses
            user.total_uploads += uploads
            user.updated_at = datetime.utcnow()
            await user.save()
        return user