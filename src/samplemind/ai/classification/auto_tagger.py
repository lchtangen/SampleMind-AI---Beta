"""Automatic tagging system for audio samples.

Integrates AI classification with the existing tagging system to
automatically tag samples based on their audio content.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from samplemind.core.engine.audio_engine import AudioFeatures

from .classifier import AIClassifier

logger = logging.getLogger(__name__)


class AutoTagger:
    """Automatically tag audio samples based on AI classification."""

    def __init__(self, confidence_threshold: float = 0.60) -> None:
        """Initialize auto-tagger.

        Args:
            confidence_threshold: Minimum confidence (0-1) for tagging
        """
        self.classifier = AIClassifier()
        self.confidence_threshold = confidence_threshold

    def auto_tag_sample(
        self,
        audio_features: AudioFeatures,
        file_path: Path,
        override_existing: bool = False,
    ) -> List[str]:
        """Auto-tag a single sample based on its features.

        Args:
            audio_features: Extracted audio features
            file_path: Path to the audio file (for reference)
            override_existing: Whether to override existing tags

        Returns:
            List of generated tags
        """
        # Classify the sample
        classification = self.classifier.classify_audio(audio_features)

        # Generate tags from classification
        tags = self._generate_tags_from_classification(classification)

        logger.info(f"Generated {len(tags)} tags for {file_path.name}: {tags}")

        return tags

    async def bulk_auto_tag(
        self,
        file_paths: List[Path],
        get_features_fn,
        progress_callback: Optional[callable] = None,
    ) -> Dict[Path, List[str]]:
        """Automatically tag multiple samples.

        Args:
            file_paths: List of audio file paths to tag
            get_features_fn: Async function to extract features: async fn(path) -> AudioFeatures
            progress_callback: Optional callback(current, total) for progress

        Returns:
            Dictionary mapping file paths to their generated tags
        """
        results = {}
        total = len(file_paths)

        for i, file_path in enumerate(file_paths):
            try:
                # Extract features
                features = await get_features_fn(file_path)

                # Auto-tag
                tags = self.auto_tag_sample(features, file_path)
                results[file_path] = tags

                logger.debug(f"Tagged {file_path.name} with {len(tags)} tags")

            except Exception as e:
                logger.error(f"Failed to tag {file_path.name}: {e}")
                results[file_path] = []

            # Call progress callback if provided
            if progress_callback:
                await progress_callback(i + 1, total)

        return results

    def _generate_tags_from_classification(self, classification) -> List[str]:
        """Generate tags from classification result."""
        tags = []

        # Add instrument if confident enough
        if classification.instrument_confidence >= self.confidence_threshold:
            tags.append(classification.instrument)

        # Add genre if confident enough
        if classification.genre_confidence >= self.confidence_threshold:
            tags.append(classification.genre)

        # Add mood if confident enough
        if classification.mood_confidence >= self.confidence_threshold:
            tags.append(classification.mood)

        # Add quality-based tags
        if classification.quality_score >= 0.80:
            tags.append("professional")
        elif classification.quality_score <= 0.30:
            tags.append("lo-fi")

        # Add tempo category
        if classification.tempo_category in ["fast", "slow", "medium"]:
            tags.append(classification.tempo_category)

        # Remove duplicates and return
        return list(set(tags))

    def get_confidence_report(
        self,
        audio_features: AudioFeatures,
    ) -> Dict[str, Dict[str, float]]:
        """Get a detailed confidence report for an audio sample.

        Args:
            audio_features: Extracted audio features

        Returns:
            Dictionary of confidence scores for all classifications
        """
        classification = self.classifier.classify_audio(audio_features)

        return {
            "instrument": {
                "detected": classification.instrument,
                "confidence": classification.instrument_confidence,
            },
            "genre": {
                "detected": classification.genre,
                "confidence": classification.genre_confidence,
            },
            "mood": {
                "detected": classification.mood,
                "confidence": classification.mood_confidence,
            },
            "quality": {
                "score": classification.quality_score,
            },
            "tempo_category": classification.tempo_category,
            "tags": classification.tags,
            "model_used": classification.model_used,
            "processing_time": classification.processing_time,
        }
