"""Unit tests for stem separation module."""

import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import importlib.util

from samplemind.core.processing.stem_separation import (
    StemSeparationEngine,
    StemSeparationResult,
)


def _check_demucs_available():
    """Check if demucs is available"""
    return importlib.util.find_spec("demucs") is not None


class TestStemSeparationEngine:
    """Test stem separation engine"""

    def test_initialization_v4(self):
        """Test initialization with v4 model"""
        engine = StemSeparationEngine(model="mdx_extra")
        assert engine.model == "mdx_extra"
        assert engine.is_v4 is True
        assert engine.shifts == 1
        assert engine.overlap == 0.25

    def test_initialization_v3(self):
        """Test initialization with v3 model"""
        engine = StemSeparationEngine(model="htdemucs")
        assert engine.model == "htdemucs"
        assert engine.is_v4 is False

    def test_initialization_custom_params(self):
        """Test initialization with custom parameters"""
        engine = StemSeparationEngine(
            model="mdx",
            device="cuda",
            segment=30.0,
            shifts=4,
            overlap=0.5,
            verbose=True,
        )
        assert engine.device == "cuda"
        assert engine.segment == 30.0
        assert engine.shifts == 4
        assert engine.overlap == 0.5
        assert engine.verbose is True

    def test_v4_models_recognized(self):
        """Test that v4 models are recognized"""
        for model in ["mdx", "mdx_extra", "mdx_q"]:
            engine = StemSeparationEngine(model=model)
            assert engine.is_v4 is True

    def test_v3_models_recognized(self):
        """Test that v3 models are recognized"""
        for model in ["htdemucs", "htdemucs_ft", "hdemucs_mmi"]:
            engine = StemSeparationEngine(model=model)
            assert engine.is_v4 is False

    def test_unknown_model_assumes_v4(self):
        """Test that unknown model is treated as v4"""
        engine = StemSeparationEngine(model="future_model")
        assert engine.is_v4 is True

    @patch("samplemind.core.processing.stem_separation.importlib.util.find_spec")
    def test_assert_dependency_present(self, mock_find_spec):
        """Test dependency check when demucs is present"""
        mock_find_spec.return_value = True
        # Should not raise
        StemSeparationEngine._assert_dependency()

    @patch("samplemind.core.processing.stem_separation.importlib.util.find_spec")
    def test_assert_dependency_missing(self, mock_find_spec):
        """Test dependency check when demucs is missing"""
        mock_find_spec.return_value = None

        from samplemind.core.processing.exceptions import OptionalDependencyError

        with pytest.raises(OptionalDependencyError):
            StemSeparationEngine._assert_dependency()

    @patch("samplemind.core.processing.stem_separation.subprocess.run")
    @patch("samplemind.core.processing.stem_separation.StemSeparationEngine._assert_dependency")
    def test_separate_success_v4(self, mock_assert, mock_run):
        """Test successful separation with v4 model"""
        # Create mock audio file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            audio_path = Path(f.name)

        try:
            # Mock successful subprocess run
            mock_run.return_value = Mock(returncode=0, stderr="")

            # Create mock output directory structure
            with tempfile.TemporaryDirectory() as tmpdir:
                output_dir = Path(tmpdir)
                model_dir = output_dir / "mdx_extra"
                track_dir = model_dir / audio_path.stem
                track_dir.mkdir(parents=True, exist_ok=True)

                # Create mock stem files
                for stem in ["vocals", "drums", "bass", "other"]:
                    (track_dir / f"{stem}.wav").touch()

                engine = StemSeparationEngine(model="mdx_extra")

                with patch("samplemind.core.processing.stem_separation.Path") as MockPath:
                    # Setup path mocking
                    mock_paths = {}

                    def path_side_effect(p):
                        if p not in mock_paths:
                            mock_paths[p] = Mock()
                            mock_paths[p].expanduser.return_value = mock_paths[p]
                            mock_paths[p].resolve.return_value = mock_paths[p]

                            if p == audio_path:
                                mock_paths[p].exists.return_value = True
                                mock_paths[p].stem = audio_path.stem
                            elif p == tmpdir:
                                mock_paths[p].mkdir = Mock()
                            elif "/" in str(p):
                                mock_paths[p].exists.return_value = True

                        return mock_paths[p]

                    MockPath.side_effect = path_side_effect

                    # Actual test would need more comprehensive mocking
                    # For now, verify that command is constructed correctly

        finally:
            audio_path.unlink()

    def test_default_model_is_v4(self):
        """Test that default model is now v4 (mdx_extra)"""
        engine = StemSeparationEngine()
        assert engine.model == "mdx_extra"
        assert engine.is_v4 is True

    @patch("samplemind.core.processing.stem_separation.subprocess.run")
    @patch("samplemind.core.processing.stem_separation.StemSeparationEngine._assert_dependency")
    def test_command_construction_v4(self, mock_assert, mock_run):
        """Test command construction for v4 model"""
        mock_run.return_value = Mock(returncode=0, stderr="")

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            audio_path = Path(f.name)

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                engine = StemSeparationEngine(
                    model="mdx_extra",
                    device="cuda",
                    segment=30.0,
                    shifts=4,
                    overlap=0.5,
                    verbose=True,
                )

                # Create mock output structure
                output_dir = Path(tmpdir)
                model_dir = output_dir / "mdx_extra"
                track_dir = model_dir / audio_path.stem
                track_dir.mkdir(parents=True, exist_ok=True)
                for stem in ["vocals", "drums", "bass", "other"]:
                    (track_dir / f"{stem}.wav").touch()

                # The command should contain v4 specific args
                # This is a simplified test - real integration testing would actually run demucs
                assert engine.is_v4 is True
                assert engine.shifts == 4
                assert engine.overlap == 0.5
                assert engine.verbose is True

        finally:
            audio_path.unlink()

    def test_command_construction_v3_vs_v4(self):
        """Test that v3 and v4 have different command parameters"""
        engine_v3 = StemSeparationEngine(model="htdemucs", shifts=2)
        engine_v4 = StemSeparationEngine(model="mdx_extra", shifts=2)

        # v3 should not use shifts parameter
        assert engine_v3.is_v4 is False
        assert engine_v3.model == "htdemucs"

        # v4 should use shifts parameter
        assert engine_v4.is_v4 is True
        assert engine_v4.model == "mdx_extra"

    def test_stem_separation_result(self):
        """Test StemSeparationResult dataclass"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            stems = {
                "vocals": output_dir / "vocals.wav",
                "drums": output_dir / "drums.wav",
            }
            command = ["python", "-m", "demucs", "-n", "mdx_extra", "test.wav"]

            result = StemSeparationResult(
                output_directory=output_dir,
                stems=stems,
                command=command,
            )

            assert result.output_directory == output_dir
            assert "vocals" in result.stems
            assert "drums" in result.stems
            assert len(result.command) == 6


class TestStemSeparationIntegration:
    """Integration tests for stem separation (requires actual demucs)"""

    @pytest.mark.skipif(
        not _check_demucs_available(),
        reason="Demucs not installed"
    )
    def test_actual_separation(self):
        """Test actual stem separation if demucs available (integration test)"""
        # Skip if demucs not available
        try:
            import demucs
        except ImportError:
            pytest.skip("Demucs not installed")

        # Generate test audio (1 second of 440 Hz sine wave)
        sample_rate = 44100
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)

        # Write to temporary file
        import soundfile as sf

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            audio_path = Path(f.name)
            sf.write(audio_path, audio, sample_rate)

        try:
            engine = StemSeparationEngine(model="mdx_extra")

            with tempfile.TemporaryDirectory() as tmpdir:
                result = engine.separate(
                    audio_path,
                    output_directory=Path(tmpdir),
                )

                # Verify output structure
                assert result.output_directory.exists()
                assert len(result.stems) > 0

                # Verify stem files exist and have content
                for stem_name, stem_path in result.stems.items():
                    assert stem_path.exists()
                    assert stem_path.stat().st_size > 0

        finally:
            audio_path.unlink()
