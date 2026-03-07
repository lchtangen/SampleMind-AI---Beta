"""
SampleMind AI — Advanced Audio Loader

Core audio loading engine with:
- Multi-strategy loading (FAST / BALANCED / QUALITY / STREAMING)
- Async loading via ThreadPoolExecutor
- LRU in-memory cache (keyed by file hash + params)
- Batch loading (parallel or sequential)
- Directory scanning and statistics
"""

import asyncio
import hashlib
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np

from .format_detector import AudioFormatDetector
from .metadata_extractor import MetadataExtractor
from .models import AudioFormat, AudioMetadata, LoadedAudio, LoadingStrategy

logger = logging.getLogger(__name__)


class AdvancedAudioLoader:
    """
    Advanced audio file loader with professional features.

    Provides intelligent loading strategies, format detection, metadata
    extraction, and batch processing for professional music production
    workflows.
    """

    def __init__(
        self,
        default_strategy: LoadingStrategy = LoadingStrategy.BALANCED,
        max_workers: int = 4,
        cache_enabled: bool = True,
        cache_size: int = 100,
    ) -> None:
        self.default_strategy = default_strategy
        self.max_workers = max_workers
        self.cache_enabled = cache_enabled
        self.cache_size = cache_size

        self.format_detector = AudioFormatDetector()
        self.metadata_extractor = MetadataExtractor()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        self.audio_cache: Dict[str, LoadedAudio] = {}
        self.metadata_cache: Dict[str, AudioMetadata] = {}
        self.loading_stats: Dict[str, Any] = {
            "total_loads": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "avg_load_time": 0.0,
            "total_files_processed": 0,
            "format_distribution": {},
        }

        logger.info("🎵 AdvancedAudioLoader initialised (strategy: %s)", default_strategy.value)

    # ── Public API ─────────────────────────────────────────────────────────────

    def load_audio(
        self,
        file_path: Union[str, Path],
        strategy: Optional[LoadingStrategy] = None,
        target_sr: Optional[int] = None,
        mono: bool = True,
        normalize: bool = True,
        use_cache: bool = True,
    ) -> LoadedAudio:
        """Load a single audio file with the specified strategy."""
        start_time = time.time()
        file_path = Path(file_path)
        strategy = strategy or self.default_strategy

        cache_key = self._generate_cache_key(file_path, strategy, target_sr, mono, normalize)

        if use_cache and self.cache_enabled and cache_key in self.audio_cache:
            self.loading_stats["cache_hits"] += 1
            logger.debug("📦 Cache hit: %s", file_path.name)
            return self.audio_cache[cache_key]

        self.loading_stats["cache_misses"] += 1

        try:
            audio_format = self.format_detector.detect_format(file_path)
            if not audio_format:
                raise ValueError(f"Unsupported audio format: {file_path}")

            metadata = self._create_metadata(file_path, audio_format)
            audio_data, actual_sr = self._load_with_strategy(file_path, strategy, target_sr)

            is_stereo = len(audio_data.shape) > 1
            if mono and is_stereo:
                audio_data = np.mean(audio_data, axis=1)
                is_stereo = False

            if normalize:
                peak = np.max(np.abs(audio_data))
                if peak > 0:
                    audio_data = audio_data * (0.95 / peak)
                    metadata.normalization_applied = True

            peak_amplitude = float(np.max(np.abs(audio_data)))
            rms_level = float(np.sqrt(np.mean(audio_data**2)))

            metadata.sample_rate = actual_sr
            metadata.channels = 1 if (mono or not is_stereo) else 2
            metadata.duration = len(audio_data) / actual_sr
            metadata.load_time = time.time() - start_time
            metadata.strategy_used = strategy

            loaded_audio = LoadedAudio(
                audio_data=audio_data,
                metadata=metadata,
                is_stereo=is_stereo,
                peak_amplitude=peak_amplitude,
                rms_level=rms_level,
            )

            if use_cache and self.cache_enabled:
                self._cache_audio(cache_key, loaded_audio)

            self._update_loading_stats(audio_format, time.time() - start_time)
            logger.info(
                "✅ Loaded: %s (%.2fs, %s)",
                file_path.name,
                loaded_audio.get_duration_seconds(),
                strategy.value,
            )
            return loaded_audio

        except Exception:
            logger.exception("❌ Failed to load %s", file_path)
            raise

    async def load_audio_async(
        self,
        file_path: Union[str, Path],
        strategy: Optional[LoadingStrategy] = None,
        **kwargs: Any,
    ) -> LoadedAudio:
        """Asynchronous wrapper around :meth:`load_audio`."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.load_audio,
            file_path,
            strategy,
            kwargs.get("target_sr"),
            kwargs.get("mono", True),
            kwargs.get("normalize", True),
            kwargs.get("use_cache", True),
        )

    # ── Batch loading ──────────────────────────────────────────────────────────

    def batch_load(
        self,
        file_paths: List[Union[str, Path]],
        strategy: Optional[LoadingStrategy] = None,
        parallel: bool = True,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[LoadedAudio]:
        """Load multiple audio files, optionally in parallel."""
        logger.info("🔄 Batch loading %d files (parallel=%s)", len(file_paths), parallel)
        strategy = strategy or self.default_strategy

        if parallel:
            return self._batch_load_parallel(file_paths, strategy, progress_callback)
        return self._batch_load_sequential(file_paths, strategy, progress_callback)

    def _batch_load_parallel(
        self,
        file_paths: List[Union[str, Path]],
        strategy: LoadingStrategy,
        progress_callback: Optional[Callable[[int, int], None]],
    ) -> List[LoadedAudio]:
        results: List[Optional[LoadedAudio]] = [None] * len(file_paths)
        futures = [
            (i, self.executor.submit(self.load_audio, fp, strategy))
            for i, fp in enumerate(file_paths)
        ]
        completed = 0
        for i, future in futures:
            try:
                results[i] = future.result()
                completed += 1
                if progress_callback:
                    progress_callback(completed, len(file_paths))
            except Exception:
                logger.exception("❌ Parallel load failed: %s", file_paths[i])
        return [r for r in results if r is not None]

    def _batch_load_sequential(
        self,
        file_paths: List[Union[str, Path]],
        strategy: LoadingStrategy,
        progress_callback: Optional[Callable[[int, int], None]],
    ) -> List[LoadedAudio]:
        results: List[LoadedAudio] = []
        for i, file_path in enumerate(file_paths):
            try:
                results.append(self.load_audio(file_path, strategy))
                if progress_callback:
                    progress_callback(i + 1, len(file_paths))
            except Exception:
                logger.exception("❌ Sequential load failed: %s", file_path)
        return results

    # ── Directory scanning ─────────────────────────────────────────────────────

    def scan_directory(
        self,
        directory: Union[str, Path],
        recursive: bool = True,
        supported_only: bool = True,
    ) -> List[Path]:
        """Return a list of audio file paths found in *directory*."""
        directory = Path(directory)
        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory}")

        pattern = "**/*" if recursive else "*"
        files = [f for f in directory.glob(pattern) if f.is_file()]

        if supported_only:
            return [f for f in files if self.format_detector.is_supported_format(f)]
        return files

    def get_directory_info(self, directory: Union[str, Path]) -> Dict[str, Any]:
        """Return stats about audio files contained in *directory*."""
        audio_files = self.scan_directory(directory, recursive=True, supported_only=True)

        info: Dict[str, Any] = {
            "total_files": len(audio_files),
            "total_size": 0,
            "format_distribution": {},
            "files_by_format": {},
        }

        for file_path in audio_files:
            info["total_size"] += file_path.stat().st_size
            fmt = self.format_detector.detect_format(file_path)
            if fmt:
                name = fmt.name
                info["format_distribution"].setdefault(name, 0)
                info["files_by_format"].setdefault(name, [])
                info["format_distribution"][name] += 1
                info["files_by_format"][name].append(str(file_path))

        return info

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _load_with_strategy(
        self,
        file_path: Path,
        strategy: LoadingStrategy,
        target_sr: Optional[int],
    ) -> Tuple[np.ndarray, int]:
        import librosa  # lazy: heavy dep, only needed at load time
        import soundfile as sf  # lazy: heavy dep
        match strategy:
            case LoadingStrategy.FAST:
                y, sr = librosa.load(str(file_path), sr=target_sr or 22050, mono=False)
            case LoadingStrategy.BALANCED:
                y, sr = librosa.load(str(file_path), sr=target_sr, mono=False)
            case LoadingStrategy.QUALITY | LoadingStrategy.STREAMING:
                y, sr = sf.read(str(file_path), always_2d=False)
                if target_sr and sr != target_sr:
                    y = librosa.resample(y, orig_sr=sr, target_sr=target_sr)
                    sr = target_sr
            case _:
                raise ValueError(f"Unknown loading strategy: {strategy}")
        return y, sr

    def _create_metadata(self, file_path: Path, audio_format: AudioFormat) -> AudioMetadata:
        file_stat = file_path.stat()
        extracted = self.metadata_extractor.extract_metadata(file_path, audio_format)

        return AudioMetadata(
            file_path=file_path,
            file_size=file_stat.st_size,
            file_hash=self._compute_file_hash(file_path),
            format=audio_format,
            creation_time=file_stat.st_ctime,
            modification_time=file_stat.st_mtime,
            duration=extracted.get("duration", 0.0),
            sample_rate=extracted.get("sample_rate", 44100),
            channels=extracted.get("channels", 2),
            bit_depth=extracted.get("bit_depth"),
            bitrate=extracted.get("bitrate"),
            title=extracted.get("title"),
            artist=extracted.get("artist"),
            album=extracted.get("album"),
            genre=extracted.get("genre"),
            year=extracted.get("year"),
            track_number=extracted.get("track_number"),
        )

    def _generate_cache_key(
        self,
        file_path: Path,
        strategy: LoadingStrategy,
        target_sr: Optional[int],
        mono: bool,
        normalize: bool,
    ) -> str:
        stat = file_path.stat()
        raw = f"{file_path}_{stat.st_mtime}_{stat.st_size}_{strategy.value}_{target_sr}_{mono}_{normalize}"
        return hashlib.md5(raw.encode()).hexdigest()

    def _compute_file_hash(self, file_path: Path) -> str:
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()

    def _cache_audio(self, cache_key: str, loaded_audio: LoadedAudio) -> None:
        if len(self.audio_cache) >= self.cache_size:
            oldest = next(iter(self.audio_cache))
            del self.audio_cache[oldest]
        self.audio_cache[cache_key] = loaded_audio

    def _update_loading_stats(self, audio_format: AudioFormat, load_time: float) -> None:
        stats = self.loading_stats
        stats["total_loads"] += 1
        prev_avg = stats["avg_load_time"]
        prev_n = stats["total_loads"] - 1
        stats["avg_load_time"] = (prev_avg * prev_n + load_time) / stats["total_loads"]
        stats["format_distribution"].setdefault(audio_format.name, 0)
        stats["format_distribution"][audio_format.name] += 1

    def get_loading_stats(self) -> Dict[str, Any]:
        """Return loading performance statistics."""
        total = self.loading_stats["cache_hits"] + self.loading_stats["cache_misses"]
        hit_rate = self.loading_stats["cache_hits"] / total if total else 0.0
        return {
            **self.loading_stats,
            "cache_hit_rate": hit_rate,
            "cache_size": len(self.audio_cache),
            "supported_formats": [fmt.name for fmt in AudioFormat],
        }

    def clear_cache(self) -> None:
        """Clear all in-memory caches."""
        self.audio_cache.clear()
        self.metadata_cache.clear()
        self.loading_stats["cache_hits"] = 0
        self.loading_stats["cache_misses"] = 0
        logger.info("🧹 Audio loader cache cleared")

    def shutdown(self) -> None:
        """Shut down the thread pool executor."""
        self.executor.shutdown(wait=True)
        logger.info("🔴 AdvancedAudioLoader shut down")


# ── Factory ────────────────────────────────────────────────────────────────────

def create_loader_from_config(config: Dict[str, Any]) -> AdvancedAudioLoader:
    """Instantiate an :class:`AdvancedAudioLoader` from a config dict."""
    return AdvancedAudioLoader(
        default_strategy=LoadingStrategy(config.get("default_strategy", "balanced")),
        max_workers=config.get("max_workers", 4),
        cache_enabled=config.get("cache_enabled", True),
        cache_size=config.get("cache_size", 100),
    )
