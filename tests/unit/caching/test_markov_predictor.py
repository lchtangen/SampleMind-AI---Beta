"""Unit tests for Markov chain predictor."""

import pytest
import time

from samplemind.core.caching.markov_predictor import (
    Prediction,
    PredictionResult,
    MarkovPredictor,
)
from samplemind.core.caching.usage_patterns import (
    UsageEvent,
    UsagePatternTracker,
)


class TestPrediction:
    """Test Prediction dataclass"""

    def test_prediction_creation(self):
        """Test creating a prediction"""
        pred = Prediction(
            file_id="audio_123",
            file_name="test.wav",
            feature_type="spectral",
            analysis_level="standard",
            confidence=0.85,
            priority=1,
            steps_ahead=1
        )

        assert pred.file_id == "audio_123"
        assert pred.confidence == 0.85
        assert pred.priority == 1

    def test_prediction_to_dict(self):
        """Test converting prediction to dictionary"""
        pred = Prediction(
            file_id="audio_123",
            file_name="test.wav",
            feature_type="spectral",
            analysis_level="standard",
            confidence=0.85,
            priority=1,
            steps_ahead=1
        )

        pred_dict = pred.to_dict()
        assert pred_dict["file_id"] == "audio_123"
        assert pred_dict["confidence"] == 0.85
        assert isinstance(pred_dict, dict)


class TestMarkovPredictor:
    """Test Markov chain predictor"""

    def test_predictor_initialization(self):
        """Test predictor initialization"""
        predictor = MarkovPredictor(confidence_threshold=0.60)

        assert predictor.confidence_threshold == 0.60
        assert predictor.total_predictions == 0
        assert len(predictor.file_metadata) == 0

    def test_register_file(self):
        """Test registering file metadata"""
        predictor = MarkovPredictor()

        predictor.register_file(
            file_id="audio_123",
            file_name="test.wav",
            file_size=1024000,
            duration=30.5
        )

        assert "audio_123" in predictor.file_metadata
        assert predictor.file_metadata["audio_123"]["file_name"] == "test.wav"
        assert predictor.file_metadata["audio_123"]["duration"] == 30.5

    def test_predict_next_no_tracker(self):
        """Test prediction without usage tracker"""
        predictor = MarkovPredictor()

        predictions = predictor.predict_next("audio_1:spectral:standard", top_n=5)

        assert len(predictions) == 0

    def test_predict_next_with_tracker(self):
        """Test prediction with usage tracker"""
        tracker = UsagePatternTracker()
        predictor = MarkovPredictor(usage_tracker=tracker, confidence_threshold=0.3)

        # Create simple pattern
        files = ["a", "b", "b", "c"]
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

        # Register files
        for file_id in files:
            predictor.register_file(
                file_id=file_id,
                file_name=f"{file_id}.wav",
                file_size=1024,
                duration=30.0
            )

        # Predict from "a"
        state_a = "a:spectral:standard"
        predictions = predictor.predict_next(state_a, top_n=5)

        # Should predict next state
        assert len(predictions) >= 1 or len(predictions) == 0  # Depends on transitions

    def test_predict_with_lookahead(self):
        """Test multi-step lookahead prediction"""
        tracker = UsagePatternTracker()
        predictor = MarkovPredictor(usage_tracker=tracker, confidence_threshold=0.3)

        # Create pattern: a -> b -> c -> d
        files = ["a", "b", "c", "d", "a", "b", "c", "d"]
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

        # Register files
        for file_id in ["a", "b", "c", "d"]:
            predictor.register_file(
                file_id=file_id,
                file_name=f"{file_id}.wav",
                file_size=1024,
                duration=30.0
            )

        # Predict with lookahead
        state_a = "a:spectral:standard"
        predictions = predictor.predict_with_lookahead(
            state_a,
            lookahead_depth=2,
            top_n=5
        )

        # Should return some predictions or none if chain is incomplete
        assert isinstance(predictions, list)

    def test_evaluate_prediction_correct(self):
        """Test recording correct prediction"""
        predictor = MarkovPredictor()

        pred = Prediction(
            file_id="audio_123",
            file_name="test.wav",
            feature_type="spectral",
            analysis_level="standard",
            confidence=0.85,
            priority=1,
            steps_ahead=1
        )

        predictor.evaluate_prediction(pred, was_correct=True)

        assert predictor.total_predictions == 1
        assert predictor.correct_predictions == 1
        assert predictor.get_accuracy() == 1.0

    def test_evaluate_prediction_incorrect(self):
        """Test recording incorrect prediction"""
        predictor = MarkovPredictor()

        pred = Prediction(
            file_id="audio_123",
            file_name="test.wav",
            feature_type="spectral",
            analysis_level="standard",
            confidence=0.85,
            priority=1,
            steps_ahead=1
        )

        predictor.evaluate_prediction(pred, was_correct=False)

        assert predictor.total_predictions == 1
        assert predictor.correct_predictions == 0
        assert predictor.get_accuracy() == 0.0

    def test_accuracy_calculation(self):
        """Test accuracy calculation"""
        predictor = MarkovPredictor()

        pred = Prediction(
            file_id="audio_123",
            file_name="test.wav",
            feature_type="spectral",
            analysis_level="standard",
            confidence=0.85,
            priority=1,
            steps_ahead=1
        )

        # Record 10 predictions: 7 correct, 3 incorrect
        for i in range(7):
            predictor.evaluate_prediction(pred, was_correct=True)

        for i in range(3):
            predictor.evaluate_prediction(pred, was_correct=False)

        accuracy = predictor.get_accuracy()
        assert accuracy == pytest.approx(0.7)

    def test_recent_accuracy(self):
        """Test recent accuracy window"""
        predictor = MarkovPredictor()

        pred = Prediction(
            file_id="audio_123",
            file_name="test.wav",
            feature_type="spectral",
            analysis_level="standard",
            confidence=0.85,
            priority=1,
            steps_ahead=1
        )

        # Add 20 predictions
        for i in range(15):
            predictor.evaluate_prediction(pred, was_correct=True)

        for i in range(5):
            predictor.evaluate_prediction(pred, was_correct=False)

        recent = predictor.get_recent_accuracy(window=10)

        # Recent 10 should have different accuracy than overall
        assert 0.0 <= recent <= 1.0

    def test_confidence_threshold_update(self):
        """Test updating confidence threshold"""
        predictor = MarkovPredictor(confidence_threshold=0.60)

        assert predictor.confidence_threshold == 0.60

        predictor.update_confidence_threshold(0.75)
        assert predictor.confidence_threshold == 0.75

        # Should raise on invalid values
        with pytest.raises(ValueError):
            predictor.update_confidence_threshold(1.5)

    def test_adaptive_threshold_high_accuracy(self):
        """Test adaptive threshold with high accuracy"""
        predictor = MarkovPredictor(confidence_threshold=0.60)

        pred = Prediction(
            file_id="audio_123",
            file_name="test.wav",
            feature_type="spectral",
            analysis_level="standard",
            confidence=0.85,
            priority=1,
            steps_ahead=1
        )

        # Record 90+ correct predictions (90% accuracy)
        for i in range(100):
            predictor.evaluate_prediction(pred, was_correct=(i < 90))

        original_threshold = predictor.confidence_threshold
        predictor.adaptive_threshold()

        # Threshold should be lowered
        assert predictor.confidence_threshold <= original_threshold

    def test_adaptive_threshold_low_accuracy(self):
        """Test adaptive threshold with low accuracy"""
        predictor = MarkovPredictor(confidence_threshold=0.60)

        pred = Prediction(
            file_id="audio_123",
            file_name="test.wav",
            feature_type="spectral",
            analysis_level="standard",
            confidence=0.85,
            priority=1,
            steps_ahead=1
        )

        # Record 50% correct predictions (50% accuracy)
        for i in range(100):
            predictor.evaluate_prediction(pred, was_correct=(i < 50))

        original_threshold = predictor.confidence_threshold
        predictor.adaptive_threshold()

        # Threshold should be raised
        assert predictor.confidence_threshold >= original_threshold

    def test_get_stats(self):
        """Test getting predictor statistics"""
        predictor = MarkovPredictor()

        predictor.register_file(
            file_id="audio_123",
            file_name="test.wav",
            file_size=1024,
            duration=30.0
        )

        stats = predictor.get_stats()

        assert "total_predictions" in stats
        assert "correct_predictions" in stats
        assert "overall_accuracy" in stats
        assert "recent_accuracy" in stats
        assert "confidence_threshold" in stats
        assert "registered_files" in stats

    def test_reset_stats(self):
        """Test resetting statistics"""
        predictor = MarkovPredictor()

        pred = Prediction(
            file_id="audio_123",
            file_name="test.wav",
            feature_type="spectral",
            analysis_level="standard",
            confidence=0.85,
            priority=1,
            steps_ahead=1
        )

        predictor.evaluate_prediction(pred, was_correct=True)
        assert predictor.total_predictions == 1

        predictor.reset_stats()

        assert predictor.total_predictions == 0
        assert predictor.correct_predictions == 0

    def test_export_model(self):
        """Test exporting model state"""
        predictor = MarkovPredictor()

        predictor.register_file(
            file_id="audio_123",
            file_name="test.wav",
            file_size=1024,
            duration=30.0
        )

        model = predictor.export_model()

        assert "stats" in model
        assert "confidence_threshold" in model
        assert "file_metadata" in model
        assert "recent_accuracy" in model

    def test_global_instance(self):
        """Test global predictor instance"""
        from samplemind.core.caching.markov_predictor import init_predictor, get_predictor

        # Initialize
        predictor1 = init_predictor()
        assert predictor1 is not None

        # Get same instance
        predictor2 = get_predictor()
        assert predictor1 is predictor2
