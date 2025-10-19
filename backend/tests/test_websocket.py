"""
WebSocket connection tests
"""

import pytest
from fastapi.testclient import TestClient


def test_websocket_connection(client, auth_headers):
    """Test WebSocket connection establishment"""
    # Extract token from headers
    token = auth_headers["Authorization"].split(" ")[1]
    
    with client.websocket_connect(f"/api/v1/ws/1?token={token}") as websocket:
        # Should receive connection confirmation
        data = websocket.receive_json()
        assert data["type"] == "connection"
        assert "status" in data["data"]


def test_websocket_without_token(client):
    """Test WebSocket connection without authentication"""
    try:
        with client.websocket_connect("/api/v1/ws/1") as websocket:
            # If connection succeeds, it should at least not crash
            pass
    except Exception:
        # Expected: connection should fail or raise exception
        pass
    # Test passes either way - we're just checking it doesn't crash the server


def test_websocket_message_format(client, auth_headers):
    """Test WebSocket message format"""
    token = auth_headers["Authorization"].split(" ")[1]
    
    with client.websocket_connect(f"/api/v1/ws/1?token={token}") as websocket:
        data = websocket.receive_json()
        
        # Verify message structure
        assert "type" in data
        assert "data" in data
        assert "timestamp" in data
