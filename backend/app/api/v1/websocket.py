"""
WebSocket endpoints for real-time updates
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Dict, Set
import json
import asyncio

router = APIRouter(prefix="/ws", tags=["websocket"])

# Connection manager for WebSocket clients
class ConnectionManager:
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept WebSocket connection and register user"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        print(f"✅ WebSocket connected: user_id={user_id}, total={len(self.active_connections[user_id])}")
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Remove WebSocket connection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        print(f"❌ WebSocket disconnected: user_id={user_id}")
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Send message to specific user's connections"""
        if user_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.add(connection)
            
            # Clean up disconnected clients
            for conn in disconnected:
                self.active_connections[user_id].discard(conn)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected users"""
        for user_connections in self.active_connections.values():
            for connection in user_connections:
                try:
                    await connection.send_json(message)
                except:
                    pass


# Global connection manager
manager = ConnectionManager()


@router.websocket("/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    token: str = Query(None)
):
    """
    WebSocket endpoint for real-time updates
    
    - **user_id**: User ID for this connection
    - **token**: JWT access token for authentication (query parameter)
    
    Message format:
    ```json
    {
        "type": "upload_progress" | "analysis_status" | "notification",
        "data": {...},
        "timestamp": "2025-10-19T20:00:00Z"
    }
    ```
    """
    # TODO: Verify token before accepting connection
    # For now, accept all connections (dev mode)
    
    await manager.connect(websocket, user_id)
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connection",
            "data": {
                "status": "connected",
                "user_id": user_id,
                "message": "WebSocket connection established"
            },
            "timestamp": "2025-10-19T20:00:00Z"
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                # Respond to ping with pong
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": "2025-10-19T20:00:00Z"
                })
            elif message.get("type") == "subscribe":
                # Subscribe to specific events
                await websocket.send_json({
                    "type": "subscribed",
                    "data": message.get("data", {}),
                    "timestamp": "2025-10-19T20:00:00Z"
                })
            else:
                # Echo back for testing
                await websocket.send_json({
                    "type": "echo",
                    "data": message,
                    "timestamp": "2025-10-19T20:00:00Z"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        manager.disconnect(websocket, user_id)


async def send_upload_progress(user_id: int, audio_id: int, progress: float, status: str):
    """
    Send upload progress update to user
    
    Args:
        user_id: User ID
        audio_id: Audio file ID
        progress: Progress percentage (0-100)
        status: Status message
    """
    await manager.send_personal_message({
        "type": "upload_progress",
        "data": {
            "audio_id": audio_id,
            "progress": progress,
            "status": status
        },
        "timestamp": "2025-10-19T20:00:00Z"
    }, user_id)


async def send_analysis_status(user_id: int, audio_id: int, status: str, progress: float = None, results: dict = None):
    """
    Send analysis status update to user
    
    Args:
        user_id: User ID
        audio_id: Audio file ID
        status: Status (processing, completed, failed)
        progress: Optional progress percentage
        results: Optional analysis results when complete
    """
    message = {
        "type": "analysis_status",
        "data": {
            "audio_id": audio_id,
            "status": status
        },
        "timestamp": "2025-10-19T20:00:00Z"
    }
    
    if progress is not None:
        message["data"]["progress"] = progress
    
    if results is not None:
        message["data"]["results"] = results
    
    await manager.send_personal_message(message, user_id)


async def send_notification(user_id: int, title: str, message: str, level: str = "info"):
    """
    Send notification to user
    
    Args:
        user_id: User ID
        title: Notification title
        message: Notification message
        level: Notification level (info, success, warning, error)
    """
    await manager.send_personal_message({
        "type": "notification",
        "data": {
            "title": title,
            "message": message,
            "level": level
        },
        "timestamp": "2025-10-19T20:00:00Z"
    }, user_id)
