"""
Tests for Agent History API endpoint (P3-009)
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client with the tasks router."""
    from fastapi import FastAPI

    from samplemind.interfaces.api.routes.tasks import router

    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return TestClient(app)


class TestAgentHistoryEndpoint:
    @patch("samplemind.ai.agents.memory.AgentMemory")
    def test_empty_history(self, MockMemory, client):
        mock_instance = MockMemory.return_value
        mock_instance._ensure_loaded = MagicMock()
        mock_instance._entries = []

        resp = client.get("/api/v1/tasks/agent/history")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["runs"] == []

    @patch("samplemind.ai.agents.memory.AgentMemory")
    def test_with_entries(self, MockMemory, client):
        from samplemind.ai.agents.memory import MemoryEntry

        entries = [
            MemoryEntry(
                memory_id=f"mem_{i}",
                file_path=f"/file_{i}.wav",
                timestamp=1000.0 + i,
                summary=f"Entry {i}",
                bpm=120.0 + i,
            )
            for i in range(5)
        ]
        mock_instance = MockMemory.return_value
        mock_instance._ensure_loaded = MagicMock()
        mock_instance._entries = entries

        resp = client.get("/api/v1/tasks/agent/history?limit=3&offset=0")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 5
        assert len(data["runs"]) == 3
        # Most recent first
        assert data["runs"][0]["memory_id"] == "mem_4"

    @patch("samplemind.ai.agents.memory.AgentMemory")
    def test_pagination(self, MockMemory, client):
        from samplemind.ai.agents.memory import MemoryEntry

        entries = [
            MemoryEntry(
                memory_id=f"mem_{i}",
                file_path=f"/file_{i}.wav",
                timestamp=1000.0 + i,
                summary=f"Entry {i}",
            )
            for i in range(10)
        ]
        mock_instance = MockMemory.return_value
        mock_instance._ensure_loaded = MagicMock()
        mock_instance._entries = entries

        resp = client.get("/api/v1/tasks/agent/history?limit=5&offset=5")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 10
        assert len(data["runs"]) == 5
        assert data["offset"] == 5

    def test_default_params(self, client):
        """Test with no AgentMemory import (fallback)."""
        resp = client.get("/api/v1/tasks/agent/history")
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data
        assert "runs" in data

    @patch("samplemind.ai.agents.memory.AgentMemory")
    def test_limit_cap(self, MockMemory, client):
        mock_instance = MockMemory.return_value
        mock_instance._ensure_loaded = MagicMock()
        mock_instance._entries = []

        resp = client.get("/api/v1/tasks/agent/history?limit=500")
        assert resp.status_code == 200
        data = resp.json()
        assert data["limit"] == 100
