#!/usr/bin/env python3
"""
PostHog Analytics Integration for SampleMind AI
Tracks user events, features usage, and performance metrics
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Standard event types for analytics tracking"""

    # Upload events
    AUDIO_UPLOADED = "audio_uploaded"
    BATCH_UPLOAD_STARTED = "batch_upload_started"
    BATCH_UPLOAD_COMPLETED = "batch_upload_completed"

    # Analysis events
    ANALYSIS_STARTED = "analysis_started"
    ANALYSIS_COMPLETED = "analysis_completed"
    ANALYSIS_FAILED = "analysis_failed"

    # Search events
    SIMILAR_SAMPLES_FOUND = "similar_samples_found"
    SEMANTIC_SEARCH_PERFORMED = "semantic_search_performed"
    LIBRARY_SEARCH_PERFORMED = "library_search_performed"

    # Feature events
    EFFECT_APPLIED = "effect_applied"
    MIDI_GENERATED = "midi_generated"
    COMMAND_PALETTE_OPENED = "command_palette_opened"
    ONBOARDING_COMPLETED = "onboarding_completed"

    # User events
    FEEDBACK_SUBMITTED = "feedback_submitted"
    FILE_DOWNLOADED = "file_downloaded"
    RESULTS_EXPORTED = "results_exported"


class PostHogAnalytics:
    """PostHog analytics client for tracking events and metrics"""

    def __init__(self, api_key: Optional[str] = None, host: Optional[str] = None):
        """Initialize PostHog analytics client"""
        self.enabled = False
        self.api_key = api_key or os.getenv("POSTHOG_API_KEY", "")
        self.host = host or os.getenv("POSTHOG_HOST", "https://app.posthog.com")
        self.client = None

        if self.api_key:
            try:
                import posthog
                posthog.api_key = self.api_key
                posthog.host = self.host
                posthog.disabled = False
                self.client = posthog
                self.enabled = True
                logger.info(f"✓ PostHog analytics enabled ({self.host})")
            except ImportError:
                logger.warning("posthog package not installed. Install with: pip install posthog")
                self.enabled = False
        else:
            logger.warning("PostHog API key not configured. Analytics disabled.")
            self.enabled = False

    def capture(
        self,
        event_name: str,
        user_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        """Capture an event with optional properties"""
        if not self.enabled or not self.client:
            return

        try:
            event_properties = properties or {}
            event_properties.update(kwargs)
            event_properties["timestamp"] = datetime.utcnow().isoformat()

            if user_id:
                self.client.capture(
                    distinct_id=user_id,
                    event=event_name,
                    properties=event_properties
                )
            else:
                # For anonymous events
                self.client.capture(
                    distinct_id="anonymous",
                    event=event_name,
                    properties=event_properties
                )
        except Exception as e:
            logger.debug(f"Error capturing event '{event_name}': {e}")

    def identify_user(self, user_id: str, properties: Optional[Dict[str, Any]] = None) -> None:
        """Identify a user and set their properties"""
        if not self.enabled or not self.client:
            return

        try:
            user_properties = properties or {}
            self.client.identify(
                distinct_id=user_id,
                properties=user_properties
            )
        except Exception as e:
            logger.debug(f"Error identifying user '{user_id}': {e}")

    def track_audio_upload(
        self,
        user_id: Optional[str],
        file_size: int,
        duration_seconds: float,
        format: str,
        **kwargs
    ) -> None:
        """Track audio file upload"""
        self.capture(
            EventType.AUDIO_UPLOADED.value,
            user_id=user_id,
            file_size=file_size,
            duration_seconds=duration_seconds,
            format=format,
            **kwargs
        )

    def track_batch_upload(
        self,
        user_id: Optional[str],
        file_count: int,
        total_size: int,
        **kwargs
    ) -> None:
        """Track batch upload start"""
        self.capture(
            EventType.BATCH_UPLOAD_STARTED.value,
            user_id=user_id,
            file_count=file_count,
            total_size=total_size,
            **kwargs
        )

    def track_analysis(
        self,
        user_id: Optional[str],
        analysis_level: str,
        duration_ms: float,
        file_size: int,
        success: bool = True,
        error: Optional[str] = None,
        **kwargs
    ) -> None:
        """Track audio analysis"""
        event_name = (
            EventType.ANALYSIS_COMPLETED.value
            if success
            else EventType.ANALYSIS_FAILED.value
        )

        properties = {
            "analysis_level": analysis_level,
            "duration_ms": duration_ms,
            "file_size": file_size,
        }

        if error:
            properties["error"] = error

        self.capture(
            event_name,
            user_id=user_id,
            properties={**properties, **kwargs}
        )

    def track_search(
        self,
        user_id: Optional[str],
        search_type: str,  # 'semantic', 'library', 'similar'
        result_count: int,
        query_time_ms: float,
        **kwargs
    ) -> None:
        """Track search operation"""
        event_map = {
            "semantic": EventType.SEMANTIC_SEARCH_PERFORMED.value,
            "library": EventType.LIBRARY_SEARCH_PERFORMED.value,
            "similar": EventType.SIMILAR_SAMPLES_FOUND.value,
        }

        event_name = event_map.get(search_type, "search_performed")

        self.capture(
            event_name,
            user_id=user_id,
            result_count=result_count,
            query_time_ms=query_time_ms,
            **kwargs
        )

    def track_feature_usage(
        self,
        user_id: Optional[str],
        feature_name: str,
        **kwargs
    ) -> None:
        """Track feature usage (effect, MIDI generation, etc.)"""
        self.capture(
            EventType.EFFECT_APPLIED.value if feature_name == "effect"
            else EventType.MIDI_GENERATED.value if feature_name == "midi"
            else "feature_used",
            user_id=user_id,
            feature=feature_name,
            **kwargs
        )

    def track_export(
        self,
        user_id: Optional[str],
        export_format: str,
        file_size: int,
        **kwargs
    ) -> None:
        """Track file export"""
        self.capture(
            EventType.RESULTS_EXPORTED.value,
            user_id=user_id,
            export_format=export_format,
            file_size=file_size,
            **kwargs
        )

    def flush(self) -> None:
        """Flush pending events"""
        if self.enabled and self.client:
            try:
                self.client.flush()
            except Exception as e:
                logger.debug(f"Error flushing events: {e}")


# Global analytics instance
_analytics_instance: Optional[PostHogAnalytics] = None


def get_analytics() -> PostHogAnalytics:
    """Get or create global analytics instance"""
    global _analytics_instance
    if _analytics_instance is None:
        _analytics_instance = PostHogAnalytics()
    return _analytics_instance


def init_analytics(api_key: Optional[str] = None, host: Optional[str] = None) -> PostHogAnalytics:
    """Initialize analytics with custom settings"""
    global _analytics_instance
    _analytics_instance = PostHogAnalytics(api_key=api_key, host=host)
    return _analytics_instance
