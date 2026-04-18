"""
Unit tests for samplemind.core.tasks.agent_tasks

Tests the Celery task wrapper logic: Redis progress publishing,
LangGraph invocation, file-not-found error path.

All Celery/Redis/LangGraph internals are mocked so the tests run
without a broker or audio files.

Strategy:
  - Override Celery config to use memory broker + backend so apply() works.
  - Patch _get_redis to return a MagicMock (avoids real Redis calls).
  - build_graph is a local import inside the function body → patch source module.

Module under test:
    samplemind.core.tasks.agent_tasks
        — run_analysis_agent (Celery task), _push_progress, _get_redis,
          PROGRESS_KEY_TEMPLATE, PROGRESS_TTL

Key test scenarios:
    _get_redis
        - Returns a redis client or None without raising, even when the
          ``redis`` package is not installed.
    _push_progress
        - Calls rpush + expire with a valid JSON event (stage, pct,
          message, ts).
        - No-ops silently when ``r`` is None.
        - Swallows ConnectionError from rpush.
    run_analysis_agent (via Celery ``apply()``)
        - FileNotFoundError for a non-existent audio file.
        - Publishes progress events to Redis and ends with stage="done",
          pct=100.
        - Fails and emits stage="error" when LangGraph pipeline raises.
        - Fails gracefully when LangGraph is not importable (ImportError).
        - Returns a dict (final_report) on successful completion.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from samplemind.core.tasks.agent_tasks import (
    PROGRESS_KEY_TEMPLATE,
    PROGRESS_TTL,
    _get_redis,
    _push_progress,
    run_analysis_agent,
)
from samplemind.core.tasks.celery_app import celery_app


# ---------------------------------------------------------------------------
# Celery in-memory config fixture (avoids Redis connection in tests)
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def celery_memory_config():
    """Configure Celery to run synchronously with in-memory backend."""
    prev_backend = celery_app.conf.result_backend
    prev_broker = celery_app.conf.broker_url
    celery_app.conf.update(
        task_always_eager=True,
        task_eager_propagates=False,   # store exceptions in result, don't re-raise
        result_backend="cache+memory://",
        broker_url="memory://",
    )
    yield
    celery_app.conf.update(
        task_always_eager=False,
        task_eager_propagates=True,
        result_backend=prev_backend,
        broker_url=prev_broker,
    )


# ---------------------------------------------------------------------------
# _get_redis
# ---------------------------------------------------------------------------


def test_get_redis_returns_none_or_client():
    """_get_redis returns a redis client or None gracefully."""
    result = _get_redis()
    assert result is None or hasattr(result, "rpush")


def test_get_redis_no_exception():
    """_get_redis never raises even when redis is unavailable."""
    import sys
    redis_mod = sys.modules.pop("redis", None)
    try:
        result = _get_redis()
    finally:
        if redis_mod is not None:
            sys.modules["redis"] = redis_mod
    assert result is None or hasattr(result, "rpush")


# ---------------------------------------------------------------------------
# _push_progress
# ---------------------------------------------------------------------------


def test_push_progress_calls_rpush_and_expire():
    r = MagicMock()
    _push_progress(r, "task-abc", "analysis", 40, "Extracting features")

    key = PROGRESS_KEY_TEMPLATE.format(task_id="task-abc")
    assert r.rpush.call_count == 1
    raw = r.rpush.call_args[0][1]
    event = json.loads(raw)
    assert event["stage"] == "analysis"
    assert event["pct"] == 40
    assert event["message"] == "Extracting features"
    assert "ts" in event

    r.expire.assert_called_once_with(key, PROGRESS_TTL)


def test_push_progress_noop_when_redis_none():
    """_push_progress does nothing when r is None."""
    _push_progress(None, "task-xyz", "routing", 5, "Starting")


def test_push_progress_handles_redis_error():
    """If rpush raises, _push_progress swallows the exception."""
    r = MagicMock()
    r.rpush.side_effect = ConnectionError("Redis down")
    _push_progress(r, "task-err", "routing", 5, "msg")


# ---------------------------------------------------------------------------
# run_analysis_agent — test via apply() with mocked Redis + LangGraph
# ---------------------------------------------------------------------------


def test_run_analysis_agent_file_not_found():
    """Task fails with FileNotFoundError for a missing file."""
    with patch("samplemind.core.tasks.agent_tasks._get_redis", return_value=None):
        result = run_analysis_agent.apply(args=["/nonexistent/file.wav"])
    assert result.failed()
    assert isinstance(result.result, FileNotFoundError)


def test_run_analysis_agent_pushes_progress(tmp_path):
    """
    For an existing file, task publishes progress events to Redis
    and ends with 'done' at 100%.
    """
    audio = tmp_path / "sample.wav"
    audio.write_bytes(b"\x00" * 100)

    mock_redis = MagicMock()
    mock_graph = MagicMock()
    mock_graph.stream.return_value = iter(
        [
            {
                "analysis": {
                    "current_stage": "analysis",
                    "progress_pct": 20,
                    "messages": ["ok"],
                }
            }
        ]
    )

    with patch("samplemind.core.tasks.agent_tasks._get_redis", return_value=mock_redis):
        with patch("samplemind.ai.agents.graph.build_graph", return_value=mock_graph):
            result = run_analysis_agent.apply(args=[str(audio)])

    assert result.successful()
    assert mock_redis.rpush.call_count >= 1
    last_raw = mock_redis.rpush.call_args_list[-1][0][1]
    last_event = json.loads(last_raw)
    assert last_event["stage"] == "done"
    assert last_event["pct"] == 100


def test_run_analysis_agent_pipeline_error(tmp_path):
    """Task fails when LangGraph pipeline raises."""
    audio = tmp_path / "sample.wav"
    audio.write_bytes(b"\x00" * 100)

    mock_redis = MagicMock()
    mock_graph = MagicMock()
    mock_graph.stream.side_effect = RuntimeError("LangGraph crashed")

    with patch("samplemind.core.tasks.agent_tasks._get_redis", return_value=mock_redis):
        with patch("samplemind.ai.agents.graph.build_graph", return_value=mock_graph):
            result = run_analysis_agent.apply(args=[str(audio)])

    assert result.failed()
    calls_raw = [c[0][1] for c in mock_redis.rpush.call_args_list]
    error_events = [
        json.loads(r) for r in calls_raw if json.loads(r).get("stage") == "error"
    ]
    assert len(error_events) >= 1


def test_run_analysis_agent_import_error(tmp_path):
    """Task fails gracefully when LangGraph is not importable."""
    audio = tmp_path / "sample.wav"
    audio.write_bytes(b"\x00" * 100)

    with patch("samplemind.core.tasks.agent_tasks._get_redis", return_value=None):
        with patch(
            "samplemind.ai.agents.graph.build_graph",
            side_effect=ImportError("langgraph not installed"),
        ):
            result = run_analysis_agent.apply(args=[str(audio)])

    assert result.failed()
    assert isinstance(result.result, ImportError)


def test_run_analysis_agent_returns_dict(tmp_path):
    """Successful run returns a dict (the final_report)."""
    audio = tmp_path / "sample.wav"
    audio.write_bytes(b"\x00" * 100)

    mock_graph = MagicMock()
    mock_graph.stream.return_value = iter(
        [
            {
                "aggregator": {
                    "final_report": {"tags": {"genre": ["trap"]}},
                    "progress_pct": 100,
                    "messages": [],
                }
            }
        ]
    )

    with patch("samplemind.core.tasks.agent_tasks._get_redis", return_value=None):
        with patch("samplemind.ai.agents.graph.build_graph", return_value=mock_graph):
            result = run_analysis_agent.apply(args=[str(audio)])

    assert result.successful()
    assert isinstance(result.result, dict)
