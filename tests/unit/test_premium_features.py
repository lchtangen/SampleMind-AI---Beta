#!/usr/bin/env python3
"""
Unit Tests for Phase 10+ Premium Features

Tests for:
- AI-Powered Sample Tagging
- Professional Mastering Analysis
- Intelligent Sample Layering
- Groove Template Extraction
"""

import pytest
import numpy as np
from pathlib import Path

# Import modules to test
from samplemind.core.tagging.tag_vocabulary import get_vocabulary, TagConfidence
from samplemind.core.tagging.ai_tagger import AITagger, get_tagger
from samplemind.core.processing.loudness_analyzer import LoudnessAnalyzer, LoudnessAnalysis
from samplemind.core.processing.mastering_analyzer import MasteringAnalyzer
from samplemind.core.processing.layering_analyzer import LayeringAnalyzer
from samplemind.core.processing.groove_extractor import GrooveExtractor, GrooveTemplate
from samplemind.core.history.recent_files import RecentFilesManager, RecentFile
from datetime import datetime


# ============================================================================
# TAG VOCABULARY TESTS
# ============================================================================

class TestTagVocabulary:
    """Test tag vocabulary system"""

    def test_vocabulary_initialization(self):
        """Test that vocabulary initializes with tags"""
        vocab = get_vocabulary()
        assert vocab is not None
        assert len(vocab.genres) > 0
        assert len(vocab.moods) > 0
        assert len(vocab.instruments) > 0

    def test_tag_validation(self):
        """Test tag validation"""
        vocab = get_vocabulary()
        assert vocab.is_valid_tag("techno")
        assert vocab.is_valid_tag("uplifting")
        assert not vocab.is_valid_tag("invalid_tag_xyz")

    def test_category_detection(self):
        """Test category detection for tags"""
        vocab = get_vocabulary()
        assert vocab.get_category("techno") == "genre"
        assert vocab.get_category("uplifting") == "mood"
        assert vocab.get_category("drums") == "instrument"

    def test_vocabulary_stats(self):
        """Test vocabulary statistics"""
        vocab = get_vocabulary()
        stats = vocab.stats()
        assert stats["genres"] > 40
        assert stats["moods"] > 20
        assert stats["instruments"] > 30
        assert stats["total"] > 100


# ============================================================================
# AI TAGGER TESTS
# ============================================================================

class TestAITagger:
    """Test AI-powered tagging engine"""

    def test_tagger_initialization(self):
        """Test tagger initializes correctly"""
        tagger = get_tagger()
        assert tagger is not None

    def test_tagging_from_features(self):
        """Test tagging from audio features"""
        tagger = get_tagger()

        features = {
            "tempo": 128,
            "key": "C",
            "mode": "minor",
            "rms_energy": 0.08,
            "crest_factor": 14.5,
            "spectral_centroid": 3500,
            "brightness": 0.72,
            "low_freq_power": 0.45,
            "onset_count": 64,
            "duration": 10.0,
        }

        tags = tagger.tag_from_features(features)

        assert len(tags) > 0
        assert all(isinstance(t, TagConfidence) for t in tags)
        assert all(t.confidence >= 0.5 for t in tags)

    def test_tag_organization(self):
        """Test tag organization by category"""
        tagger = get_tagger()

        features = {
            "tempo": 128,
            "key": "C",
            "mode": "minor",
            "rms_energy": 0.08,
            "crest_factor": 14.5,
        }

        tags = tagger.tag_from_features(features)
        organized = tagger.organize_by_category(tags)

        assert "genre" in organized
        assert "mood" in organized
        assert "energy" in organized

    def test_high_confidence_filtering(self):
        """Test filtering tags by confidence"""
        tagger = get_tagger()

        features = {
            "tempo": 128,
            "key": "C",
            "mode": "minor",
            "rms_energy": 0.08,
        }

        tags = tagger.tag_from_features(features)
        high_conf = tagger.get_high_confidence_tags(tags, threshold=0.7)

        assert all(t.confidence >= 0.7 for t in high_conf)


# ============================================================================
# LOUDNESS ANALYZER TESTS
# ============================================================================

class TestLoudnessAnalyzer:
    """Test loudness analysis"""

    def setup_method(self):
        """Setup test audio"""
        self.analyzer = LoudnessAnalyzer()
        # Generate test signal
        duration = 2
        sample_rate = 44100
        t = np.arange(duration * sample_rate) / sample_rate
        self.audio = 0.5 * np.sin(2 * np.pi * 440 * t)
        self.sr = sample_rate

    def test_loudness_analysis(self):
        """Test loudness analysis"""
        analysis = self.analyzer.analyze_loudness(self.audio, self.sr)

        assert isinstance(analysis, LoudnessAnalysis)
        assert analysis.integrated_loudness < 0  # LUFS should be negative
        assert analysis.true_peak <= 0  # Peak should be <= 0 dBFS
        assert analysis.loudness_range >= 0

    def test_platform_targets(self):
        """Test getting platform loudness targets"""
        from samplemind.core.processing.loudness_analyzer import get_platform_target

        spotify_target = get_platform_target("spotify")
        assert spotify_target["integrated_loudness"] == -14.0

        youtube_target = get_platform_target("youtube")
        assert youtube_target["integrated_loudness"] == -13.0

    def test_gain_adjustment(self):
        """Test gain adjustment calculation"""
        gain = self.analyzer.get_gain_adjustment(-18.0, -14.0)
        assert gain == 4.0  # Should be +4dB


# ============================================================================
# MASTERING ANALYZER TESTS
# ============================================================================

class TestMasteringAnalyzer:
    """Test mastering analysis"""

    def setup_method(self):
        """Setup test audio"""
        self.analyzer = MasteringAnalyzer()
        duration = 2
        sample_rate = 44100
        t = np.arange(duration * sample_rate) / sample_rate

        # Stereo signal
        left = 0.4 * np.sin(2 * np.pi * 440 * t)
        right = 0.35 * np.sin(2 * np.pi * 480 * t)
        self.audio = np.column_stack([left, right])
        self.sr = sample_rate

    def test_mastering_analysis(self):
        """Test comprehensive mastering analysis"""
        analysis = self.analyzer.analyze(self.audio, self.sr, "spotify")

        assert analysis is not None
        assert analysis.target_platform == "spotify"
        assert isinstance(analysis.spectral_balance, dict)
        assert "sub" in analysis.spectral_balance
        assert 0 <= analysis.stereo_width <= 100
        assert -1 <= analysis.phase_correlation <= 1

    def test_recommendations(self):
        """Test recommendation generation"""
        analysis = self.analyzer.analyze(self.audio, self.sr, "spotify")
        recommendations = self.analyzer.get_recommendations(analysis)

        assert len(recommendations) > 0
        assert all(isinstance(r, str) for r in recommendations)

    def test_mastering_grade(self):
        """Test mastering grade assignment"""
        analysis = self.analyzer.analyze(self.audio, self.sr, "spotify")
        grade = self.analyzer.get_mastering_grade(analysis)

        assert grade in ["A", "B", "C", "D", "F"]


# ============================================================================
# LAYERING ANALYZER TESTS
# ============================================================================

class TestLayeringAnalyzer:
    """Test sample layering analysis"""

    def setup_method(self):
        """Setup test audio"""
        self.analyzer = LayeringAnalyzer()
        sr = 44100
        duration = 1

        t = np.arange(duration * sr) / sr

        # Two different samples
        self.audio1 = 0.5 * np.sin(2 * np.pi * 60 * t)  # Bass
        self.audio2 = 0.4 * np.sin(2 * np.pi * 440 * t)  # Treble
        self.sr = sr

    def test_layering_analysis(self):
        """Test layering compatibility analysis"""
        analysis = self.analyzer.analyze(self.audio1, self.audio2, self.sr)

        assert analysis is not None
        assert 0 <= analysis.compatibility_score <= 10
        assert isinstance(analysis.can_layer, bool)

    def test_phase_correlation(self):
        """Test phase correlation calculation"""
        analysis = self.analyzer.analyze(self.audio1, self.audio2, self.sr)

        assert -1 <= analysis.phase_correlation <= 1
        assert analysis.phase_status in ["in-phase", "phase-cancellation", "orthogonal"]

    def test_loudness_balance(self):
        """Test loudness balance analysis"""
        analysis = self.analyzer.analyze(self.audio1, self.audio2, self.sr)

        assert isinstance(analysis.loudness_difference_db, float)
        assert isinstance(analysis.loudness_ratio, float)


# ============================================================================
# GROOVE EXTRACTOR TESTS
# ============================================================================

class TestGrooveExtractor:
    """Test groove extraction"""

    def setup_method(self):
        """Setup test audio"""
        self.extractor = GrooveExtractor()
        sr = 44100

        # Create drum-like pattern
        duration = 2
        t = np.arange(duration * sr) / sr

        # Simple drum pattern
        kick = np.zeros_like(t)
        kick[::int(sr*0.5)] = 1  # Kick every 0.5s
        kick = np.convolve(kick, np.hanning(int(sr*0.05)), mode='same')

        self.audio = kick
        self.sr = sr

    def test_groove_extraction(self):
        """Test groove template extraction"""
        groove = self.extractor.extract(self.audio, self.sr, "test_groove")

        assert isinstance(groove, GrooveTemplate)
        assert groove.name == "test_groove"
        assert groove.tempo_bpm > 0
        assert groove.groove_type in ["straight", "swing", "shuffle", "jdilla", "groovy"]

    def test_groove_properties(self):
        """Test groove template properties"""
        groove = self.extractor.extract(self.audio, self.sr)

        assert 0 <= groove.swing_amount <= 100
        assert groove.timing_deviation_ms >= 0
        assert len(groove.velocity_pattern) > 0


# ============================================================================
# RECENT FILES TESTS
# ============================================================================

class TestRecentFilesManager:
    """Test recent files tracking"""

    def setup_method(self):
        """Setup recent files manager"""
        self.manager = RecentFilesManager(max_history=10)

    def test_manager_initialization(self):
        """Test manager initializes"""
        assert self.manager is not None
        assert self.manager.max_history == 10

    def test_add_recent_file(self):
        """Test adding files to recent history"""
        test_file = Path("/tmp/test_audio.wav")
        self.manager.add(test_file, "STANDARD", ["test"])

        # Note: We don't check if file exists, just test the manager

    def test_get_recent_files(self):
        """Test retrieving recent files"""
        files = self.manager.get_all()
        assert isinstance(files, list)

    def test_recent_file_stats(self):
        """Test statistics generation"""
        stats = self.manager.stats()

        assert "total_files" in stats
        assert "total_size_mb" in stats
        assert "by_analysis_level" in stats


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for features working together"""

    def test_tagging_and_analysis_pipeline(self):
        """Test tagging integrated with analysis features"""
        tagger = get_tagger()

        # Create realistic audio features
        features = {
            "tempo": 120,
            "key": "A",
            "mode": "minor",
            "rms_energy": 0.1,
            "crest_factor": 12,
            "spectral_centroid": 2000,
            "brightness": 0.5,
            "low_freq_power": 0.5,
            "onset_count": 48,
            "duration": 8.0,
        }

        tags = tagger.tag_from_features(features)
        organized = tagger.organize_by_category(tags)

        # Verify tags were generated across categories
        assert len(organized["energy"]) > 0
        assert len(organized["descriptor"]) > 0

    def test_mastering_workflow(self):
        """Test complete mastering workflow"""
        analyzer = MasteringAnalyzer()

        # Create test audio
        sr = 44100
        t = np.arange(2 * sr) / sr
        audio = 0.3 * np.sin(2 * np.pi * 440 * t)

        # Analyze for different platforms
        for platform in ["spotify", "youtube", "apple-music"]:
            analysis = analyzer.analyze(audio, sr, platform)
            assert analysis is not None
            recommendations = analyzer.get_recommendations(analysis)
            assert len(recommendations) > 0


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
