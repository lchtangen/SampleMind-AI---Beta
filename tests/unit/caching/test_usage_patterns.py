"""Unit tests for usage pattern tracking."""

import pytest
import time
from pathlib import Path

from samplemind.core.caching.usage_patterns import (
    UsageEvent,
    UsagePatternTracker,
    TransitionMatrix,
)


class TestUsageEvent:
    """Test UsageEvent dataclass"""

    def test_usage_event_creation(self):
        """Test creating a usage event"""
        event = UsageEvent(
            timestamp=time.time(),
            file_id="audio_123",
            file_name="test.wav",
            feature_type="spectral",
            analysis_level="standard",
            processing_time_ms=45.2,
            cache_hit=True,
            file_size_bytes=1024000,
            duration_seconds=30.5
        )

        assert event.file_id == "audio_123"
        assert event.file_name == "test.wav"
        assert event.cache_hit is True
        assert event.processing_time_ms == 45.2

    def test_usage_event_to_dict(self):
        """Test converting event to dictionary"""
        event = UsageEvent(
            timestamp=time.time(),
            file_id="audio_123",
            file_name="test.wav",
            feature_type="spectral",
            analysis_level="standard",
            processing_time_ms=45.2,
            cache_hit=True
        )

        event_dict = event.to_dict()
        assert event_dict["file_id"] == "audio_123"
        assert event_dict["feature_type"] == "spectral"
        assert isinstance(event_dict, dict)


class TestTransitionMatrix:
    """Test Markov chain transition matrix"""

    def test_matrix_initialization(self):
        """Test transition matrix initialization"""
        matrix = TransitionMatrix()
        assert matrix.total_transitions == 0
        assert len(matrix.transitions) == 0

    def test_add_transition(self):
        """Test adding transitions"""
        matrix = TransitionMatrix()

        matrix.add_transition("state_a", "state_b")
        assert matrix.total_transitions == 1
        assert matrix.transitions["state_a"]["state_b"] == 1

        matrix.add_transition("state_a", "state_b")
        assert matrix.transitions["state_a"]["state_b"] == 2
        assert matrix.total_transitions == 2

    def test_transition_probability(self):
        """Test calculating transition probability"""
        matrix = TransitionMatrix()

        matrix.add_transition("state_a", "state_b")
        matrix.add_transition("state_a", "state_b")
        matrix.add_transition("state_a", "state_c")

        prob_b = matrix.get_transition_probability("state_a", "state_b")
        prob_c = matrix.get_transition_probability("state_a", "state_c")

        assert prob_b == pytest.approx(2.0 / 3.0)
        assert prob_c == pytest.approx(1.0 / 3.0)

    def test_top_n_transitions(self):
        """Test getting top N transitions"""
        matrix = TransitionMatrix()

        # Create transitions with different frequencies
        for _ in range(5):
            matrix.add_transition("start", "target_a")
        for _ in range(3):
            matrix.add_transition("start", "target_b")
        for _ in range(1):
            matrix.add_transition("start", "target_c")

        top_2 = matrix.get_top_n_transitions("start", 2)

        assert len(top_2) == 2
        assert top_2[0][0] == "target_a"  # Highest probability
        assert top_2[1][0] == "target_b"


class TestUsagePatternTracker:
    """Test usage pattern tracker"""

    def test_tracker_initialization(self):
        """Test tracker initialization"""
        tracker = UsagePatternTracker(max_events=100)

        assert len(tracker.events) == 0
        assert tracker.total_hits == 0
        assert tracker.total_misses == 0

    def test_record_event(self):
        """Test recording events"""
        tracker = UsagePatternTracker()

        event = UsageEvent(
            timestamp=time.time(),
            file_id="audio_123",
            file_name="test.wav",
            feature_type="spectral",
            analysis_level="standard",
            processing_time_ms=45.2,
            cache_hit=True
        )

        tracker.record_event(event)

        assert len(tracker.events) == 1
        assert tracker.total_hits == 1
        assert tracker.total_misses == 0

    def test_cache_hit_miss_tracking(self):
        """Test tracking cache hits and misses"""
        tracker = UsagePatternTracker()

        # Record hits
        for i in range(5):
            event = UsageEvent(
                timestamp=time.time(),
                file_id=f"audio_{i}",
                file_name=f"test_{i}.wav",
                feature_type="spectral",
                analysis_level="standard",
                processing_time_ms=10.0 + i,
                cache_hit=True
            )
            tracker.record_event(event)

        # Record misses
        for i in range(3):
            event = UsageEvent(
                timestamp=time.time(),
                file_id=f"audio_{i+10}",
                file_name=f"test_{i+10}.wav",
                feature_type="spectral",
                analysis_level="standard",
                processing_time_ms=20.0 + i,
                cache_hit=False
            )
            tracker.record_event(event)

        assert tracker.total_hits == 5
        assert tracker.total_misses == 3

        stats = tracker.get_stats()
        assert stats["total_requests"] == 8
        assert stats["hit_ratio_percent"] == pytest.approx(62.5)

    def test_state_transitions(self):
        """Test Markov chain state transitions"""
        tracker = UsagePatternTracker()

        # Create sequence of events
        files = ["audio_1", "audio_2", "audio_3"]
        for file_id in files:
            event = UsageEvent(
                timestamp=time.time(),
                file_id=file_id,
                file_name=f"{file_id}.wav",
                feature_type="spectral",
                analysis_level="standard",
                processing_time_ms=10.0,
                cache_hit=True
            )
            tracker.record_event(event)

        # Check transitions were recorded
        matrix_dict = tracker.export_transition_matrix()
        assert matrix_dict["total_transitions"] == 2  # audio_1->audio_2, audio_2->audio_3

    def test_max_events_limit(self):
        """Test that tracker respects max events limit"""
        tracker = UsagePatternTracker(max_events=10)

        # Add more events than limit
        for i in range(20):
            event = UsageEvent(
                timestamp=time.time(),
                file_id=f"audio_{i}",
                file_name=f"test_{i}.wav",
                feature_type="spectral",
                analysis_level="standard",
                processing_time_ms=10.0,
                cache_hit=True
            )
            tracker.record_event(event)

        assert len(tracker.events) == 10

    def test_transition_probabilities(self):
        """Test getting transition probabilities"""
        tracker = UsagePatternTracker()

        # Create specific transition pattern
        files = ["a", "b", "b", "c", "c", "c"]
        for file_id in files:
            event = UsageEvent(
                timestamp=time.time(),
                file_id=file_id,
                file_name=f"{file_id}.wav",
                feature_type="spectral",
                analysis_level="standard",
                processing_time_ms=10.0,
                cache_hit=True
            )
            tracker.record_event(event)

        # Get transition from "a"
        state_a = "a:spectral:standard"
        probs = tracker.get_transition_probabilities(state_a, top_n=5)

        assert len(probs) > 0
        # First transition should be to "b"
        if probs:
            assert "b" in probs[0][0]

    def test_get_stats(self):
        """Test getting tracker statistics"""
        tracker = UsagePatternTracker()

        # Record some events
        for i in range(5):
            event = UsageEvent(
                timestamp=time.time(),
                file_id=f"audio_{i}",
                file_name=f"test_{i}.wav",
                feature_type="spectral",
                analysis_level="standard",
                processing_time_ms=10.0 + i * 5,
                cache_hit=(i % 2 == 0)
            )
            tracker.record_event(event)

        stats = tracker.get_stats()

        assert "total_hits" in stats
        assert "total_misses" in stats
        assert "total_requests" in stats
        assert "hit_ratio_percent" in stats
        assert "avg_processing_time_ms" in stats

    def test_workflow_patterns(self):
        """Test detecting workflow patterns"""
        tracker = UsagePatternTracker()

        # Create repeating workflow pattern
        for iteration in range(3):
            files = ["a", "b", "c"]
            for file_id in files:
                event = UsageEvent(
                    timestamp=time.time(),
                    file_id=file_id,
                    file_name=f"{file_id}.wav",
                    feature_type="spectral",
                    analysis_level="standard",
                    processing_time_ms=10.0,
                    cache_hit=True
                )
                tracker.record_event(event)

        patterns = tracker.get_workflow_patterns(min_frequency=2)

        # Should find some repeating 3-state patterns
        assert len(patterns) > 0

    def test_predict_next_states(self):
        """Test predicting next states"""
        tracker = UsagePatternTracker()

        # Create simple pattern: a -> b -> c
        files = ["a", "b", "c", "a", "b", "c"]
        for file_id in files:
            event = UsageEvent(
                timestamp=time.time(),
                file_id=file_id,
                file_name=f"{file_id}.wav",
                feature_type="spectral",
                analysis_level="standard",
                processing_time_ms=10.0,
                cache_hit=True
            )
            tracker.record_event(event)

        # Predict from state "a"
        state_a = "a:spectral:standard"
        predictions = tracker.predict_next_states(state_a, depth=1)

        assert len(predictions) > 0
        # Next state should be "b"
        if predictions:
            assert predictions[0]["steps_ahead"] == 1

    def test_clear_tracker(self):
        """Test clearing tracker"""
        tracker = UsagePatternTracker()

        # Add some data
        event = UsageEvent(
            timestamp=time.time(),
            file_id="audio_1",
            file_name="test.wav",
            feature_type="spectral",
            analysis_level="standard",
            processing_time_ms=10.0,
            cache_hit=True
        )
        tracker.record_event(event)

        assert len(tracker.events) > 0

        # Clear
        tracker.clear()

        assert len(tracker.events) == 0
        assert tracker.total_hits == 0
        assert tracker.total_misses == 0

    def test_global_instance(self):
        """Test global tracker instance"""
        from samplemind.core.caching.usage_patterns import init_tracker, get_tracker

        # Initialize
        tracker1 = init_tracker()
        assert tracker1 is not None

        # Get same instance
        tracker2 = get_tracker()
        assert tracker1 is tracker2
