"""WebSocket endpoints for real-time updates"""

from typing import Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import logging
import asyncio

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
        self.active_connections: Dict[str, WebSocket] = {}

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
            await websocket.send_json({"type": "error", "message": "Invalid JSON payload"})
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
