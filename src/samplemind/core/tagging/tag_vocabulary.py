#!/usr/bin/env python3
"""
Tag Vocabulary & Classification System

Defines comprehensive tag categories and vocabularies for audio samples.
Used for consistent, searchable tagging across the sample library.

Categories:
- Genres: Electronic, Hip-Hop, Pop, Rock, Jazz, Classical, etc.
- Moods: Energetic, Dark, Uplifting, Aggressive, Calm, Melancholic, etc.
- Instruments: Drums, Bass, Synth, Piano, Guitar, Strings, etc.
- Energy Levels: Very Low, Low, Medium, High, Very High
- Descriptors: Warm, Bright, Dark, Clean, Dirty, Punchy, Smooth, etc.
"""

from dataclasses import dataclass
from typing import List, Set, Dict, Optional

# ============================================================================
# TAG CATEGORIES
# ============================================================================

GENRES = {
    # Electronic & Dance
    "techno", "house", "deep-house", "tech-house", "minimal",
    "acid", "trance", "progressive-house", "electro", "drum-and-bass",
    "liquid-funk", "dnb", "electronica", "synthwave", "vaporwave",
    "ambient", "downtempo", "chillwave", "future-bass", "trap",
    "dubstep", "grime", "garage", "uk-bass", "industrial",

    # Hip-Hop & Urban
    "hip-hop", "rap", "trap-hop", "lo-fi", "boom-bap", "conscious-hip-hop",
    "gangsta-rap", "east-coast", "west-coast", "crunk", "grime", "uk-rap",

    # Pop & Mainstream
    "pop", "indie-pop", "synth-pop", "dance-pop", "pop-rock",
    "alternative", "indie", "indie-rock", "emo", "rock",

    # Rock & Metal
    "rock", "alternative-rock", "indie-rock", "hard-rock", "classic-rock",
    "punk", "metal", "heavy-metal", "death-metal", "black-metal",
    "progressive-rock", "post-rock",

    # Jazz & Blues
    "jazz", "bebop", "cool-jazz", "fusion", "jazz-funk", "nu-jazz",
    "blues", "blues-rock", "soul", "funk", "r&b", "neo-soul",

    # Classical & Acoustic
    "classical", "orchestral", "chamber", "baroque", "romantic",
    "contemporary-classical", "acoustic", "folk", "singer-songwriter",
    "world-music",

    # Experimental & Other
    "experimental", "avant-garde", "noise", "glitch", "abstract",
    "ambient", "generative", "soundscape", "dark-ambient",
}

MOODS = {
    # Positive & Uplifting
    "uplifting", "energetic", "euphoric", "joyful", "happy", "cheerful",
    "playful", "whimsical", "inspiring", "motivating", "triumphant",
    "celebratory", "optimistic", "bright", "sunny",

    # Dark & Moody
    "dark", "moody", "melancholic", "sad", "depressing", "somber",
    "brooding", "mysterious", "eerie", "scary", "haunting", "ominous",
    "gloomy", "pessimistic", "tragic",

    # Neutral & Balanced
    "neutral", "calm", "peaceful", "serene", "tranquil", "meditative",
    "relaxing", "contemplative", "thoughtful", "introspective",
    "dreamy", "nostalgic", "wistful",

    # Intense & Aggressive
    "aggressive", "intense", "powerful", "driving", "hard", "fierce",
    "violent", "chaotic", "tense", "anxious", "unsettling",
    "confrontational", "rebellious", "raw",

    # Romantic & Sensual
    "romantic", "sensual", "seductive", "intimate", "tender", "sweet",
    "passionate", "loving", "affectionate",

    # Exotic & Unusual
    "exotic", "mysterious", "magical", "whimsical", "surreal", "abstract",
    "cosmic", "psychedelic", "hypnotic", "trance-like",
}

INSTRUMENTS = {
    # Drums & Percussion
    "drums", "drum-kit", "kick", "snare", "hi-hat", "cymbal",
    "tom", "shaker", "percussion", "timpani", "marimba", "vibraphone",
    "gong", "bell", "chime", "cowbell", "conga", "bongo",
    "tabla", "djembe", "timpani", "xylophone",

    # Bass
    "bass", "kick-bass", "sub-bass", "bass-guitar", "upright-bass",
    "synth-bass", "fretless-bass", "bass-synth", "808", "808-bass",

    # Synths & Electronic
    "synth", "synthesizer", "synth-lead", "synth-pad", "synth-bass",
    "digital-synth", "analog-synth", "modular-synth", "wavetable",
    "fm-synth", "pad", "arpeggio", "arpeggiator", "pluck",

    # Piano & Keys
    "piano", "grand-piano", "upright-piano", "electric-piano",
    "organ", "keyboard", "keys", "harpsichord", "mellotron",
    "string-machine", "synthesizer", "clavinet",

    # Strings
    "strings", "violin", "viola", "cello", "double-bass",
    "string-section", "string-quartet", "harp", "sitar", "lute",
    "mandolin", "banjo", "acoustic-guitar",

    # Brass & Winds
    "brass", "trumpet", "trombone", "french-horn", "tuba",
    "saxophone", "alto-sax", "tenor-sax", "soprano-sax",
    "flute", "clarinet", "oboe", "english-horn", "piccolo",
    "pan-flute", "pan-pipes", "didgeridoo",

    # Vocals
    "vocals", "voice", "singing", "vocal-chops", "vocal-sample",
    "vocal-melody", "vocal-harmony", "choir", "chorus", "acapella",

    # Acoustic & Other
    "acoustic-guitar", "electric-guitar", "guitar", "acoustic",
    "folk-instrument", "ethnic-instrument", "field-recording",
    "ambient-texture", "noise", "found-sound",
}

ENERGY_LEVELS = {
    "very-low": 0,      # 0-20%: Minimal, barely perceptible
    "low": 1,           # 20-40%: Subtle, background
    "medium": 2,        # 40-60%: Balanced, present
    "high": 3,          # 60-80%: Intense, prominent
    "very-high": 4,     # 80-100%: Maximum, overwhelming
}

DESCRIPTORS = {
    # Tonal Characteristics
    "warm", "cold", "bright", "dark", "harsh", "smooth",
    "crisp", "muddy", "clean", "dirty", "transparent", "opaque",
    "thin", "thick", "hollow", "resonant", "metallic", "organic",

    # Texture & Feel
    "punchy", "soft", "crunchy", "breezy", "dense", "sparse",
    "layered", "minimalist", "maximal", "intricate", "simple",
    "complex", "groovy", "static", "dynamic", "rhythmic",
    "arrhythmic", "syncopated", "straight",

    # Production Quality
    "lo-fi", "hi-fi", "analog", "digital", "vintage", "modern",
    "compressed", "dynamic", "saturated", "clean", "distorted",
    "filtered", "resonant", "processed", "raw", "polished",
    "rough", "smooth", "quantized", "humanized",

    # Spatial & Ambient
    "spacious", "intimate", "reverberant", "dry", "stereo",
    "mono", "wide", "narrow", "centered", "panned",
    "immersive", "isolated", "enveloping",

    # Temporal & Movement
    "fast", "slow", "steady", "unstable", "accelerating",
    "decelerating", "pulsing", "static", "evolving",
    "looping", "one-shot", "ambient-pad", "atmospheric",
    "percussive", "melodic", "harmonic", "textural",

    # Emotional Resonance
    "uplifting", "depressing", "calming", "tense", "exciting",
    "boring", "surprising", "expected", "unconventional",
    "nostalgic", "futuristic", "retro", "timeless",
    "mature", "playful", "serious", "humorous",
}

# ============================================================================
# TAG CONFIDENCE LEVELS
# ============================================================================

@dataclass
class TagConfidence:
    """Represents confidence in a tag assignment"""
    tag: str
    category: str  # genre, mood, instrument, energy, descriptor
    confidence: float  # 0.0-1.0
    source: str  # "ai", "rule-based", "user"

    def is_high_confidence(self, threshold: float = 0.7) -> bool:
        """Check if confidence exceeds threshold"""
        return self.confidence >= threshold

    def __repr__(self) -> str:
        return f"{self.tag} ({self.confidence:.0%})"


# ============================================================================
# TAG SETS
# ============================================================================

class TagVocabulary:
    """Manages tag vocabulary and validation"""

    def __init__(self):
        self.genres = set(GENRES)
        self.moods = set(MOODS)
        self.instruments = set(INSTRUMENTS)
        self.energy_levels = set(ENERGY_LEVELS.keys())
        self.descriptors = set(DESCRIPTORS)

    @property
    def all_tags(self) -> Set[str]:
        """Get all valid tags"""
        return (
            self.genres
            | self.moods
            | self.instruments
            | self.energy_levels
            | self.descriptors
        )

    def get_category(self, tag: str) -> Optional[str]:
        """Get category for a tag"""
        tag_lower = tag.lower().replace("_", "-")

        if tag_lower in self.genres:
            return "genre"
        elif tag_lower in self.moods:
            return "mood"
        elif tag_lower in self.instruments:
            return "instrument"
        elif tag_lower in self.energy_levels:
            return "energy"
        elif tag_lower in self.descriptors:
            return "descriptor"

        return None

    def is_valid_tag(self, tag: str) -> bool:
        """Check if tag is in vocabulary"""
        return tag.lower().replace("_", "-") in self.all_tags

    def suggest_similar(self, tag: str, category: Optional[str] = None, limit: int = 5) -> List[str]:
        """Suggest similar tags (using string similarity)"""
        tag_lower = tag.lower()
        candidates = []

        if category:
            cat_tags = getattr(self, f"{category}s", set())
        else:
            cat_tags = self.all_tags

        for candidate in cat_tags:
            # Simple similarity: shared characters
            shared = len(set(tag_lower) & set(candidate))
            candidates.append((candidate, shared))

        candidates.sort(key=lambda x: x[1], reverse=True)
        return [tag for tag, _ in candidates[:limit]]

    def get_tags_by_category(self, category: str) -> Set[str]:
        """Get all tags in a category"""
        if category == "genre":
            return self.genres
        elif category == "mood":
            return self.moods
        elif category == "instrument":
            return self.instruments
        elif category == "energy":
            return self.energy_levels
        elif category == "descriptor":
            return self.descriptors
        return set()

    def stats(self) -> Dict[str, int]:
        """Get vocabulary statistics"""
        return {
            "genres": len(self.genres),
            "moods": len(self.moods),
            "instruments": len(self.instruments),
            "energy_levels": len(self.energy_levels),
            "descriptors": len(self.descriptors),
            "total": len(self.all_tags),
        }


# ============================================================================
# GLOBAL VOCABULARY INSTANCE
# ============================================================================

_vocabulary: Optional[TagVocabulary] = None


def get_vocabulary() -> TagVocabulary:
    """Get global vocabulary instance"""
    global _vocabulary
    if _vocabulary is None:
        _vocabulary = TagVocabulary()
    return _vocabulary


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    "GENRES",
    "MOODS",
    "INSTRUMENTS",
    "ENERGY_LEVELS",
    "DESCRIPTORS",
    "TagConfidence",
    "TagVocabulary",
    "get_vocabulary",
]


if __name__ == "__main__":
    vocab = get_vocabulary()
    stats = vocab.stats()

    print("\n🏷️  Tag Vocabulary Statistics")
    print("=" * 50)
    for category, count in stats.items():
        print(f"  {category:<20} {count:>4}")
    print("=" * 50)
    print(f"  {'TOTAL':<20} {stats['total']:>4}")

    # Sample usage
    print("\n📝 Sample Tags:")
    print(f"  Genres: {', '.join(list(vocab.genres)[:5])}...")
    print(f"  Moods: {', '.join(list(vocab.moods)[:5])}...")
    print(f"  Instruments: {', '.join(list(vocab.instruments)[:5])}...")
    print(f"  Descriptors: {', '.join(list(vocab.descriptors)[:5])}...")
