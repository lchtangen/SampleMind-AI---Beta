"""
Streaming Audio Processor

Coordinates real-time audio streaming, buffering, and analysis.
"""

import asyncio
import numpy as np
from typing import Optional, Callable, Dict
from loguru import logger

from .audio_buffer import AudioBufferManager
from .realtime_analyzer import RealtimeAudioAnalyzer, RealtimeAnalysisResult


class StreamingAudioProcessor:
    """
    High-level streaming audio processor

    Combines buffer management and real-time analysis for
    complete streaming audio processing pipeline.

    Example:
        >>> processor = StreamingAudioProcessor()
        >>> stream_id = await processor.start_stream("user_123")
        >>> await processor.process_audio(stream_id, audio_data)
        >>> result = processor.get_latest_analysis(stream_id)
    """

    def __init__(
        self,
        chunk_size: int = 1024,
        sample_rate: int = 44100
    ):
        """
        Initialize streaming processor

        Args:
            chunk_size: Processing chunk size
            sample_rate: Default sample rate
        """
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate

        # Component managers
        self.buffer_manager = AudioBufferManager(chunk_size=chunk_size)
        self.analyzers: Dict[str, RealtimeAudioAnalyzer] = {}
        self.latest_results: Dict[str, RealtimeAnalysisResult] = {}

        # Statistics
        self.active_streams: set[str] = set()

        logger.info(f"StreamingAudioProcessor initialized")

    async def start_stream(
        self,
        stream_id: str,
        sample_rate: Optional[int] = None,
        enable_analysis: bool = True
    ) -> str:
        """
        Start new audio stream

        Args:
            stream_id: Unique stream identifier
            sample_rate: Stream sample rate (uses default if None)
            enable_analysis: Enable real-time analysis

        Returns:
            Stream ID
        """
        if stream_id in self.active_streams:
            logger.warning(f"Stream {stream_id} already active")
            return stream_id

        sr = sample_rate or self.sample_rate

        # Create buffer stream
        self.buffer_manager.create_stream(
            stream_id=stream_id,
            sample_rate=sr,
            buffer_size=1024 * 1024  # 1MB
        )

        # Create analyzer
        if enable_analysis:
            self.analyzers[stream_id] = RealtimeAudioAnalyzer(
                sample_rate=sr,
                enable_tempo=True,
                enable_pitch=True,
                enable_onset=True
            )

            # Register analysis callback
            async def analysis_callback(chunk: np.ndarray, sample_rate: int):
                import time
                result = await self.analyzers[stream_id].analyze_chunk(
                    chunk,
                    timestamp=time.time()
                )
                self.latest_results[stream_id] = result

            self.buffer_manager.register_callback(stream_id, analysis_callback)
            self.buffer_manager.start_processing(stream_id)

        self.active_streams.add(stream_id)
        logger.info(f"Started stream: {stream_id} (sr={sr}, analysis={enable_analysis})")

        return stream_id

    async def stop_stream(self, stream_id: str):
        """Stop audio stream"""
        if stream_id not in self.active_streams:
            logger.warning(f"Stream {stream_id} not active")
            return

        # Stop processing
        self.buffer_manager.stop_processing(stream_id)

        # Remove buffer
        self.buffer_manager.remove_stream(stream_id)

        # Remove analyzer
        if stream_id in self.analyzers:
            del self.analyzers[stream_id]

        # Remove results
        if stream_id in self.latest_results:
            del self.latest_results[stream_id]

        self.active_streams.remove(stream_id)
        logger.info(f"Stopped stream: {stream_id}")

    async def process_audio(
        self,
        stream_id: str,
        audio_data: bytes
    ) -> int:
        """
        Process incoming audio data

        Args:
            stream_id: Stream identifier
            audio_data: Raw audio data (bytes)

        Returns:
            Number of samples processed
        """
        if stream_id not in self.active_streams:
            raise ValueError(f"Stream {stream_id} not active")

        # Convert bytes to numpy array (assuming float32)
        audio_array = np.frombuffer(audio_data, dtype=np.float32)

        # Write to buffer (will automatically trigger analysis via callback)
        samples_written = self.buffer_manager.write(stream_id, audio_array)

        return samples_written

    def get_latest_analysis(self, stream_id: str) -> Optional[RealtimeAnalysisResult]:
        """Get latest analysis result for stream"""
        return self.latest_results.get(stream_id)

    def get_stream_stats(self, stream_id: str) -> dict:
        """Get statistics for stream"""
        stats = {}

        # Buffer stats
        buffer_stats = self.buffer_manager.get_stats(stream_id)
        if buffer_stats:
            stats["buffer"] = buffer_stats

        # Analyzer stats
        if stream_id in self.analyzers:
            stats["analyzer"] = self.analyzers[stream_id].get_stats()

        # Latest result
        if stream_id in self.latest_results:
            result = self.latest_results[stream_id]
            stats["latest_analysis"] = {
                "tempo": result.tempo,
                "pitch": result.pitch,
                "energy": result.energy,
                "rms": result.rms,
                "onset_detected": result.onset_detected,
            }

        return stats

    def get_all_streams(self) -> list[str]:
        """Get list of active streams"""
        return list(self.active_streams)

    async def shutdown(self):
        """Shutdown processor and all streams"""
        logger.info("Shutting down StreamingAudioProcessor...")

        # Stop all streams
        for stream_id in list(self.active_streams):
            await self.stop_stream(stream_id)

        # Shutdown buffer manager
        await self.buffer_manager.shutdown()

        logger.info("StreamingAudioProcessor shutdown complete")
