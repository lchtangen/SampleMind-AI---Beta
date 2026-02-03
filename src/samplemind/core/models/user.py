"""
User data models with role support
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from ..auth.rbac import UserRole


class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    username: str
    role: UserRole = UserRole.FREE
    is_active: bool = True
    is_verified: bool = False


class UserCreate(BaseModel):
    """User creation model"""
    email: EmailStr
    username: str
    password: str
    role: UserRole = UserRole.FREE


class UserUpdate(BaseModel):
    """User update model"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserInDB(UserBase):
    """User model as stored in database"""
    id: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    # Usage tracking
    total_uploads: int = 0
    storage_used_mb: float = 0.0
    api_calls_today: int = 0
    
    # Metadata
    metadata: dict = Field(default_factory=dict)


class UserPublic(UserBase):
    """Public user model (no sensitive data)"""
    id: str
    created_at: datetime
    
    class Config:
        """Pydantic config for UserPublic"""
        from_attributes = True


class UserWithStats(UserPublic):
    """User model with usage statistics"""
    total_uploads: int
    storage_used_mb: float
    collections_count: int = 0
    
    # Role limits
    max_uploads_per_day: int
    max_storage_mb: int
    max_collections: int
    
    class Config:
        """Pydantic config for UserWithStats"""
        from_attributes = True


class UserRoleUpdate(BaseModel):
    """Model for updating user role (admin only)"""
    user_id: str
    new_role: UserRole
    reason: Optional[str] = None


class UserList(BaseModel):
    """Paginated user list"""
    users: List[UserPublic]
    total: int
    page: int
    page_size: int
    has_more: bool
