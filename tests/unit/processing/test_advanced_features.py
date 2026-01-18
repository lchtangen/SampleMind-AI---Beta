"""Unit tests for advanced feature extraction."""

import pytest
import numpy as np

from samplemind.core.processing.advanced_features import (
    AdvancedFeatureExtractor,
    AdvancedAudioFeatures,
)


class TestAdvancedFeatureExtractor:
    """Test advanced feature extraction"""

    @pytest.fixture
    def extractor(self):
        return AdvancedFeatureExtractor(sample_rate=44100)

    @pytest.mark.asyncio
    async def test_extract_features(self, extractor):
        """Test extracting all features"""
        # Create test audio
        t = np.arange(44100) / 44100
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)

        features = await extractor.extract(audio)

        assert isinstance(features, AdvancedAudioFeatures)
        assert features.temporal_centroid > 0
        assert features.temporal_variance >= 0
        assert features.spectral_flux >= 0
        assert len(features.spectral_stability) > 0
        assert features.chromagram.shape[0] == 12  # 12 pitch classes

    def test_temporal_features(self, extractor):
        """Test temporal feature extraction"""
        # Create test audio
        t = np.arange(44100) / 44100
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)

        centroid, variance = extractor._extract_temporal_features(audio)

        assert centroid > 0
        assert variance >= 0

    def test_spectral_features(self, extractor):
        """Test spectral feature extraction"""
        # Create test audio
        t = np.arange(44100) / 44100
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)

        flux, stability = extractor._extract_spectral_features(audio)

        assert flux >= 0
        assert len(stability) > 0
        assert np.all(stability >= 0) and np.all(stability <= 1)

    def test_chromagram(self, extractor):
        """Test chromagram extraction"""
        # Create test audio
        t = np.arange(44100) / 44100
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)

        chroma = extractor._extract_chromagram(audio)

        # Should have 12 pitch classes
        assert chroma.shape[0] == 12
        assert chroma.shape[1] > 0

    def test_timbral_features(self, extractor):
        """Test timbral feature extraction"""
        # Create test audio
        t = np.arange(44100) / 44100
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)

        brightness, warmth, sharpness = extractor._extract_timbral_features(audio)

        # All features should be between 0 and 1
        assert 0.0 <= brightness <= 1.0
        assert 0.0 <= warmth <= 1.0
        assert 0.0 <= sharpness <= 1.0

    def test_timbral_profile(self, extractor):
        """Test generating timbral profile"""
        # Create mock features
        features = AdvancedAudioFeatures(
            temporal_centroid=0.5,
            temporal_variance=0.1,
            spectral_flux=0.05,
            spectral_stability=np.array([0.8, 0.85, 0.9]),
            chromagram=np.ones((12, 100)),
            tempogram=np.ones((384, 100)),
            timbral_brightness=0.8,
            timbral_warmth=0.3,
            timbral_sharpness=0.6,
        )

        profile = extractor.get_timbral_profile(features)

        assert "brightness" in profile
        assert "warmth" in profile
        assert "sharpness" in profile
        assert "Bright" in profile["brightness"]
        assert "Thin" in profile["warmth"]

    def test_harmonic_complexity(self, extractor):
        """Test harmonic complexity calculation"""
        # Create mock features
        features = AdvancedAudioFeatures(
            temporal_centroid=0.5,
            temporal_variance=0.1,
            spectral_flux=0.05,
            spectral_stability=np.array([0.8]),
            chromagram=np.ones((12, 1)),  # Equal energy in all pitch classes
            tempogram=np.ones((384, 1)),
            timbral_brightness=0.5,
            timbral_warmth=0.5,
            timbral_sharpness=0.5,
        )

        complexity = extractor.get_harmonic_complexity(features)

        assert 0.0 <= complexity <= 1.0

    def test_rhythmic_stability(self, extractor):
        """Test rhythmic stability calculation"""
        # Create mock features with stable tempo
        features = AdvancedAudioFeatures(
            temporal_centroid=0.5,
            temporal_variance=0.1,
            spectral_flux=0.05,
            spectral_stability=np.array([0.8]),
            chromagram=np.ones((12, 1)),
            tempogram=np.ones((384, 1)),  # Constant tempo
            timbral_brightness=0.5,
            timbral_warmth=0.5,
            timbral_sharpness=0.5,
        )

        stability = extractor.get_rhythmic_stability(features)

        assert 0.0 <= stability <= 1.0

    def test_features_to_dict(self, extractor):
        """Test converting features to dictionary"""
        # Create mock features
        features = AdvancedAudioFeatures(
            temporal_centroid=0.5,
            temporal_variance=0.1,
            spectral_flux=0.05,
            spectral_stability=np.array([0.8, 0.85]),
            chromagram=np.ones((12, 10)),
            tempogram=np.ones((384, 10)),
            timbral_brightness=0.7,
            timbral_warmth=0.4,
            timbral_sharpness=0.6,
        )

        features_dict = features.to_dict()

        assert isinstance(features_dict, dict)
        assert "temporal_centroid" in features_dict
        assert "timbral_brightness" in features_dict
        assert features_dict["temporal_centroid"] == 0.5

    def test_global_instance(self):
        """Test global extractor instance"""
        from samplemind.core.processing.advanced_features import init_extractor, get_extractor

        extractor1 = init_extractor()
        extractor2 = get_extractor()

        assert extractor1 is extractor2
