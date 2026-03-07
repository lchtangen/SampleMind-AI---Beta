"""
Timbral Analyzer — KP-29

Extracts high-level timbral descriptors:

- Brightness, warmth, roughness (perceptual timbral axes)
- Texture type (granular / sustained / transient / noisy)
- Instrument labels + confidence (via lazy ASTClassifier)
- Valence and arousal (Russell circumplex model approximation)
- Mood label: dark | euphoric | aggressive | chill | melancholic | epic
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="timbral")

# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------


@dataclass
class TimbralFeatures:
    """Perceptual timbral feature set."""

    # --- Timbral axes (0–1) ---
    brightness_score: float = 0.5   # high centroid → bright
    warmth_score: float = 0.5       # low centroid + strong low-mid → warm
    roughness_score: float = 0.0    # high zcr + irregular envelope → rough

    # --- Texture type ---
    texture_type: str = "unknown"   # granular | sustained | transient | noisy

    # --- Instrument detection (lazy ASTClassifier) ---
    instrument_labels: list[str] = field(default_factory=list)
    instrument_confidence: dict[str, float] = field(default_factory=dict)

    # --- Russell circumplex (−1 to +1) ---
    valence: float = 0.0    # negative = negative affect, positive = positive affect
    arousal: float = 0.0    # negative = calm, positive = energetic

    # --- Mood ---
    mood_label: str = "unknown"  # dark | euphoric | aggressive | chill | melancholic | epic

    # Metadata
    sample_rate: int = 22050
    duration: float = 0.0


# ---------------------------------------------------------------------------
# Analyzer
# ---------------------------------------------------------------------------


class TimbralAnalyzer:
    """
    Extracts perceptual timbral descriptors from audio.

    Instrument detection uses the Microsoft AST classifier from
    ``samplemind.ai.embeddings.ast_classifier`` (lazy-imported — no error
    if unavailable, ``instrument_labels`` will be empty).

    Usage::

        analyzer = TimbralAnalyzer()
        features = analyzer.analyze(y, sr, key="A", mode="minor")
        features = await analyzer.analyze_file(Path("pad.wav"))
    """

    def __init__(self, top_k_instruments: int = 5) -> None:
        self.top_k_instruments = top_k_instruments

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(
        self,
        y: np.ndarray,
        sr: int,
        key: str | None = None,
        mode: str | None = None,
    ) -> TimbralFeatures:
        """
        Compute timbral features.

        Args:
            y: Audio time-series (mono, float32)
            sr: Sample rate
            key: Optional key name ("C", "A", …) from harmonic analysis
            mode: Optional mode ("major" | "minor") from harmonic analysis

        Returns:
            TimbralFeatures dataclass
        """
        try:
            import librosa
        except ImportError:
            logger.warning("librosa not available — returning mock TimbralFeatures")
            return TimbralFeatures(sample_rate=sr, duration=float(len(y)) / max(sr, 1))

        duration = float(len(y)) / sr
        features = TimbralFeatures(sample_rate=sr, duration=duration)

        # --- Low-level features for heuristics ----------------------------
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        rms = librosa.feature.rms(y=y)[0]
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)

        centroid_mean = float(np.mean(centroid))
        rms_mean = float(np.mean(rms))
        zcr_mean = float(np.mean(zcr))
        chroma_var = float(np.var(chroma))

        # --- Perceptual timbral axes --------------------------------------
        # Brightness: normalise centroid to 0–1 (range 0–8000 Hz typical)
        features.brightness_score = round(float(np.clip(centroid_mean / 8000.0, 0.0, 1.0)), 3)

        # Warmth: inverse of brightness + low energy weight
        low_centroid_factor = 1.0 - features.brightness_score
        features.warmth_score = round(float(np.clip(low_centroid_factor * 0.7 + rms_mean * 3.0, 0.0, 1.0)), 3)

        # Roughness: high ZCR + high RMS variance → rough/distorted
        rms_var = float(np.var(rms))
        features.roughness_score = round(float(np.clip(zcr_mean * 10.0 + rms_var * 20.0, 0.0, 1.0)), 3)

        # --- Texture type -------------------------------------------------
        features.texture_type = self._classify_texture(rms_mean, zcr_mean, rms_var, duration)

        # --- Russell circumplex heuristic ---------------------------------
        # Arousal: driven by energy (RMS), centroid, ZCR
        arousal_raw = (
            0.4 * float(np.clip(rms_mean / 0.2, 0.0, 1.0))
            + 0.35 * features.brightness_score
            + 0.25 * float(np.clip(zcr_mean * 20.0, 0.0, 1.0))
        )
        features.arousal = round(float(np.clip(arousal_raw * 2.0 - 1.0, -1.0, 1.0)), 3)

        # Valence: driven by major mode, low dissonance, tonal stability
        mode_score = 0.3 if mode == "major" else (-0.2 if mode == "minor" else 0.0)
        chroma_stability = float(np.clip(1.0 - chroma_var * 5.0, 0.0, 1.0))
        valence_raw = mode_score + 0.4 * chroma_stability + 0.1 * (1.0 - features.roughness_score)
        features.valence = round(float(np.clip(valence_raw, -1.0, 1.0)), 3)

        # --- Mood label ---------------------------------------------------
        features.mood_label = self._map_mood(features.arousal, features.valence)

        # --- Instrument detection (lazy) ----------------------------------
        features.instrument_labels, features.instrument_confidence = (
            self._detect_instruments(y, sr)
        )

        return features

    async def analyze_file(
        self,
        path: Path,
        sample_rate: int = 22050,
    ) -> TimbralFeatures:
        """
        Load and analyze audio file asynchronously.

        Args:
            path: Path to audio file
            sample_rate: Target sample rate

        Returns:
            TimbralFeatures for the file
        """
        import asyncio

        path = Path(path).expanduser().resolve()
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            _EXECUTOR, self._load_and_analyze, path, sample_rate
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_and_analyze(self, path: Path, sample_rate: int) -> TimbralFeatures:
        try:
            import librosa

            y, sr = librosa.load(path, sr=sample_rate, mono=True)
            return self.analyze(y, sr)
        except Exception as exc:
            logger.error(f"TimbralAnalyzer failed for {path}: {exc}")
            return TimbralFeatures(sample_rate=sample_rate, duration=0.0)

    @staticmethod
    def _classify_texture(
        rms_mean: float,
        zcr_mean: float,
        rms_var: float,
        duration: float,
    ) -> str:
        """Heuristic texture categorisation."""
        if rms_var > 0.005:
            if zcr_mean > 0.1:
                return "transient"
            return "granular"
        if zcr_mean > 0.15:
            return "noisy"
        return "sustained"

    @staticmethod
    def _map_mood(arousal: float, valence: float) -> str:
        """
        Map Russell circumplex coordinates to a mood label.

        Quadrants::

            high arousal + high valence  → euphoric / epic
            high arousal + low valence   → aggressive / dark
            low arousal  + high valence  → chill
            low arousal  + low valence   → melancholic / dark
        """
        if arousal >= 0.3 and valence >= 0.2:
            return "euphoric" if arousal < 0.7 else "epic"
        if arousal >= 0.3 and valence < 0.0:
            return "aggressive"
        if arousal < 0.0 and valence >= 0.1:
            return "chill"
        if arousal < 0.0 and valence < 0.0:
            return "dark" if valence < -0.3 else "melancholic"
        # neutral zone
        return "chill" if valence >= 0.0 else "dark"

    def _detect_instruments(
        self,
        y: np.ndarray,
        sr: int,
    ) -> tuple[list[str], dict[str, float]]:
        """
        Attempt instrument detection via ASTClassifier (lazy import).

        Falls back to an empty result if the classifier is unavailable.
        """
        try:
            from samplemind.ai.embeddings.ast_classifier import ASTClassifier

            clf = ASTClassifier()
            results = clf.classify_audio(y, sr, top_k=self.top_k_instruments)
            labels = [r["label"] for r in results]
            confidence = {r["label"]: round(r["score"], 4) for r in results}
            return labels, confidence

        except (ImportError, Exception) as exc:
            logger.debug(f"Instrument detection unavailable: {exc}")
            return [], {}
