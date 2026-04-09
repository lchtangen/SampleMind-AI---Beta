"""
BEATsEncoder — Microsoft BEATs audio representation model (P4-011).

Provides 768-dim audio embeddings using microsoft/BEATs-iter3.
Falls back to MFCC-based embeddings when transformers / the model are
unavailable (CI, systems without GPU, air-gapped environments).

Usage::

    encoder = BEATsEncoder()
    vec = encoder.encode("/path/to/kick.wav")   # np.ndarray, shape (768,)
    print(f"Embedding dim: {vec.shape[0]}, norm: {np.linalg.norm(vec):.4f}")
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

BEATS_MODEL_ID = "microsoft/beats-iter3"
EMBEDDING_DIM = 768


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mfcc_embed(path: str, dim: int = EMBEDDING_DIM) -> np.ndarray:
    """
    MFCC-based fallback embedding.

    Computes 128-D MFCC statistics, then zero-pads / truncates to *dim*.
    Always returns a unit-normalised float32 vector.
    """
    try:
        import librosa  # type: ignore

        y, sr = librosa.load(path, sr=22050, mono=True, duration=30.0)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=64)
        feat = np.concatenate([mfcc.mean(axis=1), mfcc.std(axis=1)])  # (128,)
        # Pad / truncate to target dim
        if feat.shape[0] < dim:
            feat = np.pad(feat, (0, dim - feat.shape[0]))
        else:
            feat = feat[:dim]
    except Exception as exc:
        logger.debug("MFCC fallback failed for %s: %s", path, exc)
        feat = np.zeros(dim, dtype=np.float32)

    feat = feat.astype(np.float32)
    norm = np.linalg.norm(feat)
    return feat / norm if norm > 1e-9 else feat


# ---------------------------------------------------------------------------
# BEATsEncoder
# ---------------------------------------------------------------------------


class BEATsEncoder:
    """
    Audio encoder backed by microsoft/BEATs-iter3 (768-dim embeddings).

    The model is loaded lazily on first call to ``encode()``.  If loading
    fails the instance falls back to MFCC embeddings automatically.
    """

    def __init__(self, model_id: str = BEATS_MODEL_ID) -> None:
        self._model_id = model_id
        self._model = None
        self._processor = None
        self._use_beats = True  # optimistic; set False on first load failure

    # ---- Lazy model loading -------------------------------------------------

    def _load_model(self) -> bool:
        """
        Attempt to load BEATs via transformers.  Returns True on success.
        """
        if not self._use_beats:
            return False
        if self._model is not None:
            return True

        try:
            from transformers import AutoFeatureExtractor, AutoModel  # type: ignore

            logger.info("Loading BEATs model: %s", self._model_id)
            self._processor = AutoFeatureExtractor.from_pretrained(self._model_id)
            self._model = AutoModel.from_pretrained(self._model_id)
            self._model.eval()
            logger.info("BEATs model loaded successfully")
            return True
        except Exception as exc:
            logger.warning("BEATs model unavailable (%s). Falling back to MFCC.", exc)
            self._use_beats = False
            return False

    # ---- Public API ---------------------------------------------------------

    def encode(self, path: str) -> np.ndarray:
        """
        Encode an audio file and return a unit-normalised 768-D embedding.

        Args:
            path: Absolute path to a WAV/MP3/FLAC audio file.

        Returns:
            ``np.ndarray`` of shape ``(768,)`` and dtype ``float32``.
        """
        if not Path(path).exists():
            logger.warning("BEATsEncoder: file not found %s — returning zeros", path)
            return np.zeros(EMBEDDING_DIM, dtype=np.float32)

        # Try BEATs
        if self._load_model():
            try:
                import soundfile as sf  # type: ignore
                import torch  # type: ignore

                audio, sr = sf.read(path)
                if audio.ndim > 1:
                    audio = audio.mean(axis=1)  # stereo → mono
                audio = audio.astype(np.float32)

                inputs = self._processor(audio, sampling_rate=sr, return_tensors="pt")
                with torch.no_grad():
                    outputs = self._model(**inputs)

                # Mean-pool the last hidden state: (1, T, 768) → (768,)
                hidden = outputs.last_hidden_state.squeeze(0).mean(dim=0)
                vec = hidden.cpu().numpy().astype(np.float32)
                norm = np.linalg.norm(vec)
                return vec / norm if norm > 1e-9 else vec

            except Exception as exc:
                logger.warning("BEATs inference failed: %s — using MFCC", exc)
                self._use_beats = False

        # MFCC fallback
        return _mfcc_embed(path, dim=EMBEDDING_DIM)

    def encode_batch(self, paths: list[str]) -> np.ndarray:
        """
        Encode multiple files.

        Returns:
            ``np.ndarray`` of shape ``(N, 768)`` where N = len(paths).
        """
        return np.stack([self.encode(p) for p in paths], axis=0)

    @property
    def dim(self) -> int:
        """Embedding dimensionality."""
        return EMBEDDING_DIM

    @property
    def backend(self) -> str:
        """Which backend is active: 'beats' or 'mfcc'."""
        return "beats" if self._use_beats else "mfcc"
