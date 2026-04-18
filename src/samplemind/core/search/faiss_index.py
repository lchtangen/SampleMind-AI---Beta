"""
FAISS Semantic Index — SampleMind Phase 11
============================================

CLAP-powered audio + text embedding index for **fast approximate nearest-neighbor
search** across sample libraries.

Architecture:
  - **Embeddings**: ``laion/clap-htsat-unfused`` produces 512-dim vectors in a
    shared audio + text space, so text queries ("dark trap kick") match
    acoustically similar samples without explicit tagging.
  - **Index type**: ``IndexFlatIP`` — exact inner product. After L2-normalisation
    the inner product equals cosine similarity.
  - **Persistence**: ``~/.samplemind/faiss/index.bin`` + ``metadata.json``.
  - **Capacity**: ~1 M samples at ≈ 2 GB RAM (512-dim float32).

Fallback:
  When the CLAP model is unavailable (no GPU, missing ``transformers``),
  embeddings are computed from librosa MFCCs (20-dim, zero-padded to 512).
  Search quality is lower but the index still functions.

Usage::

    from samplemind.core.search.faiss_index import FAISSIndex

    idx = FAISSIndex()
    idx.build(audio_paths=["/path/to/kick.wav", "/path/to/snare.wav"])
    idx.save()

    results = idx.search_text("dark aggressive trap kick", top_k=10)
    for r in results:
        print(r.path, r.score)
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import NamedTuple

import numpy as np

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────

CLAP_MODEL_ID = "laion/clap-htsat-unfused"
EMBEDDING_DIM = 512
DEFAULT_INDEX_DIR = (
    Path(os.getenv("SAMPLEMIND_DATA_DIR", Path.home() / ".samplemind")) / "faiss"
)
FALLBACK_MFCC_N = 20  # MFCCs when CLAP unavailable


# ── Data types ────────────────────────────────────────────────────────────────


class SearchResult(NamedTuple):
    """A single search result from the FAISS index."""

    index_id: int  # FAISS internal ID
    path: str  # Audio file path
    filename: str
    score: float  # Cosine similarity [0, 1]
    metadata: dict  # BPM, key, genre_labels, etc.


@dataclass
class IndexEntry:
    """Metadata stored alongside each FAISS vector."""

    index_id: int
    path: str
    filename: str
    sample_id: str | None = None  # TortoiseSample.id if indexed from DB
    bpm: float | None = None
    key: str | None = None
    energy: str | None = None
    genre_labels: list[str] = None  # type: ignore[assignment]
    mood_labels: list[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.genre_labels is None:
            self.genre_labels = []
        if self.mood_labels is None:
            self.mood_labels = []


# ── CLAP embedder ─────────────────────────────────────────────────────────────


class CLAPEmbedder:
    """
    Wraps the CLAP model to produce 512-dim embeddings from audio or text.
    Falls back to MFCC-based embeddings when transformers are unavailable.
    """

    def __init__(self) -> None:
        self._model: object | None = None
        self._processor: object | None = None
        self._use_clap: bool = False
        self._load()

    def _load(self) -> None:
        try:
            from transformers import ClapModel, ClapProcessor

            logger.info("Loading CLAP model: %s", CLAP_MODEL_ID)
            self._processor = ClapProcessor.from_pretrained(CLAP_MODEL_ID)
            self._model = ClapModel.from_pretrained(CLAP_MODEL_ID)
            self._use_clap = True
            logger.info("✓ CLAP model loaded (%d-dim embeddings)", EMBEDDING_DIM)
        except Exception as exc:
            logger.warning(
                "CLAP unavailable (%s) — using MFCC fallback embeddings", exc
            )
            self._use_clap = False

    def embed_audio(self, audio_path: str, sample_rate: int = 48000) -> np.ndarray:
        """
        Compute a 512-dim audio embedding from a WAV/AIFF/MP3 file.

        Returns:
            Unit-normalized float32 array of shape [512].
        """
        if self._use_clap:
            return self._clap_audio_embed(audio_path, sample_rate)
        return self._mfcc_embed(audio_path)

    def embed_text(self, text: str) -> np.ndarray:
        """
        Compute a 512-dim text embedding for a natural language query.

        Returns:
            Unit-normalized float32 array of shape [512].
        """
        if self._use_clap:
            return self._clap_text_embed(text)
        # Fallback: keyword hash vector (very rough)
        return self._text_hash_embed(text)

    # ── CLAP implementations ──────────────────────────────────────────────────

    def _clap_audio_embed(self, audio_path: str, sample_rate: int) -> np.ndarray:
        import soundfile as sf
        import torch

        audio, sr = sf.read(audio_path, dtype="float32")
        if audio.ndim > 1:
            audio = audio.mean(axis=1)

        inputs = self._processor(  # type: ignore[call-arg]
            audios=[audio.tolist()],
            sampling_rate=sr,
            return_tensors="pt",
        )
        with torch.no_grad():
            emb = self._model.get_audio_features(**inputs)  # type: ignore[union-attr]
        vec = emb.squeeze().numpy().astype(np.float32)
        return _normalize(vec)

    def _clap_text_embed(self, text: str) -> np.ndarray:
        import torch

        inputs = self._processor(text=[text], return_tensors="pt")  # type: ignore[call-arg]
        with torch.no_grad():
            emb = self._model.get_text_features(**inputs)  # type: ignore[union-attr]
        vec = emb.squeeze().numpy().astype(np.float32)
        return _normalize(vec)

    # ── Fallback implementations ──────────────────────────────────────────────

    def _mfcc_embed(self, audio_path: str) -> np.ndarray:
        """Fallback: 20-dim MFCC mean + std, zero-padded to EMBEDDING_DIM (512)."""
        try:
            import librosa

            y, sr = librosa.load(audio_path, sr=22050, mono=True, duration=30.0)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=FALLBACK_MFCC_N)
            features = np.concatenate([mfccs.mean(axis=1), mfccs.std(axis=1)])  # 40-dim
        except Exception:
            features = np.zeros(FALLBACK_MFCC_N * 2, dtype=np.float32)

        # Pad / truncate to EMBEDDING_DIM
        vec = np.zeros(EMBEDDING_DIM, dtype=np.float32)
        n = min(len(features), EMBEDDING_DIM)
        vec[:n] = features[:n]
        return _normalize(vec)

    def _text_hash_embed(self, text: str) -> np.ndarray:
        """Deterministic keyword-hash vector — very low quality, last resort when CLAP is unavailable."""
        vec = np.zeros(EMBEDDING_DIM, dtype=np.float32)
        for _i, ch in enumerate(text.lower()):
            vec[hash(ch) % EMBEDDING_DIM] += 1.0
        return _normalize(vec)


def _normalize(v: np.ndarray) -> np.ndarray:
    """L2-normalize a vector so inner product equals cosine similarity."""
    norm = np.linalg.norm(v)
    return v / norm if norm > 1e-8 else v


# ── FAISS index ───────────────────────────────────────────────────────────────


class FAISSIndex:
    """
    Persistent FAISS index for semantic sample search.

    Supports:
    - build(paths): compute embeddings and populate index
    - add(path): add a single sample (incremental)
    - search_text(query): find similar samples by text description
    - search_audio(path): find similar samples by audio example
    - save() / load(): persist to disk
    """

    def __init__(
        self,
        index_dir: Path | None = None,
        embedder: CLAPEmbedder | None = None,
    ) -> None:
        self._dir = Path(index_dir or DEFAULT_INDEX_DIR)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._index_path = self._dir / "index.bin"
        self._meta_path = self._dir / "metadata.json"
        self._embedder = embedder or CLAPEmbedder()
        self._index: object | None = None
        self._entries: list[IndexEntry] = []

    # ── Index management ──────────────────────────────────────────────────────

    def _get_or_create_index(self) -> object:
        if self._index is None:
            try:
                import faiss

                index = faiss.IndexFlatIP(EMBEDDING_DIM)
                self._index = faiss.IndexIDMap(index)
            except ImportError:
                raise RuntimeError("faiss-cpu not installed — run: uv add faiss-cpu")
        return self._index

    def build(
        self,
        audio_paths: list[str],
        metadata_list: list[dict] | None = None,
        show_progress: bool = True,
    ) -> FAISSIndex:
        """
        Build the FAISS index from a list of audio file paths.

        Args:
            audio_paths: List of file paths to index.
            metadata_list: Optional per-path dicts with BPM/key/genre/mood.
            show_progress: Log progress every 10%.

        Returns:
            self (for chaining).
        """
        self._entries = []
        index = self._get_or_create_index()

        n = len(audio_paths)
        embeddings = []
        ids = []

        for i, path in enumerate(audio_paths):
            try:
                emb = self._embedder.embed_audio(path)
                meta = (metadata_list or [{}])[i] if metadata_list else {}
                entry = IndexEntry(
                    index_id=i,
                    path=path,
                    filename=os.path.basename(path),
                    sample_id=meta.get("sample_id"),
                    bpm=meta.get("bpm"),
                    key=meta.get("key"),
                    energy=meta.get("energy"),
                    genre_labels=meta.get("genre_labels", []),
                    mood_labels=meta.get("mood_labels", []),
                )
                embeddings.append(emb)
                ids.append(i)
                self._entries.append(entry)

                if show_progress and n > 10 and i % max(1, n // 10) == 0:
                    logger.info(
                        "FAISS build: %d/%d (%.0f%%)", i + 1, n, (i + 1) / n * 100
                    )

            except Exception as exc:
                logger.warning("Skipping %s: %s", path, exc)

        if embeddings:

            vectors = np.stack(embeddings).astype(np.float32)
            faiss_ids = np.array(ids, dtype=np.int64)
            index.add_with_ids(vectors, faiss_ids)  # type: ignore[union-attr]
            logger.info(
                "✓ FAISS index built: %d vectors (%d-dim)",
                len(embeddings),
                EMBEDDING_DIM,
            )

        return self

    def add(
        self,
        audio_path: str,
        metadata: dict | None = None,
    ) -> int:
        """
        Add a single audio file to the index.

        Returns:
            The assigned index_id.
        """

        index = self._get_or_create_index()
        index_id = len(self._entries)
        emb = self._embedder.embed_audio(audio_path)
        meta = metadata or {}

        entry = IndexEntry(
            index_id=index_id,
            path=audio_path,
            filename=os.path.basename(audio_path),
            sample_id=meta.get("sample_id"),
            bpm=meta.get("bpm"),
            key=meta.get("key"),
            energy=meta.get("energy"),
            genre_labels=meta.get("genre_labels", []),
            mood_labels=meta.get("mood_labels", []),
        )
        self._entries.append(entry)

        vec = emb.reshape(1, -1).astype(np.float32)
        ids = np.array([index_id], dtype=np.int64)
        index.add_with_ids(vec, ids)  # type: ignore[union-attr]
        return index_id

    # ── Search ────────────────────────────────────────────────────────────────

    def search_text(self, query: str, top_k: int = 20) -> list[SearchResult]:
        """Search by natural language text query (e.g. 'dark trap kick')."""
        emb = self._embedder.embed_text(query)
        return self._search_embedding(emb, top_k=top_k)

    def search_audio(self, audio_path: str, top_k: int = 20) -> list[SearchResult]:
        """Search by audio example — finds perceptually similar samples."""
        emb = self._embedder.embed_audio(audio_path)
        return self._search_embedding(emb, top_k=top_k)

    def search_by_embedding(
        self, embedding: np.ndarray, top_k: int = 20
    ) -> list[SearchResult]:
        """Search by precomputed embedding vector."""
        return self._search_embedding(embedding, top_k=top_k)

    def _search_embedding(self, emb: np.ndarray, top_k: int) -> list[SearchResult]:
        """Core search: query the FAISS index and map IDs back to metadata entries."""
        if self._index is None or not self._entries:
            return []

        vec = emb.reshape(1, -1).astype(np.float32)
        k = min(top_k, len(self._entries))

        scores, ids = self._index.search(vec, k)  # type: ignore[union-attr]
        results = []
        for score, idx in zip(scores[0], ids[0], strict=False):
            if idx < 0 or idx >= len(self._entries):
                continue
            entry = self._entries[idx]
            results.append(
                SearchResult(
                    index_id=entry.index_id,
                    path=entry.path,
                    filename=entry.filename,
                    score=float(score),
                    metadata={
                        "bpm": entry.bpm,
                        "key": entry.key,
                        "energy": entry.energy,
                        "genre_labels": entry.genre_labels,
                        "mood_labels": entry.mood_labels,
                        "sample_id": entry.sample_id,
                    },
                )
            )
        return results

    # ── Persistence ───────────────────────────────────────────────────────────

    def save(self) -> None:
        """Persist FAISS index + metadata to disk."""
        if self._index is None:
            return
        try:
            import faiss

            faiss.write_index(self._index, str(self._index_path))
            meta = [asdict(e) for e in self._entries]
            self._meta_path.write_text(json.dumps(meta, indent=2))
            logger.info(
                "✓ FAISS index saved: %s (%d entries)",
                self._index_path,
                len(self._entries),
            )
        except Exception as exc:
            logger.error("Failed to save FAISS index: %s", exc)

    def load(self) -> bool:
        """
        Load FAISS index from disk.

        Returns:
            True if loaded successfully, False if index doesn't exist.
        """
        if not self._index_path.exists():
            return False
        try:
            import faiss

            self._index = faiss.read_index(str(self._index_path))
            meta = json.loads(self._meta_path.read_text())
            self._entries = [IndexEntry(**e) for e in meta]
            logger.info("✓ FAISS index loaded: %d entries", len(self._entries))
            return True
        except Exception as exc:
            logger.error("Failed to load FAISS index: %s", exc)
            return False

    @property
    def size(self) -> int:
        """Number of indexed vectors."""
        return len(self._entries)

    @property
    def is_empty(self) -> bool:
        return self.size == 0


# ── Module-level singleton ────────────────────────────────────────────────────

_global_index: FAISSIndex | None = None


def get_index(auto_load: bool = True) -> FAISSIndex:
    """
    Return the module-level FAISSIndex singleton.

    On first call, attempts to load a previously saved index from disk.
    If no saved index exists, returns an empty index ready for build().
    """
    global _global_index
    if _global_index is None:
        _global_index = FAISSIndex()
        if auto_load:
            _global_index.load()
    return _global_index
