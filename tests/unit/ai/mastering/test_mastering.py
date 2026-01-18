"""Unit tests for mastering module."""

import numpy as np
import pytest

from samplemind.ai.mastering.mastering_engine import MasteringEngine, GENRE_PRESETS
from samplemind.ai.mastering.processing_chain import MasteringChain, ProcessingStep
from samplemind.ai.mastering.reference_analyzer import (
    MasteringProfile,
    ReferenceAnalyzer,
)


class TestReferenceAnalyzer:
    """Test ReferenceAnalyzer class."""

    def test_analyzer_initialization(self):
        """Test analyzer initializes correctly."""
        analyzer = ReferenceAnalyzer()
        assert analyzer is not None
        assert analyzer.sample_rate == 44100

    def test_measure_lufs(self):
        """Test LUFS measurement."""
        analyzer = ReferenceAnalyzer()

        # Generate silent signal
        silent = np.zeros(44100)
        lufs_silent = analyzer._measure_lufs(silent, 44100)
        assert lufs_silent < -30  # Very quiet

        # Generate sine waves and check they have different loudness
        t = np.arange(44100) / 44100
        quiet_sine = 0.1 * np.sin(2 * np.pi * 440 * t)
        loud_sine = 0.9 * np.sin(2 * np.pi * 440 * t)

        lufs_quiet = analyzer._measure_lufs(quiet_sine, 44100)
        lufs_loud = analyzer._measure_lufs(loud_sine, 44100)

        # Louder signal should have higher LUFS
        assert lufs_loud > lufs_quiet

    def test_measure_dynamic_range(self):
        """Test dynamic range measurement."""
        analyzer = ReferenceAnalyzer()

        # Compare DR between two signals
        t = np.arange(44100) / 44100

        # Sine wave (typical DR ~3dB)
        sine = 0.5 * np.sin(2 * np.pi * 440 * t)
        dr_sine = analyzer._measure_dynamic_range(sine)

        # Constant signal (very low DR)
        constant = np.ones(44100) * 0.5
        dr_constant = analyzer._measure_dynamic_range(constant)

        # Sine wave should have higher DR than constant signal
        assert dr_sine > dr_constant
        assert dr_sine > 0

    def test_measure_stereo_width(self):
        """Test stereo width measurement."""
        analyzer = ReferenceAnalyzer()

        # Test with different signals
        t = np.arange(44100) / 44100

        # Correlated signal (narrower)
        left1 = 0.5 * np.sin(2 * np.pi * 440 * t)
        right1 = 0.5 * np.sin(2 * np.pi * 440 * t)  # Identical (mono)
        stereo1 = np.array([left1, right1])
        width1 = analyzer._measure_stereo_width(stereo1)

        # Less correlated signal (wider)
        left2 = 0.5 * np.sin(2 * np.pi * 440 * t)
        right2 = 0.5 * np.sin(2 * np.pi * 440 * t + np.pi / 2)  # 90° phase difference
        stereo2 = np.array([left2, right2])
        width2 = analyzer._measure_stereo_width(stereo2)

        # Width should be greater for less-correlated signal
        assert width2 > width1

    def test_estimate_compression(self):
        """Test compression ratio estimation."""
        analyzer = ReferenceAnalyzer()

        # Low DR (heavy compression)
        highly_compressed = np.ones(44100) * 0.5
        highly_compressed[::100] = 0.6  # Slight variation
        ratio_high = analyzer._estimate_compression(highly_compressed)
        assert ratio_high >= 3.0

        # High DR (light compression)
        t = np.arange(44100) / 44100
        variable = 0.5 * np.sin(2 * np.pi * 440 * t)
        ratio_light = analyzer._estimate_compression(variable)
        # Sine wave has ~3dB DR, which should map to compression around 2-4
        assert 1.0 <= ratio_light <= 4.0


class TestMasteringChain:
    """Test MasteringChain class."""

    def test_chain_initialization(self):
        """Test chain initializes correctly."""
        chain = MasteringChain(sample_rate=44100)
        assert chain is not None
        assert len(chain.chain) == 0

    def test_add_eq(self):
        """Test EQ addition."""
        chain = MasteringChain()
        chain.add_eq(low_shelf_db=3.0, high_shelf_db=2.0)
        assert len(chain.chain) == 1
        assert chain.chain[0].name == "EQ"
        assert chain.chain[0].parameters["low_shelf_db"] == 3.0

    def test_add_compressor(self):
        """Test compressor addition."""
        chain = MasteringChain()
        chain.add_compressor(threshold=-15.0, ratio=4.0)
        assert len(chain.chain) == 1
        assert chain.chain[0].name == "Compressor"
        assert chain.chain[0].parameters["ratio"] == 4.0

    def test_add_limiter(self):
        """Test limiter addition."""
        chain = MasteringChain()
        chain.add_limiter(threshold=-0.1)
        assert len(chain.chain) == 1
        assert chain.chain[0].name == "Limiter"

    def test_process_mono_audio(self):
        """Test processing mono audio."""
        chain = MasteringChain()
        chain.add_limiter(threshold=-0.1)

        # Create test audio with 0.5 amplitude (not crossing limiter threshold)
        t = np.arange(44100) / 44100
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)

        processed = chain.process(audio)
        assert processed.shape == audio.shape
        # Since input is 0.5 and limiter at -0.1 (~0.11), signal shouldn't be clipped
        assert np.max(np.abs(processed)) <= 0.5 + 0.01  # Some small processing artifacts

    def test_process_stereo_audio(self):
        """Test processing stereo audio."""
        chain = MasteringChain()
        chain.add_limiter(threshold=-0.1)

        # Create stereo test audio
        t = np.arange(44100) / 44100
        left = 0.5 * np.sin(2 * np.pi * 440 * t)
        right = 0.5 * np.sin(2 * np.pi * 880 * t)
        audio = np.array([left, right])

        processed = chain.process(audio)
        assert processed.shape == audio.shape
        assert processed.ndim == 2

    def test_chain_order_matters(self):
        """Test that processing order matters."""
        # Chain 1: EQ then compress
        chain1 = MasteringChain()
        chain1.add_eq(low_shelf_db=3.0)
        chain1.add_compressor(threshold=-15.0, ratio=4.0)

        # Chain 2: Compress then EQ
        chain2 = MasteringChain()
        chain2.add_compressor(threshold=-15.0, ratio=4.0)
        chain2.add_eq(low_shelf_db=3.0)

        t = np.arange(44100) / 44100
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)

        result1 = chain1.process(audio)
        result2 = chain2.process(audio)

        # Results should be different
        assert not np.allclose(result1, result2)


class TestMasteringEngine:
    """Test MasteringEngine class."""

    def test_engine_initialization(self):
        """Test engine initializes correctly."""
        engine = MasteringEngine(sample_rate=44100)
        assert engine is not None
        assert engine.sample_rate == 44100

    def test_create_default_profile(self):
        """Test default profile creation."""
        engine = MasteringEngine()
        profile = engine._create_default_profile(target_lufs=-14.0)

        assert isinstance(profile, MasteringProfile)
        assert profile.target_lufs == -14.0
        assert profile.compression_ratio == 3.0

    def test_build_chain_from_profile(self):
        """Test chain building from profile."""
        engine = MasteringEngine()
        profile = engine._create_default_profile(-14.0)
        chain = engine._build_chain_from_profile(profile)

        assert isinstance(chain, MasteringChain)
        assert len(chain.chain) > 0
        # Should have EQ, Compressor, StereoWidth, and Limiter
        assert len(chain.chain) >= 3

    def test_normalize_loudness(self):
        """Test loudness normalization."""
        engine = MasteringEngine()

        # Create quiet signal
        t = np.arange(44100) / 44100
        quiet = 0.1 * np.sin(2 * np.pi * 440 * t)

        # Normalize to -14 LUFS
        normalized = engine._normalize_loudness(quiet, target_lufs=-14.0)

        # Check that normalized is louder
        assert np.max(np.abs(normalized)) > np.max(np.abs(quiet))

    def test_genre_presets_exist(self):
        """Test that genre presets are defined."""
        genres = ["techno", "house", "hiphop", "ambient", "rock", "pop", "edm"]
        for genre in genres:
            assert genre in GENRE_PRESETS
            profile = GENRE_PRESETS[genre]
            assert isinstance(profile, MasteringProfile)
            assert profile.target_lufs < 0
            assert profile.compression_ratio > 0

    def test_techno_preset_characteristics(self):
        """Test techno preset has appropriate characteristics."""
        profile = GENRE_PRESETS["techno"]
        assert profile.target_lufs == -11.0  # Loud for club
        assert profile.compression_ratio >= 4.0  # Heavy compression
        assert profile.stereo_width >= 0.85  # Wide stereo

    def test_ambient_preset_characteristics(self):
        """Test ambient preset has appropriate characteristics."""
        profile = GENRE_PRESETS["ambient"]
        assert profile.target_lufs == -16.0  # Quieter
        assert profile.compression_ratio <= 2.0  # Light compression
        assert profile.stereo_width >= 0.95  # Maximum width


class TestMasteringIntegration:
    """Integration tests for mastering system."""

    def test_full_mastering_chain(self):
        """Test full mastering chain from profile to output."""
        engine = MasteringEngine()
        profile = GENRE_PRESETS["techno"]

        # Create test audio
        t = np.arange(44100) / 44100
        audio = 0.3 * np.sin(2 * np.pi * 440 * t)

        # Build and run chain
        chain = engine._build_chain_from_profile(profile)
        mastered = chain.process(audio)

        # Normalize
        final = engine._normalize_loudness(mastered, profile.target_lufs)

        # Check results
        assert final.shape == audio.shape
        assert np.max(np.abs(final)) <= 0.99
        assert np.max(np.abs(final)) > 0.1

    def test_genre_specific_mastering(self):
        """Test that different genres produce different results."""
        engine = MasteringEngine()

        t = np.arange(44100) / 44100
        audio = 0.3 * np.sin(2 * np.pi * 440 * t)

        # Master for different genres
        chain_techno = engine._build_chain_from_profile(GENRE_PRESETS["techno"])
        chain_ambient = engine._build_chain_from_profile(GENRE_PRESETS["ambient"])

        mastered_techno = chain_techno.process(audio)
        mastered_ambient = chain_ambient.process(audio)

        # Results should be different
        assert not np.allclose(mastered_techno, mastered_ambient)
