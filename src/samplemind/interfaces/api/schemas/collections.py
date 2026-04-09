from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CollectionBase(BaseModel):
    """Base schema for Collection"""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    is_public: bool = False
    tags: list[str] = []
    metadata: dict[str, Any] = {}


class CollectionCreate(CollectionBase):
    """Schema for creating a collection"""

    pass


class CollectionUpdate(BaseModel):
    """Schema for updating a collection"""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    is_public: bool | None = None
    tags: list[str] | None = None
    metadata: dict[str, Any] | None = None


class CollectionResponse(CollectionBase):
    """Schema for collection response"""

    id: str
    user_id: str
    file_count: int = 0
    total_duration: float = 0.0
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration for ORM mode compatibility."""

        from_attributes = True
