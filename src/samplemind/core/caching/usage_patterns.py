"""
Usage Pattern Tracker for workflow analysis.

Tracks file access sequences in real-time and builds transition matrices
for use by the Markov predictor. Stores data in Redis with TTL.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class UsageEvent:
    """Single usage event in workflow"""
    timestamp: float
    file_id: str
    file_name: str
    feature_type: str  # "tempo", "key", "spectral", "forensics", "classification", etc.
    analysis_level: str  # "basic", "standard", "detailed", "professional"
    processing_time_ms: float
    cache_hit: bool
    file_size_bytes: int = 0
    duration_seconds: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class TransitionMatrix:
    """Order-2 Markov chain transition matrix"""
    # state_1 -> state_2 -> count
    transitions: Dict[str, Dict[str, int]] = field(default_factory=lambda: defaultdict(lambda: defaultdict(int)))
    # Total transitions for normalization
    total_transitions: int = 0
    # Last update time
    last_updated: float = field(default_factory=time.time)
    # Time window (30 days in seconds)
    window_seconds: int = 30 * 24 * 3600

    def add_transition(self, state_1: str, state_2: str) -> None:
        """Record a state transition"""
        self.transitions[state_1][state_2] += 1
        self.total_transitions += 1
        self.last_updated = time.time()

    def get_transition_probability(self, state_1: str, state_2: str) -> float:
        """Get probability of transition from state_1 to state_2"""
        if state_1 not in self.transitions:
            return 0.0

        count = self.transitions[state_1].get(state_2, 0)
        total = sum(self.transitions[state_1].values())

        return count / total if total > 0 else 0.0

    def get_top_n_transitions(self, state: str, n: int = 5) -> List[Tuple[str, float]]:
        """Get top n most likely next states from given state"""
        if state not in self.transitions:
            return []

        transitions = self.transitions[state]
        total = sum(transitions.values())

        # Convert to probabilities and sort
        probs = [(next_state, count / total) for next_state, count in transitions.items()]
        probs.sort(key=lambda x: x[1], reverse=True)

        return probs[:n]

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "transitions": {k: dict(v) for k, v in self.transitions.items()},
            "total_transitions": self.total_transitions,
            "last_updated": self.last_updated
        }


class UsagePatternTracker:
    """
    Tracks user workflow patterns in real-time.

    Maintains:
    - Recent events (in-memory, 1000 limit)
    - Transition matrix (2D matrix of state transitions)
    - Statistics (hit/miss ratio, processing times)
    """

    def __init__(self, max_events: int = 1000, redis_cache=None):
        """
        Initialize tracker.

        Args:
            max_events: Maximum events to keep in memory
            redis_cache: Optional RedisCache instance for persistence
        """
        self.max_events = max_events
        self.redis_cache = redis_cache

        # In-memory state
        self.events: List[UsageEvent] = []
        self.transition_matrix = TransitionMatrix()

        # Statistics
        self.total_hits = 0
        self.total_misses = 0
        self.processing_times: List[float] = []

        # Current state tracking
        self._last_state: Optional[str] = None
        self._state_history: List[str] = []

        logger.info("Usage pattern tracker initialized")

    def _make_state(self, event: UsageEvent) -> str:
        """Create state string from event"""
        return f"{event.file_id}:{event.feature_type}:{event.analysis_level}"

    def record_event(self, event: UsageEvent) -> None:
        """
        Record a usage event.

        Args:
            event: UsageEvent to record
        """
        # Limit events in memory
        if len(self.events) >= self.max_events:
            self.events.pop(0)

        self.events.append(event)

        # Update statistics
        if event.cache_hit:
            self.total_hits += 1
        else:
            self.total_misses += 1
        self.processing_times.append(event.processing_time_ms)

        # Update state tracking for Markov chain
        current_state = self._make_state(event)

        if self._last_state is not None:
            # Record transition from last state to current
            self.transition_matrix.add_transition(self._last_state, current_state)
            self._state_history.append(current_state)

            # Keep state history limited
            if len(self._state_history) > 1000:
                self._state_history.pop(0)

        self._last_state = current_state

        # Persist to Redis if available
        if self.redis_cache:
            asyncio.create_task(self._persist_to_redis(event))

    async def _persist_to_redis(self, event: UsageEvent) -> None:
        """Persist event to Redis (async)"""
        try:
            key = f"usage:event:{event.timestamp}:{event.file_id}"
            ttl = 30 * 24 * 3600  # 30 days
            await self.redis_cache.set(key, event.to_dict(), ttl=ttl)
        except Exception as e:
            logger.error(f"Failed to persist event to Redis: {e}")

    def get_stats(self) -> Dict:
        """Get current statistics"""
        total_requests = self.total_hits + self.total_misses
        hit_ratio = (self.total_hits / total_requests * 100) if total_requests > 0 else 0

        avg_processing_time = (
            sum(self.processing_times) / len(self.processing_times)
            if self.processing_times else 0
        )

        return {
            "total_hits": self.total_hits,
            "total_misses": self.total_misses,
            "total_requests": total_requests,
            "hit_ratio_percent": round(hit_ratio, 2),
            "avg_processing_time_ms": round(avg_processing_time, 2),
            "recent_events": len(self.events),
            "transition_matrix_size": len(self.transition_matrix.transitions),
            "state_history_length": len(self._state_history)
        }

    def get_recent_events(self, limit: int = 10) -> List[UsageEvent]:
        """Get most recent events"""
        return self.events[-limit:]

    def get_transition_probabilities(self, state: str, top_n: int = 5) -> List[Tuple[str, float]]:
        """
        Get most likely next states from given state.

        Args:
            state: Current state
            top_n: Number of top predictions to return

        Returns:
            List of (state, probability) tuples sorted by probability
        """
        return self.transition_matrix.get_top_n_transitions(state, top_n)

    def export_transition_matrix(self) -> Dict:
        """Export transition matrix for inspection"""
        return self.transition_matrix.to_dict()

    def clear(self) -> None:
        """Clear all tracked data"""
        self.events.clear()
        self.transition_matrix = TransitionMatrix()
        self.total_hits = 0
        self.total_misses = 0
        self.processing_times.clear()
        self._last_state = None
        self._state_history.clear()
        logger.info("Usage pattern tracker cleared")

    def get_workflow_patterns(self, min_frequency: int = 2) -> List[Tuple[List[str], int]]:
        """
        Get common workflow patterns (sequences of states).

        Args:
            min_frequency: Minimum occurrences to include

        Returns:
            List of (pattern, count) tuples sorted by frequency
        """
        patterns: Dict[Tuple[str, ...], int] = defaultdict(int)

        # Look for 3-state sequences
        for i in range(len(self._state_history) - 2):
            pattern = (
                self._state_history[i],
                self._state_history[i + 1],
                self._state_history[i + 2]
            )
            patterns[pattern] += 1

        # Filter by minimum frequency
        common_patterns = [
            (list(pattern), count)
            for pattern, count in patterns.items()
            if count >= min_frequency
        ]

        # Sort by frequency
        common_patterns.sort(key=lambda x: x[1], reverse=True)

        return common_patterns

    def predict_next_states(self, current_state: str, depth: int = 3) -> List[Dict]:
        """
        Predict next states using Markov chain.

        Args:
            current_state: Current state
            depth: Number of steps to predict ahead

        Returns:
            List of prediction dictionaries with state and probability
        """
        predictions = []

        # Get immediate next states
        next_states = self.get_transition_probabilities(current_state, top_n=5)

        for next_state, probability in next_states:
            predictions.append({
                "state": next_state,
                "probability": round(probability, 3),
                "steps_ahead": 1
            })

            # Optional: predict further ahead (can be expensive)
            if depth > 1:
                second_order = self.get_transition_probabilities(next_state, top_n=2)
                for next_next_state, next_prob in second_order:
                    predictions.append({
                        "state": next_next_state,
                        "probability": round(probability * next_prob, 3),
                        "steps_ahead": 2
                    })

        # Sort by probability
        predictions.sort(key=lambda x: x["probability"], reverse=True)

        return predictions


# Global instance
_tracker_instance: Optional[UsagePatternTracker] = None


def init_tracker(redis_cache=None) -> UsagePatternTracker:
    """Initialize global tracker instance"""
    global _tracker_instance
    _tracker_instance = UsagePatternTracker(redis_cache=redis_cache)
    return _tracker_instance


def get_tracker() -> UsagePatternTracker:
    """Get global tracker instance"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = UsagePatternTracker()
    return _tracker_instance
