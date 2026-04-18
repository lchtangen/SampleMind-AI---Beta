"""
SampleMind LangGraph Agent Graph — Phase 16 / v3.0

Orchestrates the multi-agent pipeline (9 nodes):

  Entry → Router → AnalysisAgent
                 → TaggingAgent
                 → MixingAgent
                 → QualityAgent        ← P3-006
                 → RecommendationAgent
                 → PackBuilderAgent
                 → CategorizerAgent    ← NEW
                 → MicroTimingAgent    ← NEW
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

    Also injects conversation memory from AgentMemory (P3-014) so
    downstream agents have access to relevant past analyses.
    """
    file_path = state.get("file_path", "")
    errors = list(state.get("errors", []))

    if not file_path:
        errors.append("router: file_path is required")
        return {"errors": errors, "current_stage": "error", "progress_pct": 0}

    if not Path(file_path).exists():
        errors.append(f"router: file not found: {file_path}")
        return {"errors": errors, "current_stage": "error", "progress_pct": 0}

    # P3-014: Inject conversation memory if available
    conversation_history: list[dict] = []
    try:
        import asyncio

        from samplemind.ai.agents.memory import AgentMemory

        memory = AgentMemory()
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # Already in an async context — schedule via new thread
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(
                    asyncio.run,
                    memory.get_conversation_context(file_path, top_k=3),
                )
                conversation_history = future.result(timeout=5)
        else:
            conversation_history = asyncio.run(
                memory.get_conversation_context(file_path, top_k=3)
            )
        logger.info(
            "Injected %d memory entries into pipeline", len(conversation_history)
        )
    except Exception as exc:
        logger.debug("Agent memory unavailable: %s", exc)

    return {
        "current_stage": "routing",
        "progress_pct": 5,
        "messages": [f"📂 Processing: {Path(file_path).name}"],
        "analysis_depth": state.get("analysis_depth", "standard"),
        "requested_agents": state.get("requested_agents", []),
        "conversation_history": conversation_history,
        "tool_calls": [],
        "tool_results": [],
        "errors": errors,
    }


# ── Aggregator node ───────────────────────────────────────────────────────────


def aggregator_node(state: AudioAnalysisState) -> AudioAnalysisState:
    """
    Combine all agent outputs into a unified final_report.

    Also stores the completed analysis in AgentMemory (P3-014) for
    future retrieval by subsequent pipeline runs.
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
        "categorization": state.get("categorization", {}),
        "micro_timing": state.get("micro_timing", {}),
        "errors": state.get("errors", []),
    }

    # P3-014: Store completed analysis in agent memory
    try:
        import asyncio

        from samplemind.ai.agents.memory import AgentMemory

        memory = AgentMemory()
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(asyncio.run, memory.store(dict(state)))
                future.result(timeout=5)
        else:
            asyncio.run(memory.store(dict(state)))
        logger.info("Stored pipeline result in agent memory")
    except Exception as exc:
        logger.debug("Could not store in agent memory: %s", exc)

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
        from samplemind.ai.agents.categorizer_agent import categorizer_agent
        from samplemind.ai.agents.micro_timing_agent import micro_timing_agent
        from samplemind.ai.agents.mixing_agent import mixing_agent
        from samplemind.ai.agents.pack_builder_agent import pack_builder_agent
        from samplemind.ai.agents.quality_agent import quality_agent
        from samplemind.ai.agents.recommendation_agent import recommendation_agent
        from samplemind.ai.agents.tagging_agent import tagging_agent

        graph = StateGraph(AudioAnalysisState)

        # Register nodes (9-node pipeline)
        graph.add_node("router", router_node)
        graph.add_node("analysis", analysis_agent)
        graph.add_node("tagging", tagging_agent)
        graph.add_node("mixing", mixing_agent)
        graph.add_node("quality", quality_agent)  # P3-006
        graph.add_node("recommendations", recommendation_agent)
        graph.add_node("pack_builder", pack_builder_agent)
        graph.add_node("categorizer", categorizer_agent)  # NEW
        graph.add_node("micro_timing", micro_timing_agent)  # NEW
        graph.add_node("aggregator", aggregator_node)

        # Linear pipeline edges
        graph.set_entry_point("router")
        graph.add_edge("router", "analysis")
        graph.add_edge("analysis", "tagging")
        graph.add_edge("tagging", "mixing")
        graph.add_edge("mixing", "quality")  # quality gate
        graph.add_edge("quality", "recommendations")
        graph.add_edge("recommendations", "pack_builder")
        graph.add_edge("pack_builder", "categorizer")
        graph.add_edge("categorizer", "micro_timing")
        graph.add_edge("micro_timing", "aggregator")
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
