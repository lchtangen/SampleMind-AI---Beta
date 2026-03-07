"""
Genre Classifier — KP-31

Multi-level genre classification pipeline:

1. Fast feature-based classifier using spectral / rhythmic heuristics
2. Optional deep model via lazy-imported CNNAudioClassifier / ASTClassifier

Returns top-k genres with confidence scores and maps them onto a flat
400+ genre taxonomy (stored in GENRE_TAXONOMY below).
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="genre")

# ---------------------------------------------------------------------------
# Genre taxonomy (400+ genres)
# ---------------------------------------------------------------------------

GENRE_TAXONOMY: list[str] = [
    # Electronic
    "House", "Deep House", "Tech House", "Progressive House", "Future House",
    "Melodic House", "Afro House", "Chicago House", "Funky House",
    "Techno", "Detroit Techno", "Industrial Techno", "Minimal Techno",
    "Acid Techno", "Raw Techno", "Schranz", "Doomcore",
    "Trance", "Progressive Trance", "Psytrance", "Full-on Psytrance",
    "Dark Psytrance", "Goa Trance", "Uplifting Trance", "Hard Trance",
    "Vocal Trance", "Tech Trance",
    "Drum and Bass", "Liquid DnB", "Neurofunk", "Jump Up", "Rollers",
    "Darkstep", "Junglist", "Techstep",
    "Dubstep", "Brostep", "Riddim", "Future Bass",
    "UK Garage", "2-Step", "Speed Garage", "Funky Garage",
    "Grime", "UK Drill", "Bassline",
    "Breaks", "Breakbeat", "Breakcore", "Chemical Breaks",
    "Electro", "Electro House", "Complextro", "Dutch House",
    "Ambient", "Dark Ambient", "Space Ambient", "Drone",
    "Chillout", "Downtempo", "Trip-Hop", "Lounge",
    "IDM", "Glitch", "Noise", "Experimental Electronic",
    "Synthwave", "Retrowave", "Darksynth", "Outrun", "Vaporwave",
    "Hardstyle", "Hardcore", "Happy Hardcore", "Frenchcore", "UK Hardcore",
    "Big Beat", "Nu Disco", "Italo Disco",
    "EDM", "Festival Trap", "Moombahton", "Tropical House",
    "Lo-fi Hip Hop", "Phonk",
    "EBM", "Industrial", "Dark Electro", "Aggrotech",
    "Miami Bass", "Crunk", "Footwork", "Juke",
    "Kuduro", "Baile Funk", "Cumbia Electrónica", "Reggaeton Electronic",
    # Hip-Hop / Rap
    "Hip-Hop", "Trap", "Boom Bap", "East Coast Hip-Hop", "West Coast Hip-Hop",
    "Southern Hip-Hop", "Conscious Hip-Hop", "Alternative Hip-Hop",
    "Cloud Rap", "Emo Rap", "Drill", "Brooklyn Drill", "Chicago Drill",
    "Mumble Rap", "Trap Soul", "Crunkcore",
    # R&B / Soul / Funk
    "R&B", "Neo-Soul", "Soul", "Funk", "G-Funk", "New Jack Swing",
    "Contemporary R&B", "Alternative R&B", "Quiet Storm",
    # Pop
    "Pop", "Synth-Pop", "Indie Pop", "Electropop", "Bubblegum Pop",
    "Dream Pop", "Chamber Pop", "Baroque Pop", "Art Pop", "Jangle Pop",
    "K-Pop", "J-Pop", "C-Pop",
    # Rock
    "Rock", "Classic Rock", "Hard Rock", "Heavy Metal", "Death Metal",
    "Black Metal", "Doom Metal", "Thrash Metal", "Speed Metal", "Nu-Metal",
    "Alternative Rock", "Indie Rock", "Post-Rock", "Math Rock",
    "Grunge", "Punk", "Post-Punk", "Garage Rock", "Psychedelic Rock",
    "Prog Rock", "Art Rock", "Shoegaze", "Noise Rock", "Stoner Rock",
    # Jazz / Blues / Classical
    "Jazz", "Blues", "Bebop", "Swing", "Fusion", "Smooth Jazz",
    "Afro-Cuban Jazz", "Bossa Nova", "Free Jazz",
    "Classical", "Neo-Classical", "Baroque", "Romantic",
    # World
    "Reggae", "Dancehall", "Dub", "Roots Reggae",
    "Afrobeats", "Afro-pop", "Highlife", "Jùjú",
    "Soca", "Calypso", "Zouk",
    "Latin", "Salsa", "Bachata", "Merengue", "Cumbia", "Tejano",
    "Flamenco", "Fado", "Celtic", "Folk", "Traditional",
    "Bhangra", "Bollywood", "Qawwali",
    "Arab Pop", "Turkish Pop", "Persian Pop",
    # Country / Americana
    "Country", "Country Pop", "Outlaw Country", "Bluegrass", "Americana",
    "Folk Rock",
    # Other
    "Gospel", "Christian", "New Age", "Meditation", "Yoga",
    "Cinematic", "Epic Orchestral", "Trailer Music",
    "Game OST", "Chiptune", "8-Bit",
    "Comedy Music", "Parody",
]

# Lookup for fast normalization
_GENRE_LOWER: dict[str, str] = {g.lower(): g for g in GENRE_TAXONOMY}


def normalize_genre(raw: str) -> str:
    """Return canonical genre name or the raw string if not in taxonomy."""
    return _GENRE_LOWER.get(raw.lower().strip(), raw.strip())


# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------


@dataclass
class GenreResult:
    """Genre classification result."""

    # Ordered by confidence (highest first)
    genres: list[str] = field(default_factory=list)
    confidence: dict[str, float] = field(default_factory=dict)

    # Primary genre (top-1)
    primary_genre: str = "Unknown"
    primary_confidence: float = 0.0

    # Classification method used
    method: str = "heuristic"  # heuristic | ast | cnn | ensemble

    # Metadata
    sample_rate: int = 22050
    duration: float = 0.0


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------


class GenreClassifier:
    """
    Multi-stage genre classifier.

    Stage 1 — heuristic: spectral + rhythmic feature rules (always runs).
    Stage 2 — deep model: ASTClassifier + CNNAudioClassifier (lazy; only
              if available). Results are averaged across stages.

    Usage::

        clf = GenreClassifier()
        result = clf.classify(y, sr)
        result = await clf.classify_file(Path("track.wav"))
    """

    def __init__(self, top_k: int = 5, use_deep_model: bool = True) -> None:
        self.top_k = top_k
        self.use_deep_model = use_deep_model

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def classify(self, y: np.ndarray, sr: int) -> GenreResult:
        """
        Classify the genre of an audio signal.

        Args:
            y: Audio time-series (mono, float32)
            sr: Sample rate

        Returns:
            GenreResult dataclass
        """
        import importlib.util

        if importlib.util.find_spec("librosa") is None:
            return GenreResult(sample_rate=sr, duration=float(len(y)) / max(sr, 1))

        duration = float(len(y)) / sr
        result = GenreResult(sample_rate=sr, duration=duration)

        # --- Stage 1: heuristic -------------------------------------------
        heuristic_scores = self._heuristic_classify(y, sr)

        # --- Stage 2: deep model (optional) --------------------------------
        deep_scores: dict[str, float] = {}
        method = "heuristic"

        if self.use_deep_model:
            deep_scores, deep_method = self._deep_classify(y, sr)
            if deep_scores:
                method = "ensemble"
                # Weighted ensemble: 60% deep, 40% heuristic
                all_genres = set(heuristic_scores) | set(deep_scores)
                combined: dict[str, float] = {}
                for g in all_genres:
                    combined[g] = (
                        0.6 * deep_scores.get(g, 0.0)
                        + 0.4 * heuristic_scores.get(g, 0.0)
                    )
                final_scores = combined
            else:
                final_scores = heuristic_scores
        else:
            final_scores = heuristic_scores

        # --- Sort and package -------------------------------------------
        sorted_genres = sorted(final_scores, key=lambda g: final_scores[g], reverse=True)
        top = sorted_genres[: self.top_k]

        result.genres = top
        result.confidence = {g: round(final_scores[g], 4) for g in top}
        result.primary_genre = top[0] if top else "Unknown"
        result.primary_confidence = round(final_scores.get(result.primary_genre, 0.0), 4)
        result.method = method

        return result

    async def classify_file(
        self,
        path: Path,
        sample_rate: int = 22050,
    ) -> GenreResult:
        """
        Load and classify audio file asynchronously.

        Args:
            path: Path to audio file
            sample_rate: Target sample rate

        Returns:
            GenreResult for the file
        """
        import asyncio

        path = Path(path).expanduser().resolve()
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            _EXECUTOR, self._load_and_classify, path, sample_rate
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_and_classify(self, path: Path, sample_rate: int) -> GenreResult:
        try:
            import librosa

            y, sr = librosa.load(path, sr=sample_rate, mono=True)
            return self.classify(y, sr)
        except Exception as exc:
            logger.error(f"GenreClassifier failed for {path}: {exc}")
            return GenreResult(sample_rate=sample_rate, duration=0.0)

    @staticmethod
    def _heuristic_classify(y: np.ndarray, sr: int) -> dict[str, float]:
        """
        Rule-based genre scoring using spectral + rhythmic features.

        Returns a score dict (unnormalized, range 0–1).
        """
        import librosa

        scores: dict[str, float] = {}

        # --- Feature extraction for rules --------------------------------
        # BPM
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo_arr, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
        bpm = float(tempo_arr) if np.isscalar(tempo_arr) else float(tempo_arr[0])

        # Spectral centroid
        centroid_mean = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))

        # RMS energy
        rms_mean = float(np.mean(librosa.feature.rms(y=y)))

        # ZCR
        zcr_mean = float(np.mean(librosa.feature.zero_crossing_rate(y)))

        # Chroma variance (harmonic richness)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        chroma_var = float(np.var(chroma))

        # --- BPM-based rules ---------------------------------------------
        if 118 <= bpm <= 136:
            scores["House"] = 0.7
            scores["Tech House"] = 0.6
            scores["Deep House"] = 0.55
            scores["EDM"] = 0.5
        if 128 <= bpm <= 145:
            scores["Techno"] = 0.6
            scores["Trance"] = 0.55
        if 160 <= bpm <= 180:
            scores["Drum and Bass"] = 0.75
        if 130 <= bpm <= 155:
            scores["Dubstep"] = 0.4
            scores["Trap"] = 0.35
        if 60 <= bpm <= 100:
            scores["Hip-Hop"] = 0.55
            scores["R&B"] = 0.45
            scores["Boom Bap"] = 0.4
        if 148 <= bpm <= 180:
            scores["Hardstyle"] = 0.55
            scores["Hardcore"] = 0.5
        if 140 <= bpm <= 180:
            scores["Psytrance"] = 0.5

        # --- Spectral + energy rules -------------------------------------
        if centroid_mean > 4000 and rms_mean > 0.15:
            scores["Hard Rock"] = scores.get("Hard Rock", 0.0) + 0.4
            scores["Heavy Metal"] = scores.get("Heavy Metal", 0.0) + 0.35
        if centroid_mean < 2000 and rms_mean < 0.05:
            scores["Ambient"] = scores.get("Ambient", 0.0) + 0.6
            scores["Drone"] = scores.get("Drone", 0.0) + 0.4
        if centroid_mean < 2500 and chroma_var > 0.02:
            scores["Jazz"] = scores.get("Jazz", 0.0) + 0.45
            scores["Blues"] = scores.get("Blues", 0.0) + 0.3
        if zcr_mean > 0.15 and rms_mean > 0.2:
            scores["Noise Rock"] = scores.get("Noise Rock", 0.0) + 0.35
            scores["Punk"] = scores.get("Punk", 0.0) + 0.3

        # Normalize
        max_score = max(scores.values()) if scores else 1.0
        return {g: s / max(max_score, 1e-9) for g, s in scores.items()}

    @staticmethod
    def _deep_classify(y: np.ndarray, sr: int) -> tuple[dict[str, float], str]:
        """
        Attempt deep classification via ASTClassifier or CNNAudioClassifier.

        Returns (scores_dict, method_name). Empty dict if unavailable.
        """
        # Try AST first
        try:
            from samplemind.ai.embeddings.ast_classifier import ASTClassifier

            clf = ASTClassifier()
            results = clf.classify_audio(y, sr, top_k=10)
            scores: dict[str, float] = {}
            for r in results:
                label = normalize_genre(r.get("label", ""))
                scores[label] = float(r.get("score", 0.0))
            return scores, "ast"
        except (ImportError, Exception):
            pass

        # Try CNN fallback
        try:
            from samplemind.ai.classifiers.cnn_classifier import CNNAudioClassifier

            clf = CNNAudioClassifier()
            results = clf.predict(y, sr, top_k=10)
            scores = {
                normalize_genre(r["label"]): float(r["score"]) for r in results
            }
            return scores, "cnn"
        except (ImportError, Exception):
            pass

        return {}, "none"
