""
Unit tests for the audio processing system.
"""
import os
import pytest
import numpy as np
from pathlib import Path
from samplemind.audio.processor import AudioProcessor, AudioFeatures, AudioProcessingError

# Test audio files directory
TEST_AUDIO_DIR = Path(__file__).parent.parent.parent / "test_audio_samples"
SAMPLE_FILE = TEST_AUDIO_DIR / "test_chord_120bpm.wav"

# Skip tests if test audio files are not available
pytestmark = pytest.mark.skipif(
    not SAMPLE_FILE.exists(),
    reason="Test audio files not found"
)

class TestAudioProcessor:
    """Test cases for AudioProcessor class."""
    
    @pytest.fixture
    def processor(self):
        """Create a new AudioProcessor instance for each test."""
        return AudioProcessor(sample_rate=44100)
    
    def test_load_audio(self, processor):
        """Test loading an audio file."""
        y, sr = processor.load_audio(SAMPLE_FILE)
        assert sr == 44100
        assert isinstance(y, np.ndarray)
        assert len(y) > 0
        assert y.dtype == np.float32
    
    def test_load_audio_invalid_file(self, processor):
        """Test loading a non-existent audio file."""
        with pytest.raises(AudioProcessingError):
            processor.load_audio("nonexistent_file.wav")
    
    def test_extract_features(self, processor):
        """Test feature extraction from audio data."""
        y, sr = processor.load_audio(SAMPLE_FILE)
        features = processor.extract_features(y, sr)
        
        assert isinstance(features, AudioFeatures)
        assert features.tempo > 0
        assert features.duration > 0
        assert features.sample_rate == sr
        assert features.chroma.shape[0] == 12  # 12 chroma bins
        assert features.mfcc.shape[0] == 20  # 20 MFCCs
    
    def test_process_file(self, processor):
        """Test processing an audio file."""
        features = processor.process_file(SAMPLE_FILE)
        assert isinstance(features, AudioFeatures)
        
        # Convert to dict and back
        features_dict = features.to_dict()
        assert isinstance(features_dict, dict)
        
        restored = AudioFeatures.from_dict(features_dict)
        assert isinstance(restored, AudioFeatures)
        assert restored.tempo == features.tempo
        assert restored.key == features.key
        assert restored.mode == features.mode
    
    def test_estimate_key(self, processor):
        """Test key and mode estimation."""
        # Test with a known C major chord
        sr = 44100
        t = np.linspace(0, 1, sr)  # 1 second of audio
        # C4, E4, G4 (C major chord)
        y = 0.5 * np.sin(2 * np.pi * 261.63 * t)  # C4
        y += 0.5 * np.sin(2 * np.pi * 329.63 * t)  # E4
        y += 0.5 * np.sin(2 * np.pi * 392.00 * t)  # G4
        
        key, mode = processor._estimate_key(y, sr)
        assert key == 'C'
        assert mode == 'major'


class TestAudioFeatures:
    """Test cases for AudioFeatures class."""
    
    def test_serialization(self):
        """Test serialization and deserialization of AudioFeatures."""
        # Create a sample feature set
        features = AudioFeatures(
            tempo=120.0,
            key='C',
            mode='major',
            beats=np.array([0.5, 1.0, 1.5, 2.0]),
            chroma=np.random.rand(12, 100),
            mfcc=np.random.rand(20, 100),
            spectral_contrast=np.random.rand(7, 100),
            tonnetz=np.random.rand(6, 100),
            zcr=np.random.rand(1, 100),
            rmse=np.random.rand(1, 100),
            spectral_centroid=np.random.rand(1, 100),
            spectral_bandwidth=np.random.rand(1, 100),
            spectral_rolloff=np.random.rand(1, 100),
            harmonic=np.random.rand(44100),
            percussive=np.random.rand(44100),
            beat_frames=np.array([1, 2, 3, 4]),
            beat_times=np.array([0.5, 1.0, 1.5, 2.0]),
            duration=2.0,
            sample_rate=44100
        )
        
        # Convert to dict and back
        features_dict = features.to_dict()
        restored = AudioFeatures.from_dict(features_dict)
        
        # Check basic attributes
        assert restored.tempo == features.tempo
        assert restored.key == features.key
        assert restored.mode == features.mode
        assert restored.duration == features.duration
        assert restored.sample_rate == features.sample_rate
        
        # Check array attributes
        assert np.allclose(restored.chroma, features.chroma)
        assert np.allclose(restored.mfcc, features.mfcc)
        assert np.allclose(restored.spectral_contrast, features.spectral_contrast)
        assert np.allclose(restored.tonnetz, features.tonnetz)
        assert np.allclose(restored.zcr, features.zcr)
        assert np.allclose(restored.rmse, features.rmse)
        assert np.allclose(restored.spectral_centroid, features.spectral_centroid)
        assert np.allclose(restored.spectral_bandwidth, features.spectral_bandwidth)
        assert np.allclose(restored.spectral_rolloff, features.spectral_rolloff)
        assert np.allclose(restored.beat_frames, features.beat_frames)
        assert np.allclose(restored.beat_times, features.beat_times)


def test_compute_audio_hash():
    """Test audio file hashing function."""
    from samplemind.audio.processor import compute_audio_hash
    
    # Create a temporary test file
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b'test audio data')
        temp_path = f.name
    
    try:
        # Compute hash
        hash1 = compute_audio_hash(temp_path)
        assert len(hash1) == 64  # SHA-256 produces 64-character hex string
        
        # Hash should be deterministic
        hash2 = compute_audio_hash(temp_path)
        assert hash1 == hash2
        
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)
