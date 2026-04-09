"""
Multi-Label Genre Classifier (Step 17) — SampleMind v3.0

Extends the heuristic GenreClassifier with:
  1. Sigmoid multi-label output (multiple genres can be true simultaneously).
  2. CLAP (Contrastive Language-Audio Pretraining) embedding support for
     semantic genre matching when `transformers` is available.
  3. Camelot Wheel harmonic key detection integrated into the result.

Falls back gracefully to heuristic rules if CLAP / librosa are unavailable.

Usage::

    clf = MultiLabelGenreClassifier(threshold=0.35, top_k=5)
    result = clf.classify_file("sample.wav")
    print(result.primary_genre, result.all_genres)

    # Or from raw audio:
    result = clf.classify(y, sr)
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from samplemind.core.analysis.genre_classifier import (
    GENRE_TAXONOMY,
    GenreResult,
    normalize_genre,
)

logger = logging.getLogger(__name__)

# ── Camelot Wheel ─────────────────────────────────────────────────────────────
# Maps (key, scale) → Camelot position string (e.g. "8A", "3B")

_CAMELOT: Dict[Tuple[str, str], str] = {
    ("C", "major"): "8B",  ("C", "minor"): "5A",
    ("C#", "major"): "3B", ("C#", "minor"): "12A",
    ("Db", "major"): "3B", ("Db", "minor"): "12A",
    ("D", "major"): "10B", ("D", "minor"): "7A",
    ("D#", "major"): "5B", ("D#", "minor"): "2A",
    ("Eb", "major"): "5B", ("Eb", "minor"): "2A",
    ("E", "major"): "12B", ("E", "minor"): "9A",
    ("F", "major"): "7B",  ("F", "minor"): "4A",
    ("F#", "major"): "2B", ("F#", "minor"): "11A",
    ("Gb", "major"): "2B", ("Gb", "minor"): "11A",
    ("G", "major"): "9B",  ("G", "minor"): "6A",
    ("G#", "major"): "4B", ("G#", "minor"): "1A",
    ("Ab", "major"): "4B", ("Ab", "minor"): "1A",
    ("A", "major"): "11B", ("A", "minor"): "8A",
    ("A#", "major"): "6B", ("A#", "minor"): "3A",
    ("Bb", "major"): "6B", ("Bb", "minor"): "3A",
    ("B", "major"): "1B",  ("B", "minor"): "10A",
}


def camelot_key(key: str, scale: str) -> str:
    """Return the Camelot Wheel position for a key/scale pair, or '' if unknown."""
    return _CAMELOT.get((key, scale.lower()), "")


# ── CLAP genre prompts ────────────────────────────────────────────────────────
# Semantic text prompts corresponding to every genre in the taxonomy.
# The CLAP model scores audio embeddings against these text embeddings.

_CLAP_GENRE_PROMPTS: List[str] = [f"a {g} music sample" for g in GENRE_TAXONOMY]


# ── Result dataclass ──────────────────────────────────────────────────────────


@dataclass
class MultiLabelGenreResult:
    """Multi-label genre classification result with Camelot key info."""

    # All genres above threshold, ordered by confidence (highest first)
    all_genres: List[str] = field(default_factory=list)
    # Raw sigmoid scores for every detected genre
    scores: Dict[str, float] = field(default_factory=dict)

    # Convenience — top-1 genre
    primary_genre: str = "Unknown"
    primary_confidence: float = 0.0

    # Camelot Wheel
    camelot: str = ""
    key: str = ""
    scale: str = ""

    # Method used
    method: str = "heuristic"  # heuristic | clap | ensemble


# ── Classifier ────────────────────────────────────────────────────────────────


class MultiLabelGenreClassifier:
    """
    Multi-label genre classifier using sigmoid thresholding.

    Supports:
    - Heuristic scoring (always available)
    - CLAP semantic embeddings (when `transformers` + `torch` are installed)
    - Ensemble blending: 60% CLAP + 40% heuristic

    Args:
        threshold: Minimum sigmoid score to include a genre label (0–1).
        top_k: Maximum number of genres to return.
        use_clap: Whether to attempt CLAP deep embedding.
    """

    def __init__(
        self,
        threshold: float = 0.30,
        top_k: int = 5,
        use_clap: bool = True,
    ) -> None:
        self.threshold = threshold
        self.top_k = top_k
        self.use_clap = use_clap
        self._clap_model = None  # lazy-loaded

    # ── Public API ────────────────────────────────────────────────────────────

    def classify(
        self,
        y: np.ndarray,
        sr: int,
        key: str = "",
        scale: str = "",
    ) -> MultiLabelGenreResult:
        """
        Classify genres from an audio array.

        Args:
            y: Mono audio signal (float32).
            sr: Sample rate.
            key: Musical key (e.g. "A", "C#") — used for Camelot output.
            scale: "major" or "minor" — used for Camelot output.

        Returns:
            MultiLabelGenreResult
        """
        result = MultiLabelGenreResult(key=key, scale=scale)
        result.camelot = camelot_key(key, scale)

        # Stage 1: heuristic scores
        heuristic_scores = self._heuristic_scores(y, sr)

        # Stage 2: CLAP (optional)
        clap_scores: Dict[str, float] = {}
        if self.use_clap:
            clap_scores = self._clap_scores(y, sr)

        # Blend
        if clap_scores:
            all_genres = set(heuristic_scores) | set(clap_scores)
            blended: Dict[str, float] = {
                g: 0.6 * clap_scores.get(g, 0.0) + 0.4 * heuristic_scores.get(g, 0.0)
                for g in all_genres
            }
            result.method = "ensemble"
        else:
            blended = heuristic_scores

        # Apply sigmoid to map arbitrary scores → [0, 1]
        sigmoid_scores: Dict[str, float] = {
            g: _sigmoid(s) for g, s in blended.items()
        }

        # Filter by threshold and sort
        above_threshold = {
            g: s for g, s in sigmoid_scores.items() if s >= self.threshold
        }
        sorted_genres = sorted(above_threshold, key=lambda g: above_threshold[g], reverse=True)
        top_genres = sorted_genres[: self.top_k]

        result.all_genres = [normalize_genre(g) for g in top_genres]
        result.scores = {normalize_genre(g): round(above_threshold[g], 4) for g in top_genres}
        result.primary_genre = result.all_genres[0] if result.all_genres else "Unknown"
        result.primary_confidence = result.scores.get(result.primary_genre, 0.0)

        return result

    def classify_file(
        self,
        file_path: str | Path,
        sample_rate: int = 22050,
    ) -> MultiLabelGenreResult:
        """Load and classify an audio file synchronously."""
        try:
            import librosa

            y, sr = librosa.load(str(file_path), sr=sample_rate, mono=True)
        except Exception as exc:
            logger.error("Failed to load %s: %s", file_path, exc)
            return MultiLabelGenreResult()

        # Attempt to extract key/scale via chroma
        key, scale = self._detect_key_scale(y, sr)
        return self.classify(y, sr, key=key, scale=scale)

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _detect_key_scale(y: np.ndarray, sr: int) -> Tuple[str, str]:
        """Simple chroma-based key and major/minor detection."""
        try:
            import librosa

            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            chroma_mean = np.mean(chroma, axis=1)
            key_idx = int(np.argmax(chroma_mean))
            key_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
            key = key_names[key_idx]

            # Minor heuristic: if min of chroma at (key_idx - 3) % 12 > 0.8 * root
            minor_idx = (key_idx + 9) % 12  # relative minor root
            scale = "minor" if chroma_mean[minor_idx] > 0.8 * chroma_mean[key_idx] else "major"
            return key, scale
        except Exception:
            return "", ""

    @staticmethod
    def _heuristic_scores(y: np.ndarray, sr: int) -> Dict[str, float]:
        """Feature-rule scoring (same logic as GenreClassifier._heuristic_classify)."""
        try:
            import librosa

            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            tempo_arr, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
            bpm = float(tempo_arr) if np.isscalar(tempo_arr) else float(tempo_arr[0])
            centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
            rms = float(np.mean(librosa.feature.rms(y=y)))
            zcr = float(np.mean(librosa.feature.zero_crossing_rate(y)))
            chroma_var = float(np.var(librosa.feature.chroma_stft(y=y, sr=sr)))
        except Exception:
            return {}

        scores: Dict[str, float] = {}

        # BPM-based genre rules
        if 118 <= bpm <= 136:
            scores.update({"House": 0.7, "Tech House": 0.6, "Deep House": 0.55, "EDM": 0.5})
        if 128 <= bpm <= 145:
            scores.update({"Techno": 0.6, "Trance": 0.55})
        if 160 <= bpm <= 185:
            scores.update({"Drum and Bass": 0.75, "Neurofunk": 0.55, "Liquid DnB": 0.5})
        if 130 <= bpm <= 160:
            scores.update({"Dubstep": 0.4, "Future Bass": 0.45})
        if 60 <= bpm <= 100:
            scores.update({"Hip-Hop": 0.55, "R&B": 0.45, "Boom Bap": 0.4, "Trap Soul": 0.35})
        if 130 <= bpm <= 150:
            scores.update({"Trap": 0.5, "Cloud Rap": 0.35})
        if 148 <= bpm <= 180:
            scores.update({"Hardstyle": 0.55, "Hardcore": 0.5})
        if 138 <= bpm <= 148:
            scores.update({"Psytrance": 0.55, "Goa Trance": 0.45})

        # Spectral/energy rules
        if centroid > 4000 and rms > 0.15:
            scores["Hard Rock"] = scores.get("Hard Rock", 0.0) + 0.4
            scores["Heavy Metal"] = scores.get("Heavy Metal", 0.0) + 0.35
        if centroid < 2000 and rms < 0.05:
            scores["Ambient"] = scores.get("Ambient", 0.0) + 0.65
            scores["Drone"] = scores.get("Drone", 0.0) + 0.45
            scores["Dark Ambient"] = scores.get("Dark Ambient", 0.0) + 0.4
        if centroid < 2500 and chroma_var > 0.02:
            scores["Jazz"] = scores.get("Jazz", 0.0) + 0.45
            scores["Blues"] = scores.get("Blues", 0.0) + 0.3
        if zcr > 0.15 and rms > 0.2:
            scores["Punk"] = scores.get("Punk", 0.0) + 0.4
            scores["Noise Rock"] = scores.get("Noise Rock", 0.0) + 0.3
        if centroid > 3000 and 170 <= bpm <= 220:
            scores["Breakcore"] = scores.get("Breakcore", 0.0) + 0.5

        # Normalize to [0, 1]
        max_s = max(scores.values()) if scores else 1.0
        return {g: s / max(max_s, 1e-9) for g, s in scores.items()}

    def _clap_scores(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """
        Score genres using CLAP audio embeddings (requires `transformers` + `torch`).

        Returns empty dict if unavailable.
        """
        if self._clap_model is None:
            self._clap_model = _load_clap()

        if self._clap_model is None:
            return {}

        try:
            processor, model = self._clap_model
            import torch

            # Resample to 48kHz (CLAP expectation)
            try:
                import librosa
                y_48k = librosa.resample(y, orig_sr=sr, target_sr=48000)
            except Exception:
                y_48k = y

            # Process audio and text
            audio_inputs = processor(
                audios=[y_48k],
                sampling_rate=48000,
                return_tensors="pt",
                padding=True,
            )
            text_inputs = processor(
                text=_CLAP_GENRE_PROMPTS,
                return_tensors="pt",
                padding=True,
            )

            with torch.no_grad():
                audio_embeds = model.get_audio_features(**audio_inputs)
                text_embeds = model.get_text_features(**text_inputs)

            # Cosine similarity → per-genre score
            audio_embeds = audio_embeds / audio_embeds.norm(dim=-1, keepdim=True)
            text_embeds = text_embeds / text_embeds.norm(dim=-1, keepdim=True)
            sims = (audio_embeds @ text_embeds.T).squeeze(0).tolist()

            # Map back to genre names
            return {GENRE_TAXONOMY[i]: float(s) for i, s in enumerate(sims)}

        except Exception as exc:
            logger.warning("CLAP scoring failed: %s", exc)
            return {}


# ── Utilities ─────────────────────────────────────────────────────────────────


def _sigmoid(x: float, gain: float = 4.0) -> float:
    """Sigmoid with gain parameter — maps raw scores to [0, 1]."""
    return 1.0 / (1.0 + math.exp(-gain * (x - 0.5)))


def _load_clap():
    """
    Lazy-load CLAP model from HuggingFace.

    Returns (processor, model) tuple or None if unavailable.
    Prefers `laion/clap-htsat-unfused` (audio + music trained).
    """
    try:
        from transformers import ClapModel, ClapProcessor

        model_id = "laion/clap-htsat-unfused"
        logger.info("Loading CLAP model: %s", model_id)
        processor = ClapProcessor.from_pretrained(model_id)
        model = ClapModel.from_pretrained(model_id)
        model.eval()
        logger.info("CLAP model loaded")
        return processor, model
    except Exception as exc:
        logger.warning("CLAP unavailable (%s) — using heuristic only", exc)
        return None
