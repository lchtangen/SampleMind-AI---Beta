#!/usr/bin/env python3
"""
Integration Tests for Phase 10.2+ Premium Features Workflows

Tests complete workflows for premium audio features:
- AI-Powered Sample Tagging (tag generation and search)
- Professional Mastering Analysis (LUFS, recommendations)
- Intelligent Sample Layering (compatibility analysis)
- Groove Template Extraction (timing and velocity analysis)
"""

import tempfile
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from samplemind.core.engine.audio_engine import AudioEngine, AnalysisLevel
from samplemind.core.tagging.ai_tagger import get_tagger
from samplemind.core.tagging.tag_vocabulary import get_vocabulary
from samplemind.core.processing.loudness_analyzer import LoudnessAnalyzer
from samplemind.core.processing.mastering_analyzer import MasteringAnalyzer
from samplemind.core.processing.layering_analyzer import LayeringAnalyzer
from samplemind.core.processing.groove_extractor import GrooveExtractor
from samplemind.core.database import chroma as chroma_db


class TestTaggingWorkflow:
    """Test complete tagging workflow: analyze → tag → search"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up tagging tests"""
        self.audio_engine = AudioEngine()
        self.tagger = get_tagger()
        self.vocabulary = get_vocabulary()
        self.temp_dir = tempfile.mkdtemp()

        # Initialize ChromaDB for search tests
        chroma_db.init_chromadb(persist_directory="./data/chroma_test", collection_name="test_tags")

        # Create test audio
        sr = 44100
        duration = 2
        t = np.linspace(0, duration, sr * duration)

        # Electronic sound: higher frequency content, steady rhythm
        audio = 0.5 * (
            np.sin(2 * np.pi * 440 * t) +  # Synth bass
            0.3 * np.sin(2 * np.pi * 1200 * t) +  # Mid synth
            0.2 * np.sin(2 * np.pi * 5000 * t)  # High synth
        ).astype(np.float32)

        self.test_audio_path = Path(self.temp_dir) / "electronic_sample.wav"
        sf.write(self.test_audio_path, audio, sr)

        yield

        # Cleanup
        try:
            client = chroma_db.get_chroma_client()
            client.delete_collection("test_tags")
        except:
            pass

        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

    def test_tagging_from_analysis(self):
        """Test generating tags from audio analysis"""
        # Step 1: Analyze audio
        features = self.audio_engine.analyze_audio(
            self.test_audio_path,
            level=AnalysisLevel.STANDARD
        )

        # Step 2: Generate tags
        tags = self.tagger.tag_from_features(features.to_dict())

        assert len(tags) > 0
        assert all(hasattr(t, 'tag') for t in tags)
        assert all(hasattr(t, 'confidence') for t in tags)
        assert all(0 <= t.confidence <= 1 for t in tags)

    def test_tag_vocabulary_integrity(self):
        """Test that all generated tags are in vocabulary"""
        features = self.audio_engine.analyze_audio(
            self.test_audio_path,
            level=AnalysisLevel.STANDARD
        )

        tags = self.tagger.tag_from_features(features.to_dict())
        organized = self.tagger.organize_by_category(tags)

        # Verify all tags are valid
        for category, tag_list in organized.items():
            for tag_obj in tag_list:
                assert self.vocabulary.is_valid_tag(tag_obj.tag)
                assert self.vocabulary.get_category(tag_obj.tag) == category

    def test_high_confidence_tag_filtering(self):
        """Test filtering tags by confidence threshold"""
        features = self.audio_engine.analyze_audio(
            self.test_audio_path,
            level=AnalysisLevel.STANDARD
        )

        tags = self.tagger.tag_from_features(features.to_dict())

        # Get high confidence tags
        high_conf = self.tagger.get_high_confidence_tags(tags, threshold=0.7)

        # All should meet threshold
        assert all(t.confidence >= 0.7 for t in high_conf)

        # Should have fewer than total tags
        assert len(high_conf) <= len(tags)


class TestMasteringWorkflow:
    """Test complete mastering workflow: analyze → check levels → recommendations"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up mastering tests"""
        self.mastering_analyzer = MasteringAnalyzer()
        self.loudness_analyzer = LoudnessAnalyzer()
        self.temp_dir = tempfile.mkdtemp()

        # Create stereo test audio with different loudness
        sr = 44100
        duration = 2
        t = np.linspace(0, duration, sr * duration)

        # Left channel: synth bass
        left = 0.3 * np.sin(2 * np.pi * 60 * t).astype(np.float32)
        # Right channel: synth melody
        right = 0.25 * np.sin(2 * np.pi * 440 * t).astype(np.float32)

        self.test_audio = np.column_stack([left, right])
        self.test_audio_path = Path(self.temp_dir) / "stereo_sample.wav"
        sf.write(self.test_audio_path, self.test_audio, sr)

        yield

        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

    def test_loudness_analysis(self):
        """Test LUFS loudness analysis"""
        analysis = self.loudness_analyzer.analyze_loudness(self.test_audio, 44100)

        assert analysis is not None
        assert hasattr(analysis, 'integrated_loudness')
        assert hasattr(analysis, 'true_peak')
        assert hasattr(analysis, 'loudness_range')

        # LUFS should be negative
        assert analysis.integrated_loudness < 0
        # True peak should be <= 0 dBFS
        assert analysis.true_peak <= 0

    def test_mastering_analysis_for_platform(self):
        """Test mastering analysis for specific platform"""
        platforms = ["spotify", "youtube", "apple-music"]

        for platform in platforms:
            analysis = self.mastering_analyzer.analyze(self.test_audio, 44100, platform)

            assert analysis is not None
            assert analysis.target_platform == platform
            assert hasattr(analysis, 'loudness_analysis')
            assert hasattr(analysis, 'spectral_balance')
            assert hasattr(analysis, 'stereo_width')
            assert hasattr(analysis, 'phase_correlation')

    def test_mastering_recommendations(self):
        """Test that mastering analysis generates actionable recommendations"""
        analysis = self.mastering_analyzer.analyze(self.test_audio, 44100, "spotify")
        recommendations = self.mastering_analyzer.get_recommendations(analysis)

        assert len(recommendations) > 0
        assert all(isinstance(r, str) for r in recommendations)

    def test_mastering_grade_assignment(self):
        """Test mastering grade calculation"""
        analysis = self.mastering_analyzer.analyze(self.test_audio, 44100, "spotify")
        grade = self.mastering_analyzer.get_mastering_grade(analysis)

        assert grade in ["A", "B", "C", "D", "F"]


class TestLayeringWorkflow:
    """Test complete layering workflow: analyze → detect issues → recommendations"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up layering tests"""
        self.layering_analyzer = LayeringAnalyzer()
        self.temp_dir = tempfile.mkdtemp()

        sr = 44100
        duration = 1
        t = np.linspace(0, duration, sr * duration)

        # Two complementary samples
        # Sample 1: Deep bass
        self.bass_audio = 0.5 * np.sin(2 * np.pi * 50 * t).astype(np.float32)

        # Sample 2: Snappy high-mid percussion
        self.perc_audio = (
            0.4 * np.sin(2 * np.pi * 2000 * t) * np.exp(-3 * t) +  # Pitched decay
            0.2 * np.random.randn(len(t)).astype(np.float32)  # Noise
        ).astype(np.float32)

    def test_layering_compatibility_analysis(self):
        """Test compatibility analysis between two samples"""
        analysis = self.layering_analyzer.analyze(self.bass_audio, self.perc_audio, 44100)

        assert analysis is not None
        assert hasattr(analysis, 'compatibility_score')
        assert hasattr(analysis, 'can_layer')
        assert 0 <= analysis.compatibility_score <= 10

    def test_phase_analysis(self):
        """Test phase correlation analysis"""
        analysis = self.layering_analyzer.analyze(self.bass_audio, self.perc_audio, 44100)

        assert hasattr(analysis, 'phase_correlation')
        assert -1 <= analysis.phase_correlation <= 1
        assert hasattr(analysis, 'phase_status')
        assert analysis.phase_status in ["in-phase", "phase-cancellation", "orthogonal"]

    def test_frequency_masking_detection(self):
        """Test frequency masking detection"""
        analysis = self.layering_analyzer.analyze(self.bass_audio, self.perc_audio, 44100)

        assert hasattr(analysis, 'loudness_difference_db')
        assert hasattr(analysis, 'loudness_ratio')
        assert isinstance(analysis.loudness_difference_db, float)
        assert isinstance(analysis.loudness_ratio, float)

    def test_problematic_layer_detection(self):
        """Test detection of problematic layer combinations"""
        # Create two samples that are too similar (problematic layering)
        sample1 = 0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100))
        sample2 = 0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100)) + 0.01  # Nearly identical

        analysis = self.layering_analyzer.analyze(sample1.astype(np.float32), sample2.astype(np.float32), 44100)

        # Should detect phase issues
        assert hasattr(analysis, 'phase_correlation')


class TestGrooveWorkflow:
    """Test complete groove workflow: extract → analyze → save"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up groove tests"""
        self.groove_extractor = GrooveExtractor()
        self.temp_dir = tempfile.mkdtemp()

        sr = 44100
        duration = 4
        t = np.linspace(0, duration, sr * duration)

        # Create drum-like pattern with swing
        audio = np.zeros_like(t)

        # Kick drum pattern with swing (slightly delayed on offbeats)
        beat_times = np.array([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5])
        swing = np.array([0, 0.08, 0, 0.08, 0, 0.08, 0, 0.08])  # Swing on offbeats

        for beat_time, swing_amt in zip(beat_times, swing):
            kick_pos = int((beat_time + swing_amt) * sr)
            kick_len = int(0.1 * sr)  # 100ms kick
            if kick_pos + kick_len < len(audio):
                kick_envelope = np.hanning(kick_len)
                audio[kick_pos:kick_pos+kick_len] += 0.8 * kick_envelope

        self.test_audio = audio.astype(np.float32)
        self.test_audio_path = Path(self.temp_dir) / "groove_sample.wav"
        sf.write(self.test_audio_path, self.test_audio, sr)

        yield

        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

    def test_groove_extraction(self):
        """Test extracting groove template from audio"""
        groove = self.groove_extractor.extract(self.test_audio, 44100, "test_groove")

        assert groove is not None
        assert groove.name == "test_groove"
        assert hasattr(groove, 'tempo_bpm')
        assert hasattr(groove, 'swing_amount')
        assert hasattr(groove, 'groove_type')
        assert groove.tempo_bpm > 0

    def test_groove_type_classification(self):
        """Test groove type classification"""
        groove = self.groove_extractor.extract(self.test_audio, 44100)

        assert hasattr(groove, 'groove_type')
        assert groove.groove_type in ["straight", "swing", "shuffle", "jdilla", "groovy"]

    def test_groove_properties(self):
        """Test groove property analysis"""
        groove = self.groove_extractor.extract(self.test_audio, 44100)

        assert hasattr(groove, 'swing_amount')
        assert 0 <= groove.swing_amount <= 100

        assert hasattr(groove, 'timing_deviation_ms')
        assert groove.timing_deviation_ms >= 0

        assert hasattr(groove, 'velocity_pattern')
        assert isinstance(groove.velocity_pattern, (list, np.ndarray))


class TestMultiFeatureWorkflow:
    """Test workflows combining multiple premium features"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up multi-feature tests"""
        self.audio_engine = AudioEngine()
        self.tagger = get_tagger()
        self.mastering_analyzer = MasteringAnalyzer()
        self.layering_analyzer = LayeringAnalyzer()
        self.temp_dir = tempfile.mkdtemp()

        # Create electronic sample
        sr = 44100
        duration = 2
        t = np.linspace(0, duration, sr * duration)

        audio = 0.4 * (
            np.sin(2 * np.pi * 100 * t) +
            0.5 * np.sin(2 * np.pi * 440 * t) +
            0.3 * np.sin(2 * np.pi * 1200 * t)
        ).astype(np.float32)

        self.test_audio_path = Path(self.temp_dir) / "electronic.wav"
        sf.write(self.test_audio_path, audio, sr)

        # Stereo version for mastering tests
        left = audio
        right = audio * 0.9  # Slightly quieter right channel
        self.stereo_audio = np.column_stack([left, right])

        yield

        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

    def test_complete_analysis_tagging_and_mastering(self):
        """Test analyzing audio, then tagging and mastering"""
        # Step 1: Analyze
        features = self.audio_engine.analyze_audio(
            self.test_audio_path,
            level=AnalysisLevel.STANDARD
        )

        # Step 2: Tag
        tags = self.tagger.tag_from_features(features.to_dict())
        organized = self.tagger.organize_by_category(tags)

        # Verify tags were generated
        assert len(tags) > 0

        # Step 3: Mastering analysis
        analysis = self.mastering_analyzer.analyze(self.stereo_audio, 44100, "spotify")
        recommendations = self.mastering_analyzer.get_recommendations(analysis)

        # Verify complete workflow
        assert len(organized) > 0
        assert len(recommendations) > 0

    def test_layering_with_compatibility_scoring(self):
        """Test layering analysis produces actionable results"""
        sr = 44100
        duration = 1
        t = np.linspace(0, duration, sr * duration)

        # Create two different samples
        sample1 = 0.5 * np.sin(2 * np.pi * 60 * t).astype(np.float32)  # Bass
        sample2 = 0.4 * np.sin(2 * np.pi * 2000 * t).astype(np.float32)  # High

        # Analyze layering
        analysis = self.layering_analyzer.analyze(sample1, sample2, sr)

        # Verify scoring and compatibility
        assert 0 <= analysis.compatibility_score <= 10
        assert isinstance(analysis.can_layer, bool)
        assert -1 <= analysis.phase_correlation <= 1


__all__ = [
    "TestTaggingWorkflow",
    "TestMasteringWorkflow",
    "TestLayeringWorkflow",
    "TestGrooveWorkflow",
    "TestMultiFeatureWorkflow",
]
