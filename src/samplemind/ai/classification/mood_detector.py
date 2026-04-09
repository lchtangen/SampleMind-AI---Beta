"""
Mood Detector — Russell Circumplex Model (Step 18) — SampleMind v3.0

Maps audio features onto the 2-D Russell circumplex space:
  - Valence axis: negative (sad/tense) ↔ positive (happy/content)
  - Arousal axis: low (calm/sleepy) ↔ high (excited/active)

The quadrant determines a primary mood label:
  High valence + High arousal  → Joyful / Euphoric / Energetic
  High valence + Low arousal   → Content / Relaxed / Peaceful
  Low valence  + High arousal  → Tense / Aggressive / Anxious
  Low valence  + Low arousal   → Sad / Melancholic / Dark

A lightweight CNN head (or CLAP text embedding fallback) can be swapped in
when `transformers` / `torch` are available.  Falls back to heuristic rules.

Usage::

    detector = MoodDetector()
    result = detector.detect(y, sr)
    print(result.valence, result.arousal, result.primary_mood)

    result = detector.detect_file("sample.wav")
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# ── Mood label map (Russell quadrant → labels) ────────────────────────────────

_MOOD_LABELS: Dict[str, List[str]] = {
    "high_valence_high_arousal": [
        "Euphoric", "Joyful", "Energetic", "Uplifting", "Excited", "Triumphant",
    ],
    "high_valence_low_arousal": [
        "Peaceful", "Relaxed", "Content", "Dreamy", "Serene", "Nostalgic",
    ],
    "low_valence_high_arousal": [
        "Tense", "Aggressive", "Anxious", "Intense", "Dark", "Menacing",
    ],
    "low_valence_low_arousal": [
        "Melancholic", "Sad", "Gloomy", "Somber", "Haunting", "Brooding",
    ],
}

# Mood → sub-genre affinity hints (useful for production decisions)
MOOD_PRODUCTION_HINTS: Dict[str, str] = {
    "Euphoric": "Big room drops, festival leads, supersaw stacks",
    "Joyful": "Catchy hooks, bright pads, upbeat chord progressions",
    "Energetic": "Driving kicks, layered percussion, high-energy fills",
    "Uplifting": "Rising arpeggios, major chord progressions, string swells",
    "Excited": "Fast attack transients, high BPM synths, tight sidechain",
    "Triumphant": "Brass stabs, anthemic chords, stadium reverb",
    "Peaceful": "Soft reverb tails, minimal percussion, gentle pads",
    "Relaxed": "Warm bass, low-pass filtered highs, chill groove",
    "Content": "Balanced mix, moderate dynamics, organic textures",
    "Dreamy": "Heavy reverb, tape delay, washed-out pads",
    "Serene": "Nature sounds, gentle piano, sparse arrangement",
    "Nostalgic": "Vinyl crackle, lo-fi elements, dusty drums",
    "Tense": "Dissonant chords, sharp transients, sparse silence",
    "Aggressive": "Distortion, heavy sidechain, punchy kicks",
    "Anxious": "Irregular rhythms, cluster chords, pitch modulation",
    "Intense": "Dense mix, wide stereo, building tension",
    "Dark": "Sub-bass, minor keys, detuned oscillators",
    "Menacing": "Low-end weight, slow tempo, growl bass",
    "Melancholic": "Minor scales, sparse melody, room ambience",
    "Sad": "Slow tempo, minor chords, soft dynamics",
    "Gloomy": "Dark reverb, muted tones, downward melody",
    "Somber": "Sparse piano, low-mid frequency weight, restrained dynamics",
    "Haunting": "Bell tones, ghostly pad layers, long reverb",
    "Brooding": "Low-passed everything, minor thirds, deep bass",
}


# ── Result dataclass ──────────────────────────────────────────────────────────


@dataclass
class MoodResult:
    """Russell circumplex mood analysis result."""

    # Core circumplex values (−1.0 to +1.0)
    valence: float = 0.0
    arousal: float = 0.0

    # Quadrant labels (ordered by confidence)
    moods: List[str] = field(default_factory=list)
    primary_mood: str = "Unknown"
    confidence: float = 0.0

    # Production hint for the primary mood
    production_hint: str = ""

    # Classification method
    method: str = "heuristic"  # heuristic | clap | ensemble


# ── Detector ──────────────────────────────────────────────────────────────────


class MoodDetector:
    """
    Russell Circumplex mood detector.

    Maps audio features → valence/arousal → mood labels.
    Optionally uses CLAP embeddings for richer mood detection.
    """

    def __init__(self, use_clap: bool = True) -> None:
        self.use_clap = use_clap
        self._clap = None  # lazy-loaded

    # ── Public API ────────────────────────────────────────────────────────────

    def detect(self, y: np.ndarray, sr: int) -> MoodResult:
        """
        Detect mood from a raw audio signal.

        Returns a MoodResult with valence/arousal coordinates and mood labels.
        """
        result = MoodResult()

        # Stage 1: heuristic valence/arousal estimation
        valence, arousal = self._heuristic_valence_arousal(y, sr)

        # Stage 2: CLAP mood embeddings (optional)
        if self.use_clap:
            clap_valence, clap_arousal = self._clap_valence_arousal(y, sr)
            if clap_valence is not None:
                # Blend: 60% CLAP + 40% heuristic
                valence = 0.6 * clap_valence + 0.4 * valence
                arousal = 0.6 * clap_arousal + 0.4 * arousal
                result.method = "ensemble"

        result.valence = round(float(valence), 4)
        result.arousal = round(float(arousal), 4)

        # Map to quadrant
        quadrant = _quadrant(valence, arousal)
        labels = _MOOD_LABELS.get(quadrant, ["Unknown"])

        # Confidence: distance from center (0,0) → max at (±1, ±1)
        dist = math.sqrt(valence ** 2 + arousal ** 2) / math.sqrt(2)
        result.confidence = round(min(dist, 1.0), 4)

        # Score labels by proximity
        result.moods = labels[: min(3, len(labels))]
        result.primary_mood = labels[0]
        result.production_hint = MOOD_PRODUCTION_HINTS.get(labels[0], "")

        return result

    def detect_file(self, file_path: str | Path, sample_rate: int = 22050) -> MoodResult:
        """Load and detect mood from an audio file."""
        try:
            import librosa

            y, sr = librosa.load(str(file_path), sr=sample_rate, mono=True)
            return self.detect(y, sr)
        except Exception as exc:
            logger.error("MoodDetector failed for %s: %s", file_path, exc)
            return MoodResult()

    # ── Heuristic ─────────────────────────────────────────────────────────────

    @staticmethod
    def _heuristic_valence_arousal(y: np.ndarray, sr: int) -> Tuple[float, float]:
        """
        Estimate valence and arousal from spectral + rhythmic features.

        Returns (valence, arousal) in range [−1, +1].
        """
        try:
            import librosa

            # ── Arousal features ──────────────────────────────────────────
            # High RMS, fast tempo, high spectral centroid → high arousal
            rms = float(np.mean(librosa.feature.rms(y=y)))
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            tempo_arr, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
            bpm = float(tempo_arr) if np.isscalar(tempo_arr) else float(tempo_arr[0])
            centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))

            # Normalize each to [0, 1]
            rms_norm = min(rms / 0.3, 1.0)
            bpm_norm = min(max((bpm - 60) / 140, 0.0), 1.0)  # 60→200 BPM range
            centroid_norm = min(centroid / 8000, 1.0)

            arousal_raw = 0.4 * rms_norm + 0.35 * bpm_norm + 0.25 * centroid_norm
            arousal = (arousal_raw - 0.5) * 2  # scale to [-1, +1]

            # ── Valence features ──────────────────────────────────────────
            # Major key, high chroma brightness, smooth dynamics → high valence
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            chroma_mean = np.mean(chroma, axis=1)

            # Mode estimation: compare major vs minor chroma profiles
            major_template = np.array([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1], dtype=float)
            minor_template = np.array([1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0], dtype=float)

            # Try all 12 rotations to find best fit
            best_major, best_minor = 0.0, 0.0
            for i in range(12):
                rotated = np.roll(chroma_mean, -i)
                major_sim = float(np.dot(rotated, major_template))
                minor_sim = float(np.dot(rotated, minor_template))
                if major_sim > best_major:
                    best_major = major_sim
                if minor_sim > best_minor:
                    best_minor = minor_sim

            mode_score = (best_major - best_minor) / max(best_major + best_minor, 1e-9)
            # mode_score > 0 → major (positive valence), < 0 → minor (negative valence)

            # Dynamic range as valence indicator (smooth = peaceful = positive valence)
            dynamic_range = float(np.max(np.abs(y))) - float(np.mean(np.abs(y)))
            dynamic_norm = 1.0 - min(dynamic_range / 0.5, 1.0)  # smooth → 1

            valence = 0.6 * mode_score + 0.4 * dynamic_norm * 2 - 0.4
            valence = max(min(valence, 1.0), -1.0)

            return float(valence), float(arousal)

        except Exception as exc:
            logger.warning("Heuristic valence/arousal failed: %s", exc)
            return 0.0, 0.0

    def _clap_valence_arousal(
        self, y: np.ndarray, sr: int
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Estimate valence/arousal via CLAP text-audio similarity.

        Computes similarity against polar-opposite mood prompts and derives
        valence/arousal from the score differences.
        """
        if self._clap is None:
            self._clap = _load_clap()
        if self._clap is None:
            return None, None

        try:
            processor, model = self._clap
            import torch
            import librosa

            y_48k = librosa.resample(y, orig_sr=sr, target_sr=48000)

            prompts = [
                "happy joyful uplifting music",    # +valence
                "sad dark melancholic music",       # -valence
                "energetic aggressive intense music",  # +arousal
                "calm peaceful relaxing music",        # -arousal
            ]

            audio_inputs = processor(
                audios=[y_48k], sampling_rate=48000, return_tensors="pt", padding=True
            )
            text_inputs = processor(
                text=prompts, return_tensors="pt", padding=True
            )

            with torch.no_grad():
                audio_emb = model.get_audio_features(**audio_inputs)
                text_emb = model.get_text_features(**text_inputs)

            audio_emb = audio_emb / audio_emb.norm(dim=-1, keepdim=True)
            text_emb = text_emb / text_emb.norm(dim=-1, keepdim=True)
            sims = (audio_emb @ text_emb.T).squeeze(0).tolist()

            # sims[0]=happy, sims[1]=sad, sims[2]=energetic, sims[3]=calm
            valence = float(sims[0]) - float(sims[1])
            arousal = float(sims[2]) - float(sims[3])

            return valence, arousal

        except Exception as exc:
            logger.warning("CLAP mood detection failed: %s", exc)
            return None, None


# ── Helpers ───────────────────────────────────────────────────────────────────


def _quadrant(valence: float, arousal: float) -> str:
    """Map (valence, arousal) coordinates to a Russell quadrant key."""
    if valence >= 0 and arousal >= 0:
        return "high_valence_high_arousal"
    if valence >= 0 and arousal < 0:
        return "high_valence_low_arousal"
    if valence < 0 and arousal >= 0:
        return "low_valence_high_arousal"
    return "low_valence_low_arousal"


def _load_clap():
    """Lazy-load CLAP model. Returns (processor, model) or None."""
    try:
        from transformers import ClapModel, ClapProcessor

        model_id = "laion/clap-htsat-unfused"
        processor = ClapProcessor.from_pretrained(model_id)
        model = ClapModel.from_pretrained(model_id)
        model.eval()
        return processor, model
    except Exception as exc:
        logger.info("CLAP not available for mood: %s", exc)
        return None
