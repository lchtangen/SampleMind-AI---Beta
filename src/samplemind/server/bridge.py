import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from typing import List, Optional

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

@dataclass
class BridgeMessage:
    """Message format for DAW bridge communication"""
    action: str
    payload: dict
    source: str = "Client"

class DAWBridgeServer:
    """
    WebSocket Server for real-time DAW communication.
    Allows plugins (VST/AU) to sync with SampleMind.
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._is_running = False

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Active connections: {len(self.active_connections)}")

        # Send handshake
        await self.send_message(
            BridgeMessage(action="handshake", payload={"server": "SampleMind v6", "status": "ready"}),
            websocket
        )

    def disconnect(self, websocket: WebSocket) -> None:
        """Disconnect a client from the bridge"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Active connections: {len(self.active_connections)}")

    async def broadcast(self, message: BridgeMessage):
        """Send a message to all connected clients (DAWs)."""
        if not self.active_connections:
            return

        payload_json = json.dumps(asdict(message))
        for connection in self.active_connections:
            try:
                await connection.send_text(payload_json)
            except Exception as e:
                logger.error(f"Failed to broadcast to client: {e}")

    async def send_message(self, message: BridgeMessage, websocket: WebSocket):
        """Send to a specific client."""
        try:
            await websocket.send_text(json.dumps(asdict(message)))
        except Exception as e:
            logger.error(f"Failed to send message: {e}")

    async def handle_message(self, message_data: dict, websocket: WebSocket):
        """Process incoming messages from DAW."""
        action = message_data.get("action")
        payload = message_data.get("payload", {})

        logger.info(f"Received DAW action: {action}")

        if action == "sync_bpm":
            bpm = payload.get("bpm")
            logger.info(f"DAW synced BPM: {bpm}")
            # Here we would update the collection state or notify other services

        elif action == "load_sample":
            path = payload.get("path")
            logger.info(f"DAW requesting sample: {path}")
            # Logic to locate and serve sample

# Global instance
bridge = DAWBridgeServer()

# FastAPI App Wrapper
import uvicorn
from fastapi import FastAPI

app = FastAPI(title="SampleMind DAW Bridge")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await bridge.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await bridge.handle_message(message, websocket)
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        bridge.disconnect(websocket)

def run_server(host="127.0.0.1", port=8000):
    """Run the bridge server."""
    uvicorn.run(app, host=host, port=port)

