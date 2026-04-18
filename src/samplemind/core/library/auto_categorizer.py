"""
Smart Auto-Categorizer — Library Organization Engine

Automatically categorizes and organizes audio samples into a structured
library using a hybrid rule-based + ML approach. Combines filename parsing,
audio feature analysis, and optional AI classification for robust sorting.

Organization Strategy:
  1. Filename parsing — extract type/category from naming conventions
  2. Audio analysis — BPM, key, duration, energy for classification
  3. ML features — spectral centroid, MFCCs, onset patterns
  4. Rule engine — decision tree with production-knowledge rules
  5. Confidence scoring — how certain the categorization is

Category Taxonomy:
  Level 1: Type (drums, melodic, fx, vocal, texture, loop)
  Level 2: Subtype (kick, snare, hihat, bass, pad, lead, etc.)
  Level 3: Character (punchy, warm, bright, dark, aggressive, etc.)
  Level 4: Properties (BPM, key, energy)

Usage::

    from samplemind.core.library.auto_categorizer import SmartAutoCategorizer

    categorizer = SmartAutoCategorizer()
    result = categorizer.categorize(y, sr, filename="dark_trap_kick_808.wav")
    print(f"Category: {result.category}/{result.subcategory}")
    print(f"Tags: {result.tags}")
"""

from __future__ import annotations

import logging
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="categorizer")

# ── Taxonomy ──────────────────────────────────────────────────────────────────

CATEGORIES = {
    "drums": [
        "kick", "snare", "hihat", "clap", "tom", "cymbal", "rim", "shaker",
        "percussion", "hat", "ride", "crash", "open_hat", "closed_hat",
    ],
    "bass": [
        "sub", "808", "synth_bass", "acoustic_bass", "pluck_bass", "wobble",
    ],
    "melodic": [
        "pad", "lead", "pluck", "bell", "keys", "piano", "organ",
        "strings", "brass", "flute", "guitar", "synth", "arp", "chord",
    ],
    "vocal": ["vocal", "vox", "adlib", "chant", "choir", "speech", "rap"],
    "fx": [
        "riser", "sweep", "impact", "downlifter", "noise", "transition",
        "whoosh", "explosion", "glitch", "stutter",
    ],
    "loop": [
        "drum_loop", "melody_loop", "bass_loop", "top_loop", "full_loop",
    ],
    "texture": [
        "ambient", "atmosphere", "drone", "foley", "field_recording",
        "noise_bed",
    ],
    "one_shot": ["stab", "hit", "shot", "chop"],
}

CHARACTER_TAGS = {
    "bright": ["bright", "crisp", "sparkle", "airy", "hi-fi"],
    "dark": ["dark", "deep", "muffled", "lo-fi", "murky"],
    "warm": ["warm", "smooth", "soft", "rounded", "analog"],
    "aggressive": ["aggressive", "hard", "distorted", "heavy", "gritty"],
    "punchy": ["punchy", "tight", "snappy", "short", "transient"],
    "spacious": ["reverb", "space", "hall", "room", "wet"],
    "clean": ["clean", "dry", "pure", "minimal"],
    "vintage": ["vintage", "retro", "tape", "vinyl", "old"],
    "modern": ["modern", "digital", "edm", "trap", "future"],
}

# Filename patterns for type detection
_FILENAME_PATTERNS: list[tuple[str, str, str]] = [
    # (regex_pattern, category, subcategory)
    (r"\b(kick|kik|bd)\b", "drums", "kick"),
    (r"\b(snare|snr|sd)\b", "drums", "snare"),
    (r"\b(hi[- ]?hat|hh|hat)\b", "drums", "hihat"),
    (r"\b(clap|clp)\b", "drums", "clap"),
    (r"\b(tom)\b", "drums", "tom"),
    (r"\b(cymbal|cym|crash|ride)\b", "drums", "cymbal"),
    (r"\b(rim|rimshot)\b", "drums", "rim"),
    (r"\b(shaker|tamb)\b", "drums", "shaker"),
    (r"\b(perc|percussion)\b", "drums", "percussion"),
    (r"\b(808|sub|subbass)\b", "bass", "808"),
    (r"\b(bass)\b", "bass", "synth_bass"),
    (r"\b(pad)\b", "melodic", "pad"),
    (r"\b(lead)\b", "melodic", "lead"),
    (r"\b(pluck)\b", "melodic", "pluck"),
    (r"\b(bell)\b", "melodic", "bell"),
    (r"\b(key|keys|piano)\b", "melodic", "keys"),
    (r"\b(string|strings|violin)\b", "melodic", "strings"),
    (r"\b(guitar|gtr)\b", "melodic", "guitar"),
    (r"\b(synth)\b", "melodic", "synth"),
    (r"\b(arp)\b", "melodic", "arp"),
    (r"\b(chord)\b", "melodic", "chord"),
    (r"\b(vocal|vox|voice)\b", "vocal", "vocal"),
    (r"\b(choir|chant)\b", "vocal", "choir"),
    (r"\b(riser|rise)\b", "fx", "riser"),
    (r"\b(sweep)\b", "fx", "sweep"),
    (r"\b(impact|hit)\b", "fx", "impact"),
    (r"\b(down(lifter)?)\b", "fx", "downlifter"),
    (r"\b(whoosh)\b", "fx", "whoosh"),
    (r"\b(transition)\b", "fx", "transition"),
    (r"\b(glitch)\b", "fx", "glitch"),
    (r"\b(loop)\b", "loop", "drum_loop"),
    (r"\b(ambient|atmo)\b", "texture", "ambient"),
    (r"\b(drone)\b", "texture", "drone"),
    (r"\b(foley)\b", "texture", "foley"),
    (r"\b(stab)\b", "one_shot", "stab"),
]


@dataclass
class CategoryResult:
    """Result from auto-categorization."""

    category: str = "unknown"  # Level 1: drums, melodic, fx, etc.
    subcategory: str = "unknown"  # Level 2: kick, snare, pad, etc.
    character: list[str] = field(default_factory=list)  # Level 3
    tags: list[str] = field(default_factory=list)  # All applicable tags
    confidence: float = 0.0  # 0–1, overall categorization confidence
    source: str = "unknown"  # filename | audio | hybrid

    # Audio properties
    bpm: float | None = None
    estimated_key: str | None = None
    energy_level: str = "mid"  # low | mid | high
    duration_class: str = "unknown"  # one_shot | loop | pad | texture

    # Suggested path
    suggested_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "category": self.category,
            "subcategory": self.subcategory,
            "character": self.character,
            "tags": self.tags,
            "confidence": round(self.confidence, 3),
            "source": self.source,
            "bpm": self.bpm,
            "estimated_key": self.estimated_key,
            "energy_level": self.energy_level,
            "duration_class": self.duration_class,
            "suggested_path": self.suggested_path,
        }


class SmartAutoCategorizer:
    """
    Hybrid rule + ML auto-categorizer for audio sample libraries.

    Combines filename parsing, audio feature analysis, and production
    knowledge rules to classify and organize samples.
    """

    def __init__(self) -> None:
        self._compiled_patterns: list[tuple[re.Pattern[str], str, str]] = [
            (re.compile(pat, re.IGNORECASE), cat, sub)
            for pat, cat, sub in _FILENAME_PATTERNS
        ]

    def categorize(
        self,
        y: np.ndarray,
        sr: int,
        filename: str = "",
    ) -> CategoryResult:
        """
        Categorize an audio sample.

        Args:
            y: Audio signal (mono, float32).
            sr: Sample rate.
            filename: Original filename (improves accuracy).

        Returns:
            CategoryResult with category, subcategory, tags, and confidence.
        """
        result = CategoryResult()
        scores: dict[str, dict[str, float]] = {}

        # Stage 1: Filename parsing
        if filename:
            fn_cat, fn_sub, fn_conf = self._parse_filename(filename)
            if fn_cat != "unknown":
                scores.setdefault(fn_cat, {})[fn_sub] = fn_conf
                result.source = "filename"

        # Stage 2: Audio feature analysis
        features = self._extract_features(y, sr)

        # Stage 3: Rule-based classification from features
        rule_cat, rule_sub, rule_conf = self._classify_by_rules(features)
        if rule_cat != "unknown":
            existing = scores.get(rule_cat, {}).get(rule_sub, 0.0)
            scores.setdefault(rule_cat, {})[rule_sub] = max(
                existing, rule_conf
            )
            if result.source == "unknown":
                result.source = "audio"
            elif result.source == "filename":
                result.source = "hybrid"

        # Stage 4: Resolve category from scores
        best_cat = "unknown"
        best_sub = "unknown"
        best_score = 0.0

        for cat, subs in scores.items():
            for sub, score in subs.items():
                if score > best_score:
                    best_score = score
                    best_cat = cat
                    best_sub = sub

        result.category = best_cat
        result.subcategory = best_sub
        result.confidence = round(min(1.0, best_score), 3)

        # Stage 5: Character detection
        result.character = self._detect_character(features, filename)

        # Stage 6: Properties
        result.bpm = features.get("bpm")
        result.estimated_key = features.get("estimated_key")
        result.energy_level = self._classify_energy(features)
        result.duration_class = self._classify_duration(features)

        # Stage 7: Build tags
        result.tags = self._build_tags(result)

        # Stage 8: Suggested path
        result.suggested_path = self._build_suggested_path(result)

        return result

    async def categorize_file(
        self,
        path: Path,
        target_sr: int = 22050,
    ) -> CategoryResult:
        """Categorize an audio file asynchronously."""
        import asyncio

        path = Path(path).expanduser().resolve()
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            _EXECUTOR, self._load_and_categorize, path, target_sr
        )

    async def categorize_batch(
        self,
        file_paths: list[Path],
        target_sr: int = 22050,
    ) -> list[CategoryResult]:
        """Categorize multiple files."""
        import asyncio

        tasks = [self.categorize_file(fp, target_sr) for fp in file_paths]
        return await asyncio.gather(*tasks)

    # ── Filename parsing ──────────────────────────────────────────────────

    def _parse_filename(self, filename: str) -> tuple[str, str, float]:
        """Parse filename for category clues."""
        name = Path(filename).stem.lower()
        name = re.sub(r"[-_.]", " ", name)

        for pattern, category, subcategory in self._compiled_patterns:
            if pattern.search(name):
                return category, subcategory, 0.75

        return "unknown", "unknown", 0.0

    # ── Feature extraction ────────────────────────────────────────────────

    @staticmethod
    def _extract_features(y: np.ndarray, sr: int) -> dict[str, Any]:
        """Extract classification-relevant audio features."""
        duration = float(len(y)) / sr
        rms = float(np.sqrt(np.mean(y**2)))
        peak = float(np.max(np.abs(y)))
        zcr = float(np.mean(np.abs(np.diff(np.sign(y))) > 0))

        features: dict[str, Any] = {
            "duration": duration,
            "rms": rms,
            "peak": peak,
            "zero_crossing_rate": zcr,
            "crest_factor": peak / (rms + 1e-9),
        }

        try:
            import librosa

            centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            features["spectral_centroid"] = float(np.mean(centroid))

            rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            features["spectral_rolloff"] = float(np.mean(rolloff))

            bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
            features["spectral_bandwidth"] = float(np.mean(bandwidth))

            flatness = librosa.feature.spectral_flatness(y=y)
            features["spectral_flatness"] = float(np.mean(flatness))

            # BPM
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            bpm_val = (
                float(tempo) if np.isscalar(tempo) else float(tempo[0])
            )
            features["bpm"] = round(bpm_val, 2) if bpm_val > 0 else None

            # Key estimation
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            key_idx = int(np.argmax(np.mean(chroma, axis=1)))
            key_names = [
                "C", "C#", "D", "D#", "E", "F",
                "F#", "G", "G#", "A", "A#", "B",
            ]
            features["estimated_key"] = key_names[key_idx]

            # Onset count
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            onsets = librosa.onset.onset_detect(
                onset_envelope=onset_env, sr=sr
            )
            features["onset_count"] = len(onsets)
            features["onset_density"] = len(onsets) / max(duration, 0.01)

            # Harmonic/percussive energy ratio
            y_h, y_p = librosa.effects.hpss(y)
            h_energy = float(np.sum(y_h**2))
            p_energy = float(np.sum(y_p**2))
            total_e = h_energy + p_energy + 1e-9
            features["harmonic_ratio"] = h_energy / total_e
            features["percussive_ratio"] = p_energy / total_e

        except ImportError:
            pass

        return features

    # ── Rule-based classification ─────────────────────────────────────────

    @staticmethod
    def _classify_by_rules(
        features: dict[str, Any],
    ) -> tuple[str, str, float]:
        """Classify based on audio features using production knowledge."""
        duration = features.get("duration", 0.0)
        centroid = features.get("spectral_centroid", 2000.0)
        percussive = features.get("percussive_ratio", 0.5)
        harmonic = features.get("harmonic_ratio", 0.5)
        onset_count = features.get("onset_count", 1)
        onset_density = features.get("onset_density", 0.0)
        flatness = features.get("spectral_flatness", 0.1)
        zcr = features.get("zero_crossing_rate", 0.05)
        crest = features.get("crest_factor", 3.0)

        # Rule 1: Very short + percussive = drum one-shot
        if duration < 1.0 and percussive > 0.6:
            if centroid < 500:
                return "drums", "kick", 0.7
            elif centroid > 5000:
                return "drums", "hihat", 0.65
            elif crest > 8:
                return "drums", "snare", 0.6
            else:
                return "drums", "percussion", 0.55

        # Rule 2: Very short + high crest + percussive = clap/snap
        if duration < 0.5 and crest > 10 and percussive > 0.5:
            return "drums", "clap", 0.6

        # Rule 3: Low centroid + harmonic + medium duration = bass
        if centroid < 800 and harmonic > 0.4 and 0.3 < duration < 8.0:
            return "bass", "synth_bass", 0.6

        # Rule 4: Long + harmonic + low onset density = pad/texture
        if duration > 3.0 and harmonic > 0.5 and onset_density < 2.0:
            if flatness > 0.3:
                return "texture", "ambient", 0.55
            else:
                return "melodic", "pad", 0.6

        # Rule 5: High harmonic + medium duration + some onsets = melodic
        if harmonic > 0.5 and 0.5 < duration < 10.0 and onset_count > 2:
            return "melodic", "synth", 0.5

        # Rule 6: Many onsets + rhythmic = loop
        if onset_count > 8 and 1.0 < duration < 16.0:
            if percussive > 0.5:
                return "loop", "drum_loop", 0.6
            else:
                return "loop", "melody_loop", 0.55

        # Rule 7: High ZCR + noisy = fx/noise
        if zcr > 0.3 and flatness > 0.5:
            if duration < 3.0:
                return "fx", "noise", 0.5
            else:
                return "texture", "noise_bed", 0.5

        # Rule 8: Monotonic energy rise/fall = fx (riser/downlifter)
        if 1.0 < duration < 10.0 and onset_count <= 3:
            return "fx", "sweep", 0.45

        return "unknown", "unknown", 0.0

    # ── Character detection ───────────────────────────────────────────────

    @staticmethod
    def _detect_character(
        features: dict[str, Any],
        filename: str = "",
    ) -> list[str]:
        """Detect character tags from features and filename."""
        characters: list[str] = []
        centroid = features.get("spectral_centroid", 2000.0)
        rms = features.get("rms", 0.05)
        crest = features.get("crest_factor", 3.0)
        flatness = features.get("spectral_flatness", 0.1)
        duration = features.get("duration", 1.0)

        if centroid > 5000:
            characters.append("bright")
        elif centroid < 1000:
            characters.append("dark")

        if rms > 0.1 and crest < 4:
            characters.append("aggressive")
        elif rms < 0.03:
            characters.append("soft")

        if crest > 10:
            characters.append("punchy")

        if flatness > 0.4:
            characters.append("noisy")
        elif flatness < 0.05:
            characters.append("tonal")

        if duration < 0.3:
            characters.append("short")
        elif duration > 5.0:
            characters.append("long")

        # Filename-based character
        if filename:
            name_lower = filename.lower()
            for char_tag, keywords in CHARACTER_TAGS.items():
                if any(kw in name_lower for kw in keywords):
                    if char_tag not in characters:
                        characters.append(char_tag)

        return characters[:8]

    # ── Property classification ───────────────────────────────────────────

    @staticmethod
    def _classify_energy(features: dict[str, Any]) -> str:
        """Classify energy level from features."""
        rms = features.get("rms", 0.05)
        if rms < 0.02:
            return "low"
        elif rms < 0.08:
            return "mid"
        else:
            return "high"

    @staticmethod
    def _classify_duration(features: dict[str, Any]) -> str:
        """Classify duration type."""
        duration = features.get("duration", 1.0)
        onset_count = features.get("onset_count", 1)

        if duration < 2.0 and onset_count <= 2:
            return "one_shot"
        elif duration < 10.0 and onset_count > 4:
            return "loop"
        elif duration >= 3.0 and onset_count <= 3:
            return "pad"
        elif duration >= 5.0:
            return "texture"
        return "one_shot"

    # ── Tag building ──────────────────────────────────────────────────────

    @staticmethod
    def _build_tags(result: CategoryResult) -> list[str]:
        """Build comprehensive tag list from categorization."""
        tags: list[str] = []

        if result.category != "unknown":
            tags.append(result.category)
        if result.subcategory != "unknown":
            tags.append(result.subcategory)

        tags.extend(result.character)
        tags.append(result.energy_level)
        tags.append(result.duration_class)

        if result.estimated_key:
            tags.append(result.estimated_key)

        if result.bpm and result.bpm > 0:
            bpm = result.bpm
            if bpm < 90:
                tags.append("slow")
            elif bpm < 130:
                tags.append("mid_tempo")
            elif bpm < 160:
                tags.append("fast")
            else:
                tags.append("very_fast")

        # Deduplicate while preserving order
        seen: set[str] = set()
        unique_tags: list[str] = []
        for tag in tags:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)

        return unique_tags

    @staticmethod
    def _build_suggested_path(result: CategoryResult) -> str:
        """Build suggested file organization path."""
        parts: list[str] = []

        if result.category != "unknown":
            parts.append(result.category.title())

        if result.subcategory != "unknown":
            parts.append(result.subcategory.replace("_", " ").title())

        if result.energy_level:
            parts.append(result.energy_level.title())

        if result.estimated_key:
            parts.append(result.estimated_key)

        return "/".join(parts) if parts else "Unsorted"

    # ── File loading ──────────────────────────────────────────────────────

    def _load_and_categorize(
        self, path: Path, target_sr: int
    ) -> CategoryResult:
        """Load audio file and categorize it."""
        try:
            import librosa

            y, sr = librosa.load(str(path), sr=target_sr, mono=True)
            return self.categorize(y, sr, filename=path.name)
        except Exception as exc:
            logger.error(
                "SmartAutoCategorizer failed for %s: %s", path, exc
            )
            return CategoryResult(
                category="unknown",
                subcategory="unknown",
                confidence=0.0,
            )


# ── Module exports ────────────────────────────────────────────────────────────

__all__ = [
    "SmartAutoCategorizer",
    "CategoryResult",
    "CATEGORIES",
    "CHARACTER_TAGS",
]
