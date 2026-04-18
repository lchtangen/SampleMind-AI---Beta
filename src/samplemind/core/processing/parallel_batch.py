"""
Parallel Batch Processor — P1-018

Multi-process parallel audio processing using joblib for batch analysis jobs.
Automatically scales to available CPU cores for maximum throughput.

Capabilities:
  - Parallel file analysis across multiple CPU cores
  - Configurable batch sizes and worker counts
  - Progress tracking with callback support
  - Error isolation per file (one failure doesn't kill the batch)
  - Memory-efficient processing with controlled concurrency

Usage::

    from samplemind.core.processing.parallel_batch import ParallelBatchProcessor

    processor = ParallelBatchProcessor(n_jobs=4)
    results = await processor.process_batch(
        file_paths=[Path("a.wav"), Path("b.wav"), Path("c.wav")],
        analysis_fn=my_analysis_function,
    )
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import numpy as np

logger = logging.getLogger(__name__)

# Sensible defaults
DEFAULT_N_JOBS = min(os.cpu_count() or 2, 8)
DEFAULT_BATCH_SIZE = 50
DEFAULT_SR = 22050


@dataclass
class BatchFileResult:
    """Result from processing a single file in the batch."""

    file_path: str
    success: bool = False
    features: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    processing_time_ms: float = 0.0
    file_duration: float = 0.0


@dataclass
class BatchResult:
    """Aggregated result from processing a batch of files."""

    total_files: int = 0
    successful: int = 0
    failed: int = 0
    total_audio_duration: float = 0.0
    total_processing_time_ms: float = 0.0
    files_per_second: float = 0.0
    speedup_factor: float = 1.0
    results: list[BatchFileResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "total_files": self.total_files,
            "successful": self.successful,
            "failed": self.failed,
            "total_audio_duration": round(self.total_audio_duration, 2),
            "total_processing_time_ms": round(self.total_processing_time_ms, 1),
            "files_per_second": round(self.files_per_second, 2),
            "speedup_factor": round(self.speedup_factor, 2),
            "results": [
                {
                    "file_path": r.file_path,
                    "success": r.success,
                    "features": r.features,
                    "error": r.error,
                    "processing_time_ms": round(r.processing_time_ms, 1),
                }
                for r in self.results
            ],
            "errors": self.errors,
        }


# Type for analysis functions
AnalysisFn = Callable[[np.ndarray, int], dict[str, Any]]


def _process_single_file(
    file_path: str,
    analysis_fn: AnalysisFn | None,
    target_sr: int,
) -> BatchFileResult:
    """
    Process a single audio file — designed to be called in parallel.

    This is a module-level function (not a method) so joblib can pickle it.

    Args:
        file_path: Path to the audio file.
        analysis_fn: Analysis function to call.
        target_sr: Target sample rate.

    Returns:
        BatchFileResult with features or error.
    """
    start = time.monotonic()
    result = BatchFileResult(file_path=file_path)

    try:
        import librosa

        y, sr = librosa.load(file_path, sr=target_sr, mono=True)
        result.file_duration = round(float(len(y)) / sr, 3)

        if analysis_fn is not None:
            result.features = analysis_fn(y, sr)
        else:
            result.features = _default_batch_analysis(y, sr)

        result.success = True

    except Exception as exc:
        result.error = f"{type(exc).__name__}: {exc}"
        logger.debug("Batch processing failed for %s: %s", file_path, exc)

    result.processing_time_ms = round((time.monotonic() - start) * 1000, 1)
    return result


def _default_batch_analysis(y: np.ndarray, sr: int) -> dict[str, Any]:
    """Default analysis for batch processing — fast feature extraction."""
    features: dict[str, Any] = {
        "duration": round(float(len(y)) / sr, 3),
        "rms": round(float(np.sqrt(np.mean(y**2))), 6),
        "peak": round(float(np.max(np.abs(y))), 6),
        "crest_factor": round(
            float(np.max(np.abs(y)) / (np.sqrt(np.mean(y**2)) + 1e-9)), 3
        ),
        "zero_crossing_rate": round(
            float(np.mean(np.abs(np.diff(np.sign(y))) > 0)), 6
        ),
    }

    try:
        import librosa

        # BPM
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        bpm_val = float(tempo) if np.isscalar(tempo) else float(tempo[0])
        features["bpm"] = round(bpm_val, 2)

        # Spectral features
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        features["spectral_centroid_mean"] = round(float(np.mean(centroid)), 2)

        bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        features["spectral_bandwidth_mean"] = round(float(np.mean(bandwidth)), 2)

        # Key estimation (chroma-based)
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        key_idx = int(np.argmax(np.mean(chroma, axis=1)))
        key_names = [
            "C",
            "C#",
            "D",
            "D#",
            "E",
            "F",
            "F#",
            "G",
            "G#",
            "A",
            "A#",
            "B",
        ]
        features["estimated_key"] = key_names[key_idx]

        # MFCCs (first 13)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        features["mfcc_means"] = [round(float(m), 4) for m in np.mean(mfccs, axis=1)]

    except ImportError:
        pass

    return features


class ParallelBatchProcessor:
    """
    Multi-process parallel audio processing for batch analysis jobs.

    Uses joblib for parallel execution across CPU cores with automatic
    error isolation per file.
    """

    def __init__(
        self,
        n_jobs: int = DEFAULT_N_JOBS,
        batch_size: int = DEFAULT_BATCH_SIZE,
        target_sr: int = DEFAULT_SR,
        backend: str = "loky",
    ) -> None:
        """
        Args:
            n_jobs: Number of parallel workers (-1 = all CPUs).
            batch_size: Maximum files per batch (for memory management).
            target_sr: Target sample rate for loading.
            backend: joblib backend ("loky", "threading", "multiprocessing").
        """
        self.n_jobs = n_jobs
        self.batch_size = batch_size
        self.target_sr = target_sr
        self.backend = backend

    async def process_batch(
        self,
        file_paths: list[Path],
        analysis_fn: AnalysisFn | None = None,
        on_progress: Callable[[int, int], None] | None = None,
    ) -> BatchResult:
        """
        Process a batch of audio files in parallel.

        Args:
            file_paths: List of audio file paths.
            analysis_fn: Optional analysis function for each file.
            on_progress: Optional callback(completed, total) for progress.

        Returns:
            BatchResult with all file results.
        """
        import asyncio

        overall_start = time.monotonic()
        total_files = len(file_paths)

        batch_result = BatchResult(total_files=total_files)

        if total_files == 0:
            return batch_result

        # Process in sub-batches to manage memory
        all_results: list[BatchFileResult] = []

        for batch_start in range(0, total_files, self.batch_size):
            batch_end = min(batch_start + self.batch_size, total_files)
            batch_paths = file_paths[batch_start:batch_end]

            # Run parallel processing in executor to not block event loop
            sub_results = await asyncio.get_event_loop().run_in_executor(
                None,
                self._run_parallel_batch,
                batch_paths,
                analysis_fn,
            )

            all_results.extend(sub_results)

            if on_progress:
                on_progress(len(all_results), total_files)

        # Aggregate results
        batch_result.results = all_results
        batch_result.successful = sum(1 for r in all_results if r.success)
        batch_result.failed = sum(1 for r in all_results if not r.success)
        batch_result.total_audio_duration = sum(
            r.file_duration for r in all_results
        )
        batch_result.errors = [
            f"{r.file_path}: {r.error}" for r in all_results if r.error
        ]

        elapsed_ms = (time.monotonic() - overall_start) * 1000
        batch_result.total_processing_time_ms = round(elapsed_ms, 1)

        if elapsed_ms > 0:
            batch_result.files_per_second = round(
                total_files / (elapsed_ms / 1000), 2
            )

        # Estimate speedup vs sequential
        sequential_est = sum(r.processing_time_ms for r in all_results)
        if elapsed_ms > 0 and sequential_est > 0:
            batch_result.speedup_factor = round(sequential_est / elapsed_ms, 2)

        logger.info(
            "Batch complete: %d/%d succeeded in %.1fms (%.1fx speedup, %.1f files/s)",
            batch_result.successful,
            total_files,
            elapsed_ms,
            batch_result.speedup_factor,
            batch_result.files_per_second,
        )

        return batch_result

    def _run_parallel_batch(
        self,
        file_paths: list[Path],
        analysis_fn: AnalysisFn | None,
    ) -> list[BatchFileResult]:
        """Run joblib parallel processing on a sub-batch."""
        try:
            from joblib import Parallel, delayed

            results = Parallel(
                n_jobs=self.n_jobs,
                backend=self.backend,
                verbose=0,
            )(
                delayed(_process_single_file)(
                    str(fp), analysis_fn, self.target_sr
                )
                for fp in file_paths
            )
            return list(results)

        except ImportError:
            logger.warning(
                "joblib not available — falling back to sequential processing"
            )
            return [
                _process_single_file(str(fp), analysis_fn, self.target_sr)
                for fp in file_paths
            ]

    def process_batch_sync(
        self,
        file_paths: list[Path],
        analysis_fn: AnalysisFn | None = None,
    ) -> BatchResult:
        """
        Synchronous batch processing (for CLI/non-async contexts).

        Args:
            file_paths: List of audio file paths.
            analysis_fn: Optional analysis function.

        Returns:
            BatchResult with all file results.
        """
        overall_start = time.monotonic()
        total_files = len(file_paths)

        all_results = self._run_parallel_batch(file_paths, analysis_fn)

        batch_result = BatchResult(
            total_files=total_files,
            results=all_results,
            successful=sum(1 for r in all_results if r.success),
            failed=sum(1 for r in all_results if not r.success),
            total_audio_duration=sum(r.file_duration for r in all_results),
            errors=[
                f"{r.file_path}: {r.error}" for r in all_results if r.error
            ],
        )

        elapsed_ms = (time.monotonic() - overall_start) * 1000
        batch_result.total_processing_time_ms = round(elapsed_ms, 1)

        if elapsed_ms > 0:
            batch_result.files_per_second = round(
                total_files / (elapsed_ms / 1000), 2
            )

        sequential_est = sum(r.processing_time_ms for r in all_results)
        if elapsed_ms > 0 and sequential_est > 0:
            batch_result.speedup_factor = round(sequential_est / elapsed_ms, 2)

        return batch_result


# ── Module exports ────────────────────────────────────────────────────────────

__all__ = [
    "ParallelBatchProcessor",
    "BatchResult",
    "BatchFileResult",
]
