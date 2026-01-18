"""
AI Coaching System for SampleMind TUI
Real-time production tips, genre-specific advice, and suggestions
"""

import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class GenreType(Enum):
    """Supported music genres"""
    ELECTRONIC = "electronic"
    HIP_HOP = "hip_hop"
    AMBIENT = "ambient"
    ORCHESTRAL = "orchestral"
    JAZZ = "jazz"
    ROCK = "rock"
    POP = "pop"
    TECHNO = "techno"
    HOUSE = "house"
    DUBSTEP = "dubstep"
    TRAP = "trap"
    DNB = "dnb"
    EXPERIMENTAL = "experimental"
    UNKNOWN = "unknown"


class ProductionTipCategory(Enum):
    """Production tip categories"""
    ARRANGEMENT = "arrangement"
    MIXING = "mixing"
    SOUND_DESIGN = "sound_design"
    PERFORMANCE = "performance"
    WORKFLOW = "workflow"
    THEORY = "theory"
    TECHNIQUE = "technique"


@dataclass
class ProductionTip:
    """Production tip with context"""
    category: ProductionTipCategory
    title: str
    description: str
    genre: GenreType
    difficulty: int  # 1-5
    related_feature: Optional[str] = None
    example: Optional[str] = None


@dataclass
class GenreAdvice:
    """Genre-specific production advice"""
    genre: GenreType
    tempo_range: tuple  # (min, max)
    key_recommendations: List[str]
    typical_instruments: List[str]
    production_techniques: List[str]
    mixing_tips: List[str]
    sample_characteristics: List[str]


@dataclass
class SamplePairing:
    """Suggested sample pairing"""
    sample_name: str
    reason: str
    compatibility_score: float  # 0-1
    genre: GenreType
    tempo_match: bool
    key_compatible: bool


class AICoach:
    """Real-time AI coaching system for music production"""

    # Production tips database
    PRODUCTION_TIPS: Dict[GenreType, List[ProductionTip]] = {
        GenreType.TECHNO: [
            ProductionTip(
                category=ProductionTipCategory.ARRANGEMENT,
                title="Layered Progression",
                description="Build techno tracks by adding elements every 16 bars",
                genre=GenreType.TECHNO,
                difficulty=2,
                example="Kick (0-16) → Bassline (16-32) → Hi-hat (32-48) → Pad (48-64)"
            ),
            ProductionTip(
                category=ProductionTipCategory.SOUND_DESIGN,
                title="Analog Warmth",
                description="Use saturation on basslines for thick, analog-style sound",
                genre=GenreType.TECHNO,
                difficulty=2
            ),
            ProductionTip(
                category=ProductionTipCategory.MIXING,
                title="Compression Trick",
                description="Use parallel compression on drums for punch without losing dynamics",
                genre=GenreType.TECHNO,
                difficulty=3
            ),
        ],
        GenreType.HOUSE: [
            ProductionTip(
                category=ProductionTipCategory.ARRANGEMENT,
                title="4-Bar Structure",
                description="Build house tracks in 4 and 8-bar sections for cohesive flow",
                genre=GenreType.HOUSE,
                difficulty=2
            ),
            ProductionTip(
                category=ProductionTipCategory.SOUND_DESIGN,
                title="Sidechain Pumping",
                description="Create dynamic pumping effect using sidechain compression",
                genre=GenreType.HOUSE,
                difficulty=2
            ),
        ],
        GenreType.TRAP: [
            ProductionTip(
                category=ProductionTipCategory.SOUND_DESIGN,
                title="808 Layering",
                description="Layer 808s with sub-bass for depth and punch",
                genre=GenreType.TRAP,
                difficulty=2
            ),
            ProductionTip(
                category=ProductionTipCategory.MIXING,
                title="Snare Compression",
                description="Use fast attack compression to tighten snare hits",
                genre=GenreType.TRAP,
                difficulty=2
            ),
        ],
        GenreType.AMBIENT: [
            ProductionTip(
                category=ProductionTipCategory.ARRANGEMENT,
                title="Subtle Evolution",
                description="Let ambient tracks evolve slowly over time with gradual changes",
                genre=GenreType.AMBIENT,
                difficulty=3
            ),
            ProductionTip(
                category=ProductionTipCategory.MIXING,
                title="Reverb and Space",
                description="Use reverb creatively to create depth and space",
                genre=GenreType.AMBIENT,
                difficulty=2
            ),
        ],
    }

    # Genre advice database
    GENRE_ADVICE: Dict[GenreType, GenreAdvice] = {
        GenreType.TECHNO: GenreAdvice(
            genre=GenreType.TECHNO,
            tempo_range=(120, 130),
            key_recommendations=["A minor", "C minor", "D minor", "E minor"],
            typical_instruments=["Kick drum", "Bassline", "Closed hi-hat", "Crash", "Pad", "Synth"],
            production_techniques=["Sidechain compression", "Saturation", "EQ automation"],
            mixing_tips=["Deep bass essential", "Tight drums", "Minimal reverb"],
            sample_characteristics=["Dark", "Percussive", "Synthetic", "Repetitive"]
        ),
        GenreType.HOUSE: GenreAdvice(
            genre=GenreType.HOUSE,
            tempo_range=(120, 128),
            key_recommendations=["A minor", "E major", "D minor", "G major"],
            typical_instruments=["Kick drum", "Bassline", "Open/closed hi-hat", "Clap", "String pad", "Vocal"],
            production_techniques=["Sidechain pumping", "Filter sweeps", "Automation"],
            mixing_tips=["Punchy kick", "Warm bass", "Spacious vocals"],
            sample_characteristics=["Groovy", "Warm", "Soulful", "Syncopated"]
        ),
        GenreType.TRAP: GenreAdvice(
            genre=GenreType.TRAP,
            tempo_range=(140, 160),
            key_recommendations=["A minor", "C minor", "D minor", "E minor"],
            typical_instruments=["808 drum", "Snare", "Hi-hat", "Clap", "Synth pad", "Vocal"],
            production_techniques=["808 layering", "Snare rolls", "Reverse cymbals"],
            mixing_tips=["Sub-bass focus", "Punchy snare", "Clear vocals"],
            sample_characteristics=["Heavy bass", "Percussive", "Modern", "Dark"]
        ),
        GenreType.AMBIENT: GenreAdvice(
            genre=GenreType.AMBIENT,
            tempo_range=(60, 90),
            key_recommendations=["Any minor key", "Any major key"],
            typical_instruments=["Pad", "String", "Piano", "Field recording", "Atmospheric FX"],
            production_techniques=["Reverb", "Delay", "Granular synthesis"],
            mixing_tips=["Ethereal reverb", "Minimal compression", "Slow automation"],
            sample_characteristics=["Textured", "Atmospheric", "Harmonic", "Evolving"]
        ),
    }

    def __init__(self):
        """Initialize AI coach"""
        self.tips_shown: List[str] = []
        self.current_context: Dict[str, Any] = {}

    def detect_genre(self, features: Dict[str, Any]) -> GenreType:
        """
        Detect genre based on audio features

        Args:
            features: Audio analysis features

        Returns:
            Detected genre
        """
        tempo = features.get("tempo", 0)
        energy = features.get("energy", 0)
        spectral_centroid = features.get("spectral_centroid", 0)
        zero_crossing_rate = features.get("zero_crossing_rate", 0)

        # Simple heuristic-based genre detection
        if 120 <= tempo <= 130 and energy > 0.6 and spectral_centroid < 3000:
            return GenreType.TECHNO
        elif 120 <= tempo <= 128 and energy > 0.5 and spectral_centroid < 3500:
            return GenreType.HOUSE
        elif 140 <= tempo <= 160 and energy > 0.7 and spectral_centroid < 2000:
            return GenreType.TRAP
        elif tempo < 100 and energy < 0.4:
            return GenreType.AMBIENT
        else:
            return GenreType.UNKNOWN

    def get_production_tips(
        self,
        genre: GenreType = GenreType.UNKNOWN,
        difficulty_level: int = 2,
        category: Optional[ProductionTipCategory] = None,
        limit: int = 3
    ) -> List[ProductionTip]:
        """
        Get production tips

        Args:
            genre: Genre type for tips
            difficulty_level: 1-5, difficulty filter
            category: Optional category filter
            limit: Maximum tips to return

        Returns:
            List of production tips
        """
        if genre not in self.PRODUCTION_TIPS:
            logger.warning(f"No tips for genre: {genre}")
            return []

        tips = self.PRODUCTION_TIPS.get(genre, [])

        # Filter by difficulty
        tips = [t for t in tips if t.difficulty <= difficulty_level]

        # Filter by category
        if category:
            tips = [t for t in tips if t.category == category]

        # Avoid duplicates shown recently
        tips = [t for t in tips if t.title not in self.tips_shown]

        # Track shown tips
        for tip in tips[:limit]:
            self.tips_shown.append(tip.title)

        # Keep history limited
        if len(self.tips_shown) > 20:
            self.tips_shown = self.tips_shown[-20:]

        return tips[:limit]

    def get_genre_advice(self, genre: GenreType) -> Optional[GenreAdvice]:
        """
        Get genre-specific advice

        Args:
            genre: Genre type

        Returns:
            Genre advice or None
        """
        return self.GENRE_ADVICE.get(genre)

    def suggest_sample_pairings(
        self,
        current_sample: Dict[str, Any],
        available_samples: List[Dict[str, Any]]
    ) -> List[SamplePairing]:
        """
        Suggest compatible sample pairings

        Args:
            current_sample: Current sample features
            available_samples: Available samples to pair with

        Returns:
            List of suggested pairings with scores
        """
        current_tempo = current_sample.get("tempo", 120)
        current_key = current_sample.get("key", "C")
        current_energy = current_sample.get("energy", 0.5)
        current_name = current_sample.get("name", "Unknown")

        pairings: List[SamplePairing] = []

        for sample in available_samples:
            sample_tempo = sample.get("tempo", 120)
            sample_key = sample.get("key", "C")
            sample_energy = sample.get("energy", 0.5)
            sample_name = sample.get("name", "Unknown")

            # Skip self
            if sample_name == current_name:
                continue

            # Calculate compatibility
            tempo_diff = abs(current_tempo - sample_tempo)
            tempo_match = tempo_diff < 5 or tempo_diff > 115  # Harmonic tempo relationship

            key_compatible = current_key == sample_key or self._is_compatible_key(current_key, sample_key)
            energy_complement = 0.3 < abs(current_energy - sample_energy) < 0.7

            # Score calculation
            tempo_score = 1.0 if tempo_match else (1.0 - (tempo_diff / 60))
            key_score = 1.0 if key_compatible else 0.5
            energy_score = 1.0 if energy_complement else 0.7

            compatibility = (tempo_score + key_score + energy_score) / 3

            reason = []
            if tempo_match:
                reason.append("Matching tempo")
            if key_compatible:
                reason.append(f"Compatible key ({sample_key})")
            if energy_complement:
                reason.append("Good energy balance")

            pairings.append(
                SamplePairing(
                    sample_name=sample_name,
                    reason=" + ".join(reason) if reason else "Good pairing",
                    compatibility_score=max(0, min(1, compatibility)),
                    genre=self.detect_genre(sample),
                    tempo_match=tempo_match,
                    key_compatible=key_compatible
                )
            )

        # Sort by score
        pairings.sort(key=lambda x: x.compatibility_score, reverse=True)
        return pairings[:5]

    def get_context_tips(self, context: Dict[str, Any], limit: int = 3) -> List[str]:
        """
        Get context-aware tips

        Args:
            context: Current context (analyzed_count, current_genre, user_level, etc.)
            limit: Max tips

        Returns:
            List of tip strings
        """
        tips: List[str] = []
        analyzed_count = context.get("analyzed_count", 0)
        current_genre = context.get("current_genre", GenreType.UNKNOWN)
        user_level = context.get("user_level", "beginner")

        # Workflow tips
        if analyzed_count == 0:
            tips.append("💡 Start by analyzing your first sample to get detailed audio features")
        elif analyzed_count == 1:
            tips.append("💡 Try comparing samples to see how they differ")
        elif analyzed_count == 5:
            tips.append("💡 Add tags to organize your samples for quick access")

        # Genre tips
        if current_genre != GenreType.UNKNOWN:
            advice = self.get_genre_advice(current_genre)
            if advice:
                if len(advice.tempo_range) > 0:
                    tips.append(
                        f"🎵 {current_genre.value}: Typical tempo {advice.tempo_range[0]}-{advice.tempo_range[1]} BPM"
                    )

        # Difficulty-based tips
        if user_level == "beginner":
            tips.append("📚 Check out the settings to customize the theme and analysis levels")
        elif user_level == "intermediate":
            tips.append("🔧 Try using the comparison feature to analyze sample differences")
        elif user_level == "advanced":
            tips.append("⚙️ Consider creating custom presets for your workflow")

        return tips[:limit]

    def _is_compatible_key(self, key1: str, key2: str) -> bool:
        """Check if two keys are musically compatible"""
        # Relative minor/major
        relative_pairs = [
            ("C major", "A minor"),
            ("D major", "B minor"),
            ("E major", "C# minor"),
            ("F major", "D minor"),
            ("G major", "E minor"),
            ("A major", "F# minor"),
            ("B major", "G# minor"),
        ]

        # Circle of fifths (5 semitones)
        circle_pairs = [
            ("C major", "G major"),
            ("G major", "D major"),
            ("D major", "A major"),
            ("A major", "E major"),
            ("E major", "B major"),
            ("B major", "F# major"),
        ]

        return (
            (key1, key2) in relative_pairs
            or (key2, key1) in relative_pairs
            or (key1, key2) in circle_pairs
            or (key2, key1) in circle_pairs
            or key1 == key2
        )

    def format_pairing_suggestion(self, pairing: SamplePairing) -> str:
        """Format pairing suggestion for display"""
        confidence = "🟢" if pairing.compatibility_score > 0.8 else "🟡" if pairing.compatibility_score > 0.6 else "🔴"
        return (
            f"{confidence} {pairing.sample_name}\n"
            f"   {pairing.reason}\n"
            f"   Score: {pairing.compatibility_score:.0%}"
        )


# Global singleton instance
_ai_coach: Optional[AICoach] = None


def get_ai_coach() -> AICoach:
    """Get or create AI coach singleton"""
    global _ai_coach
    if _ai_coach is None:
        _ai_coach = AICoach()
    return _ai_coach
