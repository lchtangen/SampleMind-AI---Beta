"""WebSocket endpoints for real-time updates"""

import asyncio
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()
logger = logging.getLogger(__name__)


# Connection manager
class ConnectionManager:
    """Manages WebSocket connections for real-time updates.

    Handles client connections, disconnections, and message broadcasting
    for real-time communication with clients.

    Attributes:
        active_connections: Dictionary mapping client IDs to WebSocket instances
    """

    def __init__(self) -> None:
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")

    def disconnect(self, client_id: str) -> None:
        """Disconnect a client and remove from active connections.

        Args:
            client_id: Unique identifier for the client to disconnect
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected")

    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)


manager = ConnectionManager()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket connection for real-time updates"""
    await manager.connect(client_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now - extend for actual processing updates
            await manager.send_message(
                client_id, {"type": "message", "client_id": client_id, "data": data}
            )
    except WebSocketDisconnect:
        manager.disconnect(client_id)


@router.websocket("/ws/progress/{job_id}")
async def progress_websocket(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time batch job progress updates

    Sends progress updates every second while job is processing
    """
    await manager.connect(job_id, websocket)

    try:
        # Import here to avoid circular dependency
        from .batch import active_jobs

        while True:
            if job_id not in active_jobs:
                await websocket.send_json({"error": "Job not found", "job_id": job_id})
                break

            job = active_jobs[job_id]

            # Send progress update
            await websocket.send_json(
                {
                    "job_id": job_id,
                    "status": job.status,
                    "progress": job.progress_percent,
                    "processed": job.processed_files,
                    "total": job.total_files,
                    "errors": len(job.errors),
                }
            )

            # Stop if job is completed or failed
            if job.status in ["completed", "failed"]:
                break

            # Wait before next update
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        manager.disconnect(job_id)
        logger.info(f"Client {job_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for {job_id}: {e}")
        manager.disconnect(job_id)


@router.websocket("/ws/agents/{session_id}")
async def agent_pipeline_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for streaming LangGraph agent pipeline progress.

    Client sends: {"file_path": "/path/to/sample.wav", "depth": "standard"}
    Server streams: partial AudioAnalysisState updates as each agent completes.

    Final message has type="done" and contains the full final_report.
    """
    await manager.connect(session_id, websocket)
    try:
        # Wait for the client to send the file path
        raw = await websocket.receive_text()
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            await websocket.send_json(
                {"type": "error", "message": "Invalid JSON payload"}
            )
            return

        file_path = payload.get("file_path", "")
        depth = payload.get("depth", "standard")

        if not file_path:
            await websocket.send_json(
                {"type": "error", "message": "file_path is required"}
            )
            return

        await websocket.send_json(
            {"type": "start", "session_id": session_id, "file_path": file_path}
        )

        # Stream agent state updates
        try:
            from samplemind.ai.agents.graph import stream_analysis_pipeline

            async for partial_state in stream_analysis_pipeline(
                file_path=file_path,
                session_id=session_id,
                analysis_depth=depth,
            ):
                event = {
                    "type": "progress",
                    "stage": partial_state.get("current_stage", ""),
                    "pct": partial_state.get("progress_pct", 0),
                    "messages": partial_state.get("messages", []),
                    "errors": partial_state.get("errors", []),
                }
                await websocket.send_json(event)

                # Send done when aggregator finishes
                if partial_state.get("current_stage") == "done":
                    await websocket.send_json(
                        {
                            "type": "done",
                            "session_id": session_id,
                            "final_report": partial_state.get("final_report", {}),
                        }
                    )
                    break

        except ImportError:
            await websocket.send_json(
                {
                    "type": "error",
                    "message": "LangGraph not installed. Run: pip install langgraph",
                }
            )
        except Exception as exc:
            logger.error("Agent pipeline error for session %s: %s", session_id, exc)
            await websocket.send_json({"type": "error", "message": str(exc)})

    except WebSocketDisconnect:
        logger.info("Agent WebSocket client %s disconnected", session_id)
    finally:
        manager.disconnect(session_id)


# ---------------------------------------------------------------------------
# Phase 16: Redis-backed Celery agent progress stream
# ---------------------------------------------------------------------------

import os  # noqa: E402


def _get_redis_sync():  # type: ignore[return]
    """Return a redis.Redis client or None if unavailable."""
    try:
        import redis  # type: ignore

        url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        return redis.from_url(url, decode_responses=True)
    except Exception:
        return None


@router.websocket("/ws/agent/{task_id}")
async def agent_task_progress(websocket: WebSocket, task_id: str):
    """
    Stream Celery agent-task progress events over WebSocket.

    Polls the Redis list ``agent_progress:{task_id}`` every 500 ms and
    forwards every new JSON event to the client.

    Event schema::

        {"stage": "tagging", "pct": 40, "message": "Running CLAP...", "ts": 1234567890.0}

    The connection is closed automatically when ``pct == 100`` or
    ``stage == "error"``.

    Usage::

        wscat -c ws://localhost:8000/api/v1/ws/agent/<task_id>
    """
    await websocket.accept()
    logger.info("Agent progress stream opened for task %s", task_id)

    redis_key = f"agent_progress:{task_id}"
    r = await asyncio.get_event_loop().run_in_executor(None, _get_redis_sync)

    # Index of the next event to read from the Redis list
    cursor = 0

    try:
        while True:
            if r is not None:
                try:
                    # Fetch all events from cursor onwards (non-blocking)
                    raw_events = await asyncio.get_event_loop().run_in_executor(
                        None, lambda: r.lrange(redis_key, cursor, -1)
                    )
                except Exception as redis_exc:
                    logger.debug("Redis lrange failed: %s", redis_exc)
                    raw_events = []
            else:
                raw_events = []

            for raw in raw_events:
                try:
                    event = json.loads(raw)
                except json.JSONDecodeError:
                    event = {"stage": "unknown", "pct": 0, "message": raw}

                await websocket.send_json(event)
                cursor += 1

                pct = event.get("pct", 0)
                stage = event.get("stage", "")
                if pct >= 100 or stage == "error":
                    logger.info(
                        "Agent task %s finished (stage=%s pct=%s)", task_id, stage, pct
                    )
                    return

            await asyncio.sleep(0.5)

    except WebSocketDisconnect:
        logger.info("Agent progress client disconnected for task %s", task_id)
    except Exception as exc:
        logger.error("Agent progress stream error for task %s: %s", task_id, exc)
        try:
            await websocket.send_json({"stage": "error", "pct": 0, "message": str(exc)})
        except Exception:
            pass
