"""
Unit tests for samplemind.ai.agents.quality_agent (P3-006)

Covers: _run_quality_check backend selection, warning generation,
quality_agent() node integration.

Module under test:
    samplemind.ai.agents.quality_agent
        — _run_quality_check, quality_agent (LangGraph node function)

Key test scenarios:
    _run_quality_check — backend selection
        - Uses pyloudnorm when available (returns method="pyloudnorm").
        - Falls back to ffmpeg when pyloudnorm raises ImportError.
        - Returns method="unavailable" stub when both backends fail.
    Warning generation
        - Clipping detected → "clipping" warning.
        - High LUFS (> −5) → "loudness" / "lufs" warning.
        - Low dynamic range (< 3 dB) → "dynamic range" warning.
        - Ideal signal → empty warnings list.
    quality_agent() node
        - Sets current_stage="quality" and progress_pct=65.
        - Skips gracefully for missing or empty file paths.
        - Populates quality_flags from a successful check and appends a
          message.
        - Catches RuntimeError from _run_quality_check and records the
          error.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from samplemind.ai.agents.quality_agent import (
    _run_quality_check,
    quality_agent,
)

# ---------------------------------------------------------------------------
# _run_quality_check — backend selection
# ---------------------------------------------------------------------------


def test_run_quality_check_pyloudnorm_path(tmp_path):
    """Uses pyloudnorm when available."""
    dummy_wav = tmp_path / "clip.wav"
    dummy_wav.write_bytes(b"\x00" * 44)

    mock_metrics = {
        "lufs": -14.0,
        "peak_db": -1.0,
        "clipping": False,
        "dynamic_range_db": 12.0,
        "method": "pyloudnorm",
    }
    with patch(
        "samplemind.ai.agents.quality_agent._measure_loudness_pyloudnorm",
        return_value=mock_metrics,
    ):
        result = _run_quality_check(str(dummy_wav))

    assert result["method"] == "pyloudnorm"
    assert result["lufs"] == pytest.approx(-14.0)
    assert result["clipping"] is False
    assert isinstance(result["warnings"], list)


def test_run_quality_check_ffmpeg_fallback(tmp_path):
    """Falls back to ffmpeg when pyloudnorm is unavailable."""
    dummy_wav = tmp_path / "test.wav"
    dummy_wav.write_bytes(b"\x00" * 44)

    ffmpeg_metrics = {
        "lufs": -20.0,
        "peak_db": -3.0,
        "clipping": False,
        "dynamic_range_db": 8.0,
        "method": "ffmpeg",
    }

    with patch(
        "samplemind.ai.agents.quality_agent._measure_loudness_pyloudnorm",
        side_effect=ImportError("no pyloudnorm"),
    ):
        with patch(
            "samplemind.ai.agents.quality_agent._measure_loudness_ffmpeg",
            return_value=ffmpeg_metrics,
        ):
            result = _run_quality_check(str(dummy_wav))

    assert result["method"] == "ffmpeg"


def test_run_quality_check_unavailable_stub(tmp_path):
    """Returns unavailable stub when both backends fail."""
    dummy_wav = tmp_path / "test.wav"
    dummy_wav.write_bytes(b"\x00" * 44)

    with patch(
        "samplemind.ai.agents.quality_agent._measure_loudness_pyloudnorm",
        side_effect=ImportError,
    ):
        with patch(
            "samplemind.ai.agents.quality_agent._measure_loudness_ffmpeg",
            side_effect=FileNotFoundError("ffmpeg not installed"),
        ):
            result = _run_quality_check(str(dummy_wav))

    assert result["method"] == "unavailable"
    assert result["clipping"] is False
    assert isinstance(result["warnings"], list)


# ---------------------------------------------------------------------------
# Warning generation
# ---------------------------------------------------------------------------


def test_clipping_warning_generated(tmp_path):
    dummy_wav = tmp_path / "clipped.wav"
    dummy_wav.write_bytes(b"\x00" * 44)

    clip_metrics = {
        "lufs": -6.0,
        "peak_db": 1.0,
        "clipping": True,
        "dynamic_range_db": 5.0,
        "method": "pyloudnorm",
    }
    with patch(
        "samplemind.ai.agents.quality_agent._measure_loudness_pyloudnorm",
        return_value=clip_metrics,
    ):
        result = _run_quality_check(str(dummy_wav))

    warnings = result["warnings"]
    assert any("clipping" in w.lower() for w in warnings)


def test_high_lufs_warning(tmp_path):
    dummy_wav = tmp_path / "loud.wav"
    dummy_wav.write_bytes(b"\x00" * 44)

    loud_metrics = {
        "lufs": -3.0,
        "peak_db": -1.0,
        "clipping": False,
        "dynamic_range_db": 2.0,
        "method": "pyloudnorm",
    }
    with patch(
        "samplemind.ai.agents.quality_agent._measure_loudness_pyloudnorm",
        return_value=loud_metrics,
    ):
        result = _run_quality_check(str(dummy_wav))

    warnings = result["warnings"]
    assert any("loudness" in w.lower() or "lufs" in w.lower() for w in warnings)


def test_low_dynamic_range_warning(tmp_path):
    dummy_wav = tmp_path / "compressed.wav"
    dummy_wav.write_bytes(b"\x00" * 44)

    flat_metrics = {
        "lufs": -18.0,
        "peak_db": -2.0,
        "clipping": False,
        "dynamic_range_db": 1.5,
        "method": "pyloudnorm",
    }
    with patch(
        "samplemind.ai.agents.quality_agent._measure_loudness_pyloudnorm",
        return_value=flat_metrics,
    ):
        result = _run_quality_check(str(dummy_wav))

    assert any("dynamic range" in w.lower() for w in result["warnings"])


def test_no_warnings_for_ideal_signal(tmp_path):
    dummy_wav = tmp_path / "ideal.wav"
    dummy_wav.write_bytes(b"\x00" * 44)

    ideal_metrics = {
        "lufs": -18.0,
        "peak_db": -3.0,
        "clipping": False,
        "dynamic_range_db": 12.0,
        "method": "pyloudnorm",
    }
    with patch(
        "samplemind.ai.agents.quality_agent._measure_loudness_pyloudnorm",
        return_value=ideal_metrics,
    ):
        result = _run_quality_check(str(dummy_wav))

    assert result["warnings"] == []


# ---------------------------------------------------------------------------
# quality_agent() node
# ---------------------------------------------------------------------------


def test_quality_agent_sets_stage():
    state = {"file_path": "/nonexistent.wav", "messages": [], "errors": []}
    result = quality_agent(state)
    assert result["current_stage"] == "quality"
    assert result["progress_pct"] == 65


def test_quality_agent_skips_for_missing_file():
    state = {"file_path": "/absolutely/missing.wav", "messages": [], "errors": []}
    result = quality_agent(state)
    assert result["quality_flags"]["skipped"] is True


def test_quality_agent_skips_for_empty_path():
    state = {"file_path": "", "messages": [], "errors": []}
    result = quality_agent(state)
    assert result["quality_flags"]["skipped"] is True


def test_quality_agent_populates_quality_flags(tmp_path):
    audio = tmp_path / "kick.wav"
    audio.write_bytes(b"\x00" * 44)

    good_metrics = {
        "lufs": -18.0,
        "peak_db": -3.0,
        "clipping": False,
        "dynamic_range_db": 12.0,
        "method": "pyloudnorm",
        "warnings": [],
    }

    state = {"file_path": str(audio), "messages": ["prev"], "errors": []}
    with patch(
        "samplemind.ai.agents.quality_agent._run_quality_check",
        return_value=good_metrics,
    ):
        result = quality_agent(state)

    assert "quality_flags" in result
    assert result["quality_flags"]["method"] == "pyloudnorm"
    assert len(result["messages"]) > 1


def test_quality_agent_handles_check_exception(tmp_path):
    audio = tmp_path / "bad.wav"
    audio.write_bytes(b"\x00" * 44)

    state = {"file_path": str(audio), "messages": [], "errors": []}
    with patch(
        "samplemind.ai.agents.quality_agent._run_quality_check",
        side_effect=RuntimeError("unexpected crash"),
    ):
        result = quality_agent(state)

    assert "error" in result["quality_flags"]
    assert len(result["errors"]) == 1
