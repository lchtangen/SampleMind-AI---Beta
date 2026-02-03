#!/usr/bin/env python3
"""
AI-Powered Sample Tagger

Generates intelligent, searchable tags for audio samples using:
1. AI analysis (Google Gemini for semantic understanding)
2. Rule-based feature extraction (tempo, key, energy, spectral features)
3. Hybrid approach with high confidence scoring

Produces tags in 5 categories:
- Genres, Moods, Instruments, Energy Levels, Descriptors
"""

import logging
from typing import List, Dict, Optional, Set
from dataclasses import dataclass

from samplemind.core.tagging.tag_vocabulary import (
    TagConfidence,
    get_vocabulary,
    ENERGY_LEVELS,
)

logger = logging.getLogger(__name__)


# ============================================================================
# AI TAGGER ENGINE
# ============================================================================

class AITagger:
    """Generates AI-powered tags for audio samples"""

    def __init__(self) -> None:
        self.vocabulary = get_vocabulary()
        self.min_confidence = 0.5  # Only include tags with 50%+ confidence

    def tag_from_features(
        self,
        features: Dict,
        ai_analysis: Optional[Dict] = None,
        use_ai: bool = True,
    ) -> List[TagConfidence]:
        """
        Generate tags from audio features and optional AI analysis

        Args:
            features: Audio features dict (tempo, key, mode, spectral data, etc.)
            ai_analysis: Optional AI analysis result (genre, mood, descriptors)
            use_ai: Whether to include AI-generated tags

        Returns:
            List of TagConfidence objects, sorted by confidence
        """
        tags = []

        # 1. Rule-based tagging from features
        tags.extend(self._tag_from_tempo(features.get("tempo", 0)))
        tags.extend(self._tag_from_key_mode(features.get("key"), features.get("mode")))
        tags.extend(self._tag_from_energy(features))
        tags.extend(self._tag_from_spectral(features))
        tags.extend(self._tag_from_rhythm(features))

        # 2. AI-based tagging if provided
        if use_ai and ai_analysis:
            tags.extend(self._tag_from_ai_analysis(ai_analysis))

        # 3. Filter by confidence threshold
        tags = [t for t in tags if t.confidence >= self.min_confidence]

        # 4. Sort by confidence (descending)
        tags.sort(key=lambda t: t.confidence, reverse=True)

        # 5. Remove duplicates (keep highest confidence)
        seen = set()
        unique_tags = []
        for tag in tags:
            if tag.tag not in seen:
                unique_tags.append(tag)
                seen.add(tag.tag)

        logger.debug(f"Generated {len(unique_tags)} tags from features and AI")
        return unique_tags

    # ========================================================================
    # RULE-BASED TAGGING METHODS
    # ========================================================================

    def _tag_from_tempo(self, tempo: float) -> List[TagConfidence]:
        """Infer mood/energy from tempo"""
        tags = []

        if 0 < tempo < 60:
            # Very slow
            tags.append(TagConfidence("very-low", "energy", 0.8, "rule-based"))
            tags.append(TagConfidence("calm", "mood", 0.7, "rule-based"))
            tags.append(TagConfidence("slow", "descriptor", 0.8, "rule-based"))

        elif 60 <= tempo < 90:
            # Slow
            tags.append(TagConfidence("low", "energy", 0.8, "rule-based"))
            tags.append(TagConfidence("calm", "mood", 0.8, "rule-based"))
            tags.append(TagConfidence("relaxing", "mood", 0.7, "rule-based"))

        elif 90 <= tempo < 120:
            # Medium
            tags.append(TagConfidence("medium", "energy", 0.8, "rule-based"))
            tags.append(TagConfidence("steady", "descriptor", 0.7, "rule-based"))

        elif 120 <= tempo < 140:
            # Fast
            tags.append(TagConfidence("high", "energy", 0.8, "rule-based"))
            tags.append(TagConfidence("energetic", "mood", 0.75, "rule-based"))
            tags.append(TagConfidence("driving", "mood", 0.7, "rule-based"))

        elif tempo >= 140:
            # Very fast
            tags.append(TagConfidence("very-high", "energy", 0.85, "rule-based"))
            tags.append(TagConfidence("intense", "mood", 0.8, "rule-based"))
            tags.append(TagConfidence("fast", "descriptor", 0.85, "rule-based"))

        return tags

    def _tag_from_key_mode(self, key: Optional[str], mode: Optional[str]) -> List[TagConfidence]:
        """Infer mood from key and mode"""
        tags = []

        # Major keys tend to sound happy
        if mode and mode.lower() == "major":
            tags.append(TagConfidence("uplifting", "mood", 0.6, "rule-based"))
            tags.append(TagConfidence("bright", "descriptor", 0.65, "rule-based"))

        # Minor keys tend to sound sad
        elif mode and mode.lower() == "minor":
            tags.append(TagConfidence("melancholic", "mood", 0.6, "rule-based"))
            tags.append(TagConfidence("dark", "descriptor", 0.65, "rule-based"))

        return tags

    def _tag_from_energy(self, features: Dict) -> List[TagConfidence]:
        """Infer energy level from RMS energy and dynamics"""
        tags = []

        rms_energy = features.get("rms_energy", 0)
        crest_factor = features.get("crest_factor", 0)

        # Normalize RMS energy to 0-1
        normalized_energy = min(rms_energy / 0.1, 1.0)

        if normalized_energy < 0.2:
            tags.append(TagConfidence("very-low", "energy", 0.8, "rule-based"))
        elif normalized_energy < 0.4:
            tags.append(TagConfidence("low", "energy", 0.8, "rule-based"))
        elif normalized_energy < 0.6:
            tags.append(TagConfidence("medium", "energy", 0.8, "rule-based"))
        elif normalized_energy < 0.8:
            tags.append(TagConfidence("high", "energy", 0.8, "rule-based"))
        else:
            tags.append(TagConfidence("very-high", "energy", 0.8, "rule-based"))

        # High crest factor = dynamic, has peaks
        if crest_factor and crest_factor > 12:
            tags.append(TagConfidence("dynamic", "descriptor", 0.7, "rule-based"))
            tags.append(TagConfidence("punchy", "descriptor", 0.65, "rule-based"))

        return tags

    def _tag_from_spectral(self, features: Dict) -> List[TagConfidence]:
        """Infer tonal characteristics from spectral features"""
        tags = []

        spectral_centroid = features.get("spectral_centroid", 0)
        spectral_brightness = features.get("brightness", 0)

        # Bright samples have high spectral centroid
        if spectral_centroid > 4000:
            tags.append(TagConfidence("bright", "descriptor", 0.75, "rule-based"))
            tags.append(TagConfidence("crisp", "descriptor", 0.65, "rule-based"))

        # Dark samples have low spectral centroid
        elif spectral_centroid < 2000:
            tags.append(TagConfidence("dark", "descriptor", 0.75, "rule-based"))
            tags.append(TagConfidence("warm", "descriptor", 0.65, "rule-based"))

        # High brightness
        if spectral_brightness and spectral_brightness > 0.7:
            tags.append(TagConfidence("bright", "descriptor", 0.7, "rule-based"))

        # Warm/muddy (low frequency heavy)
        low_freq_power = features.get("low_freq_power", 0)
        if low_freq_power and low_freq_power > 0.6:
            tags.append(TagConfidence("warm", "descriptor", 0.7, "rule-based"))
            tags.append(TagConfidence("thick", "descriptor", 0.65, "rule-based"))

        return tags

    def _tag_from_rhythm(self, features: Dict) -> List[TagConfidence]:
        """Infer rhythmic characteristics"""
        tags = []

        # Check if sample has rhythmic content (high onset detection)
        onset_count = features.get("onset_count", 0)
        duration = features.get("duration", 1)
        onset_density = onset_count / max(duration, 1)

        if onset_density > 5:  # More than 5 onsets per second = rhythmic
            tags.append(TagConfidence("rhythmic", "descriptor", 0.8, "rule-based"))
            tags.append(TagConfidence("percussive", "descriptor", 0.75, "rule-based"))

            # Very high density might indicate drums or percussion
            if onset_density > 10:
                tags.append(TagConfidence("drums", "instrument", 0.6, "rule-based"))

        # Low onset density = smooth, continuous
        elif onset_density < 1:
            tags.append(TagConfidence("smooth", "descriptor", 0.8, "rule-based"))
            tags.append(TagConfidence("melodic", "descriptor", 0.7, "rule-based"))

        return tags

    # ========================================================================
    # AI-BASED TAGGING
    # ========================================================================

    def _tag_from_ai_analysis(self, ai_analysis: Dict) -> List[TagConfidence]:
        """Extract tags from AI analysis results"""
        tags = []

        # Genre tags (high confidence from AI)
        if "genre" in ai_analysis:
            genre = ai_analysis["genre"].lower().replace(" ", "-")
            if self.vocabulary.is_valid_tag(genre):
                tags.append(TagConfidence(genre, "genre", 0.85, "ai"))

        # Mood tags
        if "mood" in ai_analysis:
            mood = ai_analysis["mood"].lower().replace(" ", "-")
            if self.vocabulary.is_valid_tag(mood):
                tags.append(TagConfidence(mood, "mood", 0.85, "ai"))

        # Instrument tags
        if "instruments" in ai_analysis:
            instruments = ai_analysis["instruments"]
            if isinstance(instruments, list):
                for inst in instruments:
                    inst_lower = inst.lower().replace(" ", "-")
                    if self.vocabulary.is_valid_tag(inst_lower):
                        tags.append(TagConfidence(inst_lower, "instrument", 0.75, "ai"))

        # Descriptors from AI
        if "descriptors" in ai_analysis:
            descriptors = ai_analysis["descriptors"]
            if isinstance(descriptors, list):
                for desc in descriptors:
                    desc_lower = desc.lower().replace(" ", "-")
                    if self.vocabulary.is_valid_tag(desc_lower):
                        tags.append(TagConfidence(desc_lower, "descriptor", 0.7, "ai"))

        return tags

    # ========================================================================
    # TAG ORGANIZATION & FILTERING
    # ========================================================================

    def organize_by_category(self, tags: List[TagConfidence]) -> Dict[str, List[TagConfidence]]:
        """Organize tags by category"""
        organized = {
            "genre": [],
            "mood": [],
            "instrument": [],
            "energy": [],
            "descriptor": [],
        }

        for tag in tags:
            organized[tag.category].append(tag)

        # Sort each category by confidence
        for category in organized:
            organized[category].sort(key=lambda t: t.confidence, reverse=True)

        return organized

    def get_high_confidence_tags(
        self,
        tags: List[TagConfidence],
        threshold: float = 0.7,
    ) -> List[TagConfidence]:
        """Filter tags by confidence threshold"""
        return [t for t in tags if t.confidence >= threshold]

    def to_simple_dict(self, tags: List[TagConfidence]) -> Dict[str, List[str]]:
        """Convert tags to simple dictionary format"""
        organized = self.organize_by_category(tags)
        return {
            category: [tag.tag for tag in tag_list]
            for category, tag_list in organized.items()
        }

    def to_detailed_dict(self, tags: List[TagConfidence]) -> Dict[str, List[Dict]]:
        """Convert tags to detailed format with confidence scores"""
        organized = self.organize_by_category(tags)
        return {
            category: [
                {
                    "tag": tag.tag,
                    "confidence": round(tag.confidence, 2),
                    "source": tag.source,
                }
                for tag in tag_list
            ]
            for category, tag_list in organized.items()
        }


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_tagger: Optional[AITagger] = None


def get_tagger() -> AITagger:
    """Get global AI tagger instance"""
    global _tagger
    if _tagger is None:
        _tagger = AITagger()
    return _tagger


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    "AITagger",
    "get_tagger",
    "TagConfidence",
]


if __name__ == "__main__":
    # Demo
    tagger = get_tagger()

    # Sample features
    sample_features = {
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

    # Sample AI analysis
    sample_ai = {
        "genre": "techno",
        "mood": "driving",
        "instruments": ["drums", "bass", "synth"],
        "descriptors": ["dark", "punchy", "rhythmic"],
    }

    # Generate tags
    tags = tagger.tag_from_features(sample_features, sample_ai)

    print("\n🏷️  Generated Tags")
    print("=" * 50)

    organized = tagger.organize_by_category(tags)
    for category, tag_list in organized.items():
        if tag_list:
            print(f"\n{category.upper()}:")
            for tag in tag_list:
                print(f"  {tag.tag:<20} ({tag.confidence:.0%}) [{tag.source}]")
