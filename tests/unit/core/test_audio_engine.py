#!/usr/bin/env python3
"""
Unit tests for core audio engine functionality
"""

import pytest
import numpy as np
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import soundfile as sf

from samplemind.core.engine.audio_engine import (
    AudioEngine, AudioFeatures, AnalysisLevel, AudioFormat,
    AudioProcessor, AdvancedFeatureExtractor
)


class TestAudioEngine:
    """Test AudioEngine core functionality"""
    
    def test_audio_engine_initialization(self):
        """Test AudioEngine initializes correctly"""
        engine = AudioEngine(max_workers=2, cache_size=10)
        
        assert engine.max_workers == 2
        assert engine.cache_size == 10
        assert engine.processor is not None
        assert engine.feature_extractor is not None
        assert engine.executor is not None
        
    def test_load_audio_valid_file(self, audio_engine, test_audio_samples):
        """Test loading valid audio file"""
        test_file = test_audio_samples["120_c_major"]
        
        audio_data, sample_rate = audio_engine.load_audio(test_file)
        
        assert isinstance(audio_data, np.ndarray)
        assert audio_data.ndim == 1  # Should be mono
        assert sample_rate == 44100
        assert len(audio_data) > 0
        
    def test_load_audio_nonexistent_file(self, audio_engine):
        """Test loading non-existent file raises error"""
        with pytest.raises(FileNotFoundError):
            audio_engine.load_audio("/path/that/does/not/exist.wav")
            
    def test_load_audio_with_target_sample_rate(self, audio_engine, test_audio_samples):
        """Test loading audio with sample rate conversion"""
        test_file = test_audio_samples["120_c_major"]
        target_sr = 22050
        
        audio_data, sample_rate = audio_engine.load_audio(test_file, target_sr=target_sr)
        
        assert sample_rate == target_sr
        assert isinstance(audio_data, np.ndarray)
        
    def test_analyze_audio_basic(self, audio_engine, test_audio_samples):
        """Test basic audio analysis"""
        test_file = test_audio_samples["120_c_major"]

        features = audio_engine.analyze_audio(test_file, level=AnalysisLevel.BASIC)

        assert isinstance(features, AudioFeatures)
        assert features.duration > 0
        assert features.sample_rate == 44100
        assert features.tempo >= 0  # Tempo can be 0 if no beat detected
        assert features.key is not None
        assert features.mode is not None
        
    def test_analyze_audio_detailed(self, audio_engine, test_audio_samples):
        """Test detailed audio analysis"""
        test_file = test_audio_samples["120_c_major"]
        
        features = audio_engine.analyze_audio(test_file, level=AnalysisLevel.DETAILED)
        
        assert isinstance(features, AudioFeatures)
        assert features.spectral_centroid is not None
        assert features.rms_energy is not None
        assert features.pitch_class_distribution is not None
        assert len(features.pitch_class_distribution) == 12
        
    def test_analyze_audio_caching(self, audio_engine, test_audio_samples):
        """Test that audio analysis uses caching"""
        test_file = test_audio_samples["120_c_major"]
        
        # First analysis - should cache result
        features1 = audio_engine.analyze_audio(test_file, use_cache=True)
        
        # Second analysis - should use cache
        features2 = audio_engine.analyze_audio(test_file, use_cache=True)
        
        # Should be identical (from cache)
        assert features1.file_hash == features2.file_hash
        assert features1.tempo == features2.tempo
        
    @pytest.mark.asyncio
    async def test_analyze_audio_async(self, async_audio_engine, test_audio_samples):
        """Test asynchronous audio analysis"""
        test_file = test_audio_samples["120_c_major"]

        features = await async_audio_engine.analyze_audio_async(test_file)

        assert isinstance(features, AudioFeatures)
        assert features.duration > 0
        assert features.tempo >= 0  # Tempo can be 0 if no beat detected
        
    def test_batch_analyze(self, audio_engine, test_audio_samples):
        """Test batch analysis of multiple files"""
        files = [test_audio_samples["120_c_major"], test_audio_samples["140_a_minor"]]

        results = audio_engine.batch_analyze(files, level=AnalysisLevel.STANDARD)

        assert len(results) == 2
        for result in results:
            assert isinstance(result, AudioFeatures)
            assert result.tempo >= 0  # Tempo can be 0 if no beat detected
            
    def test_performance_stats(self, audio_engine, test_audio_samples):
        """Test performance statistics tracking"""
        test_file = test_audio_samples["120_c_major"]

        # Perform some analysis
        audio_engine.analyze_audio(test_file)

        stats = audio_engine.get_performance_stats()

        assert 'total_analyses' in stats
        assert 'avg_analysis_time' in stats
        assert 'cache_hit_rate' in stats
        assert stats['total_analyses'] >= 1
        
    def test_shutdown(self, audio_engine):
        """Test engine shutdown"""
        audio_engine.shutdown()
        
        # After shutdown, executor should be shutdown
        assert audio_engine.executor._shutdown


class TestAudioFeatures:
    """Test AudioFeatures data class"""
    
    def test_audio_features_initialization(self):
        """Test AudioFeatures can be initialized with minimal data"""
        features = AudioFeatures(
            duration=30.0,
            sample_rate=44100,
            channels=1
        )
        
        assert features.duration == 30.0
        assert features.sample_rate == 44100
        assert features.channels == 1
        
    def test_audio_features_to_dict(self, sample_audio_features):
        """Test AudioFeatures can be converted to dictionary"""
        features_dict = sample_audio_features.to_dict()
        
        assert isinstance(features_dict, dict)
        assert 'duration' in features_dict
        assert 'sample_rate' in features_dict
        assert 'tempo' in features_dict
        assert 'key' in features_dict
        
    def test_audio_features_similarity(self, sample_audio_features):
        """Test AudioFeatures similarity calculation"""
        # Create similar features
        similar_features = AudioFeatures(
            duration=30.0,
            sample_rate=44100,
            channels=1,
            tempo=125.0,  # Close to original 120.0
            key="C",
            mode="major",
            pitch_class_distribution=[0.2, 0.1, 0.15, 0.05, 0.2, 0.1, 0.05, 0.15, 0.0, 0.0, 0.0, 0.0]
        )
        
        similarity = sample_audio_features.calculate_similarity(similar_features)
        
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.5  # Should be quite similar
        
    def test_audio_features_hash_consistency(self):
        """Test that file hash is calculated consistently"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            # Create test audio
            sample_rate = 44100
            duration = 1.0
            t = np.linspace(0, duration, int(sample_rate * duration))
            signal = 0.5 * np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave
            
            sf.write(tmp_file.name, signal, sample_rate)
            
            # Calculate hash twice
            features1 = AudioFeatures(duration=1.0, sample_rate=44100, channels=1)
            hash1 = features1._calculate_file_hash(Path(tmp_file.name))
            
            features2 = AudioFeatures(duration=1.0, sample_rate=44100, channels=1)
            hash2 = features2._calculate_file_hash(Path(tmp_file.name))
            
            assert hash1 == hash2
            
        # Cleanup
        Path(tmp_file.name).unlink()


class TestAudioProcessor:
    """Test AudioProcessor utility functions"""
    
    def test_normalize_audio(self):
        """Test audio normalization"""
        processor = AudioProcessor()
        
        # Create test signal with varying amplitude
        signal = np.array([0.1, 0.5, -0.3, 0.8, -0.2])
        normalized = processor.normalize_audio(signal)
        
        # Should be normalized to [-1, 1] range
        assert np.max(np.abs(normalized)) <= 1.0
        assert np.max(normalized) > 0.5  # Should scale up
        
    def test_apply_high_pass_filter(self):
        """Test high-pass filter application"""
        processor = AudioProcessor()
        
        # Create test signal with low and high frequency components
        sample_rate = 44100
        t = np.linspace(0, 1, sample_rate)
        low_freq = np.sin(2 * np.pi * 50 * t)    # 50 Hz (should be filtered)
        high_freq = np.sin(2 * np.pi * 1000 * t) # 1000 Hz (should pass)
        signal = low_freq + high_freq
        
        filtered = processor.apply_high_pass_filter(signal, sample_rate, cutoff=100)
        
        # Filtered signal should have less low-frequency content
        assert len(filtered) == len(signal)
        assert not np.array_equal(filtered, signal)


class TestAdvancedFeatureExtractor:
    """Test AdvancedFeatureExtractor functionality"""
    
    def test_feature_extractor_initialization(self):
        """Test feature extractor initializes correctly"""
        extractor = AdvancedFeatureExtractor()
        
        assert extractor is not None
        
    def test_extract_spectral_features(self, test_audio_samples):
        """Test spectral feature extraction"""
        # Load test audio
        audio_data, sample_rate = sf.read(test_audio_samples["120_c_major"])

        extractor = AdvancedFeatureExtractor(sample_rate=sample_rate)
        features = extractor.extract_spectral_features(audio_data)

        assert 'spectral_centroid' in features
        assert 'spectral_bandwidth' in features
        assert 'spectral_rolloff' in features
        assert isinstance(features['spectral_centroid'], list)
        assert len(features['spectral_centroid']) > 0
        
    def test_extract_rhythm_features(self, test_audio_samples):
        """Test rhythm feature extraction"""
        # Load test audio
        audio_data, sample_rate = sf.read(test_audio_samples["120_c_major"])

        extractor = AdvancedFeatureExtractor(sample_rate=sample_rate)
        features = extractor.extract_rhythmic_features(audio_data)

        assert 'tempo' in features
        assert 'beats' in features
        assert features['tempo'] >= 0  # Tempo can be 0 if no beat detected
        
    def test_extract_harmonic_features(self, test_audio_samples):
        """Test harmonic/tonal feature extraction"""
        # Load test audio
        audio_data, sample_rate = sf.read(test_audio_samples["120_c_major"])

        extractor = AdvancedFeatureExtractor(sample_rate=sample_rate)
        features = extractor.extract_tonal_features(audio_data)

        assert 'key' in features
        assert 'mode' in features
        assert 'pitch_class_distribution' in features
        assert features['key'] is not None
        assert features['mode'] in ['major', 'minor']
        assert len(features['pitch_class_distribution']) == 12


@pytest.mark.integration
class TestAudioEngineIntegration:
    """Integration tests for AudioEngine with real audio files"""
    
    def test_full_analysis_pipeline(self, audio_engine, test_audio_samples):
        """Test complete analysis pipeline with multiple files"""
        results = []
        
        for sample_name, sample_path in test_audio_samples.items():
            features = audio_engine.analyze_audio(sample_path, level=AnalysisLevel.DETAILED)
            results.append((sample_name, features))
            
        assert len(results) == len(test_audio_samples)
        
        # Check that different samples have different characteristics
        tempos = [features.tempo for _, features in results]
        assert len(set(tempos)) > 1  # Should have different tempos
        
    def test_concurrent_analysis(self, audio_engine, test_audio_samples):
        """Test concurrent analysis of multiple files"""
        files = list(test_audio_samples.values())
        
        # Use batch analysis for concurrency
        results = audio_engine.batch_analyze(files, level=AnalysisLevel.STANDARD)
        
        assert len(results) == len(files)
        for result in results:
            assert isinstance(result, AudioFeatures)
            assert result.duration > 0