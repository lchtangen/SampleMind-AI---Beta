from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CollectionBase(BaseModel):
    """Base schema for Collection"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: bool = False
    tags: List[str] = []
    metadata: Dict[str, Any] = {}

class CollectionCreate(CollectionBase):
    """Schema for creating a collection"""
    pass

class CollectionUpdate(BaseModel):
    """Schema for updating a collection"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class CollectionResponse(CollectionBase):
    """Schema for collection response"""
    id: str
    user_id: str
    file_count: int = 0
    total_duration: float = 0.0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
