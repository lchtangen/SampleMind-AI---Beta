"""Tests for MicroTimingAnalyzer (P4-006)."""

from __future__ import annotations

import numpy as np
import pytest

from samplemind.core.analysis.micro_timing_analyzer import (
    GhostNoteProfile,
    MicroTimingAnalyzer,
    MicroTimingResult,
    PocketProfile,
    SwingProfile,
)


class TestMicroTimingResult:
    """Tests for MicroTimingResult dataclass."""

    def test_default_values(self) -> None:
        result = MicroTimingResult()
        assert result.human_feel_score == 0.0
        assert result.groove_dna == ""
        assert result.bpm == 0.0
        assert isinstance(result.swing, SwingProfile)
        assert isinstance(result.pocket, PocketProfile)
        assert isinstance(result.ghost_notes, GhostNoteProfile)

    def test_to_dict_keys(self) -> None:
        result = MicroTimingResult(bpm=120.0, human_feel_score=0.75)
        d = result.to_dict()
        assert "swing" in d
        assert "ghost_notes" in d
        assert "pocket" in d
        assert "human_feel_score" in d
        assert "groove_dna" in d
        assert "bpm" in d
        assert d["bpm"] == 120.0
        assert d["human_feel_score"] == 0.75

    def test_to_dict_swing_fields(self) -> None:
        result = MicroTimingResult()
        d = result.to_dict()
        assert "ratio" in d["swing"]
        assert "style" in d["swing"]
        assert "consistency" in d["swing"]


class TestSwingProfile:
    """Tests for SwingProfile."""

    def test_defaults(self) -> None:
        profile = SwingProfile()
        assert profile.ratio == 0.5
        assert profile.style == "straight"
        assert profile.consistency == 0.0

    def test_custom_values(self) -> None:
        profile = SwingProfile(ratio=0.67, style="shuffle", consistency=0.8)
        assert profile.ratio == 0.67
        assert profile.style == "shuffle"


class TestMicroTimingAnalyzer:
    """Tests for MicroTimingAnalyzer."""

    def test_init(self) -> None:
        analyzer = MicroTimingAnalyzer()
        assert analyzer.hop_length == 512

    def test_init_custom_hop(self) -> None:
        analyzer = MicroTimingAnalyzer(hop_length=256)
        assert analyzer.hop_length == 256

    def test_analyze_silence(self) -> None:
        """Analyzing silence should not crash."""
        analyzer = MicroTimingAnalyzer()
        y = np.zeros(22050, dtype=np.float32)  # 1 second of silence
        result = analyzer.analyze(y, 22050)
        assert isinstance(result, MicroTimingResult)
        assert result.duration == pytest.approx(1.0, abs=0.01)

    def test_analyze_sine_wave(self) -> None:
        """Analyzing a simple sine wave should produce valid results."""
        analyzer = MicroTimingAnalyzer()
        sr = 22050
        t = np.linspace(0, 2.0, int(sr * 2.0), dtype=np.float32)
        y = np.sin(2 * np.pi * 440 * t).astype(np.float32)
        result = analyzer.analyze(y, sr)
        assert isinstance(result, MicroTimingResult)
        assert result.bpm >= 0
        assert result.sample_rate == sr

    def test_analyze_short_signal(self) -> None:
        """Very short signals should not crash."""
        analyzer = MicroTimingAnalyzer()
        y = np.random.randn(512).astype(np.float32)
        result = analyzer.analyze(y, 22050)
        assert isinstance(result, MicroTimingResult)

    def test_analyze_with_bpm(self) -> None:
        """Providing BPM should be respected."""
        analyzer = MicroTimingAnalyzer()
        sr = 22050
        y = np.random.randn(sr * 2).astype(np.float32) * 0.1
        result = analyzer.analyze(y, sr, bpm=140.0)
        assert result.bpm == 140.0

    def test_groove_dna_is_hex(self) -> None:
        """Groove DNA should be a 32-char hex string."""
        analyzer = MicroTimingAnalyzer()
        sr = 22050
        t = np.linspace(0, 2.0, sr * 2, dtype=np.float32)
        # Create a signal with some transients
        y = np.zeros_like(t)
        for i in range(0, len(y), sr // 4):
            end = min(i + 200, len(y))
            y[i:end] = 0.8
        result = analyzer.analyze(y, sr)
        if result.groove_dna:
            assert len(result.groove_dna) == 32
            # Verify it's valid hex
            int(result.groove_dna, 16)

    def test_human_feel_zero_for_silence(self) -> None:
        """Silence should have 0 human feel."""
        analyzer = MicroTimingAnalyzer()
        y = np.zeros(22050 * 2, dtype=np.float32)
        result = analyzer.analyze(y, 22050)
        assert result.human_feel_score == 0.0


class TestPocketProfile:
    """Tests for PocketProfile."""

    def test_defaults(self) -> None:
        pocket = PocketProfile()
        assert pocket.score == 0.0
        assert pocket.feel == "neutral"

    def test_description(self) -> None:
        pocket = PocketProfile(feel="ahead", description="Playing ahead of the beat")
        assert "ahead" in pocket.description


class TestGhostNoteProfile:
    """Tests for GhostNoteProfile."""

    def test_defaults(self) -> None:
        ghost = GhostNoteProfile()
        assert ghost.count == 0
        assert ghost.density == 0.0
        assert ghost.positions == []
