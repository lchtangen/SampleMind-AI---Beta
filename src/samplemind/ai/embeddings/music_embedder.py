#!/usr/bin/env python3
"""
SampleMind AI — Music Embedder (music2vec / MusicFM)
768-dimensional music-domain embeddings via ``m-a-p/music2vec-v1``.

Integrates with ChromaDB for persistent similarity search storage.
Follows the lazy-load + mock-fallback pattern from neural_engine.py.

Model: ``m-a-p/music2vec-v1`` (768-dim, trained on FMA + music4all)
"""

import hashlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy globals
# ---------------------------------------------------------------------------

_torch: Any = None
_AutoModel: Any = None
_AutoProcessor: Any = None
_MUSIC2VEC_AVAILABLE = False
_MUSIC2VEC_MODEL = "m-a-p/music2vec-v1"
_EMBED_DIM = 768


def _ensure_music2vec() -> bool:
    global _torch, _AutoModel, _AutoProcessor, _MUSIC2VEC_AVAILABLE
    if _MUSIC2VEC_AVAILABLE:
        return True
    try:
        import torch as _t
        from transformers import AutoModel as _AM
        from transformers import AutoProcessor as _AP

        _torch = _t
        _AutoModel = _AM
        _AutoProcessor = _AP
        _MUSIC2VEC_AVAILABLE = True
    except ImportError:
        logger.warning(
            "transformers or torch not installed — MusicEmbedder falling back to mock mode"
        )
    return _MUSIC2VEC_AVAILABLE


# ---------------------------------------------------------------------------
# Embedder
# ---------------------------------------------------------------------------


class MusicEmbedder:
    """
    Music2vec embedder creating 768-dim music-domain embeddings.

    Optionally stores embeddings in ChromaDB for persistent similarity search.

    Usage::

        embedder = MusicEmbedder()
        emb = embedder.embed("loop.wav")                   # np.ndarray (768,)
        embedder.store_in_chroma("loop.wav", metadata={})  # persist to ChromaDB
        similar = embedder.search_similar("loop.wav", top_k=5)
    """

    def __init__(
        self,
        model_name: str = _MUSIC2VEC_MODEL,
        use_gpu: bool = True,
        use_mock: bool = False,
        enable_cache: bool = True,
        chroma_collection: str = "samplemind_music2vec",
    ) -> None:
        self.model_name = model_name
        self.use_mock = use_mock or (model_name == "mock")
        self.enable_cache = enable_cache
        self.chroma_collection = chroma_collection
        self.device = "cpu"
        self._processor: Any = None
        self._model: Any = None
        self._cache: Dict[str, np.ndarray] = {}
        self._chroma: Any = None  # lazy-loaded on first chroma call

        if not self.use_mock:
            if _ensure_music2vec():
                self._init_device(use_gpu)
                self._load_model()
            else:
                self.use_mock = True
        if self.use_mock:
            logger.info("MusicEmbedder initialised in MOCK mode")

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _init_device(self, use_gpu: bool) -> None:
        if use_gpu and _MUSIC2VEC_AVAILABLE:
            if _torch.cuda.is_available():
                self.device = "cuda"
            elif _torch.backends.mps.is_available():
                self.device = "mps"

    def _load_model(self) -> None:
        try:
            logger.info(f"Loading music2vec model: {self.model_name} on {self.device}")
            self._processor = _AutoProcessor.from_pretrained(self.model_name)
            self._model = _AutoModel.from_pretrained(self.model_name).to(self.device)
            self._model.eval()
            logger.info("music2vec model loaded successfully")
        except Exception as exc:
            logger.error(f"Failed to load music2vec: {exc}")
            logger.warning("Falling back to mock mode")
            self.use_mock = True

    def _get_chroma(self) -> Any:
        """Lazy-load ChromaDB collection."""
        if self._chroma is not None:
            return self._chroma
        try:
            import chromadb

            client = chromadb.Client()
            self._chroma = client.get_or_create_collection(
                name=self.chroma_collection,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception as exc:
            logger.warning(f"ChromaDB unavailable: {exc}")
            self._chroma = None
        return self._chroma

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def embed(self, audio_path: str | Path) -> np.ndarray:
        """
        Produce a 768-dim music2vec embedding for an audio file.

        Returns:
            ``np.ndarray`` of shape ``(768,)`` — L2-normalised.
        """
        audio_path = Path(audio_path)
        cache_key = self._cache_key(audio_path)

        if self.enable_cache and cache_key in self._cache:
            return self._cache[cache_key]

        emb = (
            self._mock_embedding(cache_key)
            if self.use_mock
            else self._embed_file(audio_path)
        )

        if self.enable_cache:
            self._cache[cache_key] = emb
        return emb

    def embed_batch(self, paths: List[str | Path]) -> List[np.ndarray]:
        """Embed a list of audio files."""
        return [self.embed(p) for p in paths]

    def store_in_chroma(
        self,
        audio_path: str | Path,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None,
    ) -> bool:
        """
        Compute embedding and persist it in ChromaDB.

        Args:
            audio_path:  Source audio file.
            metadata:    Arbitrary key-value metadata (tags, genre, BPM…).
            doc_id:      Unique document ID.  Defaults to the file path.

        Returns:
            ``True`` on success, ``False`` if ChromaDB is unavailable.
        """
        col = self._get_chroma()
        if col is None:
            return False

        emb = self.embed(audio_path)
        _id = doc_id or str(audio_path)
        _meta = metadata or {}
        _meta["source_path"] = str(audio_path)

        try:
            col.upsert(
                ids=[_id],
                embeddings=[emb.tolist()],
                metadatas=[_meta],
            )
            logger.debug(f"Stored music2vec embedding for: {audio_path}")
            return True
        except Exception as exc:
            logger.error(f"ChromaDB upsert failed: {exc}")
            return False

    def search_similar(
        self,
        audio_path: str | Path,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Find the most similar samples in ChromaDB for a given audio file.

        Args:
            audio_path:  Query audio file.
            top_k:       Number of results to return.

        Returns:
            List of result dicts with ``id``, ``distance``, and ``metadata``.
        """
        col = self._get_chroma()
        if col is None:
            return []

        emb = self.embed(audio_path)
        try:
            results = col.query(
                query_embeddings=[emb.tolist()],
                n_results=top_k,
                include=["metadatas", "distances"],
            )
            output: List[Dict[str, Any]] = []
            for i, doc_id in enumerate(results.get("ids", [[]])[0]):
                output.append(
                    {
                        "id": doc_id,
                        "distance": results["distances"][0][i],
                        "metadata": results["metadatas"][0][i],
                    }
                )
            return output
        except Exception as exc:
            logger.error(f"ChromaDB search failed: {exc}")
            return []

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _embed_file(self, audio_path: Path) -> np.ndarray:
        try:
            import librosa

            waveform, _ = librosa.load(str(audio_path), sr=16000, mono=True)
        except Exception as exc:
            logger.error(f"Load failed {audio_path}: {exc}")
            return self._mock_embedding(str(audio_path))

        try:
            inputs = self._processor(
                waveform, sampling_rate=16000, return_tensors="pt"
            ).to(self.device)
            with _torch.no_grad():
                outputs = self._model(**inputs)
                hidden = outputs.last_hidden_state
                pooled = hidden.mean(dim=1).squeeze(0).cpu().numpy()
            norm = np.linalg.norm(pooled)
            return pooled / norm if norm > 0 else pooled
        except Exception as exc:
            logger.error(f"music2vec inference failed: {exc}")
            return self._mock_embedding(str(audio_path))

    def _cache_key(self, path: Path) -> str:
        stat = path.stat() if path.exists() else None
        mtime = str(stat.st_mtime) if stat else "0"
        return hashlib.md5(f"{path}{mtime}".encode()).hexdigest()

    def _mock_embedding(self, seed: str) -> np.ndarray:
        seed_int = int(hashlib.md5(seed.encode()).hexdigest(), 16) % (2**32)
        rng = np.random.default_rng(seed_int)
        emb = rng.standard_normal(_EMBED_DIM).astype(np.float32)
        norm = np.linalg.norm(emb)
        return emb / norm if norm > 0 else emb

    def clear_cache(self) -> None:
        self._cache.clear()
