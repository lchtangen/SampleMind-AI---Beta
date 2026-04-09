"""
SampleMind — Claude tool_use integration with Redis caching (Step 16).

Defines the 5 MCP-compatible tool schemas for Claude's tool_use API,
implements a synchronous tool-execution loop, and caches results in Redis
so repeated calls with identical arguments are served instantly.

Cache key: sha256(tool_name + json(sorted_args)) → TTL 1 hour.

Usage (inside an agent node):
    from samplemind.ai.agents.tool_use import run_tool_use_loop

    result = run_tool_use_loop(
        system_prompt="You are a music analysis assistant.",
        user_prompt="Analyse this sample and return structured insights.",
        initial_tool_results={"audio_features": features_dict},
    )
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ── Tool schemas (Claude tool_use format) ────────────────────────────────────

SAMPLEMIND_TOOLS: List[Dict[str, Any]] = [
    {
        "name": "analyze_audio",
        "description": (
            "Run the full SampleMind audio analysis pipeline on a local file. "
            "Returns BPM, key, scale, energy, spectral centroid, duration, and "
            "a structured AI coaching summary."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute path to a WAV, MP3, FLAC, or AIFF file.",
                },
                "depth": {
                    "type": "string",
                    "enum": ["quick", "standard", "deep"],
                    "description": "Analysis depth. Default: standard.",
                },
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "search_similar",
        "description": (
            "Find samples in the library that are similar to the given audio file "
            "using vector embeddings stored in ChromaDB."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the reference audio file.",
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of results (1–20). Default: 5.",
                },
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "get_recommendations",
        "description": (
            "Get mixing/arrangement recommendations for an audio file based on its "
            "BPM, key, and energy. Returns Camelot wheel position, compatible keys, "
            "BPM range, and mixing tips."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the audio file.",
                },
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "tag_sample",
        "description": (
            "Generate multi-label genre, mood, energy, and instrument tags "
            "for an audio file."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the audio file to tag.",
                },
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "build_pack",
        "description": (
            "Analyse a folder of audio files and generate a structured sample pack "
            "manifest with per-file metadata and suggested folder/naming structure."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "folder_path": {
                    "type": "string",
                    "description": "Path to the folder containing audio files.",
                },
                "pack_name": {
                    "type": "string",
                    "description": "Name for the sample pack.",
                },
                "max_files": {
                    "type": "integer",
                    "description": "Maximum files to process (default 50).",
                },
            },
            "required": ["folder_path"],
        },
    },
]


# ── Cache helpers ─────────────────────────────────────────────────────────────

_CACHE_TTL = 3600  # 1 hour


def _cache_key(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """Deterministic cache key from tool name + sorted JSON args."""
    payload = json.dumps({"tool": tool_name, "args": tool_input}, sort_keys=True)
    return "sm:tool:" + hashlib.sha256(payload.encode()).hexdigest()


def _try_get_cache(key: str) -> Optional[Dict[str, Any]]:
    """Non-blocking Redis GET. Returns None if Redis unavailable."""
    try:
        import redis as sync_redis

        r = sync_redis.from_url("redis://localhost:6379", decode_responses=True)
        raw = r.get(key)
        r.close()
        if raw:
            return json.loads(raw)
    except Exception as exc:
        logger.debug("Redis GET skipped: %s", exc)
    return None


def _try_set_cache(key: str, value: Dict[str, Any]) -> None:
    """Non-blocking Redis SET with TTL. Silently skips if Redis unavailable."""
    try:
        import redis as sync_redis

        r = sync_redis.from_url("redis://localhost:6379", decode_responses=True)
        r.setex(key, _CACHE_TTL, json.dumps(value))
        r.close()
    except Exception as exc:
        logger.debug("Redis SET skipped: %s", exc)


# ── Tool dispatcher ───────────────────────────────────────────────────────────


def _execute_tool(tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a SampleMind tool by name and return a JSON-serializable result.
    Checks the Redis cache before executing and stores the result after.
    """
    cache_key = _cache_key(tool_name, tool_input)
    cached = _try_get_cache(cache_key)
    if cached is not None:
        logger.info("Cache HIT for tool=%s", tool_name)
        return cached

    logger.info("Cache MISS — executing tool=%s args=%s", tool_name, tool_input)
    result: Dict[str, Any]

    try:
        if tool_name == "analyze_audio":
            from samplemind.ai.agents.graph import run_analysis_pipeline

            state = run_analysis_pipeline(
                file_path=tool_input["file_path"],
                analysis_depth=tool_input.get("depth", "standard"),
            )
            result = state.get("final_report", {"error": "No output"})

        elif tool_name == "search_similar":
            from samplemind.core.similarity.similarity import AudioEmbeddingEngine

            engine = AudioEmbeddingEngine()
            hits = engine.find_similar(
                tool_input["file_path"], top_k=tool_input.get("top_k", 5)
            )
            result = {
                "similar": [
                    {
                        "path": str(r.path),
                        "score": round(r.score, 4),
                        "bpm": r.metadata.get("bpm"),
                        "key": r.metadata.get("key"),
                    }
                    for r in (hits or [])
                ]
            }

        elif tool_name == "get_recommendations":
            from samplemind.core.engine.audio_engine import AnalysisLevel, AudioEngine
            from samplemind.ai.agents.mixing_agent import mixing_agent
            from samplemind.ai.agents.state import AudioAnalysisState

            engine = AudioEngine()
            features = engine.analyze_file(
                tool_input["file_path"], level=AnalysisLevel.STANDARD
            )
            state: AudioAnalysisState = {
                "file_path": tool_input["file_path"],
                "audio_features": {
                    "bpm": features.bpm,
                    "key": features.key,
                    "scale": features.scale,
                    "rms_energy": features.rms_energy,
                },
                "messages": [],
                "errors": [],
            }
            out = mixing_agent(state)
            result = out.get("mixing_recommendations", {})

        elif tool_name == "tag_sample":
            from samplemind.core.engine.audio_engine import AnalysisLevel, AudioEngine
            from samplemind.ai.agents.tagging_agent import tagging_agent
            from samplemind.ai.agents.state import AudioAnalysisState

            engine = AudioEngine()
            features = engine.analyze_file(
                tool_input["file_path"], level=AnalysisLevel.STANDARD
            )
            state: AudioAnalysisState = {
                "file_path": tool_input["file_path"],
                "audio_features": {
                    "bpm": features.bpm,
                    "key": features.key,
                    "scale": features.scale,
                    "rms_energy": features.rms_energy,
                    "spectral_centroid": features.spectral_centroid,
                    "duration": features.duration,
                },
                "messages": [],
                "errors": [],
            }
            out = tagging_agent(state)
            result = out.get("tags", {})

        elif tool_name == "build_pack":
            from samplemind.server.mcp_server import build_sample_pack

            result = build_sample_pack(
                folder_path=tool_input["folder_path"],
                pack_name=tool_input.get("pack_name", "My Pack"),
                max_files=tool_input.get("max_files", 50),
            )

        else:
            result = {"error": f"Unknown tool: {tool_name}"}

    except Exception as exc:
        logger.error("Tool %s failed: %s", tool_name, exc)
        result = {"error": str(exc)}

    _try_set_cache(cache_key, result)
    return result


# ── Claude tool_use loop ──────────────────────────────────────────────────────


def run_tool_use_loop(
    system_prompt: str,
    user_prompt: str,
    model: str = "claude-sonnet-4-6",
    max_tokens: int = 4096,
    max_rounds: int = 5,
) -> Dict[str, Any]:
    """
    Run a synchronous Claude tool_use conversation loop.

    Claude may call any of the SAMPLEMIND_TOOLS. Each tool call is executed
    locally (with Redis caching) and the result is fed back to Claude.
    The loop ends when Claude emits a `stop_reason == "end_turn"` or the
    maximum number of rounds is reached.

    Args:
        system_prompt: System prompt for Claude.
        user_prompt: Initial user message.
        model: Claude model ID.
        max_tokens: Max tokens per response.
        max_rounds: Safety limit on tool-call rounds.

    Returns:
        Dict with "text" (final answer) and "tool_calls" (list of calls made).
    """
    try:
        from anthropic import Anthropic
    except ImportError:
        logger.warning("Anthropic SDK not installed — tool_use loop unavailable")
        return {"text": "Anthropic SDK not installed.", "tool_calls": []}

    client = Anthropic()
    messages: List[Dict[str, Any]] = [{"role": "user", "content": user_prompt}]
    all_tool_calls: List[Dict[str, Any]] = []

    for round_num in range(max_rounds):
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            tools=SAMPLEMIND_TOOLS,
            messages=messages,
        )

        # Collect text content from response
        text_parts: List[str] = []
        tool_use_blocks: List[Any] = []

        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_use_blocks.append(block)

        # If Claude is done, return final text
        if response.stop_reason == "end_turn" or not tool_use_blocks:
            return {
                "text": "\n".join(text_parts).strip(),
                "tool_calls": all_tool_calls,
            }

        # Append Claude's response to the conversation
        messages.append({"role": "assistant", "content": response.content})

        # Execute each tool call and build tool_result blocks
        tool_results: List[Dict[str, Any]] = []
        for block in tool_use_blocks:
            tool_result = _execute_tool(block.name, block.input)
            all_tool_calls.append(
                {"tool": block.name, "input": block.input, "result": tool_result}
            )
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(tool_result),
                }
            )
            logger.info(
                "Round %d — tool=%s result_keys=%s",
                round_num + 1,
                block.name,
                list(tool_result.keys()) if isinstance(tool_result, dict) else "non-dict",
            )

        # Feed tool results back to Claude
        messages.append({"role": "user", "content": tool_results})

    # Exceeded max rounds — return whatever was collected
    logger.warning("tool_use loop exceeded max_rounds=%d", max_rounds)
    return {
        "text": "Analysis reached the tool-call limit.",
        "tool_calls": all_tool_calls,
    }
