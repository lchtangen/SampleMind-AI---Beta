"""
Tests for AgentMemory (P3-014)

Tests the FAISS-backed conversation memory for the agent pipeline.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from samplemind.ai.agents.memory import (
    AgentMemory,
    MemoryEntry,
    RecalledMemory,
    _state_to_memory_entry,
    _state_to_summary,
    _text_to_embedding,
)


@pytest.fixture
def memory_dir(tmp_path):
    return tmp_path / "agent_memory"


@pytest.fixture
def memory(memory_dir):
    return AgentMemory(memory_dir=str(memory_dir))


@pytest.fixture
def sample_state():
    return {
        "file_path": "/samples/kick_808.wav",
        "analysis_depth": "standard",
        "audio_features": {"bpm": 140.0, "key": "A minor"},
        "tags": {
            "genre": "trap",
            "mood": "dark",
            "instrument": "kick",
            "tags": ["808", "bass", "heavy"],
        },
        "analysis_result": {"description": "Heavy 808 kick with deep sub bass"},
        "quality_flags": {"issues": ["clipping"]},
        "mixing_recommendations": {"eq_suggestion": "cut 200Hz"},
        "categorization": {"category": "drums/kick"},
        "micro_timing": {"groove": "straight"},
    }


class TestMemoryEntry:
    def test_defaults(self):
        e = MemoryEntry(
            memory_id="abc123",
            file_path="/test.wav",
            timestamp=1000.0,
            summary="Test entry",
        )
        assert e.tags == []
        assert e.bpm is None
        assert e.genre is None
        assert e.agent_outputs == {}

    def test_full(self):
        e = MemoryEntry(
            memory_id="abc123",
            file_path="/test.wav",
            timestamp=1000.0,
            summary="Test",
            tags=["kick", "808"],
            bpm=140.0,
            key="A minor",
            genre="trap",
            mood="dark",
        )
        assert e.bpm == 140.0
        assert e.genre == "trap"


class TestTextToEmbedding:
    def test_returns_correct_shape(self):
        import numpy as np

        # Force hash-based fallback by patching CLAPEmbedder import
        with patch.dict("sys.modules", {"samplemind.core.search.faiss_index": MagicMock(CLAPEmbedder=MagicMock(side_effect=ImportError))}):
            # Clear any cached module reference so _text_to_embedding hits the fallback
            vec = _text_to_embedding("dark trap kick")
        assert len(vec) == 512
        assert isinstance(vec, np.ndarray)

    def test_normalized(self):
        import numpy as np

        with patch.dict("sys.modules", {"samplemind.core.search.faiss_index": MagicMock(CLAPEmbedder=MagicMock(side_effect=ImportError))}):
            vec = _text_to_embedding("test query")
        norm = np.linalg.norm(vec)
        assert abs(norm - 1.0) < 0.01

    def test_deterministic(self):
        import numpy as np

        with patch.dict("sys.modules", {"samplemind.core.search.faiss_index": MagicMock(CLAPEmbedder=MagicMock(side_effect=ImportError))}):
            v1 = _text_to_embedding("same input text")
            v2 = _text_to_embedding("same input text")
        assert np.allclose(v1, v2)

    def test_different_for_different_input(self):
        import numpy as np

        with patch.dict("sys.modules", {"samplemind.core.search.faiss_index": MagicMock(CLAPEmbedder=MagicMock(side_effect=ImportError))}):
            v1 = _text_to_embedding("dark trap kick")
            v2 = _text_to_embedding("bright jazz piano")
        assert not np.allclose(v1, v2)


class TestStateToSummary:
    def test_basic_state(self, sample_state):
        summary = _state_to_summary(sample_state)
        assert "kick_808" in summary
        assert "BPM: 140" in summary
        assert "Key: A minor" in summary
        assert "Genre: trap" in summary

    def test_empty_state(self):
        summary = _state_to_summary({})
        assert summary == "Audio analysis"

    def test_partial_state(self):
        summary = _state_to_summary({"file_path": "/test.wav"})
        assert "test.wav" in summary


class TestStateToMemoryEntry:
    def test_creates_entry(self, sample_state):
        entry = _state_to_memory_entry(sample_state)
        assert entry.file_path == "/samples/kick_808.wav"
        assert entry.bpm == 140.0
        assert entry.key == "A minor"
        assert entry.genre == "trap"
        assert entry.mood == "dark"
        assert len(entry.memory_id) == 12
        assert entry.timestamp > 0

    def test_handles_empty_state(self):
        entry = _state_to_memory_entry({})
        assert entry.file_path == "unknown"
        assert entry.bpm is None


class TestAgentMemory:
    def test_init_creates_dir(self, memory_dir):
        mem = AgentMemory(memory_dir=str(memory_dir))
        assert memory_dir.exists()

    def test_entry_count_empty(self, memory):
        assert memory.entry_count == 0

    def test_store_and_count(self, memory, sample_state):
        asyncio.get_event_loop().run_until_complete(memory.store(sample_state))
        assert memory.entry_count == 1

    def test_store_multiple(self, memory, sample_state):
        for _ in range(3):
            asyncio.get_event_loop().run_until_complete(memory.store(sample_state))
        assert memory.entry_count == 3

    def test_recall_empty(self, memory):
        results = asyncio.get_event_loop().run_until_complete(
            memory.recall("dark trap kick")
        )
        assert results == []

    def test_store_and_recall(self, memory, sample_state):
        asyncio.get_event_loop().run_until_complete(memory.store(sample_state))
        results = asyncio.get_event_loop().run_until_complete(
            memory.recall("dark trap kick 140", top_k=5, min_relevance=0.0)
        )
        # With FAISS installed, recall should return results
        assert isinstance(results, list)
        assert len(results) >= 1

    def test_clear(self, memory, sample_state):
        asyncio.get_event_loop().run_until_complete(memory.store(sample_state))
        assert memory.entry_count == 1
        asyncio.get_event_loop().run_until_complete(memory.clear())
        assert memory.entry_count == 0

    def test_get_conversation_context(self, memory, sample_state):
        asyncio.get_event_loop().run_until_complete(memory.store(sample_state))
        context = asyncio.get_event_loop().run_until_complete(
            memory.get_conversation_context("/samples/test.wav", top_k=3)
        )
        assert isinstance(context, list)

    def test_persistence(self, memory_dir, sample_state):
        mem1 = AgentMemory(memory_dir=str(memory_dir))
        asyncio.get_event_loop().run_until_complete(mem1.store(sample_state))
        assert mem1.entry_count == 1

        # Create new instance that loads from disk
        mem2 = AgentMemory(memory_dir=str(memory_dir))
        assert mem2.entry_count == 1

    def test_metadata_file_created(self, memory, memory_dir, sample_state):
        asyncio.get_event_loop().run_until_complete(memory.store(sample_state))
        meta_path = memory_dir / "memory_meta.json"
        assert meta_path.exists()
        data = json.loads(meta_path.read_text())
        assert len(data) == 1
        assert data[0]["file_path"] == "/samples/kick_808.wav"
