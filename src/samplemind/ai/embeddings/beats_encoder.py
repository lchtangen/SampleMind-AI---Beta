#!/usr/bin/env python3
"""
SampleMind AI — BEATs Audio Encoder
768-dimensional audio embeddings via Microsoft BEATs (Bidirectional Encoder
representation from Audio Transformers).

Model: ``microsoft/BEATs-iter3-AS2M``
Embedding dim: 768
Trained on AudioSet (2M clips, 527 classes)

Follows the lazy-load + mock-fallback pattern from neural_engine.py.
"""

import hashlib
import logging
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy globals
# ---------------------------------------------------------------------------

_torch: Any = None
_AutoModel: Any = None
_AutoProcessor: Any = None
_BEATS_AVAILABLE = False
_BEATS_MODEL_NAME = "microsoft/BEATs-iter3-AS2M"
_EMBED_DIM = 768


def _ensure_beats() -> bool:
    global _torch, _AutoModel, _AutoProcessor, _BEATS_AVAILABLE
    if _BEATS_AVAILABLE:
        return True
    try:
        import torch as _t
        from transformers import AutoModel as _AM
        from transformers import AutoProcessor as _AP

        _torch = _t
        _AutoModel = _AM
        _AutoProcessor = _AP
        _BEATS_AVAILABLE = True
    except ImportError:
        logger.warning(
            "transformers or torch not installed — BEATsEncoder falling back to mock mode"
        )
    return _BEATS_AVAILABLE


# ---------------------------------------------------------------------------
# Encoder
# ---------------------------------------------------------------------------


class BEATsEncoder:
    """
    Microsoft BEATs audio encoder producing 768-dim embeddings.

    Embeddings are suitable for:
    - Audio event classification (527 AudioSet labels)
    - Semantic similarity search
    - Cross-modal retrieval with text embeddings

    GPU acceleration is used when available.

    Usage::

        encoder = BEATsEncoder()
        emb = encoder.encode("kick.wav")   # np.ndarray shape (768,)
    """

    def __init__(
        self,
        model_name: str = _BEATS_MODEL_NAME,
        use_gpu: bool = True,
        use_mock: bool = False,
        enable_cache: bool = True,
    ) -> None:
        """
        Args:
            model_name:    HuggingFace model identifier.
            use_gpu:       Prefer CUDA / MPS when available.
            use_mock:      Force mock mode (random deterministic embeddings).
            enable_cache:  Cache embeddings keyed by file path + mtime.
        """
        self.model_name = model_name
        self.use_mock = use_mock or (model_name == "mock")
        self.enable_cache = enable_cache
        self.device = "cpu"
        self._processor: Any = None
        self._model: Any = None
        self._cache: dict = {}

        if not self.use_mock:
            if _ensure_beats():
                self._init_device(use_gpu)
                self._load_model()
            else:
                self.use_mock = True
        if self.use_mock:
            logger.info("BEATsEncoder initialised in MOCK mode")

    # ------------------------------------------------------------------
    # Device + model setup
    # ------------------------------------------------------------------

    def _init_device(self, use_gpu: bool) -> None:
        if use_gpu and _BEATS_AVAILABLE:
            if _torch.cuda.is_available():
                self.device = "cuda"
            elif _torch.backends.mps.is_available():
                self.device = "mps"

    def _load_model(self) -> None:
        try:
            logger.info(f"Loading BEATs model: {self.model_name} on {self.device}")
            self._processor = _AutoProcessor.from_pretrained(self.model_name)
            self._model = _AutoModel.from_pretrained(self.model_name).to(self.device)
            self._model.eval()
            logger.info("BEATs model loaded successfully")
        except Exception as exc:
            logger.error(f"Failed to load BEATs model: {exc}")
            logger.warning("Falling back to mock mode")
            self.use_mock = True

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def encode(self, audio_path: str | Path) -> np.ndarray:
        """
        Encode an audio file into a 768-dim BEATs embedding.

        Args:
            audio_path: Path to the audio file (WAV, MP3, FLAC).

        Returns:
            ``np.ndarray`` of shape ``(768,)`` — L2-normalised embedding.
        """
        audio_path = Path(audio_path)

        # Cache lookup
        cache_key = self._cache_key(audio_path)
        if self.enable_cache and cache_key in self._cache:
            return self._cache[cache_key]

        if self.use_mock:
            emb = self._mock_embedding(cache_key)
        else:
            emb = self._encode_file(audio_path)

        if self.enable_cache:
            self._cache[cache_key] = emb
        return emb

    def encode_batch(self, paths: list[str | Path]) -> list[np.ndarray]:
        """Encode multiple files, returning a list of 768-dim arrays."""
        return [self.encode(p) for p in paths]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _encode_file(self, audio_path: Path) -> np.ndarray:
        """Perform actual BEATs inference."""
        try:
            import librosa

            waveform, sr = librosa.load(str(audio_path), sr=16000, mono=True)
        except Exception as exc:
            logger.error(f"Audio load failed for {audio_path}: {exc}")
            return self._mock_embedding(str(audio_path))

        try:
            inputs = self._processor(
                waveform,
                sampling_rate=16000,
                return_tensors="pt",
            ).to(self.device)

            with _torch.no_grad():
                outputs = self._model(**inputs)
                # Pool over time dimension → (embed_dim,)
                hidden: Any = outputs.last_hidden_state
                pooled = hidden.mean(dim=1).squeeze(0).cpu().numpy()

            # L2-normalise
            norm = np.linalg.norm(pooled)
            return pooled / norm if norm > 0 else pooled

        except Exception as exc:
            logger.error(f"BEATs inference failed: {exc}")
            return self._mock_embedding(str(audio_path))

    def _cache_key(self, path: Path) -> str:
        stat = path.stat() if path.exists() else None
        mtime = str(stat.st_mtime) if stat else "0"
        return hashlib.md5(f"{path}{mtime}".encode()).hexdigest()

    def _mock_embedding(self, seed: str) -> np.ndarray:
        """Deterministic random embedding for tests."""
        seed_int = int(hashlib.md5(seed.encode()).hexdigest(), 16) % (2**32)
        rng = np.random.default_rng(seed_int)
        emb = rng.standard_normal(_EMBED_DIM).astype(np.float32)
        norm = np.linalg.norm(emb)
        return emb / norm if norm > 0 else emb

    def clear_cache(self) -> None:
        self._cache.clear()
        logger.debug("BEATsEncoder cache cleared")
