"""
Pytest configuration for TUI interface tests.

Provides fixtures and configuration for testing TUI components
without requiring full dependency installation.
"""

import sys
import pytest
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


@pytest.fixture
def mock_audio_engine():
    """Provide mock AudioEngine for testing."""
    from unittest.mock import Mock, AsyncMock

    engine = Mock()
    engine.analyze_audio = Mock()
    engine.batch_analyze = Mock()
    engine.get_performance_stats = Mock(return_value={})
    return engine


@pytest.fixture
def mock_features():
    """Provide mock AudioFeatures for testing."""
    from unittest.mock import Mock

    features = Mock()
    features.file_path = "/path/to/audio.wav"
    features.duration = 10.5
    features.sample_rate = 44100
    features.channels = 2
    features.bit_depth = 16
    features.tempo = 120.0
    features.key = "C"
    features.mode = "Major"
    features.time_signature = (4, 4)
    features.spectral_centroid = 2450.0
    features.spectral_rolloff = 8200.0
    features.zero_crossing_rate = 0.045
    features.rms_energy = 0.123
    features.mfccs = [0.1] * 13
    features.beats = [0.5, 1.0, 1.5, 2.0]
    features.onset_times = [0.2, 0.7, 1.2]
    features.chroma_features = [0.08] * 12
    features.harmonic_content = 0.8
    features.percussive_content = 0.2
    features.pitch_class_distribution = [0.08] * 12

    return features
