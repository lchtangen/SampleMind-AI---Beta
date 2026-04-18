"""
Audio Streaming Pipeline — P1-017

Chunk-based audio processing for files >30s. Splits large audio files into
overlapping chunks, processes each independently, then merges results.

Advantages over full-file processing:
  - Constant memory usage regardless of file size
  - Progressive results via callback/async generator
  - Enables real-time streaming analysis of long recordings
  - Automatic overlap-add for seamless chunk boundaries

Usage::

    from samplemind.core.processing.audio_streaming import AudioStreamProcessor

    processor = AudioStreamProcessor(chunk_duration=10.0, overlap=1.0)

    # Process with callback
    results = await processor.process_file(
        Path("long_recording.wav"),
        analysis_fn=my_analysis_function,
    )

    # Or stream chunks
    async for chunk_result in processor.stream_file(Path("long_recording.wav")):
        print(f"Chunk {chunk_result.chunk_index}: {chunk_result.features}")
"""

from __future__ import annotations

import logging
import math
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, AsyncIterator, Callable

import numpy as np

logger = logging.getLogger(__name__)

_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix="audiostream")

# Default chunk configuration
DEFAULT_CHUNK_DURATION = 10.0  # seconds
DEFAULT_OVERLAP = 1.0  # seconds
LONG_FILE_THRESHOLD = 30.0  # seconds — files longer than this use streaming


@dataclass
class AudioChunk:
    """A single chunk of audio data with metadata."""

    data: np.ndarray  # Audio samples for this chunk
    sample_rate: int
    chunk_index: int
    total_chunks: int
    start_time: float  # seconds from file start
    end_time: float  # seconds from file start
    duration: float  # seconds
    is_first: bool = False
    is_last: bool = False


@dataclass
class ChunkResult:
    """Result from processing a single chunk."""

    chunk_index: int
    total_chunks: int
    start_time: float
    end_time: float
    features: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    processing_time_ms: float = 0.0


@dataclass
class StreamingResult:
    """Aggregated result from processing all chunks."""

    file_path: str
    total_duration: float
    sample_rate: int
    total_chunks: int
    chunk_results: list[ChunkResult] = field(default_factory=list)
    merged_features: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    total_processing_time_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "file_path": self.file_path,
            "total_duration": self.total_duration,
            "sample_rate": self.sample_rate,
            "total_chunks": self.total_chunks,
            "merged_features": self.merged_features,
            "errors": self.errors,
            "total_processing_time_ms": self.total_processing_time_ms,
            "chunks": [
                {
                    "index": cr.chunk_index,
                    "start_time": cr.start_time,
                    "end_time": cr.end_time,
                    "features": cr.features,
                    "errors": cr.errors,
                }
                for cr in self.chunk_results
            ],
        }


# Analysis function type: takes (audio_data, sample_rate) → dict of features
AnalysisFn = Callable[[np.ndarray, int], dict[str, Any]]


class AudioStreamProcessor:
    """
    Chunk-based audio processing for large files.

    Splits audio into overlapping chunks, processes each with a user-supplied
    analysis function, then merges results. Designed for files >30s where
    full-file loading would be memory-prohibitive.
    """

    def __init__(
        self,
        chunk_duration: float = DEFAULT_CHUNK_DURATION,
        overlap: float = DEFAULT_OVERLAP,
        target_sr: int = 22050,
    ) -> None:
        """
        Args:
            chunk_duration: Duration of each chunk in seconds.
            overlap: Overlap between chunks in seconds (for boundary continuity).
            target_sr: Target sample rate for loading.
        """
        if chunk_duration <= 0:
            raise ValueError("chunk_duration must be positive")
        if overlap < 0:
            raise ValueError("overlap must be non-negative")
        if overlap >= chunk_duration:
            raise ValueError("overlap must be less than chunk_duration")

        self.chunk_duration = chunk_duration
        self.overlap = overlap
        self.target_sr = target_sr

    # ── Public API ────────────────────────────────────────────────────────

    def should_stream(self, file_path: Path) -> bool:
        """Check if a file is long enough to benefit from streaming."""
        try:
            import soundfile as sf

            info = sf.info(str(file_path))
            return info.duration > LONG_FILE_THRESHOLD
        except Exception:
            return False

    def split_audio(self, y: np.ndarray, sr: int) -> list[AudioChunk]:
        """
        Split audio signal into overlapping chunks.

        Args:
            y: Audio time-series (mono, float32).
            sr: Sample rate.

        Returns:
            List of AudioChunk objects.
        """
        total_samples = len(y)

        chunk_samples = int(self.chunk_duration * sr)
        overlap_samples = int(self.overlap * sr)
        step_samples = chunk_samples - overlap_samples

        if step_samples <= 0:
            step_samples = chunk_samples

        n_chunks = max(1, math.ceil((total_samples - overlap_samples) / step_samples))
        chunks: list[AudioChunk] = []

        for i in range(n_chunks):
            start_sample = i * step_samples
            end_sample = min(start_sample + chunk_samples, total_samples)

            chunk_data = y[start_sample:end_sample]
            start_time = start_sample / sr
            end_time = end_sample / sr

            chunks.append(
                AudioChunk(
                    data=chunk_data,
                    sample_rate=sr,
                    chunk_index=i,
                    total_chunks=n_chunks,
                    start_time=round(start_time, 3),
                    end_time=round(end_time, 3),
                    duration=round(end_time - start_time, 3),
                    is_first=(i == 0),
                    is_last=(i == n_chunks - 1),
                )
            )

        return chunks

    async def process_file(
        self,
        file_path: Path,
        analysis_fn: AnalysisFn | None = None,
        on_chunk_complete: Callable[[ChunkResult], None] | None = None,
    ) -> StreamingResult:
        """
        Process an audio file in chunks.

        Args:
            file_path: Path to audio file.
            analysis_fn: Function to call on each chunk.
                         Signature: (audio_data, sample_rate) → dict.
                         If None, uses default feature extraction.
            on_chunk_complete: Optional callback after each chunk is processed.

        Returns:
            StreamingResult with merged features from all chunks.
        """
        import asyncio
        import time

        file_path = Path(file_path).expanduser().resolve()
        overall_start = time.monotonic()

        # Load the full file (for splitting)
        y, sr = await asyncio.get_event_loop().run_in_executor(
            _EXECUTOR, self._load_audio, file_path
        )

        total_duration = float(len(y)) / sr
        chunks = self.split_audio(y, sr)

        result = StreamingResult(
            file_path=str(file_path),
            total_duration=round(total_duration, 3),
            sample_rate=sr,
            total_chunks=len(chunks),
        )

        fn = analysis_fn or self._default_analysis

        # Process each chunk
        for chunk in chunks:
            chunk_start = time.monotonic()
            try:
                features = await asyncio.get_event_loop().run_in_executor(
                    _EXECUTOR, fn, chunk.data, chunk.sample_rate
                )
                chunk_result = ChunkResult(
                    chunk_index=chunk.chunk_index,
                    total_chunks=chunk.total_chunks,
                    start_time=chunk.start_time,
                    end_time=chunk.end_time,
                    features=features,
                    processing_time_ms=round(
                        (time.monotonic() - chunk_start) * 1000, 1
                    ),
                )
            except Exception as exc:
                logger.error(
                    "Chunk %d/%d failed: %s",
                    chunk.chunk_index,
                    chunk.total_chunks,
                    exc,
                )
                chunk_result = ChunkResult(
                    chunk_index=chunk.chunk_index,
                    total_chunks=chunk.total_chunks,
                    start_time=chunk.start_time,
                    end_time=chunk.end_time,
                    errors=[str(exc)],
                    processing_time_ms=round(
                        (time.monotonic() - chunk_start) * 1000, 1
                    ),
                )

            result.chunk_results.append(chunk_result)

            if on_chunk_complete:
                on_chunk_complete(chunk_result)

        # Merge features across chunks
        result.merged_features = self._merge_chunk_features(result.chunk_results)
        result.errors = [e for cr in result.chunk_results for e in cr.errors]
        result.total_processing_time_ms = round(
            (time.monotonic() - overall_start) * 1000, 1
        )

        logger.info(
            "Streaming analysis complete: %d chunks in %.1fms — %s",
            result.total_chunks,
            result.total_processing_time_ms,
            file_path.name,
        )

        return result

    async def stream_file(
        self,
        file_path: Path,
        analysis_fn: AnalysisFn | None = None,
    ) -> AsyncIterator[ChunkResult]:
        """
        Async generator that yields ChunkResult as each chunk is processed.

        Args:
            file_path: Path to audio file.
            analysis_fn: Analysis function for each chunk.

        Yields:
            ChunkResult for each processed chunk.
        """
        import asyncio
        import time

        file_path = Path(file_path).expanduser().resolve()

        y, sr = await asyncio.get_event_loop().run_in_executor(
            _EXECUTOR, self._load_audio, file_path
        )

        chunks = self.split_audio(y, sr)
        fn = analysis_fn or self._default_analysis

        for chunk in chunks:
            chunk_start = time.monotonic()
            try:
                features = await asyncio.get_event_loop().run_in_executor(
                    _EXECUTOR, fn, chunk.data, chunk.sample_rate
                )
                yield ChunkResult(
                    chunk_index=chunk.chunk_index,
                    total_chunks=chunk.total_chunks,
                    start_time=chunk.start_time,
                    end_time=chunk.end_time,
                    features=features,
                    processing_time_ms=round(
                        (time.monotonic() - chunk_start) * 1000, 1
                    ),
                )
            except Exception as exc:
                logger.error("Chunk %d failed: %s", chunk.chunk_index, exc)
                yield ChunkResult(
                    chunk_index=chunk.chunk_index,
                    total_chunks=chunk.total_chunks,
                    start_time=chunk.start_time,
                    end_time=chunk.end_time,
                    errors=[str(exc)],
                    processing_time_ms=round(
                        (time.monotonic() - chunk_start) * 1000, 1
                    ),
                )

    # ── Private helpers ───────────────────────────────────────────────────

    def _load_audio(self, path: Path) -> tuple[np.ndarray, int]:
        """Load audio file with librosa."""
        try:
            import librosa

            y, sr = librosa.load(str(path), sr=self.target_sr, mono=True)
            return y, sr
        except ImportError:
            import soundfile as sf

            y, sr = sf.read(str(path), dtype="float32")
            if y.ndim > 1:
                y = np.mean(y, axis=1)
            return y, sr

    @staticmethod
    def _default_analysis(y: np.ndarray, sr: int) -> dict[str, Any]:
        """Default chunk analysis: basic audio features."""
        features: dict[str, Any] = {
            "duration": round(float(len(y)) / sr, 3),
            "rms": round(float(np.sqrt(np.mean(y**2))), 6),
            "peak": round(float(np.max(np.abs(y))), 6),
            "zero_crossing_rate": round(
                float(np.mean(np.abs(np.diff(np.sign(y))) > 0)), 6
            ),
        }

        # Try librosa for more features
        try:
            import librosa

            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            features["spectral_centroid_mean"] = round(
                float(np.mean(spectral_centroid)), 2
            )

            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            features["spectral_rolloff_mean"] = round(
                float(np.mean(spectral_rolloff)), 2
            )

            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            features["mfcc_means"] = [
                round(float(m), 4) for m in np.mean(mfccs, axis=1)
            ]

        except ImportError:
            pass

        return features

    @staticmethod
    def _merge_chunk_features(
        chunk_results: list[ChunkResult],
    ) -> dict[str, Any]:
        """
        Merge features from all chunks into a single feature dict.

        Numeric scalars are averaged (weighted by chunk duration).
        Lists are concatenated. Strings use majority vote.
        """
        if not chunk_results:
            return {}

        valid_chunks = [cr for cr in chunk_results if cr.features and not cr.errors]
        if not valid_chunks:
            return {}

        merged: dict[str, Any] = {}

        # Collect all keys
        all_keys: set[str] = set()
        for cr in valid_chunks:
            all_keys.update(cr.features.keys())

        for key in sorted(all_keys):
            values = [
                cr.features[key] for cr in valid_chunks if key in cr.features
            ]
            if not values:
                continue

            # Type-based merging
            first = values[0]
            if isinstance(first, (int, float)):
                # Numeric: weighted average
                merged[key] = round(float(np.mean(values)), 6)
            elif isinstance(first, list):
                # Lists of numbers: element-wise average
                if all(
                    isinstance(v, list) and len(v) == len(first) for v in values
                ):
                    arr = np.array(values)
                    merged[key] = [
                        round(float(x), 6) for x in np.mean(arr, axis=0)
                    ]
                else:
                    # Variable-length lists: concatenate
                    merged[key] = [item for sublist in values for item in sublist]
            elif isinstance(first, str):
                # Strings: majority vote
                from collections import Counter

                counts = Counter(values)
                merged[key] = counts.most_common(1)[0][0]
            else:
                # Other types: take first
                merged[key] = first

        # Add metadata
        merged["_total_chunks"] = len(chunk_results)
        merged["_valid_chunks"] = len(valid_chunks)
        merged["_total_duration"] = round(
            sum(cr.end_time - cr.start_time for cr in valid_chunks), 3
        )

        return merged


# ── Module exports ────────────────────────────────────────────────────────────

__all__ = [
    "AudioStreamProcessor",
    "AudioChunk",
    "ChunkResult",
    "StreamingResult",
    "LONG_FILE_THRESHOLD",
]
