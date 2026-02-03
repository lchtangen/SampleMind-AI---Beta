"""
Markov Chain Predictor for predictive caching.

Uses Order-2 Markov chains to predict the next file/features
user will need, enabling preemptive cache warming.
"""

import asyncio
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class Prediction:
    """Single cache prediction"""
    file_id: str
    file_name: str
    feature_type: str
    analysis_level: str
    confidence: float  # 0.0 - 1.0
    priority: int  # 1 = highest
    steps_ahead: int  # How many steps in the future
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "file_id": self.file_id,
            "file_name": self.file_name,
            "feature_type": self.feature_type,
            "analysis_level": self.analysis_level,
            "confidence": self.confidence,
            "priority": self.priority,
            "steps_ahead": self.steps_ahead,
            "timestamp": self.timestamp
        }


@dataclass
class PredictionResult:
    """Result of a prediction cycle"""
    timestamp: float
    current_state: str
    predictions: List[Prediction] = field(default_factory=list)
    accuracy: float = 0.0  # Accuracy of recent predictions
    model_updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "timestamp": self.timestamp,
            "current_state": self.current_state,
            "predictions": [p.to_dict() for p in self.predictions],
            "accuracy": self.accuracy,
            "model_updated_at": self.model_updated_at
        }


class MarkovPredictor:
    """
    Markov chain-based predictor for file access patterns.

    Predicts which files/features the user will access next based on
    historical transition patterns.
    """

    def __init__(self, usage_tracker=None, confidence_threshold: float = 0.60) -> None:
        """
        Initialize predictor.

        Args:
            usage_tracker: UsagePatternTracker instance
            confidence_threshold: Minimum confidence to include prediction (0.0-1.0)
        """
        self.usage_tracker = usage_tracker
        self.confidence_threshold = confidence_threshold

        # Prediction history for accuracy tracking
        self.prediction_history: List[Dict] = []
        self.correct_predictions = 0
        self.total_predictions = 0

        # File metadata cache
        self.file_metadata: Dict[str, Dict] = {}

        logger.info(f"Markov predictor initialized (threshold={confidence_threshold})")

    def set_usage_tracker(self, tracker) -> None:
        """Set or update the usage tracker"""
        self.usage_tracker = tracker
        logger.info("Usage tracker attached to predictor")

    def register_file(self, file_id: str, file_name: str, file_size: int, duration: float) -> None:
        """
        Register file metadata for predictions.

        Args:
            file_id: Unique file identifier
            file_name: Human-readable file name
            file_size: File size in bytes
            duration: Audio duration in seconds
        """
        self.file_metadata[file_id] = {
            "file_name": file_name,
            "file_size": file_size,
            "duration": duration
        }

    def predict_next(self, current_state: str, top_n: int = 5) -> List[Prediction]:
        """
        Predict next states the user will access.

        Args:
            current_state: Current state (file_id:feature_type:analysis_level)
            top_n: Number of predictions to return

        Returns:
            List of Prediction objects sorted by confidence
        """
        if self.usage_tracker is None:
            logger.warning("No usage tracker available for prediction")
            return []

        # Get transition probabilities from tracker
        transitions = self.usage_tracker.get_transition_probabilities(
            current_state, top_n=top_n
        )

        predictions = []

        for i, (next_state, probability) in enumerate(transitions):
            # Filter by confidence threshold
            if probability < self.confidence_threshold:
                continue

            # Parse state
            try:
                file_id, feature_type, analysis_level = next_state.split(":")
            except ValueError:
                logger.warning(f"Invalid state format: {next_state}")
                continue

            # Get file metadata
            metadata = self.file_metadata.get(file_id, {})
            file_name = metadata.get("file_name", file_id)

            # Create prediction
            prediction = Prediction(
                file_id=file_id,
                file_name=file_name,
                feature_type=feature_type,
                analysis_level=analysis_level,
                confidence=round(probability, 3),
                priority=i + 1,
                steps_ahead=1
            )

            predictions.append(prediction)

        return predictions

    def predict_with_lookahead(
        self,
        current_state: str,
        lookahead_depth: int = 2,
        top_n: int = 5
    ) -> List[Prediction]:
        """
        Predict with multiple lookahead steps.

        Combines predictions from multiple steps ahead, weighted by depth.

        Args:
            current_state: Current state
            lookahead_depth: Number of steps to predict ahead
            top_n: Top predictions at each level

        Returns:
            Merged list of predictions weighted by depth
        """
        all_predictions: Dict[str, Prediction] = {}

        for depth in range(1, lookahead_depth + 1):
            # Get predictions at this depth
            current = current_state

            for _ in range(depth):
                predictions = self.predict_next(current, top_n=top_n)
                if not predictions:
                    break

                for pred in predictions:
                    # Calculate depth-weighted confidence
                    depth_weight = 1.0 / (1.0 + (depth - 1) * 0.3)  # Decay with depth
                    weighted_confidence = pred.confidence * depth_weight

                    state_key = f"{pred.file_id}:{pred.feature_type}:{pred.analysis_level}"

                    if state_key in all_predictions:
                        # Accumulate confidence
                        existing = all_predictions[state_key]
                        existing.confidence = min(
                            1.0,
                            existing.confidence + weighted_confidence
                        )
                    else:
                        pred.confidence = weighted_confidence
                        pred.steps_ahead = depth
                        all_predictions[state_key] = pred

                # Continue with top prediction for next level
                current = predictions[0].file_id

        # Sort by confidence and return
        sorted_predictions = sorted(
            all_predictions.values(),
            key=lambda p: p.confidence,
            reverse=True
        )

        return sorted_predictions[:top_n]

    def evaluate_prediction(self, prediction: Prediction, was_correct: bool) -> None:
        """
        Record prediction accuracy for model improvement.

        Args:
            prediction: Original prediction
            was_correct: Whether the prediction was correct
        """
        self.prediction_history.append({
            "prediction": prediction.to_dict(),
            "was_correct": was_correct,
            "timestamp": time.time()
        })

        self.total_predictions += 1
        if was_correct:
            self.correct_predictions += 1

        # Keep history limited
        if len(self.prediction_history) > 1000:
            self.prediction_history.pop(0)

    def get_accuracy(self) -> float:
        """Get prediction accuracy (0.0 - 1.0)"""
        if self.total_predictions == 0:
            return 0.0

        return self.correct_predictions / self.total_predictions

    def get_recent_accuracy(self, window: int = 100) -> float:
        """Get accuracy for recent predictions"""
        if len(self.prediction_history) < window:
            window = len(self.prediction_history)

        if window == 0:
            return 0.0

        recent = self.prediction_history[-window:]
        correct = sum(1 for p in recent if p["was_correct"])

        return correct / window

    def get_stats(self) -> Dict:
        """Get predictor statistics"""
        return {
            "total_predictions": self.total_predictions,
            "correct_predictions": self.correct_predictions,
            "overall_accuracy": round(self.get_accuracy(), 3),
            "recent_accuracy": round(self.get_recent_accuracy(), 3),
            "confidence_threshold": self.confidence_threshold,
            "registered_files": len(self.file_metadata),
            "prediction_history_size": len(self.prediction_history)
        }

    def update_confidence_threshold(self, threshold: float) -> None:
        """
        Dynamically update confidence threshold.

        Higher threshold = fewer but more confident predictions.

        Args:
            threshold: Confidence threshold (0.0 - 1.0)
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"Threshold must be 0.0-1.0, got {threshold}")

        self.confidence_threshold = threshold
        logger.info(f"Confidence threshold updated to {threshold}")

    def adaptive_threshold(self) -> None:
        """
        Automatically adjust confidence threshold based on accuracy.

        - If accuracy > 80%: lower threshold (be more aggressive)
        - If accuracy < 60%: raise threshold (be more conservative)
        """
        accuracy = self.get_recent_accuracy()

        if accuracy > 0.80 and self.confidence_threshold > 0.40:
            self.confidence_threshold = max(0.40, self.confidence_threshold - 0.05)
            logger.info(f"Lowered threshold to {self.confidence_threshold:.2f} (high accuracy)")

        elif accuracy < 0.60 and self.confidence_threshold < 0.80:
            self.confidence_threshold = min(0.80, self.confidence_threshold + 0.05)
            logger.info(f"Raised threshold to {self.confidence_threshold:.2f} (low accuracy)")

    def reset_stats(self) -> None:
        """Reset prediction statistics"""
        self.correct_predictions = 0
        self.total_predictions = 0
        self.prediction_history.clear()
        logger.info("Predictor statistics reset")

    def export_model(self) -> Dict:
        """Export model state for inspection or persistence"""
        return {
            "stats": self.get_stats(),
            "confidence_threshold": self.confidence_threshold,
            "file_metadata": self.file_metadata,
            "recent_accuracy": self.get_recent_accuracy(),
            "prediction_history_sample": self.prediction_history[-10:] if self.prediction_history else []
        }


# Global instance
_predictor_instance: Optional[MarkovPredictor] = None


def init_predictor(usage_tracker=None, **kwargs) -> MarkovPredictor:
    """Initialize global predictor instance"""
    global _predictor_instance
    _predictor_instance = MarkovPredictor(usage_tracker, **kwargs)
    return _predictor_instance


def get_predictor() -> MarkovPredictor:
    """Get global predictor instance"""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = MarkovPredictor()
    return _predictor_instance
