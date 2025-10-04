"""AI-related schemas"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class AIProviderInfo(BaseModel):
    """AI provider information"""
    name: str
    status: str = Field(description="Status: available, unavailable, error")
    model: Optional[str] = None
    features: List[str] = Field(default_factory=list)
    avg_response_time: Optional[float] = None


class AIAnalysisRequest(BaseModel):
    """Request for AI analysis"""
    analysis_type: str = Field(
        "comprehensive_analysis",
        description="Type: quick_analysis, comprehensive_analysis, production_coaching, creative_suggestions"
    )
    provider: Optional[str] = Field(None, description="Preferred provider: google_ai or openai")


class AIAnalysisResponse(BaseModel):
    """AI analysis results"""
    provider: str
    model: str
    summary: str
    detailed_analysis: Dict[str, Any]
    production_tips: List[str] = Field(default_factory=list)
    creative_ideas: List[str] = Field(default_factory=list)
    fl_studio_recommendations: List[str] = Field(default_factory=list)
    confidence_score: float
    processing_time: float
    tokens_used: int