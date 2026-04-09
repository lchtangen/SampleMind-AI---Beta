"""Common schemas used across the API"""

from typing import Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response"""

    error: str
    message: str
    details: dict[str, Any] | None = None


class HealthCheckResponse(BaseModel):
    """Health check response"""

    status: str = "healthy"
    version: str
    environment: str
    components: dict[str, str] = Field(default_factory=dict)


class PaginationParams(BaseModel):
    """Pagination parameters"""

    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(50, ge=1, le=100, description="Items per page")
