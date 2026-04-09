"""
SampleMind AI — LangGraph Agent Celery Task (Phase 16)

Wraps the full LangGraph analysis pipeline in a Celery task so it can run
as a background job and publish step-by-step progress to Redis.

Progress events are stored at Redis key:  agent_progress:{task_id}
as a JSON list, enabling the WebSocket endpoint to stream them.

Usage::

    from samplemind.core.tasks.agent_tasks import run_analysis_agent

    # Queue a job
    task = run_analysis_agent.delay("/path/to/sample.wav")
    print(task.id)  # pass this to /ws/agent/{task_id}

    # Synchronous (testing / CLI)
    result = run_analysis_agent("/path/to/sample.wav")
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

from samplemind.core.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)

# Redis key template — used by the WebSocket progress endpoint
PROGRESS_KEY_TEMPLATE = "agent_progress:{task_id}"
PROGRESS_TTL = 3600  # seconds


# ---------------------------------------------------------------------------
# Redis helper (lazy import so Redis is not required at import time)
# ---------------------------------------------------------------------------

def _get_redis():  # type: ignore[return]
    """Return a redis.Redis client, or None if Redis is unavailable."""
    try:
        import redis  # type: ignore

        url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        return redis.from_url(url, decode_responses=True)
    except Exception:  # pragma: no cover
        return None


def _push_progress(
    r,
    task_id: str,
    stage: str,
    pct: int,
    message: str,
) -> None:
    """Append a progress event to the Redis list and refresh TTL."""
    if r is None:
        return
    key = PROGRESS_KEY_TEMPLATE.format(task_id=task_id)
    event = json.dumps({"stage": stage, "pct": pct, "message": message, "ts": time.time()})
    try:
        r.rpush(key, event)
        r.expire(key, PROGRESS_TTL)
    except Exception as exc:  # pragma: no cover
        logger.debug("Redis progress push failed: %s", exc)


# ---------------------------------------------------------------------------
# Celery task
# ---------------------------------------------------------------------------

@celery_app.task(
    bind=True,
    name="samplemind.tasks.run_analysis_agent",
    queue="ai_analysis",
    max_retries=1,
    default_retry_delay=5,
)
def run_analysis_agent(
    self,
    file_path: str,
    analysis_depth: str = "standard",
    session_id: str | None = None,
) -> dict[str, Any]:
    """
    Run the full LangGraph multi-agent analysis pipeline on a single audio file.

    Stages (progress %):
      5%   → routing / validation
      20%  → audio feature extraction (AudioEngine)
      40%  → AI classification (CLAP + ensemble tagging)
      60%  → mixing recommendations
      80%  → FAISS similarity search
      95%  → final aggregation + LiteLLM narrative
      100% → done

    Args:
        file_path: Absolute path to the audio file to analyse.
        analysis_depth: "basic" | "standard" | "detailed" | "professional"
        session_id: Optional WebSocket session ID for targeted push.

    Returns:
        The ``final_report`` dict from ``AudioAnalysisState``.
    """
    task_id: str = self.request.id or "sync"
    r = _get_redis()

    def push(stage: str, pct: int, message: str) -> None:
        _push_progress(r, task_id, stage, pct, message)
        self.update_state(state="PROGRESS", meta={"stage": stage, "pct": pct, "message": message})

    push("routing", 5, f"Validating file: {Path(file_path).name}")

    # Validate file exists
    if not Path(file_path).exists():
        push("error", 0, f"File not found: {file_path}")
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    push("routing", 10, "Building LangGraph pipeline…")

    try:
        from samplemind.ai.agents.graph import build_graph
        from samplemind.ai.agents.state import AudioAnalysisState
    except ImportError as exc:
        push("error", 0, f"LangGraph not available: {exc}")
        raise

    graph = build_graph()

    # Build initial state
    initial_state: AudioAnalysisState = {  # type: ignore[assignment]
        "file_path": file_path,
        "analysis_depth": analysis_depth,
        "session_id": session_id or task_id,
        "requested_agents": [],
        "current_stage": "routing",
        "progress_pct": 10,
        "messages": [],
        "tool_calls": [],
        "tool_results": [],
        "errors": [],
        "audio_features": {},
        "analysis_result": {},
        "tags": {},
        "mixing_recommendations": {},
        "similar_samples": [],
        "pack_manifest": {},
        "final_report": {},
    }

    push("analysis", 20, "Running audio feature extraction…")

    # Stream graph execution so we can publish intermediate progress
    final_state: dict[str, Any] = {}
    try:
        for chunk in graph.stream(initial_state):
            node_name = list(chunk.keys())[0] if chunk else "unknown"
            state_update = chunk.get(node_name, {})
            pct = state_update.get("progress_pct", 20)
            stage = state_update.get("current_stage", node_name)
            msgs = state_update.get("messages", [])
            msg = msgs[-1] if msgs else f"Running {node_name}…"
            push(stage, int(pct), str(msg))
            final_state.update(state_update)
    except Exception as exc:
        push("error", 0, f"Pipeline error: {exc}")
        logger.exception("LangGraph pipeline failed for %s", file_path)
        raise

    push("done", 100, "Analysis complete!")
    return final_state.get("final_report", {})
