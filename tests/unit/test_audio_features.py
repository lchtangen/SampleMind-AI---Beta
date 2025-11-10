"""Legacy audio feature tests (superseded by tests/unit/core/test_audio_engine.py)."""

import pytest

pytest.skip("Legacy audio feature tests replaced by core audio engine suite", allow_module_level=True)

import numpy as np
import librosa
from pathlib import Path
import os
import tempfile

from src.samplemind.core.engine.audio_engine import (
    AudioProcessor,
    AdvancedFeatureExtractor,
    AudioFeatures
)

# Test audio generation utilities
def generate_sine_wave(freq, sample_rate, duration, amplitude=0.5):
    """Generate a sine wave with the given frequency and duration."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return amplitude * np.sin(2 * np.pi * freq * t)

def generate_silence(sample_rate, duration):
    """Generate silence (zeros) for the given duration."""
    return np.zeros(int(sample_rate * duration))

def generate_impulse(sample_rate, duration, position=0.5, amplitude=1.0):
    """Generate an impulse at the specified position."""
    signal = np.zeros(int(sample_rate * duration))
    idx = int(position * len(signal))
    if idx < len(signal):
        signal[idx] = amplitude
    return signal

class TestAudioFeatureExtraction:
    """Test audio feature extraction functionality"""
    
    @pytest.fixture(params=[
        (44100, 5.0, 440, 0.5),  # Standard case
        (48000, 1.0, 1000, 0.1),  # High frequency, short duration
        (22050, 10.0, 55, 1.0),   # Low frequency, long duration
    ])
    def sample_audio(self, request):
        """Generate sample audio with different parameters"""
        sr, duration, freq, amp = request.param
        y = generate_sine_wave(freq, sr, duration, amp)
        return y, sr
    
    @pytest.fixture
    def silent_audio(self):
        """Generate silent audio"""
        return generate_silence(44100, 1.0), 44100
    
    @pytest.fixture
    def impulse_audio(self):
        """Generate audio with a single impulse"""
        return generate_impulse(44100, 1.0), 44100
    
    @pytest.fixture
    def stereo_audio(self):
        """Generate stereo audio"""
        left = generate_sine_wave(440, 44100, 1.0, 0.5)
        right = generate_sine_wave(660, 44100, 1.0, 0.3)
        return np.column_stack((left, right)), 44100
    
    def test_tempo_detection(self, sample_audio):
        """Test tempo detection accuracy"""
        y, sr = sample_audio
        extractor = AdvancedFeatureExtractor(sample_rate=sr)
        
        # Extract rhythmic features
        features = extractor.extract_rhythmic_features(y)
        
        assert 'tempo' in features
        assert isinstance(features['tempo'], float)
        assert features['tempo'] > 0
        assert features['tempo'] < 300  # Reasonable tempo range
    
    def test_tempo_with_silence(self, silent_audio):
        """Test tempo detection with silent audio"""
        y, sr = silent_audio
        extractor = AdvancedFeatureExtractor(sample_rate=sr)
        
        # Should handle silence without crashing
        features = extractor.extract_rhythmic_features(y)
        
        assert 'tempo' in features
        assert isinstance(features['tempo'], float)
    
    def test_tempo_with_impulse(self, impulse_audio):
        """Test tempo detection with impulse audio"""
        y, sr = impulse_audio
        extractor = AdvancedFeatureExtractor(sample_rate=sr)
        
        features = extractor.extract_rhythmic_features(y)
        
        assert 'tempo' in features
        assert isinstance(features['tempo'], float)
    
    def test_key_detection(self, sample_audio):
        """Test musical key detection"""
        y, sr = sample_audio
        extractor = AdvancedFeatureExtractor(sample_rate=sr)
        
        # Extract tonal features
        features = extractor.extract_tonal_features(y)
        
        assert 'key' in features
        assert 'mode' in features
        assert features['key'] in ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
        assert features['mode'] in ['major', 'minor']
    
    def test_key_detection_silence(self, silent_audio):
        """Test key detection with silent audio"""
        y, sr = silent_audio
        extractor = AdvancedFeatureExtractor(sample_rate=sr)
        
        features = extractor.extract_tonal_features(y)
        
        # Should still return valid key/mode even with silence
        assert 'key' in features
        assert 'mode' in features
        assert features['key'] in ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
        assert features['mode'] in ['major', 'minor']
    
    def test_spectral_features(self, sample_audio):
        """Test spectral feature extraction"""
        y, sr = sample_audio
        extractor = AdvancedFeatureExtractor(sample_rate=sr)
        
        # Extract spectral features
        features = extractor.extract_spectral_features(y)
        
        # Check all expected features are present
        expected_features = [
            'spectral_centroid',
            'spectral_bandwidth',
            'spectral_rolloff',
            'zero_crossing_rate',
            'rms_energy'
        ]
        
        for feature in expected_features:
            assert feature in features
            assert len(features[feature]) > 0
            
            # Check for NaN or infinite values
            assert not np.any(np.isnan(features[feature]))
            assert not np.any(np.isinf(features[feature]))
        
        # Check specific feature properties
        assert np.all(np.array(features['spectral_centroid']) >= 0)
        assert np.all(np.array(features['spectral_bandwidth']) >= 0)
        assert np.all(np.array(features['spectral_rolloff']) > 0)
        assert np.all(np.array(features['zero_crossing_rate']) >= 0)
        assert np.all(np.array(features['rms_energy']) >= 0)
    
    def test_spectral_features_silence(self, silent_audio):
        """Test spectral features with silent audio"""
        y, sr = silent_audio
        extractor = AdvancedFeatureExtractor(sample_rate=sr)
        
        features = extractor.extract_spectral_features(y)
        
        # Should handle silence without crashing
        assert 'spectral_centroid' in features
        assert len(features['spectral_centroid']) > 0
        
        # Convert to numpy arrays for comparison
        spectral_centroid = np.array(features['spectral_centroid'])
        rms_energy = np.array(features['rms_energy'])
        
        # Spectral centroid should be 0 for silence
        assert np.allclose(spectral_centroid, 0, atol=1e-6)
        
        # RMS energy should be very close to 0
        assert np.all(rms_energy < 1e-6)
    
    def test_mfcc_extraction(self, sample_audio):
        """Test MFCC feature extraction"""
        y, sr = sample_audio
        extractor = AdvancedFeatureExtractor(sample_rate=sr)
        
        # Test with different numbers of coefficients
        for n_mfcc in [13, 20, 5]:
            features = extractor.extract_mfcc_features(y, n_mfcc=n_mfcc)
            
            # Check all expected features are present
            expected_features = [
                'mfccs',
                'mfcc_delta',
                'mfcc_delta2',
                'mfcc_mean',
                'mfcc_std'
            ]
            
            for feature in expected_features:
                assert feature in features
                assert len(features[feature]) == n_mfcc
                
                # Check for NaN or infinite values
                assert not np.any(np.isnan(features[feature]))
                assert not np.any(np.isinf(features[feature]))
    
    def test_mfcc_extraction_edge_cases(self):
        """Test MFCC extraction with edge cases"""
        extractor = AdvancedFeatureExtractor(sample_rate=44100)
        
        # Test with very short audio (shorter than window size)
        y_short = generate_sine_wave(440, 44100, 0.1)  # 100ms
        features = extractor.extract_mfcc_features(y_short)
        assert 'mfccs' in features
        assert len(features['mfccs']) > 0  # Should still return some MFCCs
        
        # Test with very quiet audio
        y_quiet = generate_sine_wave(440, 44100, 1.0, amplitude=1e-6)
        features = extractor.extract_mfcc_features(y_quiet)
        assert 'mfccs' in features
        assert len(features['mfccs']) > 0  # Should still return some MFCCs
        
        # Test with silence
        y_silent = np.zeros(44100)  # 1 second of silence
        features = extractor.extract_mfcc_features(y_silent)
        assert 'mfccs' in features
        assert len(features['mfccs']) > 0  # Should handle silence gracefully
    
    def test_harmonic_percussive_separation(self, sample_audio):
        """Test harmonic/percussive source separation"""
        y, _ = sample_audio
        
        # Skip very short signals as they may not work well with HPSS
        if len(y) < 2048:  # Minimum length for reasonable HPSS
            pytest.skip("Signal too short for HPSS testing")
            
        # Normalize the input signal to prevent numerical issues
        y = y / (np.max(np.abs(y)) + 1e-8)
        
        # Test with different margin values
        for margin in [1.0, 2.0, 3.0]:
            y_harmonic, y_percussive = AudioProcessor.extract_harmonic_percussive(y, margin=margin)
            
            # Check output shapes
            assert len(y_harmonic) == len(y)
            assert len(y_percussive) == len(y)
            
            # For a pure sine wave, most energy should be in harmonic component
            if len(y) > 1000:  # Only for reasonably long signals
                harmonic_energy = np.sum(y_harmonic**2)
                percussive_energy = np.sum(y_percussive**2)
                total_energy = harmonic_energy + percussive_energy
                
                if total_energy > 1e-10:  # Only check if there's significant energy
                    # Most energy should be in harmonic for a pure tone
                    # Be more lenient with the energy ratio
                    assert harmonic_energy > 0.5 * total_energy
    
    def test_harmonic_percussive_edge_cases(self):
        """Test edge cases for harmonic/percussive separation"""
        # Test with silence
        y_silent = np.zeros(44100)  # 1 second of silence
        y_h, y_p = AudioProcessor.extract_harmonic_percussive(y_silent)
        assert np.allclose(y_h, 0, atol=1e-10)
        assert np.allclose(y_p, 0, atol=1e-10)
        
        # Test with impulse
        y_impulse = generate_impulse(44100, 1.0)
        y_h, y_p = AudioProcessor.extract_harmonic_percussive(y_impulse)
        
        # Check that the sum is close to the original
        assert np.allclose(y_impulse, y_h + y_p, atol=1e-6)
        
        # For an impulse, most energy should be in the percussive component
        if np.sum(y_h**2) + np.sum(y_p**2) > 1e-10:  # Only if not both zero
            percussive_energy = np.sum(y_p**2)
            total_energy = np.sum(y_h**2) + percussive_energy
            assert percussive_energy > 0.5 * total_energy
        
        # Test with very short signal (should not crash)
        y_short = np.random.randn(10)
        try:
            y_h, y_p = AudioProcessor.extract_harmonic_percussive(y_short)
            assert len(y_h) == len(y_short)
            assert len(y_p) == len(y_short)
        except Exception as e:
            # It's acceptable for this to fail with a clear error message
            assert "too short" in str(e).lower() or "too small" in str(e).lower()
        
        # Test with NaN/Inf values (should raise ValueError from our validation)
        y_nan = np.full(44100, np.nan)
        y_inf = np.full(44100, np.inf)
        
        with pytest.raises(ValueError, match="contains NaN or infinite"):
            AudioProcessor.extract_harmonic_percussive(y_nan)
            
        with pytest.raises(ValueError, match="contains NaN or infinite"):
            AudioProcessor.extract_harmonic_percussive(y_inf)

class TestAudioFeaturesClass:
    """Test AudioFeatures dataclass"""
    
    def test_audio_features_creation(self):
        """Test AudioFeatures initialization"""
        features = AudioFeatures(
            duration=5.0,
            sample_rate=44100,
            channels=2,
            bit_depth=16,
            tempo=120.0,
            time_signature=(4, 4),
            key="C",
            mode="major",
            mfccs=np.zeros((13, 100)),
            spectral_centroid=[0.5, 0.6, 0.7],
            spectral_bandwidth=[1000, 1200, 1100],
            spectral_rolloff=[5000, 5200, 5100],
            zero_crossing_rate=[0.1, 0.2, 0.15],
            rms_energy=[0.5, 0.6, 0.55],
            pitch_class_distribution=[0.1] * 12,
            chroma_features=np.zeros((12, 100)),
            harmonic_content=np.zeros(1000),
            percussive_content=np.zeros(1000),
            beats=[0.5, 1.0, 1.5, 2.0, 2.5],
            onset_times=[0.12, 0.25, 0.38, 0.5, 0.62],
            rhythm_pattern=[4.0, 0.5, 0.5, 0.2],
            groove_template=np.zeros(16),
            analysis_timestamp=1234567890.0,
            file_hash="abc123",
            file_size=1024,
            analysis_level="standard"
        )
        
        assert features.duration == 5.0
        assert features.sample_rate == 44100
        assert features.channels == 2
        assert features.bit_depth == 16
        assert features.tempo == 120.0
        assert features.time_signature == (4, 4)
        assert features.key == "C"
        assert features.mode == "major"
        assert features.mfccs.shape == (13, 100)
        assert len(features.spectral_centroid) == 3
        assert features.analysis_level == "standard"
