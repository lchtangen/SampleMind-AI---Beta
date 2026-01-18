"""Unit tests for AI classifier module."""

import pytest
from pathlib import Path
import numpy as np

from samplemind.ai.classification.classifier import AIClassifier, ClassificationResult
from samplemind.ai.classification.auto_tagger import AutoTagger
from samplemind.core.engine.audio_engine import AudioFeatures


class TestAIClassifier:
    """Test AIClassifier class."""

    def test_classifier_initialization(self):
        """Test classifier initializes correctly."""
        classifier = AIClassifier(use_gpu=False, cache_size=100)
        assert classifier is not None
        assert classifier.model is None
        assert len(classifier._cache) == 0
        assert classifier.cache_size == 100

    def test_classifier_instrument_detection_kick(self):
        """Test kick drum detection."""
        classifier = AIClassifier()

        # Mock features for kick drum (low frequency, high energy)
        features = AudioFeatures(
            duration=1.0,
            sample_rate=44100,
            channels=1,
            tempo=128.0,
            spectral_centroid=[100.0] * 10,  # Arrays, not scalars
            zero_crossing_rate=[0.05] * 10,
            rms_energy=[0.25] * 10,
        )

        instrument, confidence = classifier._classify_instrument(features)
        assert instrument == "kick"
        assert 0.7 <= confidence <= 0.8

    def test_classifier_instrument_detection_hihat(self):
        """Test hi-hat detection."""
        classifier = AIClassifier()

        features = AudioFeatures(
            duration=0.5,
            sample_rate=44100,
            channels=1,
            spectral_centroid=[8000.0] * 10,
            zero_crossing_rate=[0.20] * 10,
            rms_energy=[0.1] * 10,
        )

        instrument, confidence = classifier._classify_instrument(features)
        assert instrument == "hihat"
        assert 0.6 <= confidence <= 0.8

    def test_classifier_genre_classification_techno(self):
        """Test techno genre detection."""
        classifier = AIClassifier()

        features = AudioFeatures(
            duration=4.0,
            sample_rate=44100,
            channels=2,
            tempo=128.0,
            spectral_centroid=[2500.0] * 10,
        )

        genre, confidence = classifier._classify_genre(features)
        assert genre == "techno"
        assert confidence >= 0.7

    def test_classifier_genre_classification_hiphop(self):
        """Test hip-hop genre detection."""
        classifier = AIClassifier()

        features = AudioFeatures(
            duration=2.0,
            sample_rate=44100,
            channels=2,
            tempo=95.0,
        )

        genre, confidence = classifier._classify_genre(features)
        assert genre == "hiphop"
        assert confidence >= 0.7

    def test_classifier_genre_classification_dnb(self):
        """Test drum and bass genre detection."""
        classifier = AIClassifier()

        features = AudioFeatures(
            duration=2.0,
            sample_rate=44100,
            channels=2,
            tempo=170.0,
        )

        genre, confidence = classifier._classify_genre(features)
        assert genre == "dnb"
        assert confidence >= 0.7

    def test_classifier_mood_classification_dark(self):
        """Test dark mood detection."""
        classifier = AIClassifier()

        features = AudioFeatures(
            duration=2.0,
            sample_rate=44100,
            channels=2,
            rms_energy=[0.05] * 10,
            spectral_centroid=[300.0] * 10,
            mode="minor",
            tempo=80.0,
        )

        mood, confidence = classifier._classify_mood(features)
        assert mood == "dark"
        assert confidence >= 0.65

    def test_classifier_mood_classification_aggressive(self):
        """Test aggressive mood detection."""
        classifier = AIClassifier()

        features = AudioFeatures(
            duration=2.0,
            sample_rate=44100,
            channels=2,
            rms_energy=[0.30] * 10,
            spectral_centroid=[2000.0] * 10,
            tempo=140.0,
        )

        mood, confidence = classifier._classify_mood(features)
        assert mood == "aggressive"
        assert confidence >= 0.7

    def test_classifier_quality_assessment_professional(self):
        """Test professional quality assessment."""
        classifier = AIClassifier()

        features = AudioFeatures(
            duration=2.0,
            sample_rate=44100,
            channels=2,
            bit_depth=24,
            rms_energy=[0.09] * 10,
            spectral_bandwidth=[2000.0] * 10,
        )

        quality = classifier._assess_quality(features)
        assert quality >= 0.65

    def test_classifier_quality_assessment_lofi(self):
        """Test lo-fi quality assessment."""
        classifier = AIClassifier()

        features = AudioFeatures(
            duration=2.0,
            sample_rate=11025,
            channels=1,
            bit_depth=8,
            rms_energy=[0.8] * 10,
            spectral_bandwidth=[500.0] * 10,
        )

        quality = classifier._assess_quality(features)
        assert quality <= 0.40

    def test_classifier_tempo_categorization(self):
        """Test tempo categorization."""
        classifier = AIClassifier()

        # Slow
        features_slow = AudioFeatures(
            duration=2.0,
            sample_rate=44100,
            channels=2,
            tempo=70.0,
        )
        assert classifier._categorize_tempo(features_slow) == "slow"

        # Medium
        features_medium = AudioFeatures(
            duration=2.0,
            sample_rate=44100,
            channels=2,
            tempo=110.0,
        )
        assert classifier._categorize_tempo(features_medium) == "medium"

        # Fast
        features_fast = AudioFeatures(
            duration=2.0,
            sample_rate=44100,
            channels=2,
            tempo=140.0,
        )
        assert classifier._categorize_tempo(features_fast) == "fast"

    def test_classifier_generates_tags(self):
        """Test tag generation."""
        classifier = AIClassifier()

        features = AudioFeatures(
            duration=2.0,
            sample_rate=44100,
            channels=2,
            tempo=150.0,  # Fast tempo
            spectral_centroid=[2500.0] * 10,
            rms_energy=[0.20] * 10,
            bit_depth=24,
            spectral_bandwidth=[2000.0] * 10,
        )

        result = classifier._classify_with_rules(features)
        assert isinstance(result, ClassificationResult)
        assert len(result.tags) > 0
        assert "techno" in result.tags or "house" in result.tags or "upbeat" in result.tags
        assert "fast" in result.tags

    def test_classifier_caching(self):
        """Test classifier caching."""
        classifier = AIClassifier(cache_size=10)

        features = AudioFeatures(
            duration=2.0,
            sample_rate=44100,
            channels=2,
            tempo=128.0,
            file_hash="test_hash_123",
        )

        # First call
        result1 = classifier.classify_audio(features)
        assert len(classifier._cache) == 1

        # Second call (should hit cache)
        result2 = classifier.classify_audio(features)
        assert len(classifier._cache) == 1
        assert result1.instrument == result2.instrument

    def test_classifier_cache_lru_eviction(self):
        """Test cache LRU eviction."""
        classifier = AIClassifier(cache_size=2)

        # Add three features
        for i in range(3):
            features = AudioFeatures(
                duration=2.0,
                sample_rate=44100,
                channels=2,
                tempo=100.0 + i,
                file_hash=f"hash_{i}",
            )
            classifier.classify_audio(features)

        # Cache should only have 2 items
        assert len(classifier._cache) == 2

    def test_classifier_cache_stats(self):
        """Test cache statistics."""
        classifier = AIClassifier(cache_size=50)

        stats = classifier.get_cache_stats()
        assert "cache_size" in stats
        assert "max_cache_size" in stats
        assert stats["max_cache_size"] == 50
        assert stats["cache_size"] == 0

    def test_classifier_clear_cache(self):
        """Test cache clearing."""
        classifier = AIClassifier()

        features = AudioFeatures(
            duration=2.0,
            sample_rate=44100,
            channels=2,
            file_hash="test_hash",
        )

        classifier.classify_audio(features)
        assert len(classifier._cache) > 0

        classifier.clear_cache()
        assert len(classifier._cache) == 0


class TestAutoTagger:
    """Test AutoTagger class."""

    def test_auto_tagger_initialization(self):
        """Test auto-tagger initializes correctly."""
        tagger = AutoTagger(confidence_threshold=0.60)
        assert tagger is not None
        assert tagger.confidence_threshold == 0.60

    def test_auto_tagger_generates_tags(self):
        """Test auto-tagger generates tags."""
        tagger = AutoTagger()

        features = AudioFeatures(
            duration=2.0,
            sample_rate=44100,
            channels=2,
            tempo=128.0,
            spectral_centroid=[2500.0] * 10,
            rms_energy=[0.20] * 10,
            bit_depth=24,
        )

        tags = tagger.auto_tag_sample(features, Path("test.wav"))
        assert isinstance(tags, list)
        assert len(tags) > 0

    def test_auto_tagger_confidence_threshold(self):
        """Test confidence threshold filtering."""
        tagger = AutoTagger(confidence_threshold=0.95)

        features = AudioFeatures(
            duration=2.0,
            sample_rate=44100,
            channels=2,
            tempo=128.0,
            spectral_centroid=[2500.0] * 10,
        )

        tags = tagger.auto_tag_sample(features, Path("test.wav"))
        # With high threshold, fewer tags should be generated
        assert isinstance(tags, list)

    def test_auto_tagger_confidence_report(self):
        """Test confidence report generation."""
        tagger = AutoTagger()

        features = AudioFeatures(
            duration=2.0,
            sample_rate=44100,
            channels=2,
            tempo=128.0,
            spectral_centroid=[2500.0] * 10,
            rms_energy=[0.20] * 10,
        )

        report = tagger.get_confidence_report(features)
        assert "instrument" in report
        assert "genre" in report
        assert "mood" in report
        assert "quality" in report
        assert "tags" in report


class TestClassificationResult:
    """Test ClassificationResult dataclass."""

    def test_classification_result_creation(self):
        """Test creating a classification result."""
        result = ClassificationResult(
            instrument="kick",
            instrument_confidence=0.75,
            genre="techno",
            genre_confidence=0.80,
            mood="dark",
            mood_confidence=0.70,
            quality_score=0.85,
            tempo_category="fast",
            tags=["kick", "techno", "dark"],
            processing_time=0.5,
            model_used="rule-based",
        )

        assert result.instrument == "kick"
        assert result.genre == "techno"
        assert result.quality_score == 0.85
        assert len(result.tags) == 3
