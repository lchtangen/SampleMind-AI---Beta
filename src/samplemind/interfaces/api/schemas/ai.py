"""AI-related schemas"""

from typing import Any

from pydantic import BaseModel, Field


class AIProviderInfo(BaseModel):
    """AI provider information"""

    name: str
    status: str = Field(description="Status: available, unavailable, error")
    model: str | None = None
    features: list[str] = Field(default_factory=list)
    avg_response_time: float | None = None


class AIAnalysisRequest(BaseModel):
    """Request for AI analysis"""

    analysis_type: str = Field(
        "comprehensive_analysis",
        description="Type: quick_analysis, comprehensive_analysis, production_coaching, creative_suggestions",
    )
    provider: str | None = Field(
        None, description="Preferred provider: google_ai or openai"
    )


class AIAnalysisResponse(BaseModel):
    """AI analysis results"""

    provider: str
    model: str
    summary: str
    detailed_analysis: dict[str, Any]
    production_tips: list[str] = Field(default_factory=list)
    creative_ideas: list[str] = Field(default_factory=list)
    fl_studio_recommendations: list[str] = Field(default_factory=list)
    confidence_score: float
    processing_time: float
    tokens_used: int
