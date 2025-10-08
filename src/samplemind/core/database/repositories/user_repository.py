"""User repository"""

from typing import Optional
from datetime import datetime
from samplemind.core.database.mongo import User


class UserRepository:
    """Repository for user CRUD operations (for future auth)"""
    
    @staticmethod
    async def create(
        user_id: str,
        email: str,
        username: str,
        hashed_password: str
    ) -> User:
        """Create new user"""
        user = User(
            user_id=user_id,
            email=email,
            username=username,
            hashed_password=hashed_password
        )
        await user.insert()
        return user
    
    @staticmethod
    async def get_by_id(user_id: str) -> Optional[User]:
        """Get user by ID"""
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
    async def find_one(filter_dict: dict) -> Optional[User]:
        """Find single user matching filter criteria"""
        if 'username' in filter_dict:
            return await User.find_one(User.username == filter_dict['username'])
        elif 'email' in filter_dict:
            return await User.find_one(User.email == filter_dict['email'])
        elif 'user_id' in filter_dict:
            return await User.find_one(User.user_id == filter_dict['user_id'])
        return None
    
    @staticmethod
    async def update(user_id: str, **kwargs) -> Optional[User]:
        """Update user fields"""
        user = await User.find_one(User.user_id == user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            await user.save()
        return user
    
    @staticmethod
    async def update_last_login(user_id: str) -> Optional[User]:
        """Update user last login timestamp"""
        user = await User.find_one(User.user_id == user_id)
        if user:
            user.last_login = datetime.utcnow()
            await user.save()
        return user
    
    @staticmethod
    async def increment_usage(user_id: str, analyses: int = 0, uploads: int = 0) -> Optional[User]:
        """Increment user usage counters"""
        user = await User.find_one(User.user_id == user_id)
        if user:
            user.total_analyses += analyses
            user.total_uploads += uploads
            await user.save()
        return user