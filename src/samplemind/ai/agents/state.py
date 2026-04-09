"""
AudioAnalysisState — Shared state schema for the LangGraph agent graph.

Each node in the graph receives and returns a partial or full AudioAnalysisState.
LangGraph merges updates via TypedDict semantics (last-write wins per key).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict


class AudioAnalysisState(TypedDict, total=False):
    """
    Shared state flowing through the multi-agent graph.

    Keys are populated incrementally as agents complete their work.
    All fields are optional so agents can return only their contribution.
    """

    # ── Input ───────────────────────────────────────────────────────────────
    file_path: str                    # Absolute path to the audio file
    user_id: Optional[str]            # Optional user ID for personalization
    session_id: Optional[str]         # Trace ID for WebSocket streaming

    # ── Audio features (from AudioEngine) ───────────────────────────────────
    audio_features: Dict[str, Any]    # librosa/demucs features dict
    duration: Optional[float]         # File duration in seconds
    sample_rate: Optional[int]        # Sample rate in Hz

    # ── Routing ─────────────────────────────────────────────────────────────
    analysis_depth: str               # "quick" | "standard" | "deep"
    requested_agents: List[str]       # Which agents to invoke (empty = all)

    # ── Agent outputs ────────────────────────────────────────────────────────
    analysis_result: Optional[Dict[str, Any]]       # AnalysisAgent output
    tags: Optional[Dict[str, Any]]                  # TaggingAgent output
    mixing_recommendations: Optional[Dict[str, Any]] # MixingAgent output
    similar_samples: Optional[List[Dict[str, Any]]] # RecommendationAgent output
    pack_manifest: Optional[Dict[str, Any]]         # PackBuilderAgent output

    # ── Claude tool_use ──────────────────────────────────────────────────────
    tool_calls: List[Dict[str, Any]]   # Accumulated tool calls across agents
    tool_results: List[Dict[str, Any]] # Results from tool executions

    # ── Progress / streaming ─────────────────────────────────────────────────
    current_stage: str                 # E.g. "analysis", "tagging", "done"
    progress_pct: int                  # 0–100
    messages: List[str]                # User-facing progress messages

    # ── Final aggregated output ──────────────────────────────────────────────
    final_report: Optional[Dict[str, Any]]
    errors: List[str]                  # Non-fatal errors accumulated
