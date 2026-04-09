"""
LiteLLM Router — SampleMind v0.3.0

Unified multi-provider AI router using LiteLLM as the orchestration layer.
Provides automatic fallback: Claude (primary) → Gemini (fast) → GPT-4o → Ollama (offline).

Usage::

    from samplemind.integrations.litellm_router import get_router, chat_completion

    # Simple completion
    response = await chat_completion(
        messages=[{"role": "user", "content": "Analyze this sample: ..."}],
        prefer_fast=True,   # Uses Gemini flash
    )
    print(response.choices[0].message.content)

    # Streaming
    async for chunk in stream_completion(messages=[...]):
        print(chunk, end="", flush=True)

Configuration (env vars):
    ANTHROPIC_API_KEY   — Claude API key (primary)
    GEMINI_API_KEY      — Google Gemini API key (fast/cheap)
    OPENAI_API_KEY      — OpenAI GPT-4o key (agents)
    OLLAMA_BASE_URL     — Ollama server (default: http://localhost:11434)
    OLLAMA_MODEL        — Local model (default: qwen2.5-coder:7b)
    LITELLM_VERBOSE     — Set to "1" to enable debug logging
"""

from __future__ import annotations

import logging
import os
from collections.abc import AsyncIterator
from typing import Any

logger = logging.getLogger(__name__)

# ── Model constants ───────────────────────────────────────────────────────────

MODEL_PRIMARY = "claude-sonnet-4-6"  # Anthropic — best quality
MODEL_FAST = "gemini/gemini-2.5-flash"  # Google — fast/cheap
MODEL_AGENTS = "gpt-4o"  # OpenAI — tool use / agents
MODEL_OFFLINE = f"ollama/{os.getenv('OLLAMA_MODEL', 'qwen2.5-coder:7b')}"


def _get_fallback_list(
    prefer_fast: bool = False, agents_mode: bool = False
) -> list[dict]:
    """Build LiteLLM fallback model list."""
    if agents_mode:
        return [
            {"model": MODEL_AGENTS},
            {"model": MODEL_PRIMARY},
            {
                "model": MODEL_OFFLINE,
                "api_base": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            },
        ]
    if prefer_fast:
        return [
            {"model": MODEL_FAST},
            {"model": MODEL_PRIMARY},
            {
                "model": MODEL_OFFLINE,
                "api_base": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            },
        ]
    return [
        {"model": MODEL_PRIMARY},
        {"model": MODEL_FAST},
        {"model": MODEL_AGENTS},
        {
            "model": MODEL_OFFLINE,
            "api_base": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        },
    ]


# ── Router singleton ──────────────────────────────────────────────────────────

_router: Any = None


def get_router() -> Any:
    """
    Return the LiteLLM Router singleton.

    The router is created lazily on first call and reused thereafter.
    Configures round-robin fallback across all available providers.
    """
    global _router

    if _router is not None:
        return _router

    try:
        from litellm import Router

        model_list = []

        if os.getenv("ANTHROPIC_API_KEY"):
            model_list.append(
                {
                    "model_name": "primary",
                    "litellm_params": {
                        "model": MODEL_PRIMARY,
                        "api_key": os.getenv("ANTHROPIC_API_KEY"),
                    },
                }
            )

        if os.getenv("GEMINI_API_KEY"):
            model_list.append(
                {
                    "model_name": "fast",
                    "litellm_params": {
                        "model": MODEL_FAST,
                        "api_key": os.getenv("GEMINI_API_KEY"),
                    },
                }
            )

        if os.getenv("OPENAI_API_KEY"):
            model_list.append(
                {
                    "model_name": "agents",
                    "litellm_params": {
                        "model": MODEL_AGENTS,
                        "api_key": os.getenv("OPENAI_API_KEY"),
                    },
                }
            )

        # Always add Ollama (offline fallback — no key needed)
        model_list.append(
            {
                "model_name": "offline",
                "litellm_params": {
                    "model": MODEL_OFFLINE,
                    "api_base": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                },
            }
        )

        if not model_list:
            logger.warning(
                "No AI provider API keys configured — LiteLLM router disabled"
            )
            return None

        _router = Router(
            model_list=model_list,
            fallbacks=[
                {"primary": ["fast", "agents", "offline"]},
                {"fast": ["primary", "agents", "offline"]},
                {"agents": ["primary", "fast", "offline"]},
            ],
            num_retries=2,
            retry_after=1,
            allowed_fails=2,
            cooldown_time=30,
            routing_strategy="least-busy",
        )

        providers = [m["model_name"] for m in model_list]
        logger.info("✓ LiteLLM router initialized with providers: %s", providers)
        return _router

    except ImportError:
        logger.warning("litellm not installed — run: uv add litellm")
        return None
    except Exception as exc:
        logger.error("LiteLLM router initialization failed: %s", exc)
        return None


# ── Convenience functions ─────────────────────────────────────────────────────


async def chat_completion(
    messages: list[dict],
    prefer_fast: bool = False,
    agents_mode: bool = False,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    **kwargs: Any,
) -> Any:
    """
    Async chat completion with automatic provider fallback.

    Args:
        messages: OpenAI-format messages list.
        prefer_fast: Use Gemini Flash as primary (cheaper, faster).
        agents_mode: Use GPT-4o as primary (best for tool use).
        temperature: Sampling temperature (0–2).
        max_tokens: Maximum tokens to generate.
        **kwargs: Extra kwargs forwarded to litellm.acompletion.

    Returns:
        LiteLLM ModelResponse object.

    Raises:
        RuntimeError: If no providers available and no fallback possible.
    """
    try:
        import litellm

        if os.getenv("LITELLM_VERBOSE") == "1":
            litellm.set_verbose = True

        router = get_router()
        if router:
            model_name = (
                "fast" if prefer_fast else ("agents" if agents_mode else "primary")
            )
            return await router.acompletion(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

        # Direct fallback without router
        fallbacks = _get_fallback_list(prefer_fast=prefer_fast, agents_mode=agents_mode)
        for fb in fallbacks:
            try:
                model = fb["model"]
                extra: dict = {}
                if "api_base" in fb:
                    extra["api_base"] = fb["api_base"]
                return await litellm.acompletion(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **extra,
                    **kwargs,
                )
            except Exception as exc:
                logger.debug("Provider %s failed: %s — trying next", model, exc)

        raise RuntimeError("All LiteLLM providers failed")

    except ImportError:
        logger.error("litellm not installed — cannot complete chat")
        raise


async def stream_completion(
    messages: list[dict],
    prefer_fast: bool = False,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    **kwargs: Any,
) -> AsyncIterator[str]:
    """
    Async streaming chat completion.

    Yields text deltas as they arrive from the provider.
    Falls back to non-streaming if the provider doesn't support it.
    """
    try:
        import litellm

        fallbacks = _get_fallback_list(prefer_fast=prefer_fast)
        for fb in fallbacks:
            try:
                model = fb["model"]
                extra: dict = {}
                if "api_base" in fb:
                    extra["api_base"] = fb["api_base"]

                response = await litellm.acompletion(
                    model=model,
                    messages=messages,
                    stream=True,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **extra,
                    **kwargs,
                )
                async for chunk in response:
                    delta = chunk.choices[0].delta.content or ""
                    if delta:
                        yield delta
                return

            except Exception as exc:
                logger.debug("Streaming provider %s failed: %s", fb["model"], exc)

        raise RuntimeError("All streaming providers failed")

    except ImportError:
        logger.error("litellm not installed")
        raise


def get_available_providers() -> list[str]:
    """Return list of configured provider names based on env vars."""
    providers = []
    if os.getenv("ANTHROPIC_API_KEY"):
        providers.append("anthropic/claude-sonnet-4-6")
    if os.getenv("GEMINI_API_KEY"):
        providers.append("gemini/gemini-2.5-flash")
    if os.getenv("OPENAI_API_KEY"):
        providers.append("openai/gpt-4o")
    providers.append(f"ollama/{os.getenv('OLLAMA_MODEL', 'qwen2.5-coder:7b')}")
    return providers
