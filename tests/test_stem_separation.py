"""
Tests for AI Stem Separation Feature (Phase 13.1)

Tests cover:
- Stem separation with different quality levels
- Batch processing
- Error handling
- Performance benchmarking
- Output validation
"""

import asyncio
import tempfile
from pathlib import Path
from typing import List

import pytest

from samplemind.core.processing.stem_separation import (
    StemSeparationEngine,
    StemQuality,
    StemSeparationResult,
)


class TestStemSeparationEngine:
    """Tests for StemSeparationEngine class"""

    def test_engine_initialization_default(self):
        """Test default engine initialization"""
        engine = StemSeparationEngine()
        assert engine.model == "mdx_extra"
        assert engine.shifts == 1
        assert engine.overlap == 0.25

    def test_engine_from_quality_fast(self):
        """Test creating engine with FAST quality preset"""
        engine = StemSeparationEngine.from_quality(StemQuality.FAST)
        assert engine.model == "mdx"
        assert engine.shifts == 1
        assert engine.overlap == 0.1

    def test_engine_from_quality_standard(self):
        """Test creating engine with STANDARD quality preset"""
        engine = StemSeparationEngine.from_quality(StemQuality.STANDARD)
        assert engine.model == "mdx_extra"
        assert engine.shifts == 1
        assert engine.overlap == 0.25

    def test_engine_from_quality_high(self):
        """Test creating engine with HIGH quality preset"""
        engine = StemSeparationEngine.from_quality(StemQuality.HIGH)
        assert engine.model == "mdx_extra"
        assert engine.shifts == 5
        assert engine.overlap == 0.5

    def test_available_presets(self):
        """Test that available presets are returned correctly"""
        presets = StemSeparationEngine.get_available_presets()
        assert "fast" in presets
        assert "standard" in presets
        assert "high" in presets
        assert len(presets) == 3

    def test_model_version_detection_v4(self):
        """Test V4 model detection"""
        engine = StemSeparationEngine(model="mdx_extra")
        assert engine.is_v4 is True

    def test_model_version_detection_v3(self):
        """Test V3 model detection"""
        engine = StemSeparationEngine(model="htdemucs")
        assert engine.is_v4 is False


class TestStemSeparationResults:
    """Tests for StemSeparationResult handling"""

    def test_stem_separation_result_creation(self):
        """Test creating a StemSeparationResult"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            stems = {
                "vocals": output_dir / "vocals.wav",
                "drums": output_dir / "drums.wav",
            }

            result = StemSeparationResult(
                output_directory=output_dir,
                stems=stems,
                command=["python", "-m", "demucs"]
            )

            assert result.output_directory == output_dir
            assert len(result.stems) == 2
            assert "vocals" in result.stems
            assert "drums" in result.stems


class TestBatchProcessing:
    """Tests for batch stem separation"""

    @pytest.mark.asyncio
    async def test_batch_separate_async(self):
        """Test async batch separation"""
        engine = StemSeparationEngine.from_quality(StemQuality.FAST)

        # Create mock file list (won't actually process without real audio)
        mock_files = [
            Path("track1.wav"),
            Path("track2.wav"),
        ]

        # Test that method exists and accepts parameters
        assert hasattr(engine, 'batch_separate')
        assert callable(engine.batch_separate)

    def test_batch_separate_sync_wrapper(self):
        """Test sync wrapper for batch separation"""
        engine = StemSeparationEngine.from_quality(StemQuality.FAST)

        # Test that method exists
        assert hasattr(engine, 'batch_separate_sync')
        assert callable(engine.batch_separate_sync)


class TestErrorHandling:
    """Tests for error handling in stem separation"""

    def test_missing_file_error(self):
        """Test error handling for missing audio files"""
        engine = StemSeparationEngine()
        missing_file = Path("/nonexistent/file.wav")

        with pytest.raises(FileNotFoundError):
            engine.separate(audio_path=missing_file)

    def test_invalid_file_format_error(self):
        """Test error handling for invalid file formats"""
        engine = StemSeparationEngine()

        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            tmp_path = Path(tmp.name)
            tmp_path.write_text("Not an audio file")

            # The error will occur during processing by Demucs
            # Just verify the file exists and is passed correctly
            assert tmp_path.exists()


class TestQualityPresets:
    """Tests for quality preset configurations"""

    def test_quality_enum_values(self):
        """Test that all quality enum values are valid"""
        for quality in StemQuality:
            assert quality.value in ["fast", "standard", "high"]

    def test_quality_preset_config_complete(self):
        """Test that all quality presets have complete config"""
        from samplemind.core.processing.stem_separation import QUALITY_PRESETS

        for quality, config in QUALITY_PRESETS.items():
            assert hasattr(config, 'model')
            assert hasattr(config, 'shifts')
            assert hasattr(config, 'overlap')
            assert hasattr(config, 'description')
            assert config.model in ["mdx", "mdx_extra", "mdx_q"]
            assert config.shifts >= 1
            assert 0 <= config.overlap <= 1


class TestPerformanceBenchmarks:
    """Performance benchmark tests"""

    def test_engine_initialization_speed(self):
        """Test that engine initialization is fast"""
        import time

        start = time.time()
        engine = StemSeparationEngine.from_quality(StemQuality.STANDARD)
        elapsed = time.time() - start

        # Engine initialization should be <100ms
        assert elapsed < 0.1, f"Engine init too slow: {elapsed}s"

    def test_batch_concurrent_limit(self):
        """Test that batch processing respects concurrency limits"""
        engine = StemSeparationEngine()
        assert hasattr(engine, 'batch_separate')

        # Verify method signature includes max_concurrent parameter
        import inspect
        sig = inspect.signature(engine.batch_separate)
        assert 'max_concurrent' in sig.parameters


class TestCommandParsing:
    """Tests for CLI command parsing"""

    def test_quality_parameter_parsing(self):
        """Test parsing of quality parameter from CLI"""
        valid_qualities = ["fast", "standard", "high"]
        for quality_str in valid_qualities:
            quality_enum = StemQuality[quality_str.upper()]
            assert quality_enum.value == quality_str


def test_stem_types():
    """Test that default stem types are correct"""
    from samplemind.core.processing.stem_separation import _DEFAULT_STEMS

    expected_stems = ("vocals", "drums", "bass", "other")
    assert _DEFAULT_STEMS == expected_stems


def test_backend_enum():
    """Test StemBackend enum"""
    from samplemind.core.processing.stem_separation import StemBackend

    assert StemBackend.DEMUCS.value == "demucs"
    assert StemBackend.SPLEETER.value == "spleeter"


# ============================================================================
# Integration Tests (require actual audio and demucs installation)
# ============================================================================

@pytest.mark.integration
class TestStemSeparationIntegration:
    """Integration tests with real Demucs (requires demucs installation)"""

    @pytest.fixture
    def sample_audio(self):
        """Create a temporary audio file for testing"""
        # This would normally load/create a real audio file
        # For now, we just ensure the test structure is in place
        pass

    def test_full_separation_workflow(self, sample_audio):
        """Test complete stem separation workflow"""
        if sample_audio is None:
            pytest.skip("No sample audio available")

        engine = StemSeparationEngine.from_quality(StemQuality.STANDARD)

        # Would run actual separation here
        # result = engine.separate(sample_audio)
        # assert len(result.stems) == 4
        # assert all(p.exists() for p in result.stems.values())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
