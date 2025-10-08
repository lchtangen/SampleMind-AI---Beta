"""Intelligent AI provider routing with automatic fallbacks

This module routes AI requests to the optimal provider based on:
- Task type (genre classification, creative, factual, etc.)
- Priority (speed, quality, cost)
- Provider health and latency
- Automatic failover on errors

Provider priority:
1. Ollama (local, ultra-fast, free)
2. Gemini (fast, cheap, good quality)
3. Claude (smart, expensive, best quality)
4. OpenAI (fallback, reliable)

Expected benefits:
- <50ms for local Ollama requests
- Intelligent routing based on task requirements
- Automatic fallback on provider failures
- Cost optimization through smart routing
"""

from enum import Enum
from typing import Optional, Dict, Any
import logging
import os

logger = logging.getLogger(__name__)


class Provider(Enum):
    """AI provider enumeration with priority order"""
    OLLAMA = "ollama"      # Priority 0: Local, ultra-fast, free
    GEMINI = "gemini"      # Priority 1: Fast, cheap, good quality
    CLAUDE = "anthropic"   # Priority 2: Smart, expensive, best quality
    OPENAI = "openai"      # Priority 3: Fallback


class TaskType(Enum):
    """Task classification for intelligent routing"""
    GENRE_CLASSIFICATION = "genre"
    AUDIO_ANALYSIS = "audio"
    CREATIVE = "creative"
    FACTUAL = "factual"
    TOOL_CALLING = "tools"
    SUMMARIZATION = "summary"
    TRANSCRIPTION = "transcription"


# Provider API endpoints
PROVIDER_URLS = {
    Provider.OLLAMA: os.getenv(
        "OLLAMA_URL",
        "http://ollama:11434/api/generate"
    ),
    Provider.GEMINI: os.getenv(
        "GEMINI_URL",
        "https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash-exp:generateContent"
    ),
    Provider.CLAUDE: os.getenv(
        "CLAUDE_URL",
        "https://api.anthropic.com/v1/messages"
    ),
    Provider.OPENAI: os.getenv(
        "OPENAI_URL",
        "https://api.openai.com/v1/chat/completions"
    )
}

# Model selection per provider
PROVIDER_MODELS = {
    Provider.OLLAMA: "llama3.2:3b-instruct-q8_0",          # Fast, quantized
    Provider.GEMINI: "gemini-2.5-pro",                     # Latest (2M context)
    Provider.CLAUDE: "claude-4-sonnet-20250514",           # Best quality (200K context)
    Provider.OPENAI: "gpt-5"                               # Flagship model (256K context)
}

# Cost per 1M tokens (approximate USD)
PROVIDER_COSTS = {
    Provider.OLLAMA: 0.0,     # Free (local)
    Provider.GEMINI: 0.0,     # Free tier (50 requests/day)
    Provider.CLAUDE: 3.0,     # $3.00 per 1M tokens (Sonnet 4.5)
    Provider.OPENAI: 10.0     # $10.00 per 1M tokens (GPT-5)
}


def route_request(
    task_type: TaskType,
    priority: str = "speed",
    max_tokens: int = 1000
) -> Provider:
    """Route AI request to best provider based on requirements

    Routing logic:
    - Speed priority: Prefer local > fast cloud
    - Quality priority: Prefer Claude for creative, OpenAI for tools
    - Cost priority: Prefer local > Gemini

    Args:
        task_type: Type of AI task
        priority: "speed", "quality", or "cost"
        max_tokens: Expected token count (for cost estimation)

    Returns:
        Selected Provider enum
    """

    # Speed priority: minimize latency
    if priority == "speed":
        if task_type in [
            TaskType.GENRE_CLASSIFICATION,
            TaskType.FACTUAL,
            TaskType.SUMMARIZATION
        ]:
            # Short, factual tasks -> Ollama (local, <50ms)
            logger.debug(f"Routing {task_type.value} to Ollama (speed)")
            return Provider.OLLAMA
        elif task_type == TaskType.AUDIO_ANALYSIS:
            # Audio analysis -> Gemini (optimized for this)
            logger.debug(f"Routing {task_type.value} to Gemini (speed)")
            return Provider.GEMINI
        elif task_type == TaskType.CREATIVE:
            # Creative tasks -> Claude (best quality)
            logger.debug(f"Routing {task_type.value} to Claude (speed+quality)")
            return Provider.CLAUDE
        else:
            # Default to Ollama for speed
            return Provider.OLLAMA

    # Quality priority: best output
    elif priority == "quality":
        if task_type == TaskType.CREATIVE:
            # Creative -> Claude (best quality)
            logger.debug(f"Routing {task_type.value} to Claude (quality)")
            return Provider.CLAUDE
        elif task_type == TaskType.TOOL_CALLING:
            # Tools -> OpenAI (best function calling)
            logger.debug(f"Routing {task_type.value} to OpenAI (quality)")
            return Provider.OPENAI
        else:
            # General quality -> Gemini
            logger.debug(f"Routing {task_type.value} to Gemini (quality)")
            return Provider.GEMINI

    # Cost priority: minimize API costs
    elif priority == "cost":
        if task_type == TaskType.TOOL_CALLING:
            # Tools need OpenAI's specialized API
            logger.debug(f"Routing {task_type.value} to OpenAI (required)")
            return Provider.OPENAI
        else:
            # Everything else -> free local Ollama
            logger.debug(f"Routing {task_type.value} to Ollama (cost)")
            return Provider.OLLAMA

    # Default fallback
    logger.warning(f"Unknown priority '{priority}', defaulting to Ollama")
    return Provider.OLLAMA


def get_provider_url(provider: Provider) -> str:
    """Get API URL for provider

    Args:
        provider: Provider enum

    Returns:
        API endpoint URL
    """
    url = PROVIDER_URLS.get(provider)
    if not url:
        logger.error(f"No URL configured for {provider.value}")
        return PROVIDER_URLS[Provider.OLLAMA]  # Fallback to local
    return url


def get_provider_model(provider: Provider) -> str:
    """Get recommended model for provider

    Args:
        provider: Provider enum

    Returns:
        Model identifier
    """
    return PROVIDER_MODELS.get(provider, "default")


def estimate_cost(
    provider: Provider,
    input_tokens: int,
    output_tokens: int
) -> float:
    """Estimate cost for a request

    Args:
        provider: Provider to use
        input_tokens: Input token count
        output_tokens: Expected output tokens

    Returns:
        Estimated cost in USD
    """
    cost_per_million = PROVIDER_COSTS.get(provider, 0.0)
    total_tokens = input_tokens + output_tokens
    return (total_tokens / 1_000_000) * cost_per_million


def get_fallback_chain(primary: Provider) -> list[Provider]:
    """Get fallback providers in priority order

    If primary fails, try fallbacks in order.

    Args:
        primary: Primary provider

    Returns:
        Ordered list of fallback providers
    """
    all_providers = [
        Provider.OLLAMA,
        Provider.GEMINI,
        Provider.CLAUDE,
        Provider.OPENAI
    ]

    # Remove primary and return rest
    fallbacks = [p for p in all_providers if p != primary]

    logger.debug(
        f"Fallback chain for {primary.value}: "
        f"{[p.value for p in fallbacks]}"
    )

    return fallbacks


def get_routing_stats() -> Dict[str, Any]:
    """Get routing statistics

    Returns:
        Router configuration and costs
    """
    return {
        "providers": {
            provider.value: {
                "url": get_provider_url(provider),
                "model": get_provider_model(provider),
                "cost_per_1m_tokens": PROVIDER_COSTS.get(provider, 0.0)
            }
            for provider in Provider
        },
        "default_priority": "speed",
        "task_types": [t.value for t in TaskType]
    }
