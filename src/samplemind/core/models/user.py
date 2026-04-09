"""
User data models with role support
"""

from datetime import datetime

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

    email: EmailStr | None = None
    username: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None
    is_verified: bool | None = None


class UserInDB(UserBase):
    """User model as stored in database"""

    id: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None = None

    # Usage tracking
    total_uploads: int = 0
    storage_used_mb: float = 0.0
    api_calls_today: int = 0
    api_calls_this_month: int = 0

    # Billing
    stripe_customer_id: str | None = None
    tier: str = "free"  # "free" | "pro" | "team"

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
    reason: str | None = None


class UserList(BaseModel):
    """Paginated user list"""

    users: list[UserPublic]
    total: int
    page: int
    page_size: int
    has_more: bool
