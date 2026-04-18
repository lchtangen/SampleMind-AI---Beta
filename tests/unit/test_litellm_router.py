"""
Unit tests for samplemind.integrations.litellm_router

litellm and external providers are fully mocked so no API keys are needed.

Module under test:
    samplemind.integrations.litellm_router
        — chat_completion, get_router, get_available_providers,
          _get_fallback_list, MODEL_PRIMARY, MODEL_FAST, MODEL_AGENTS,
          MODEL_OFFLINE

Key test scenarios:
    _get_fallback_list
        - Default list starts with MODEL_PRIMARY.
        - ``prefer_fast=True`` starts with MODEL_FAST.
        - ``agents_mode=True`` starts with MODEL_AGENTS.
        - Every variant includes the offline/Ollama model as a fallback.
    get_available_providers
        - Always includes Ollama (local, always available).
        - Includes Anthropic/Claude when ANTHROPIC_API_KEY is set.
        - Returns only local providers when no cloud API keys are present.
    get_router
        - Returns None when litellm is not importable.
        - Singleton behaviour (same object returned on repeated calls).
    chat_completion
        - Delegates to router.acompletion when a router is available.
        - Falls back to direct litellm.acompletion when router is None.
        - Raises RuntimeError when all providers fail.
    prefer_fast / agents_mode routing
        - ``prefer_fast=True`` routes the call with model="fast".
"""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import samplemind.integrations.litellm_router as lr_mod
from samplemind.integrations.litellm_router import (
    MODEL_AGENTS,
    MODEL_FAST,
    MODEL_OFFLINE,
    MODEL_PRIMARY,
    _get_fallback_list,
    get_available_providers,
    get_router,
)

# ── _get_fallback_list ────────────────────────────────────────────────────────


def test_default_fallback_starts_with_primary():
    fbs = _get_fallback_list()
    assert fbs[0]["model"] == MODEL_PRIMARY


def test_prefer_fast_fallback_starts_with_fast():
    fbs = _get_fallback_list(prefer_fast=True)
    assert fbs[0]["model"] == MODEL_FAST


def test_agents_mode_fallback_starts_with_agents():
    fbs = _get_fallback_list(agents_mode=True)
    assert fbs[0]["model"] == MODEL_AGENTS


def test_all_fallbacks_include_offline():
    for kwargs in [{}, {"prefer_fast": True}, {"agents_mode": True}]:
        fbs = _get_fallback_list(**kwargs)
        models = [fb["model"] for fb in fbs]
        assert any(MODEL_OFFLINE in m for m in models), f"Offline not in {models}"


# ── get_available_providers ───────────────────────────────────────────────────


def test_available_providers_always_includes_ollama():
    with patch.dict(os.environ, {}, clear=True):
        providers = get_available_providers()
    assert any("ollama" in p for p in providers)


def test_available_providers_includes_anthropic_when_key_set():
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake-key"}):
        providers = get_available_providers()
    assert any("claude" in p for p in providers)


def test_available_providers_no_cloud_when_no_keys():
    env = dict.fromkeys(("ANTHROPIC_API_KEY", "GEMINI_API_KEY", "OPENAI_API_KEY"), "")
    with patch.dict(os.environ, env, clear=False):
        # Remove the keys so getenv returns None
        for k in env:
            os.environ.pop(k, None)
        providers = get_available_providers()
    assert all("ollama" in p or "qwen" in p for p in providers)


# ── get_router ────────────────────────────────────────────────────────────────


def test_get_router_returns_none_without_litellm():
    lr_mod._router = None  # reset singleton

    with patch.dict("sys.modules", {"litellm": None}):
        result = get_router()

    assert result is None
    lr_mod._router = None


def test_get_router_singleton():
    lr_mod._router = None

    fake_router = MagicMock()
    fake_Router_cls = MagicMock(return_value=fake_router)
    fake_litellm = MagicMock()
    fake_litellm.Router = fake_Router_cls

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "k"}):
        with patch.dict("sys.modules", {"litellm": fake_litellm}):
            r1 = get_router()
            r2 = get_router()

    assert r1 is r2  # same object (singleton)
    lr_mod._router = None


# ── chat_completion ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_chat_completion_uses_router_when_available():
    lr_mod._router = None

    fake_response = MagicMock()
    fake_response.choices = [MagicMock()]
    fake_response.choices[0].message.content = "Hello"

    fake_router = MagicMock()
    fake_router.acompletion = AsyncMock(return_value=fake_response)

    with patch(
        "samplemind.integrations.litellm_router.get_router", return_value=fake_router
    ):
        with patch.dict("sys.modules", {"litellm": MagicMock()}):
            from samplemind.integrations.litellm_router import chat_completion

            resp = await chat_completion(
                messages=[{"role": "user", "content": "hello"}]
            )

    assert resp is fake_response
    fake_router.acompletion.assert_called_once()


@pytest.mark.asyncio
async def test_chat_completion_falls_back_when_router_none():
    """When router is None, falls back to direct litellm.acompletion calls."""
    fake_response = MagicMock()
    fake_litellm = MagicMock()
    fake_litellm.acompletion = AsyncMock(return_value=fake_response)

    with patch("samplemind.integrations.litellm_router.get_router", return_value=None):
        with patch.dict("sys.modules", {"litellm": fake_litellm}):
            import samplemind.integrations.litellm_router as reloaded

            # Patch directly on the module
            reloaded._router = None
            with patch.object(
                reloaded, "_get_fallback_list", return_value=[{"model": MODEL_PRIMARY}]
            ):
                await reloaded.chat_completion(
                    messages=[{"role": "user", "content": "test"}]
                )

    # litellm.acompletion was called
    fake_litellm.acompletion.assert_called_once()


@pytest.mark.asyncio
async def test_chat_completion_raises_when_all_providers_fail():
    fake_litellm = MagicMock()
    fake_litellm.acompletion = AsyncMock(side_effect=Exception("network error"))

    with patch("samplemind.integrations.litellm_router.get_router", return_value=None):
        with patch.dict("sys.modules", {"litellm": fake_litellm}):
            from samplemind.integrations.litellm_router import chat_completion

            with patch(
                "samplemind.integrations.litellm_router._get_fallback_list",
                return_value=[{"model": MODEL_PRIMARY}],
            ):
                with pytest.raises(RuntimeError, match="All LiteLLM providers failed"):
                    await chat_completion(
                        messages=[{"role": "user", "content": "fail"}]
                    )


# ── prefer_fast / agents_mode routing ────────────────────────────────────────


@pytest.mark.asyncio
async def test_prefer_fast_routes_to_fast_model_name():
    fake_response = MagicMock()
    fake_router = MagicMock()
    fake_router.acompletion = AsyncMock(return_value=fake_response)

    with patch(
        "samplemind.integrations.litellm_router.get_router", return_value=fake_router
    ):
        with patch.dict("sys.modules", {"litellm": MagicMock()}):
            from samplemind.integrations.litellm_router import chat_completion

            await chat_completion(
                messages=[{"role": "user", "content": "x"}],
                prefer_fast=True,
            )

    call_kwargs = fake_router.acompletion.call_args
    assert (
        call_kwargs.kwargs.get("model") == "fast"
        or call_kwargs[1].get("model") == "fast"
    )
