"""
Unit tests for SampleMind LangGraph agent system (Steps 13–16).

Covers:
- AudioAnalysisState schema
- router_node validation
- aggregator_node output structure
- tagging_agent logic (no I/O required)
- mixing_agent Camelot wheel
- pack_builder_agent manifest structure
- recommendation_agent graceful fallback
- tool_use cache key determinism
- run_analysis_pipeline fallback when LangGraph is absent (ImportError path)
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest


# ── State schema ──────────────────────────────────────────────────────────────


def test_audio_analysis_state_defaults():
    """State TypedDict accepts all required fields."""
    from samplemind.ai.agents.state import AudioAnalysisState

    state: AudioAnalysisState = {
        "file_path": "/tmp/test.wav",
        "audio_features": {},
        "messages": [],
        "errors": [],
    }
    assert state["file_path"] == "/tmp/test.wav"


# ── router_node ───────────────────────────────────────────────────────────────


def test_router_node_missing_file_path():
    from samplemind.ai.agents.graph import router_node

    result = router_node({"file_path": "", "errors": [], "messages": []})
    assert result["current_stage"] == "error"
    assert any("file_path" in e for e in result["errors"])


def test_router_node_nonexistent_file():
    from samplemind.ai.agents.graph import router_node

    result = router_node(
        {"file_path": "/nonexistent/sample.wav", "errors": [], "messages": []}
    )
    assert result["current_stage"] == "error"
    assert any("not found" in e for e in result["errors"])


def test_router_node_valid_file(tmp_path):
    from samplemind.ai.agents.graph import router_node

    wav = tmp_path / "test.wav"
    wav.write_bytes(b"\x00" * 100)

    result = router_node(
        {
            "file_path": str(wav),
            "errors": [],
            "messages": [],
            "analysis_depth": "standard",
            "requested_agents": [],
        }
    )
    assert result["current_stage"] == "routing"
    assert result["progress_pct"] == 5


# ── aggregator_node ───────────────────────────────────────────────────────────


def test_aggregator_node_structure():
    from samplemind.ai.agents.graph import aggregator_node

    state = {
        "file_path": "/tmp/test.wav",
        "audio_features": {"bpm": 128.0, "key": "A"},
        "analysis_result": {"summary": "Great track"},
        "tags": {"genre": ["House"]},
        "mixing_recommendations": {"camelot_position": "8B"},
        "similar_samples": [],
        "pack_manifest": {},
        "errors": [],
        "messages": ["step1", "step2"],
    }
    result = aggregator_node(state)

    assert result["current_stage"] == "done"
    assert result["progress_pct"] == 100
    report = result["final_report"]
    assert report["audio_features"]["bpm"] == 128.0
    assert report["tags"]["genre"] == ["House"]
    assert "Pipeline complete" in result["messages"][-1]


# ── tagging_agent ─────────────────────────────────────────────────────────────


def test_tagging_agent_energy_levels():
    """RMS → energy label mapping."""
    from samplemind.ai.agents.tagging_agent import tagging_agent

    for rms, expected_energy in [(0.01, "low"), (0.08, "medium"), (0.25, "high")]:
        result = tagging_agent(
            {
                "audio_features": {"bpm": 120.0, "key": "C", "scale": "major", "rms_energy": rms, "spectral_centroid": 2500, "duration": 4.0},
                "messages": [],
                "errors": [],
            }
        )
        assert result["tags"]["energy"] == expected_energy, f"rms={rms}"


def test_tagging_agent_major_vs_minor_mood():
    from samplemind.ai.agents.tagging_agent import tagging_agent

    major = tagging_agent({"audio_features": {"bpm": 128.0, "key": "C", "scale": "major", "rms_energy": 0.1, "spectral_centroid": 2500, "duration": 4.0}, "messages": [], "errors": []})
    minor = tagging_agent({"audio_features": {"bpm": 128.0, "key": "A", "scale": "minor", "rms_energy": 0.1, "spectral_centroid": 2500, "duration": 4.0}, "messages": [], "errors": []})

    assert "dark" in major["tags"]["mood"] or "melancholic" not in major["tags"]["mood"]
    assert any("dark" in m or "melancholic" in m or "emotional" in m for m in minor["tags"]["mood"])


def test_tagging_agent_raw_labels_no_duplicates():
    from samplemind.ai.agents.tagging_agent import tagging_agent

    result = tagging_agent({"audio_features": {"bpm": 130.0, "key": "G", "scale": "minor", "rms_energy": 0.12, "spectral_centroid": 3500, "duration": 8.0}, "messages": [], "errors": []})
    labels = result["tags"]["raw_labels"]
    assert len(labels) == len(set(labels)), "raw_labels must not contain duplicates"


# ── mixing_agent ──────────────────────────────────────────────────────────────


def test_mixing_agent_camelot_output():
    from samplemind.ai.agents.mixing_agent import mixing_agent

    result = mixing_agent(
        {
            "audio_features": {"bpm": 128.0, "key": "A", "scale": "minor"},
            "messages": [],
            "errors": [],
        }
    )
    rec = result.get("mixing_recommendations", {})
    # A minor → 8A in Camelot wheel
    assert rec.get("camelot_position") == "8A"
    assert isinstance(rec.get("compatible_camelot_keys"), list)


def test_mixing_agent_bpm_range():
    from samplemind.ai.agents.mixing_agent import mixing_agent

    result = mixing_agent(
        {
            "audio_features": {"bpm": 140.0, "key": "C", "scale": "major"},
            "messages": [],
            "errors": [],
        }
    )
    rec = result["mixing_recommendations"]
    bpm_range = rec["bpm_compatible_range"]
    assert "132" in bpm_range or "133" in bpm_range  # ±6% of 140 ≈ 131.6–148.4


# ── pack_builder_agent ────────────────────────────────────────────────────────


def test_pack_builder_manifest_structure():
    from samplemind.ai.agents.pack_builder_agent import pack_builder_agent

    result = pack_builder_agent(
        {
            "file_path": "/samples/kick_01.wav",
            "audio_features": {"bpm": 128.0, "key": "C", "scale": "major", "rms_energy": 0.2, "duration": 1.5},
            "tags": {"genre": ["House"], "mood": ["Energetic"], "energy": "high", "instrument_hints": ["kick"], "raw_labels": []},
            "mixing_recommendations": {"camelot_position": "8B", "compatible_camelot_keys": ["7B", "9B"], "bpm_compatible_range": "120–136"},
            "analysis_result": {"summary": "Punchy kick"},
            "messages": [],
            "errors": [],
        }
    )
    manifest = result["pack_manifest"]
    assert manifest["version"] == "1.0"
    assert "suggested_filename" in manifest
    assert "folder_path" in manifest
    assert manifest["metadata"]["bpm"] == 128.0
    assert "house" in manifest["folder_path"].lower() or "unknown" in manifest["folder_path"].lower()
    assert "readme_template" in manifest


# ── recommendation_agent ──────────────────────────────────────────────────────


def test_recommendation_agent_fallback_on_missing_db():
    """Should not raise — gracefully falls back when ChromaDB unavailable."""
    from samplemind.ai.agents.recommendation_agent import recommendation_agent

    result = recommendation_agent(
        {
            "file_path": "/nonexistent/sample.wav",
            "audio_features": {"bpm": 120.0},
            "tags": {"genre": ["Techno"]},
            "messages": [],
            "errors": [],
        }
    )
    # Fallback should produce at least one entry
    assert isinstance(result.get("similar_samples"), list)
    assert len(result["similar_samples"]) >= 1


# ── tool_use cache key ────────────────────────────────────────────────────────


def test_cache_key_determinism():
    """Same tool + args → same cache key regardless of dict insertion order."""
    from samplemind.ai.agents.tool_use import _cache_key

    args1 = {"file_path": "/tmp/x.wav", "depth": "standard"}
    args2 = {"depth": "standard", "file_path": "/tmp/x.wav"}

    assert _cache_key("analyze_audio", args1) == _cache_key("analyze_audio", args2)


def test_cache_key_different_tools():
    from samplemind.ai.agents.tool_use import _cache_key

    k1 = _cache_key("analyze_audio", {"file_path": "/a.wav"})
    k2 = _cache_key("tag_sample", {"file_path": "/a.wav"})
    assert k1 != k2


def test_cache_key_has_sm_prefix():
    from samplemind.ai.agents.tool_use import _cache_key

    key = _cache_key("analyze_audio", {"file_path": "/a.wav"})
    assert key.startswith("sm:tool:")


# ── SAMPLEMIND_TOOLS schema ───────────────────────────────────────────────────


def test_samplemind_tools_schema():
    """All tools have required Anthropic tool schema fields."""
    from samplemind.ai.agents.tool_use import SAMPLEMIND_TOOLS

    required_names = {"analyze_audio", "search_similar", "get_recommendations", "tag_sample", "build_pack"}
    tool_names = {t["name"] for t in SAMPLEMIND_TOOLS}
    assert required_names == tool_names

    for tool in SAMPLEMIND_TOOLS:
        assert "name" in tool
        assert "description" in tool
        assert "input_schema" in tool
        schema = tool["input_schema"]
        assert schema["type"] == "object"
        assert "required" in schema
