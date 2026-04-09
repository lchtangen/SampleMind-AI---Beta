"""
SampleMind AI v3.0 — Unified Server Entry Point

Exposes the full FastAPI application at samplemind.server.main:app
as required by the Dockerfile CMD directive:

    uvicorn samplemind.server.main:app --host 0.0.0.0 --port 8000

This module re-exports the production FastAPI app from the interfaces layer
and mounts the DAW bridge WebSocket on a dedicated path.
"""

import json
import logging

from fastapi import WebSocket, WebSocketDisconnect

from samplemind.interfaces.api.main import app  # noqa: F401 — re-export for Dockerfile
from samplemind.server.bridge import bridge

logger = logging.getLogger(__name__)


@app.websocket("/daw/ws")
async def daw_bridge_websocket(websocket: WebSocket):
    """
    DAW Plugin Bridge WebSocket endpoint.

    Allows Ableton Live (Max for Live), FL Studio, and other DAW plugins
    to connect and receive real-time sync events (BPM, sample loads, etc.).

    Path: /daw/ws
    """
    await bridge.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await bridge.handle_message(message, websocket)
            except json.JSONDecodeError:
                logger.warning("DAW bridge received invalid JSON payload")
    except WebSocketDisconnect:
        bridge.disconnect(websocket)


__all__ = ["app"]
