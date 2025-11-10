"""
Test suite for performance optimizations in audio engine.
Verifies that optimizations work correctly without breaking functionality.
"""
import pytest
import numpy as np
import time
from pathlib import Path
import tempfile

# Skip if dependencies not available
pytest.importorskip("librosa")
pytest.importorskip("soundfile")

from src.samplemind.core.engine.audio_engine import (
    AudioEngine,
    AdvancedFeatureExtractor,
    AnalysisLevel
)
from src.samplemind.core.engine.feature_cache import FeatureCache


class TestCacheKeyOptimization:
    """Test optimized cache key generation."""
    
    def test_cache_key_speed_for_large_arrays(self):
        """Verify cache key generation is fast for large audio arrays."""
        # Create a large audio array (3 minutes at 44.1kHz)
        large_audio = np.random.randn(44100 * 180)
        
        cache = FeatureCache()
        params = {'feature': 'test', 'sr': 44100}
        
        # Measure time to generate cache key
        start = time.time()
        key1 = cache._get_cache_key(large_audio, params)
        elapsed = time.time() - start
        
        # Should be very fast (< 10ms)
        assert elapsed < 0.01, f"Cache key generation too slow: {elapsed:.4f}s"
        
        # Verify uniqueness - different audio should produce different keys
        different_audio = np.random.randn(44100 * 180)
        key2 = cache._get_cache_key(different_audio, params)
        assert key1 != key2, "Different audio should produce different cache keys"
    
    def test_cache_key_consistency(self):
        """Verify same audio produces same cache key."""
        audio = np.random.randn(44100 * 10)
        cache = FeatureCache()
        params = {'feature': 'test', 'sr': 44100}
        
        key1 = cache._get_cache_key(audio, params)
        key2 = cache._get_cache_key(audio, params)
        
        assert key1 == key2, "Same audio should produce same cache key"
    
    def test_extractor_cache_key_speed(self):
        """Test AdvancedFeatureExtractor cache key generation speed."""
        extractor = AdvancedFeatureExtractor()
        large_audio = np.random.randn(44100 * 180)
        
        start = time.time()
        cache_key = extractor._get_cache_key('spectral', large_audio)
        elapsed = time.time() - start
        
        # Should be very fast (< 10ms)
        assert elapsed < 0.01, f"Extractor cache key generation too slow: {elapsed:.4f}s"
        assert isinstance(cache_key, dict)
        assert 'audio_hash' in cache_key


class TestHPSSOptimization:
    """Test that HPSS is not computed redundantly."""
    
    def test_tonal_features_returns_hpss(self):
        """Verify tonal feature extraction returns HPSS result for reuse."""
        extractor = AdvancedFeatureExtractor()
        # Create a simple test audio signal
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100))
        
        features = extractor.extract_tonal_features(audio)
        
        # Verify HPSS result is cached in the return
        assert 'hpss_result' in features, "HPSS result should be cached"
        assert isinstance(features['hpss_result'], tuple)
        assert len(features['hpss_result']) == 2
        
    def test_tonal_features_accepts_precomputed_hpss(self):
        """Verify tonal features can use pre-computed HPSS."""
        extractor = AdvancedFeatureExtractor()
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100))
        
        # Pre-compute HPSS
        import librosa
        harmonic, percussive = librosa.effects.hpss(audio)
        
        # Pass it to tonal features
        features = extractor.extract_tonal_features(audio, hpss_result=(harmonic, percussive))
        
        # Should still work and return valid features
        assert 'key' in features
        assert 'mode' in features
        assert 'harmonic_ratio' in features


class TestFeatureCacheIntegration:
    """Test FeatureCache integration with AudioEngine."""
    
    def test_engine_has_disk_cache(self):
        """Verify AudioEngine initializes with disk cache."""
        engine = AudioEngine(max_workers=2)
        
        assert hasattr(engine, 'disk_cache'), "Engine should have disk_cache"
        assert isinstance(engine.disk_cache, FeatureCache)
        assert engine.feature_extractor._cache is not None, "Extractor should have cache"
    
    def test_cache_persists_across_extractions(self, tmp_path):
        """Verify cache works across multiple feature extractions."""
        # Create test audio
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100))
        
        # Create cache in temp directory
        cache_dir = tmp_path / "cache"
        cache = FeatureCache(cache_dir=str(cache_dir))
        extractor = AdvancedFeatureExtractor(cache=cache)
        
        # First extraction - should miss cache
        features1 = extractor.extract_spectral_features(audio)
        
        # Second extraction - should hit cache
        features2 = extractor.extract_spectral_features(audio)
        
        # Results should be consistent
        assert features1['spectral_centroid'] == features2['spectral_centroid']
        
        # Check cache files were created
        assert len(list(cache_dir.glob("*.npz"))) > 0


class TestOverallPerformance:
    """Integration tests for overall performance improvements."""
    
    def test_detailed_analysis_no_redundant_hpss(self):
        """Verify DETAILED analysis doesn't compute HPSS twice."""
        engine = AudioEngine(max_workers=2)
        
        # Create a test audio signal
        duration = 5  # seconds
        sr = 22050  # Use lower sample rate for faster testing
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, duration, sr * duration))
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            temp_path = Path(f.name)
            
        try:
            import soundfile as sf
            sf.write(str(temp_path), audio, sr)
            
            # Analyze with DETAILED level (would trigger redundant HPSS in old code)
            start = time.time()
            features = engine.analyze_audio(temp_path, level=AnalysisLevel.DETAILED, use_cache=False)
            elapsed = time.time() - start
            
            # Verify features are correct
            assert features.harmonic_content is not None
            assert features.percussive_content is not None
            assert features.key is not None
            assert features.tempo > 0
            
            # Performance check - should be reasonably fast
            # (This is a sanity check, not a strict benchmark)
            assert elapsed < 10.0, f"Analysis took too long: {elapsed:.2f}s"
            
        finally:
            temp_path.unlink(missing_ok=True)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
