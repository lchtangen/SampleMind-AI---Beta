"""
Agent Conversation Memory — SampleMind Phase 17 (P3-014)

Provides persistent vector-backed memory for the LangGraph agent pipeline.
Past analysis results are embedded (via CLAP or MFCC fallback) and stored
in a FAISS index, enabling retrieval-augmented analysis where agents can
reference similar past results.

Architecture:
  - Each completed pipeline run produces a summary dict stored as a "memory".
  - Memories are embedded using text summarisation → embedding vector.
  - A separate FAISS IndexFlatIP stores memory embeddings (512-dim).
  - Text queries ("dark trap kick 140 BPM") retrieve relevant past analyses.

Persistence:
  - Index: ~/.samplemind/agent_memory/memory_index.bin
  - Metadata: ~/.samplemind/agent_memory/memory_meta.json

Usage::

    from samplemind.ai.agents.memory import AgentMemory

    mem = AgentMemory()
    await mem.store(analysis_state)  # after pipeline completes

    context = await mem.recall("dark 808 kick drum", top_k=3)
    for entry in context:
        print(entry.summary, entry.relevance_score)
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────

MEMORY_DIR = Path(
    os.getenv(
        "AGENT_MEMORY_DIR",
        str(Path.home() / ".samplemind" / "agent_memory"),
    )
)
EMBEDDING_DIM = 512
MAX_MEMORY_ENTRIES = int(os.getenv("AGENT_MEMORY_MAX_ENTRIES", "10000"))


# ── Data types ────────────────────────────────────────────────────────────────


@dataclass
class MemoryEntry:
    """A single stored analysis memory."""

    memory_id: str
    file_path: str
    timestamp: float
    summary: str
    tags: list[str] = field(default_factory=list)
    bpm: float | None = None
    key: str | None = None
    genre: str | None = None
    mood: str | None = None
    quality_flags: list[str] = field(default_factory=list)
    analysis_depth: str = "standard"
    agent_outputs: dict[str, Any] = field(default_factory=dict)


@dataclass
class RecalledMemory:
    """A memory entry with relevance score from retrieval."""

    entry: MemoryEntry
    relevance_score: float
    context_text: str = ""


# ── Embedding helper ──────────────────────────────────────────────────────────


def _text_to_embedding(text: str) -> Any:
    """Convert text to 512-dim embedding vector."""
    import numpy as np

    try:
        from samplemind.core.search.faiss_index import CLAPEmbedder

        embedder = CLAPEmbedder()
        result = embedder.embed_text(text)
        # Validate result is a real numpy array with correct dimension
        if isinstance(result, np.ndarray) and result.shape[-1] == EMBEDDING_DIM:
            return result
        # Fall through to hash-based fallback
    except Exception:
        pass

    logger.debug("Using hash-based fallback embedding for text")
    import hashlib

    # Deterministic fallback: hash text into pseudo-embedding
    chunks = []
    for i in range((EMBEDDING_DIM * 4 // 32) + 1):
        h = hashlib.sha256(f"{text}:{i}".encode()).digest()
        chunks.append(h)
    raw = b"".join(chunks)
    vec = np.frombuffer(raw, dtype=np.uint8)[: EMBEDDING_DIM].astype(
        np.float32
    )
    vec = vec / 255.0 - 0.5
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec


def _state_to_summary(state: dict[str, Any]) -> str:
    """Extract a text summary from an AudioAnalysisState for embedding."""
    parts = []

    file_path = state.get("file_path", "")
    if file_path:
        parts.append(f"File: {Path(file_path).name}")

    features = state.get("audio_features", {})
    if features.get("bpm"):
        parts.append(f"BPM: {features['bpm']}")
    if features.get("key"):
        parts.append(f"Key: {features['key']}")

    tags = state.get("tags", {})
    if isinstance(tags, dict):
        if tags.get("genre"):
            parts.append(f"Genre: {tags['genre']}")
        if tags.get("mood"):
            parts.append(f"Mood: {tags['mood']}")
        if tags.get("instrument"):
            parts.append(f"Instrument: {tags['instrument']}")
        tag_list = tags.get("tags", [])
        if tag_list:
            parts.append(f"Tags: {', '.join(tag_list[:10])}")

    analysis = state.get("analysis_result", {})
    if isinstance(analysis, dict) and analysis.get("description"):
        parts.append(analysis["description"][:200])

    return " | ".join(parts) if parts else "Audio analysis"


def _state_to_memory_entry(state: dict[str, Any]) -> MemoryEntry:
    """Convert an AudioAnalysisState dict to a MemoryEntry."""
    import hashlib

    file_path = state.get("file_path", "unknown")
    ts = time.time()
    memory_id = hashlib.md5(f"{file_path}:{ts}".encode()).hexdigest()[:12]

    features = state.get("audio_features", {})
    tags = state.get("tags", {})
    tag_list = tags.get("tags", []) if isinstance(tags, dict) else []
    quality = state.get("quality_flags", {})
    quality_issues = quality.get("issues", []) if isinstance(quality, dict) else []

    return MemoryEntry(
        memory_id=memory_id,
        file_path=file_path,
        timestamp=ts,
        summary=_state_to_summary(state),
        tags=tag_list[:20],
        bpm=features.get("bpm"),
        key=features.get("key"),
        genre=tags.get("genre") if isinstance(tags, dict) else None,
        mood=tags.get("mood") if isinstance(tags, dict) else None,
        quality_flags=[str(q) for q in quality_issues[:10]],
        analysis_depth=state.get("analysis_depth", "standard"),
        agent_outputs={
            k: state.get(k)
            for k in [
                "analysis_result",
                "mixing_recommendations",
                "categorization",
                "micro_timing",
            ]
            if state.get(k)
        },
    )


# ── Main memory class ────────────────────────────────────────────────────────


class AgentMemory:
    """
    FAISS-backed conversation memory for the agent pipeline.

    Stores completed analysis results and enables semantic recall
    of relevant past analyses to inform current runs.
    """

    def __init__(self, memory_dir: str | Path | None = None) -> None:
        self.memory_dir = Path(memory_dir) if memory_dir else MEMORY_DIR
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self._index_path = self.memory_dir / "memory_index.bin"
        self._meta_path = self.memory_dir / "memory_meta.json"
        self._index: Any = None  # Lazy-loaded FAISS index
        self._entries: list[MemoryEntry] = []
        self._loaded = False

    def _ensure_loaded(self) -> None:
        """Lazy-load the index and metadata from disk."""
        if self._loaded:
            return

        import numpy as np

        # Load metadata
        if self._meta_path.exists():
            try:
                with open(self._meta_path) as f:
                    raw = json.load(f)
                self._entries = [MemoryEntry(**e) for e in raw]
                logger.info(
                    "Loaded %d memory entries from %s",
                    len(self._entries),
                    self._meta_path,
                )
            except Exception as exc:
                logger.warning("Failed to load memory metadata: %s", exc)
                self._entries = []

        # Load FAISS index
        try:
            import faiss

            if self._index_path.exists():
                self._index = faiss.read_index(str(self._index_path))
                logger.info(
                    "Loaded FAISS memory index with %d vectors",
                    self._index.ntotal,
                )
            else:
                self._index = faiss.IndexFlatIP(EMBEDDING_DIM)
                logger.info(
                    "Created new FAISS memory index (dim=%d)", EMBEDDING_DIM
                )
        except ImportError:
            logger.info(
                "FAISS not available — memory recall will use brute-force"
            )
            self._index = None

        self._loaded = True

    def _save(self) -> None:
        """Persist index and metadata to disk."""
        try:
            with open(self._meta_path, "w") as f:
                json.dump(
                    [asdict(e) for e in self._entries], f, indent=2, default=str
                )
        except Exception as exc:
            logger.warning("Failed to save memory metadata: %s", exc)

        if self._index is not None:
            try:
                import faiss

                faiss.write_index(self._index, str(self._index_path))
            except Exception as exc:
                logger.warning("Failed to save FAISS memory index: %s", exc)

    async def store(self, state: dict[str, Any]) -> MemoryEntry:
        """
        Store a completed pipeline state as a memory entry.

        Args:
            state: AudioAnalysisState dict from a completed pipeline run.

        Returns:
            The created MemoryEntry.
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        self._ensure_loaded()

        entry = _state_to_memory_entry(state)
        summary_text = entry.summary

        def _embed_and_store() -> None:
            import numpy as np

            embedding = _text_to_embedding(summary_text)
            embedding = np.array(embedding, dtype=np.float32).reshape(1, -1)

            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm

            if self._index is not None:
                self._index.add(embedding)

            self._entries.append(entry)

            # Enforce max entries
            if len(self._entries) > MAX_MEMORY_ENTRIES:
                overflow = len(self._entries) - MAX_MEMORY_ENTRIES
                self._entries = self._entries[overflow:]
                if self._index is not None:
                    try:
                        import faiss

                        new_index = faiss.IndexFlatIP(EMBEDDING_DIM)
                        if self._index.ntotal > overflow:
                            vectors = np.zeros(
                                (self._index.ntotal - overflow, EMBEDDING_DIM),
                                dtype=np.float32,
                            )
                            for i in range(overflow, self._index.ntotal):
                                vectors[i - overflow] = (
                                    self._index.reconstruct(i)
                                )
                            new_index.add(vectors)
                        self._index = new_index
                    except Exception as exc:
                        logger.warning("Failed to trim index: %s", exc)

            self._save()

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=1) as executor:
            await loop.run_in_executor(executor, _embed_and_store)

        logger.info(
            "Stored memory entry %s for %s",
            entry.memory_id,
            entry.file_path,
        )
        return entry

    async def recall(
        self,
        query: str,
        top_k: int = 5,
        min_relevance: float = 0.3,
    ) -> list[RecalledMemory]:
        """
        Recall relevant past analyses for the given query.

        Args:
            query: Natural language query (e.g. "dark 808 kick 140 BPM")
            top_k: Maximum number of memories to return.
            min_relevance: Minimum cosine similarity threshold.

        Returns:
            List of RecalledMemory sorted by relevance (descending).
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        self._ensure_loaded()

        if not self._entries:
            return []

        def _search() -> list[RecalledMemory]:
            import numpy as np

            query_vec = _text_to_embedding(query)
            query_vec = np.array(query_vec, dtype=np.float32).reshape(1, -1)
            norm = np.linalg.norm(query_vec)
            if norm > 0:
                query_vec = query_vec / norm

            results: list[RecalledMemory] = []
            used_faiss = False

            if (
                self._index is not None
                and hasattr(self._index, "ntotal")
            ):
                try:
                    ntotal = int(self._index.ntotal)
                except (TypeError, ValueError):
                    ntotal = 0

                if ntotal > 0:
                    try:
                        k = min(top_k, ntotal)
                        scores, indices = self._index.search(query_vec, k)

                        for score, idx in zip(scores[0], indices[0]):
                            if idx < 0 or idx >= len(self._entries):
                                continue
                            if score < min_relevance:
                                continue
                            entry = self._entries[idx]
                            context = (
                                f"Previous analysis of {Path(entry.file_path).name}: "
                                f"{entry.summary}"
                            )
                            results.append(
                                RecalledMemory(
                                    entry=entry,
                                    relevance_score=float(score),
                                    context_text=context,
                                )
                            )
                        used_faiss = True
                    except Exception as exc:
                        logger.debug("FAISS search failed: %s — using brute-force", exc)

            if not used_faiss:
                # Brute-force fallback without FAISS
                for entry in self._entries[-100:]:
                    query_lower = query.lower()
                    summary_lower = entry.summary.lower()
                    words = query_lower.split()
                    matches = sum(1 for w in words if w in summary_lower)
                    score = matches / max(len(words), 1)
                    if score >= min_relevance:
                        results.append(
                            RecalledMemory(
                                entry=entry,
                                relevance_score=score,
                                context_text=f"Previous: {entry.summary}",
                            )
                        )

            results.sort(key=lambda r: r.relevance_score, reverse=True)
            return results[:top_k]

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=1) as executor:
            results = await loop.run_in_executor(executor, _search)

        logger.info(
            "Recalled %d memories for query: %s", len(results), query[:80]
        )
        return results

    async def get_conversation_context(
        self,
        file_path: str,
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
        """
        Build conversation context messages from similar past analyses.

        Designed to be injected into the LangGraph state as prior context
        so agents can reference related past work.

        Args:
            file_path: Path to the current audio file being analyzed.
            top_k: Number of past analyses to include.

        Returns:
            List of context dicts suitable for agent prompts.
        """
        query = f"Similar audio to {Path(file_path).name}"
        memories = await self.recall(query, top_k=top_k, min_relevance=0.2)

        context: list[dict[str, Any]] = []
        for mem in memories:
            context.append(
                {
                    "role": "system",
                    "content": (
                        f"[Past analysis reference] {mem.context_text}\n"
                        f"BPM: {mem.entry.bpm}, Key: {mem.entry.key}, "
                        f"Genre: {mem.entry.genre}, Mood: {mem.entry.mood}"
                    ),
                    "metadata": {
                        "memory_id": mem.entry.memory_id,
                        "relevance": mem.relevance_score,
                        "file": mem.entry.file_path,
                    },
                }
            )

        return context

    @property
    def entry_count(self) -> int:
        """Number of stored memory entries."""
        self._ensure_loaded()
        return len(self._entries)

    async def clear(self) -> None:
        """Clear all stored memories."""
        self._entries = []
        self._loaded = False

        try:
            import faiss

            self._index = faiss.IndexFlatIP(EMBEDDING_DIM)
        except ImportError:
            self._index = None

        self._save()
        logger.info("Cleared all agent memory entries")
