"""Telemetry schemas"""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field
from pydantic import AliasChoices


class RecommendationTelemetryEvent(BaseModel):
    event: Literal['view', 'preview', 'accept', 'skip']
    audio_id: Optional[int] = Field(default=None, ge=1)
    score: Optional[float] = None
    rank: Optional[int] = Field(default=None, ge=0)
    source: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RecommendationTelemetryBatch(BaseModel):
    session_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices('session_id', 'sessionId'),
    )
    events: List[RecommendationTelemetryEvent] = Field(default_factory=list)
