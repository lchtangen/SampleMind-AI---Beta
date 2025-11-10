"""Legacy audio engine tests (superseded by tests/unit/core/test_audio_engine.py)"""

import pytest

pytest.skip("Legacy audio engine tests replaced by tests/unit/core/test_audio_engine.py", allow_module_level=True)

import numpy as np
from pathlib import Path

from src.samplemind.core.engine.audio_engine import AudioEngine, AnalysisLevel, AudioFeatures


class TestAudioEngine:
    """Test AudioEngine functionality"""
    
    def test_engine_initialization(self, audio_engine):
        """Test AudioEngine initialization"""
        assert audio_engine is not None
        assert audio_engine.max_workers >= 1
        assert audio_engine.cache_size > 0
    
    @pytest.mark.asyncio
    async def test_analyze_audio_basic(self, audio_engine, test_audio_samples):
        """Test basic audio analysis"""
        audio_file = test_audio_samples["120_c_major"]
        
        features = await audio_engine.analyze_audio(
            str(audio_file),
            level=AnalysisLevel.BASIC
        )
        
        assert features is not None
        assert isinstance(features, AudioFeatures)
        assert features.duration > 0
        assert features.sample_rate > 0
    
    @pytest.mark.asyncio
    async def test_analyze_audio_standard(self, audio_engine, test_audio_samples):
        """Test standard audio analysis"""
        audio_file = test_audio_samples["120_c_major"]
        
        features = await audio_engine.analyze_audio(
            str(audio_file),
            level=AnalysisLevel.STANDARD
        )
        
        assert features is not None
        assert features.tempo is not None
        assert features.key is not None
        assert 100 <= features.tempo <= 150  # Should be around 120 BPM
    
    @pytest.mark.asyncio
    async def test_analyze_audio_advanced(self, audio_engine, test_audio_samples):
        """Test advanced audio analysis"""
        audio_file = test_audio_samples["140_a_minor"]
        
        features = await audio_engine.analyze_audio(
            str(audio_file),
            level=AnalysisLevel.ADVANCED
        )
        
        assert features is not None
        assert features.spectral_centroid is not None
        assert len(features.spectral_centroid) > 0
        assert features.rms_energy is not None
        assert len(features.rms_energy) > 0
    
    @pytest.mark.asyncio
    async def test_batch_analysis(self, audio_engine, test_audio_samples):
        """Test batch audio analysis"""
        files = [
            str(test_audio_samples["120_c_major"]),
            str(test_audio_samples["140_a_minor"])
        ]
        
        results = await audio_engine.analyze_batch(files, level=AnalysisLevel.BASIC)
        
        assert len(results) == 2
        assert all(isinstance(r, AudioFeatures) for r in results)
    
    def test_cache_functionality(self, audio_engine, test_audio_samples):
        """Test caching mechanism"""
        audio_file = test_audio_samples["120_c_major"]
        
        # First analysis
        result1 = audio_engine.analyze_audio_sync(str(audio_file))
        
        # Second analysis (should hit cache)
        result2 = audio_engine.analyze_audio_sync(str(audio_file))
        
        assert result1.file_hash == result2.file_hash
        stats = audio_engine.get_cache_stats()
        assert stats["hits"] >= 1
    
    def test_invalid_file(self, audio_engine):
        """Test handling of invalid file"""
        with pytest.raises(FileNotFoundError):
            audio_engine.analyze_audio_sync("nonexistent_file.wav")
    
    def test_engine_shutdown(self):
        """Test engine shutdown"""
        engine = AudioEngine(max_workers=2)
        engine.shutdown()
        # Should not raise exception


class TestAudioFeatures:
    """Test AudioFeatures data class"""
    
    def test_audio_features_creation(self, sample_audio_features):
        """Test AudioFeatures creation"""
        assert sample_audio_features.duration == 30.0
        assert sample_audio_features.sample_rate == 44100
        assert sample_audio_features.tempo == 120.0
        assert sample_audio_features.key == "C"
    
    def test_audio_features_to_dict(self, sample_audio_features):
        """Test converting AudioFeatures to dict"""
        features_dict = sample_audio_features.to_dict()
        
        assert isinstance(features_dict, dict)
        assert "duration" in features_dict
        assert "tempo" in features_dict
        assert features_dict["duration"] == 30.0
    
    def test_audio_features_validation(self):
        """Test AudioFeatures validation"""
        with pytest.raises(ValueError):
            AudioFeatures(
                duration=-1.0,  # Invalid
                sample_rate=44100,
                channels=1
            )
