"""AI performance optimization modules"""
from .cache import get_cached_response, cache_response, cache_key, prompt_fingerprint, get_cache_stats, clear_provider_cache
from .http_client import get_http_client, close_http_client, make_ai_request, make_streaming_request
from .router import Provider, TaskType, route_request, get_provider_url, get_provider_model, estimate_cost, get_fallback_chain
from .warm import warm_cache_for_provider, warm_all_caches, schedule_cache_warming, COMMON_PROMPTS
from .providers import (
    StreamingMode,
    get_task_config,
    should_stream,
    build_openai_request,
    build_anthropic_request,
    build_gemini_request,
    build_ollama_request,
    build_provider_request,
    get_provider_headers,
    get_provider_stats,
    get_anthropic_headers,
    get_gemini_model,
    get_ollama_model_for_task,
    optimize_for_tool_calling,
    OLLAMA_MODELS,
    TASK_CONFIGS,
)

__all__ = [
    # Cache
    "get_cached_response",
    "cache_response",
    "cache_key",
    "prompt_fingerprint",
    "get_cache_stats",
    "clear_provider_cache",
    # HTTP Client
    "get_http_client",
    "close_http_client",
    "make_ai_request",
    "make_streaming_request",
    # Router
    "Provider",
    "TaskType",
    "route_request",
    "get_provider_url",
    "get_provider_model",
    "estimate_cost",
    "get_fallback_chain",
    # Cache warming
    "warm_cache_for_provider",
    "warm_all_caches",
    "schedule_cache_warming",
    "COMMON_PROMPTS",
    # Provider features
    "StreamingMode",
    "get_task_config",
    "should_stream",
    "build_openai_request",
    "build_anthropic_request",
    "build_gemini_request",
    "build_ollama_request",
    "build_provider_request",
    "get_provider_headers",
    "get_provider_stats",
    "get_anthropic_headers",
    "get_gemini_model",
    "get_ollama_model_for_task",
    "optimize_for_tool_calling",
    "OLLAMA_MODELS",
    "TASK_CONFIGS",
]
