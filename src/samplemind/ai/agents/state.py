"""
AudioAnalysisState — Shared state schema for the LangGraph agent graph.

Each node in the graph receives and returns a partial or full AudioAnalysisState.
LangGraph merges updates via TypedDict semantics (last-write wins per key).
"""

from __future__ import annotations

from typing import Any, TypedDict


class AudioAnalysisState(TypedDict, total=False):
    """
    Shared state flowing through the multi-agent graph.

    Keys are populated incrementally as agents complete their work.
    All fields are optional so agents can return only their contribution.
    """

    # ── Input ───────────────────────────────────────────────────────────────
    file_path: str  # Absolute path to the audio file
    user_id: str | None  # Optional user ID for personalization
    session_id: str | None  # Trace ID for WebSocket streaming

    # ── Audio features (from AudioEngine) ───────────────────────────────────
    audio_features: dict[str, Any]  # librosa/demucs features dict
    duration: float | None  # File duration in seconds
    sample_rate: int | None  # Sample rate in Hz

    # ── Routing ─────────────────────────────────────────────────────────────
    analysis_depth: str  # "quick" | "standard" | "deep"
    requested_agents: list[str]  # Which agents to invoke (empty = all)

    # ── Agent outputs ────────────────────────────────────────────────────────
    analysis_result: dict[str, Any] | None  # AnalysisAgent output
    tags: dict[str, Any] | None  # TaggingAgent output
    mixing_recommendations: dict[str, Any] | None  # MixingAgent output
    quality_flags: dict[str, Any] | None  # QualityAgent output (P3-006)
    similar_samples: list[dict[str, Any]] | None  # RecommendationAgent output
    pack_manifest: dict[str, Any] | None  # PackBuilderAgent output
    categorization: dict[str, Any] | None  # CategorizerAgent output
    micro_timing: dict[str, Any] | None  # MicroTimingAgent output

    # ── Claude tool_use ──────────────────────────────────────────────────────
    tool_calls: list[dict[str, Any]]  # Accumulated tool calls across agents
    tool_results: list[dict[str, Any]]  # Results from tool executions

    # ── Progress / streaming ─────────────────────────────────────────────────
    current_stage: str  # E.g. "analysis", "tagging", "done"
    progress_pct: int  # 0–100
    messages: list[str]  # User-facing progress messages

    # ── Final aggregated output ──────────────────────────────────────────────
    final_report: dict[str, Any] | None
    errors: list[str]  # Non-fatal errors accumulated
