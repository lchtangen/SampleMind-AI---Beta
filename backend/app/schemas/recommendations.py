"""Recommendation-related schemas"""

from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class SessionContext(BaseModel):
    bpm: Optional[float] = Field(None, ge=0)
    key: Optional[str] = None
    mode: Optional[str] = None
    mood_tags: List[str] = Field(default_factory=list)
    genre: Optional[str] = None
    energy: Optional[float] = Field(None, ge=0.0, le=1.0)
    project_id: Optional[str] = None
    user_preferences: List[str] = Field(default_factory=list)
    target_embedding: Optional[List[float]] = Field(default=None)
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ContextUpdateRequest(BaseModel):
    context: SessionContext


class RecommendationRequest(BaseModel):
    top_k: int = Field(default=10, ge=1, le=50)
    include_rationale: bool = False
    mode: Optional[Literal['fusion', 'rules']] = None


class RecommendationItem(BaseModel):
    audio_id: int
    filename: Optional[str] = None
    score: float = Field(..., ge=0.0)
    rationale: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    tempo: Optional[float] = None
    source: Optional[str] = None
    score_components: Optional[Dict[str, float]] = None


class RecommendationResponse(BaseModel):
    context: SessionContext
    suggestions: List[RecommendationItem] = Field(default_factory=list)
    mode: Optional[str] = None

    class Config:
        orm_mode = True
