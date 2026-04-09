"""
SampleMind LangGraph Agent Graph — Phase 16 / v3.0

Orchestrates the multi-agent pipeline (7 nodes):

  Entry → Router → AnalysisAgent
                 → TaggingAgent
                 → MixingAgent
                 → QualityAgent      ← NEW (P3-006)
                 → RecommendationAgent
                 → PackBuilderAgent
                 → Aggregator → END

Agents run sequentially (each builds on prior results).
The graph is designed for:
- Synchronous use via run_analysis_pipeline()
- Async streaming via stream_analysis_pipeline()
- WebSocket progress events via the session_id field

Usage:
    from samplemind.ai.agents import run_analysis_pipeline, AudioAnalysisState

    result: AudioAnalysisState = run_analysis_pipeline("/path/to/sample.wav")
    print(result["final_report"])
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from pathlib import Path

from samplemind.ai.agents.state import AudioAnalysisState

logger = logging.getLogger(__name__)


# ── Router node ───────────────────────────────────────────────────────────────


def router_node(state: AudioAnalysisState) -> AudioAnalysisState:
    """
    Validate input and set default pipeline configuration.
    """
    file_path = state.get("file_path", "")
    errors = list(state.get("errors", []))

    if not file_path:
        errors.append("router: file_path is required")
        return {"errors": errors, "current_stage": "error", "progress_pct": 0}

    if not Path(file_path).exists():
        errors.append(f"router: file not found: {file_path}")
        return {"errors": errors, "current_stage": "error", "progress_pct": 0}

    return {
        "current_stage": "routing",
        "progress_pct": 5,
        "messages": [f"📂 Processing: {Path(file_path).name}"],
        "analysis_depth": state.get("analysis_depth", "standard"),
        "requested_agents": state.get("requested_agents", []),
        "tool_calls": [],
        "tool_results": [],
        "errors": errors,
    }


# ── Aggregator node ───────────────────────────────────────────────────────────


def aggregator_node(state: AudioAnalysisState) -> AudioAnalysisState:
    """
    Combine all agent outputs into a unified final_report.
    """
    final_report = {
        "file": state.get("file_path", ""),
        "audio_features": state.get("audio_features", {}),
        "analysis": state.get("analysis_result", {}),
        "tags": state.get("tags", {}),
        "mixing_recommendations": state.get("mixing_recommendations", {}),
        "quality_flags": state.get("quality_flags", {}),
        "similar_samples": state.get("similar_samples", []),
        "pack_manifest": state.get("pack_manifest", {}),
        "errors": state.get("errors", []),
    }
    return {
        "final_report": final_report,
        "current_stage": "done",
        "progress_pct": 100,
        "messages": state.get("messages", []) + ["🎉 Pipeline complete!"],
    }


# ── Graph builder ─────────────────────────────────────────────────────────────


def build_graph():
    """
    Build and compile the LangGraph StateGraph.

    Returns:
        Compiled LangGraph app ready for .invoke() and .stream()
    """
    try:
        from langgraph.graph import END, StateGraph

        from samplemind.ai.agents.analysis_agent import analysis_agent
        from samplemind.ai.agents.mixing_agent import mixing_agent
        from samplemind.ai.agents.pack_builder_agent import pack_builder_agent
        from samplemind.ai.agents.quality_agent import quality_agent
        from samplemind.ai.agents.recommendation_agent import recommendation_agent
        from samplemind.ai.agents.tagging_agent import tagging_agent

        graph = StateGraph(AudioAnalysisState)

        # Register nodes (7-node pipeline)
        graph.add_node("router", router_node)
        graph.add_node("analysis", analysis_agent)
        graph.add_node("tagging", tagging_agent)
        graph.add_node("mixing", mixing_agent)
        graph.add_node("quality", quality_agent)  # P3-006
        graph.add_node("recommendations", recommendation_agent)
        graph.add_node("pack_builder", pack_builder_agent)
        graph.add_node("aggregator", aggregator_node)

        # Linear pipeline edges
        graph.set_entry_point("router")
        graph.add_edge("router", "analysis")
        graph.add_edge("analysis", "tagging")
        graph.add_edge("tagging", "mixing")
        graph.add_edge("mixing", "quality")  # quality gate
        graph.add_edge("quality", "recommendations")
        graph.add_edge("recommendations", "pack_builder")
        graph.add_edge("pack_builder", "aggregator")
        graph.add_edge("aggregator", END)

        return graph.compile()

    except ImportError as exc:
        raise ImportError(
            "LangGraph is required for the agent system. "
            "Install with: pip install langgraph"
        ) from exc


# ── Convenience runners ───────────────────────────────────────────────────────


def run_analysis_pipeline(
    file_path: str,
    user_id: str | None = None,
    session_id: str | None = None,
    analysis_depth: str = "standard",
) -> AudioAnalysisState:
    """
    Run the full analysis pipeline synchronously.

    Args:
        file_path: Path to the audio file to analyze
        user_id: Optional user ID for personalization
        session_id: Optional session ID for WebSocket streaming
        analysis_depth: "quick" | "standard" | "deep"

    Returns:
        Final AudioAnalysisState with all agent outputs populated
    """
    app = build_graph()
    initial_state: AudioAnalysisState = {
        "file_path": file_path,
        "user_id": user_id,
        "session_id": session_id,
        "analysis_depth": analysis_depth,
        "requested_agents": [],
        "audio_features": {},
        "messages": [],
        "errors": [],
        "tool_calls": [],
        "tool_results": [],
        "current_stage": "init",
        "progress_pct": 0,
    }
    result = app.invoke(initial_state)
    logger.info(
        "Pipeline complete for %s — %d errors",
        file_path,
        len(result.get("errors", [])),
    )
    return result


async def stream_analysis_pipeline(
    file_path: str,
    user_id: str | None = None,
    session_id: str | None = None,
    analysis_depth: str = "standard",
) -> AsyncIterator[AudioAnalysisState]:
    """
    Stream agent state updates as they occur (for WebSocket/SSE endpoints).

    Yields partial AudioAnalysisState after each node completes.
    """
    app = build_graph()
    initial_state: AudioAnalysisState = {
        "file_path": file_path,
        "user_id": user_id,
        "session_id": session_id,
        "analysis_depth": analysis_depth,
        "requested_agents": [],
        "audio_features": {},
        "messages": [],
        "errors": [],
        "tool_calls": [],
        "tool_results": [],
        "current_stage": "init",
        "progress_pct": 0,
    }
    async for chunk in app.astream(initial_state):
        for _node_name, node_state in chunk.items():
            yield node_state
