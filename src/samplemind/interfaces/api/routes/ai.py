"""AI integration endpoints"""

from typing import List
from fastapi import APIRouter
from samplemind.interfaces.api.schemas.ai import AIProviderInfo, AIAnalysisRequest, AIAnalysisResponse
from samplemind.interfaces.api.dependencies import get_app_state
from samplemind.integrations.ai_manager import AIProvider

router = APIRouter()


@router.get("/providers", response_model=List[AIProviderInfo])
async def list_ai_providers():
    """List available AI providers and their status"""
    ai_manager = get_app_state("ai_manager")
    
    if not ai_manager:
        return []
    
    providers = ai_manager.get_available_providers()
    stats = ai_manager.get_global_stats()
    
    result = []
    for provider in [AIProvider.GOOGLE_AI, AIProvider.OPENAI]:
        is_available = provider in providers
        provider_stats = stats.get("provider_usage", {}).get(provider.value, {})
        
        result.append(AIProviderInfo(
            name=provider.value,
            status="available" if is_available else "unavailable",
            model=provider_stats.get("model"),
            features=["comprehensive_analysis", "production_coaching", "creative_suggestions"],
            avg_response_time=provider_stats.get("avg_response_time")
        ))
    
    return result
