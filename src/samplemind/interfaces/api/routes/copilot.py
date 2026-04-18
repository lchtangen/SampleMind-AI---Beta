"""
AI Copilot — Streaming chat endpoint for SampleMind AI.

Provides real-time Server-Sent Events (SSE) streaming from LiteLLM,
with built-in tool calling for FAISS search, audio analysis, and
playlist generation.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from samplemind.interfaces.api.rate_limiter import limit as rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/copilot", tags=["copilot"])

# ── System prompt ─────────────────────────────────────────────────────────────

COPILOT_SYSTEM_PROMPT = """You are SampleMind AI Copilot — an expert music production assistant.

You help producers with:
- Audio analysis (BPM, key, mood, energy, spectral features)
- Sample discovery via semantic search (FAISS + CLAP embeddings)
- Mixing & mastering advice
- Music theory explanations
- Sample pack curation and playlist generation
- Genre classification and mood detection

When the user asks about specific samples or wants to find sounds, use the
available tools. Always be concise, practical, and production-focused.

Format responses in markdown. Use bullet points for lists. Use code blocks
for technical values (BPM, key signatures, frequency ranges)."""

# ── Tool definitions (for structured tool calling) ────────────────────────────

COPILOT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_samples",
            "description": "Search the sample library using natural language. Returns similar audio samples ranked by relevance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query, e.g. 'dark trap 808 bass' or 'ambient pad with reverb'",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return (default 5, max 20)",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_audio_features",
            "description": "Get detailed audio features for a sample by filename or path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Filename or path of the sample to analyze",
                    },
                },
                "required": ["filename"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_playlist",
            "description": "Generate an AI-curated playlist with a specific mood and energy arc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mood": {
                        "type": "string",
                        "enum": [
                            "dark",
                            "chill",
                            "aggressive",
                            "euphoric",
                            "melancholic",
                            "neutral",
                        ],
                        "description": "Target mood for the playlist",
                    },
                    "energy_arc": {
                        "type": "string",
                        "enum": ["build", "drop", "plateau", "tension"],
                        "description": "Energy progression arc",
                    },
                },
                "required": ["mood"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_library_stats",
            "description": "Get statistics about the user's sample library (total samples, genre distribution, BPM range, key distribution).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


# ── Tool execution ────────────────────────────────────────────────────────────


async def _execute_tool(name: str, arguments: dict[str, Any]) -> str:
    """Execute a copilot tool and return the result as a string."""
    try:
        if name == "search_samples":
            return await _tool_search_samples(
                query=arguments["query"],
                top_k=arguments.get("top_k", 5),
            )
        elif name == "analyze_audio_features":
            return await _tool_analyze_audio(filename=arguments["filename"])
        elif name == "generate_playlist":
            return await _tool_generate_playlist(
                mood=arguments["mood"],
                energy_arc=arguments.get("energy_arc", "build"),
            )
        elif name == "get_library_stats":
            return await _tool_library_stats()
        else:
            return json.dumps({"error": f"Unknown tool: {name}"})
    except Exception as exc:
        logger.error("Tool %s failed: %s", name, exc, exc_info=True)
        return json.dumps({"error": str(exc)})


async def _tool_search_samples(query: str, top_k: int = 5) -> str:
    """Search FAISS index for matching samples."""
    try:
        from samplemind.core.search.faiss_index import get_index

        idx = get_index(auto_load=True)
        if idx.is_empty:
            return json.dumps(
                {"results": [], "message": "No samples indexed. Run index rebuild."}
            )

        results = idx.search_text(query, top_k=min(top_k, 20))
        return json.dumps(
            {
                "results": [
                    {
                        "filename": r.filename,
                        "score": round(r.score, 3),
                        "bpm": r.metadata.get("bpm"),
                        "key": r.metadata.get("key"),
                        "energy": r.metadata.get("energy"),
                        "genre": r.metadata.get("genre_labels", []),
                        "mood": r.metadata.get("mood_labels", []),
                    }
                    for r in results
                ],
                "total": len(results),
            }
        )
    except Exception as exc:
        return json.dumps({"error": f"Search failed: {exc}"})


async def _tool_analyze_audio(filename: str) -> str:
    """Analyze audio features for a specific file."""
    try:
        from samplemind.core.search.faiss_index import get_index

        idx = get_index(auto_load=True)
        for entry in idx._entries:
            if filename.lower() in entry.filename.lower():
                return json.dumps(
                    {
                        "filename": entry.filename,
                        "bpm": entry.bpm,
                        "key": entry.key,
                        "energy": entry.energy,
                        "genre_labels": entry.genre_labels,
                        "mood_labels": entry.mood_labels,
                        "path": entry.path,
                    }
                )
        return json.dumps({"error": f"Sample '{filename}' not found in index"})
    except Exception as exc:
        return json.dumps({"error": f"Analysis failed: {exc}"})


async def _tool_generate_playlist(
    mood: str = "dark", energy_arc: str = "build"
) -> str:
    """Generate an AI-curated playlist."""
    try:
        from samplemind.ai.curation.playlist_generator import PlaylistGenerator

        gen = PlaylistGenerator()
        playlist = await gen.generate(
            mood=mood,
            energy_arc=energy_arc,  # type: ignore[arg-type]
            duration_minutes=15.0,
        )
        return json.dumps(
            {
                "name": playlist.name,
                "mood": playlist.mood,
                "energy_arc": playlist.energy_arc,
                "sample_count": len(playlist.samples),
                "samples": playlist.samples[:10],
                "narrative": playlist.narrative,
            }
        )
    except Exception as exc:
        return json.dumps({"error": f"Playlist generation failed: {exc}"})


async def _tool_library_stats() -> str:
    """Get library statistics."""
    try:
        from samplemind.core.search.faiss_index import get_index

        idx = get_index(auto_load=True)
        if idx.is_empty:
            return json.dumps({"total_samples": 0, "message": "No samples indexed"})

        entries = idx._entries
        genres: dict[str, int] = {}
        keys: dict[str, int] = {}
        bpms: list[float] = []
        energies: dict[str, int] = {"low": 0, "mid": 0, "high": 0}

        for e in entries:
            if e.bpm:
                bpms.append(e.bpm)
            if e.key:
                keys[e.key] = keys.get(e.key, 0) + 1
            if e.energy:
                energies[e.energy] = energies.get(e.energy, 0) + 1
            for g in e.genre_labels or []:
                genres[g] = genres.get(g, 0) + 1

        return json.dumps(
            {
                "total_samples": len(entries),
                "bpm_range": {
                    "min": round(min(bpms), 1) if bpms else None,
                    "max": round(max(bpms), 1) if bpms else None,
                    "avg": round(sum(bpms) / len(bpms), 1) if bpms else None,
                },
                "top_genres": dict(
                    sorted(genres.items(), key=lambda x: x[1], reverse=True)[:10]
                ),
                "top_keys": dict(
                    sorted(keys.items(), key=lambda x: x[1], reverse=True)[:5]
                ),
                "energy_distribution": energies,
            }
        )
    except Exception as exc:
        return json.dumps({"error": f"Stats failed: {exc}"})


# ── Request / Response schemas ────────────────────────────────────────────────


class ChatMessage(BaseModel):
    role: str = Field(
        ..., description="Message role: 'user', 'assistant', or 'system'"
    )
    content: str = Field(..., description="Message content")


class CopilotChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(
        ..., description="Conversation messages", min_length=1
    )
    context: dict[str, Any] | None = Field(
        None,
        description="Optional context (selected sample metadata, current page, etc.)",
    )
    prefer_fast: bool = Field(
        False, description="Use fast model (Gemini Flash) instead of Claude"
    )


class CopilotContextRequest(BaseModel):
    sample_id: str | None = None
    query: str = Field(..., description="Question about the sample or context")


# ── SSE streaming endpoint ────────────────────────────────────────────────────


@router.post("/chat")
@rate_limit("60/minute")
async def copilot_chat(request: Request, body: CopilotChatRequest) -> StreamingResponse:
    """
    Stream an AI copilot response via Server-Sent Events (SSE).

    The copilot can call tools (FAISS search, audio analysis, playlist gen)
    during the conversation, and the tool results are streamed back as
    structured SSE events.
    """

    async def _event_stream():
        try:
            from samplemind.integrations.litellm_router import stream_completion

            # Build messages with system prompt
            messages: list[dict[str, str]] = [
                {"role": "system", "content": COPILOT_SYSTEM_PROMPT}
            ]

            # Inject context if provided
            if body.context:
                ctx_str = json.dumps(body.context, default=str)
                messages.append(
                    {
                        "role": "system",
                        "content": f"Current session context:\n```json\n{ctx_str}\n```",
                    }
                )

            # Add conversation messages
            for msg in body.messages:
                messages.append({"role": msg.role, "content": msg.content})

            # First try: non-streaming with tools to check for tool calls
            try:
                from samplemind.integrations.litellm_router import chat_completion

                tool_response = await chat_completion(
                    messages=messages,
                    prefer_fast=body.prefer_fast,
                    tools=COPILOT_TOOLS,
                    tool_choice="auto",
                    max_tokens=4096,
                )

                response_msg = tool_response.choices[0].message

                # Handle tool calls
                if hasattr(response_msg, "tool_calls") and response_msg.tool_calls:
                    for tool_call in response_msg.tool_calls:
                        fn_name = tool_call.function.name
                        fn_args = json.loads(tool_call.function.arguments)

                        # Stream tool invocation event
                        yield f"data: {json.dumps({'type': 'tool_call', 'name': fn_name, 'arguments': fn_args})}\n\n"

                        # Execute tool
                        result = await _execute_tool(fn_name, fn_args)

                        # Stream tool result event
                        yield f"data: {json.dumps({'type': 'tool_result', 'name': fn_name, 'result': json.loads(result)})}\n\n"

                        # Add tool interaction to messages for follow-up
                        messages.append(
                            {
                                "role": "assistant",
                                "content": f"[Tool: {fn_name}] {result}",
                            }
                        )
                        messages.append(
                            {
                                "role": "system",
                                "content": f"Tool '{fn_name}' returned: {result}. Now summarize the results for the user.",
                            }
                        )

                    # Stream the final response after tool calls
                    async for delta in stream_completion(
                        messages=messages,
                        prefer_fast=body.prefer_fast,
                        max_tokens=4096,
                    ):
                        yield f"data: {json.dumps({'type': 'delta', 'content': delta})}\n\n"

                else:
                    # No tool calls — stream the response content
                    content = response_msg.content or ""
                    if content:
                        # We got a non-streaming response, emit it as a single delta
                        yield f"data: {json.dumps({'type': 'delta', 'content': content})}\n\n"
                    else:
                        # Fallback to streaming
                        async for delta in stream_completion(
                            messages=messages,
                            prefer_fast=body.prefer_fast,
                            max_tokens=4096,
                        ):
                            yield f"data: {json.dumps({'type': 'delta', 'content': delta})}\n\n"

            except Exception as tool_exc:
                logger.warning(
                    "Tool-based completion failed, falling back to streaming: %s",
                    tool_exc,
                )
                # Fallback: pure streaming without tools
                async for delta in stream_completion(
                    messages=messages,
                    prefer_fast=body.prefer_fast,
                    max_tokens=4096,
                ):
                    yield f"data: {json.dumps({'type': 'delta', 'content': delta})}\n\n"

            # End-of-stream marker
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as exc:
            logger.error("Copilot chat stream error: %s", exc, exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': str(exc)})}\n\n"

    return StreamingResponse(
        _event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/analyze-context")
@rate_limit("30/minute")
async def copilot_analyze_context(
    request: Request, body: CopilotContextRequest
) -> dict[str, Any]:
    """
    Quick contextual analysis — ask a question about a specific sample
    or the current session state. Returns a non-streaming JSON response.
    """
    from samplemind.integrations.litellm_router import chat_completion

    messages: list[dict[str, str]] = [
        {"role": "system", "content": COPILOT_SYSTEM_PROMPT},
    ]

    # Fetch sample context if provided
    if body.sample_id:
        sample_info = await _tool_analyze_audio(body.sample_id)
        messages.append(
            {
                "role": "system",
                "content": f"User is asking about this sample:\n{sample_info}",
            }
        )

    messages.append({"role": "user", "content": body.query})

    try:
        response = await chat_completion(
            messages=messages,
            prefer_fast=True,
            max_tokens=1024,
        )
        content = response.choices[0].message.content
        return {"answer": content, "sample_id": body.sample_id}
    except Exception as exc:
        logger.error("Context analysis failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed")
