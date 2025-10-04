"""
SampleMind AI Integrations
Multi-provider AI integration layer for music analysis

Supports:
- Google Gemini (Primary): Fast audio analysis & genre classification
- Anthropic Claude (Specialist): Production coaching & creative suggestions
- OpenAI GPT (Fallback): Emergency backup
"""

from .google_ai_integration import GoogleAIMusicProducer
from .openai_integration import OpenAIMusicProducer
from .ai_manager import SampleMindAIManager, AIProviderConfig, AIProvider, AnalysisType

try:
    from .anthropic_integration import AnthropicMusicProducer
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    AnthropicMusicProducer = None

__all__ = [
    'GoogleAIMusicProducer',
    'OpenAIMusicProducer',
    'AnthropicMusicProducer',
    'SampleMindAIManager',
    'AIProviderConfig',
    'AIProvider',
    'AnalysisType',
    'ANTHROPIC_AVAILABLE',
]
