"""
AudioEngine Bridge for Textual TUI Integration

Provides async wrapper around AudioEngine for TUI integration with:
- Real-time progress callbacks
- Caching support
- Session statistics tracking
- Error handling and recovery
"""

import asyncio
import hashlib
import os
import time
from typing import Callable, Dict, List, Optional, Tuple

from samplemind.core.engine.audio_engine import AudioEngine, AudioFeatures, AnalysisLevel


class SessionStats:
    """Track session-level statistics for TUI status bar."""

    def __init__(self) -> None:
        """Initialize session statistics."""
        self.files_analyzed = 0
        self.total_analysis_time = 0.0
        self.session_start_time = time.time()
        self.current_file = ""
        self.current_status = "Ready"

    def increment_analyzed(self, duration: float = 0.0) -> None:
        """Increment analyzed file count and track time."""
        self.files_analyzed += 1
        self.total_analysis_time += duration

    def set_current_file(self, file_path: str) -> None:
        """Set the file currently being analyzed."""
        self.current_file = os.path.basename(file_path)

    def set_status(self, status: str) -> None:
        """Update current status message."""
        self.current_status = status

    def get_uptime(self) -> float:
        """Get session uptime in seconds."""
        return time.time() - self.session_start_time

    def get_avg_time(self) -> float:
        """Get average analysis time per file."""
        if self.files_analyzed == 0:
            return 0.0
        return self.total_analysis_time / self.files_analyzed

    def reset(self) -> None:
        """Reset session statistics."""
        self.files_analyzed = 0
        self.total_analysis_time = 0.0
        self.session_start_time = time.time()
        self.current_file = ""
        self.current_status = "Ready"


class AudioCache:
    """Simple in-memory cache for audio analysis results."""

    def __init__(self, max_size: int = 100) -> None:
        """Initialize cache with maximum size."""
        self.cache: Dict[str, Tuple[AudioFeatures, float]] = {}
        self.max_size = max_size
        self.hit_count = 0
        self.miss_count = 0

    async def get(self, file_path: str) -> Optional[AudioFeatures]:
        """Get cached result for file."""
        file_hash = self._hash_file(file_path)

        if file_hash in self.cache:
            features, cached_time = self.cache[file_hash]

            # Validate file hasn't changed
            if os.path.getmtime(file_path) <= cached_time:
                self.hit_count += 1
                return features

        self.miss_count += 1
        return None

    async def set(self, file_path: str, features: AudioFeatures) -> None:
        """Store result in cache."""
        file_hash = self._hash_file(file_path)

        # Evict oldest if cache full (FIFO)
        if len(self.cache) >= self.max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]

        self.cache[file_hash] = (features, time.time())

    def get_hit_rate(self) -> float:
        """Get cache hit rate (0.0-1.0)."""
        total = self.hit_count + self.miss_count
        if total == 0:
            return 0.0
        return self.hit_count / total

    def clear(self) -> None:
        """Clear cache."""
        self.cache.clear()
        self.hit_count = 0
        self.miss_count = 0

    @staticmethod
    def _hash_file(file_path: str) -> str:
        """Generate SHA-256 hash of file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


class TUIAudioEngine:
    """Bridge between AudioEngine and Textual TUI with async support."""

    def __init__(self) -> None:
        """Initialize TUI AudioEngine bridge."""
        self.engine = AudioEngine()
        self.cache = AudioCache()
        self.session_stats = SessionStats()
        self._analysis_start_time = 0.0

    async def analyze_file(
        self,
        file_path: str,
        progress_callback: Optional[Callable[[float], None]] = None,
        level: AnalysisLevel = AnalysisLevel.STANDARD,
    ) -> AudioFeatures:
        """
        Analyze single audio file with real-time progress tracking.

        Args:
            file_path: Path to audio file
            progress_callback: Optional callback receiving progress 0.0-1.0
            level: Analysis level (BASIC, STANDARD, DETAILED, PROFESSIONAL)

        Returns:
            AudioFeatures object with extracted audio features

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format not supported
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        self.session_stats.set_current_file(file_path)
        self.session_stats.set_status("Checking cache...")

        # Check cache first
        cached_result = await self.cache.get(file_path)
        if cached_result:
            if progress_callback:
                progress_callback(1.0)
            self.session_stats.set_status(f"✓ Cached: {self.session_stats.current_file}")
            return cached_result

        self.session_stats.set_status("Loading audio...")
        self._analysis_start_time = time.time()

        # Run analysis in thread pool to avoid blocking event loop
        try:
            result = await asyncio.to_thread(
                self._analyze_with_progress,
                file_path,
                progress_callback,
                level,
            )

            # Cache result
            await self.cache.set(file_path, result)

            # Update session stats
            analysis_time = time.time() - self._analysis_start_time
            self.session_stats.increment_analyzed(analysis_time)
            self.session_stats.set_status(
                f"✓ Complete: {self.session_stats.current_file} ({analysis_time:.2f}s)"
            )

            return result

        except Exception as e:
            self.session_stats.set_status(f"✗ Error: {str(e)[:40]}...")
            raise

    async def analyze_batch(
        self,
        file_paths: List[str],
        progress_callback: Optional[Callable[[int, int], None]] = None,
        level: AnalysisLevel = AnalysisLevel.STANDARD,
    ) -> List[AudioFeatures]:
        """
        Analyze multiple files with batch progress tracking.

        Args:
            file_paths: List of paths to audio files
            progress_callback: Optional callback receiving (current, total) counts
            level: Analysis level (BASIC, STANDARD, DETAILED, PROFESSIONAL)

        Returns:
            List of AudioFeatures objects

        Raises:
            ValueError: If no valid files provided
        """
        if not file_paths:
            raise ValueError("No files provided for batch analysis")

        results = []
        valid_files = [f for f in file_paths if os.path.exists(f)]

        if not valid_files:
            raise ValueError("No valid audio files found")

        for i, file_path in enumerate(valid_files):
            try:
                # Report progress
                if progress_callback:
                    progress_callback(i, len(valid_files))

                # Analyze file
                result = await self.analyze_file(
                    file_path,
                    lambda p: None,  # Don't report per-file progress in batch
                    level,
                )

                results.append(result)

            except Exception as e:
                # Log error but continue with next file
                print(f"Error analyzing {file_path}: {e}")
                continue

            # Final progress update
            if progress_callback:
                progress_callback(i + 1, len(valid_files))

        return results

    def _analyze_with_progress(
        self,
        file_path: str,
        progress_callback: Optional[Callable[[float], None]],
        level: AnalysisLevel,
    ) -> AudioFeatures:
        """
        Analyze file with estimated progress (internal method for thread pool).

        Args:
            file_path: Path to audio file
            progress_callback: Optional progress callback
            level: Analysis level

        Returns:
            AudioFeatures object
        """
        # Estimate durations based on analysis level
        estimated_durations = {
            AnalysisLevel.BASIC: 0.5,
            AnalysisLevel.STANDARD: 1.5,
            AnalysisLevel.DETAILED: 2.5,
            AnalysisLevel.PROFESSIONAL: 3.5,
        }

        estimated_duration = estimated_durations.get(level, 1.5)
        start_time = time.time()

        # Simulate progress updates every 0.1 seconds
        while True:
            elapsed = time.time() - start_time
            progress = min(elapsed / estimated_duration, 0.95)

            if progress_callback:
                progress_callback(progress)

            if elapsed > estimated_duration * 0.95:
                break

            time.sleep(0.1)

        # Run actual analysis
        result = self.engine.analyze_audio(file_path, level=level)

        # Final progress
        if progress_callback:
            progress_callback(1.0)

        return result

    def format_features_for_display(self, features: AudioFeatures) -> Dict[str, str]:
        """
        Format audio features for beautiful TUI display.

        Args:
            features: AudioFeatures object

        Returns:
            Dictionary of formatted feature strings

        Raises:
            ValueError: If features object is invalid
        """
        if not isinstance(features, AudioFeatures):
            raise ValueError("Invalid AudioFeatures object")

        def format_time(seconds: float) -> str:
            """Format seconds to MM:SS format."""
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}:{secs:02d}"

        return {
            # Audio Properties
            "Duration": f"{features.duration:.2f}s ({format_time(features.duration)})",
            "Sample Rate": f"{features.sample_rate:,} Hz",
            "Channels": f"{features.channels} ({'Stereo' if features.channels == 2 else 'Mono' if features.channels == 1 else f'{features.channels}-channel'})",
            "Bit Depth": f"{features.bit_depth}-bit",
            # Temporal Features
            "Tempo": f"{features.tempo:.1f} BPM",
            "Key": f"{features.key} {features.mode}",
            "Time Signature": str(features.time_signature),
            "Beats": f"{len(features.beats) if features.beats else 0} detected",
            # Spectral Features
            "Spectral Centroid": f"{features.spectral_centroid:.0f} Hz",
            "Spectral Bandwidth": f"{features.spectral_bandwidth:.0f} Hz",
            "Spectral Rolloff": f"{features.spectral_rolloff:.0f} Hz",
            "Zero Crossing Rate": f"{features.zero_crossing_rate:.4f}",
            # Energy Features
            "RMS Energy": f"{features.rms_energy:.4f}",
            # MFCC Summary
            "MFCC Coefficients": f"{len(features.mfccs) if features.mfccs else 0}",
            # Advanced Features
            "Harmonic Content": f"{features.harmonic_content:.4f}" if features.harmonic_content else "N/A",
            "Percussive Content": f"{features.percussive_content:.4f}" if features.percussive_content else "N/A",
        }

    def get_performance_stats(self) -> Dict[str, any]:
        """
        Get performance metrics for display in performance dashboard.

        Returns:
            Dictionary with cache stats, analysis times, etc.
        """
        return {
            "cache_hit_rate": self.cache.get_hit_rate(),
            "cache_hits": self.cache.hit_count,
            "cache_misses": self.cache.miss_count,
            "files_analyzed": self.session_stats.files_analyzed,
            "total_analysis_time": self.session_stats.total_analysis_time,
            "avg_analysis_time": self.session_stats.get_avg_time(),
            "session_uptime": self.session_stats.get_uptime(),
            "current_file": self.session_stats.current_file,
            "current_status": self.session_stats.current_status,
        }

    def reset_session(self) -> None:
        """Reset session statistics and cache."""
        self.session_stats.reset()
        self.cache.clear()


# Module-level singleton instance
_tui_engine: Optional[TUIAudioEngine] = None


def get_tui_engine() -> TUIAudioEngine:
    """
    Get or create singleton TUIAudioEngine instance.

    Returns:
        TUIAudioEngine instance
    """
    global _tui_engine
    if _tui_engine is None:
        _tui_engine = TUIAudioEngine()
    return _tui_engine


def reset_tui_engine() -> None:
    """Reset the singleton instance."""
    global _tui_engine
    if _tui_engine is not None:
        _tui_engine.reset_session()
