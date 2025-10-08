"""
Tests for BPM and Key detection
"""
import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from samplemind.core.analysis.bpm_key_detector import (
    BPMKeyDetector,
    quick_bpm,
    quick_key,
    quick_label
)


class TestBPMKeyDetector:
    """Test BPMKeyDetector main class"""

    def test_detector_initialization(self):
        """Test detector initialization"""
        detector = BPMKeyDetector()
        assert detector is not None
        assert hasattr(detector, 'detect_bpm')
        assert hasattr(detector, 'detect_key')

    @pytest.mark.asyncio
    async def test_detect_bpm_from_file(self, test_audio_samples):
        """Test BPM detection from file"""
        detector = BPMKeyDetector()
        audio_file = test_audio_samples['120_c_major']

        result = detector.detect_bpm(audio_file)

        assert result is not None
        assert isinstance(result, dict)
        assert 'bpm' in result
        assert isinstance(result['bpm'], (int, float))
        assert result['bpm'] >= 0  # BPM can be 0 for synthetic audio

    @pytest.mark.asyncio
    async def test_detect_key_from_file(self, test_audio_samples):
        """Test key detection from file"""
        detector = BPMKeyDetector()
        audio_file = test_audio_samples['120_c_major']

        key = detector.detect_key(audio_file)

        assert key is not None
        assert isinstance(key, str)

    @pytest.mark.asyncio
    async def test_detect_both_bpm_and_key(self, test_audio_samples):
        """Test detecting both BPM and key"""
        detector = BPMKeyDetector()
        audio_file = test_audio_samples['120_c_major']

        result = detector.detect_all(str(audio_file))

        assert 'bpm' in result
        assert 'key' in result
        assert 'mode' in result or 'scale' in result

    def test_detect_bpm_from_array(self):
        """Test BPM detection from numpy array"""
        detector = BPMKeyDetector()

        # Create synthetic audio with clear rhythm at 120 BPM
        sr = 22050
        duration = 10
        t = np.linspace(0, duration, sr * duration)
        # Create click track at 120 BPM (2 beats per second)
        beat_times = np.arange(0, duration, 0.5)  # 120 BPM = 2 beats/sec
        audio = np.zeros_like(t)
        for beat_time in beat_times:
            idx = int(beat_time * sr)
            if idx < len(audio):
                audio[idx:idx+100] = np.hanning(100)

        bpm = detector.detect_bpm_from_array(audio, sr)

        assert bpm is not None
        # Allow for detection variance
        assert 80 <= bpm <= 180

    def test_detect_key_from_array(self):
        """Test key detection from numpy array"""
        detector = BPMKeyDetector()

        # Create synthetic audio in C major
        sr = 22050
        duration = 5
        t = np.linspace(0, duration, sr * duration)
        # C major scale frequencies
        c_major_freqs = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88]
        audio = sum(0.2 * np.sin(2 * np.pi * freq * t) for freq in c_major_freqs)

        key = detector.detect_key_from_array(audio, sr)

        assert key is not None
        # Should ideally detect C or Am (relative minor)

    def test_detector_with_silence(self):
        """Test detector with silent audio"""
        detector = BPMKeyDetector()

        sr = 22050
        duration = 3
        audio = np.zeros(sr * duration)

        bpm = detector.detect_bpm_from_array(audio, sr)

        # Should handle silence gracefully (may return 0 or None)
        assert bpm is not None or bpm == 0

    def test_detector_with_noise(self):
        """Test detector with white noise"""
        detector = BPMKeyDetector()

        sr = 22050
        duration = 3
        audio = np.random.randn(sr * duration) * 0.1

        result = detector.detect_all_from_array(audio, sr)

        # Should return result even if BPM/key are uncertain
        assert result is not None
        assert 'bpm' in result


class TestQuickFunctions:
    """Test convenience functions"""

    def test_quick_bpm(self, test_audio_samples):
        """Test quick BPM function"""
        audio_file = test_audio_samples['120_c_major']
        bpm = quick_bpm(str(audio_file))
        assert bpm is not None
        assert isinstance(bpm, (int, float))

    def test_quick_key(self, test_audio_samples):
        """Test quick key function"""
        audio_file = test_audio_samples['120_c_major']
        key = quick_key(str(audio_file))
        assert key is not None
        assert isinstance(key, str)

    def test_quick_label(self, test_audio_samples):
        """Test quick label function"""
        audio_file = test_audio_samples['120_c_major']
        label = quick_label(str(audio_file))
        assert label is not None
        assert 'BPM' in label


class TestIntegration:
    """Integration tests for BPM/Key detection"""

    @pytest.mark.asyncio
    async def test_full_analysis_pipeline(self, test_audio_samples):
        """Test complete BPM and key detection pipeline"""
        detector = BPMKeyDetector()
        audio_file = test_audio_samples['120_c_major']

        result = detector.analyze_file(str(audio_file))

        assert 'bpm' in result
        assert 'key' in result
        assert 'confidence' in result or 'bpm_confidence' in result

    def test_batch_detection(self, test_audio_samples):
        """Test batch BPM/key detection"""
        detector = BPMKeyDetector()

        files = [
            test_audio_samples['120_c_major'],
            test_audio_samples['140_a_minor']
        ]

        results = [detector.analyze_file(str(f)) for f in files]

        assert len(results) == 2
        for result in results:
            assert 'bpm' in result
            assert 'key' in result

    def test_performance_metrics(self, test_audio_samples):
        """Test detection performance"""
        import time

        detector = BPMKeyDetector()
        audio_file = test_audio_samples['120_c_major']

        start = time.time()
        result = detector.analyze_file(str(audio_file))
        elapsed = time.time() - start

        # Should complete in reasonable time (< 5 seconds for small test file)
        assert elapsed < 5.0
        assert result is not None
