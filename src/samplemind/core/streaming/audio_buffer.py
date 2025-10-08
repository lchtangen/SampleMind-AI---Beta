"""
Audio Buffer Management for Real-time Streaming

Efficiently manages audio data buffers for real-time processing with:
- Ring buffer for continuous audio streaming
- Automatic buffer management
- Thread-safe operations
- Chunk-based processing
"""

import asyncio
import numpy as np
from collections import deque
from typing import Optional, Callable, List
from dataclasses import dataclass
from threading import Lock
from loguru import logger


@dataclass
class AudioChunk:
    """Single audio data chunk"""
    data: np.ndarray
    timestamp: float
    sample_rate: int
    channels: int


class AudioBuffer:
    """
    Circular audio buffer for real-time streaming

    Manages a fixed-size buffer with automatic overflow handling.
    Supports both blocking and non-blocking read/write operations.

    Example:
        >>> buffer = AudioBuffer(max_size=1024 * 1024)  # 1MB buffer
        >>> buffer.write(audio_chunk)
        >>> chunk = buffer.read(chunk_size=1024)
    """

    def __init__(
        self,
        max_size: int = 1024 * 1024,  # 1MB default
        sample_rate: int = 44100,
        channels: int = 1
    ):
        """
        Initialize audio buffer

        Args:
            max_size: Maximum buffer size in samples
            sample_rate: Audio sample rate
            channels: Number of audio channels
        """
        self.max_size = max_size
        self.sample_rate = sample_rate
        self.channels = channels

        # Ring buffer storage
        self.buffer = np.zeros(max_size, dtype=np.float32)
        self.write_pos = 0
        self.read_pos = 0
        self.available_samples = 0

        # Thread safety
        self.lock = Lock()

        # Statistics
        self.total_written = 0
        self.total_read = 0
        self.overflow_count = 0

        logger.info(f"AudioBuffer initialized: {max_size} samples, {sample_rate}Hz, {channels}ch")

    def write(self, data: np.ndarray) -> int:
        """
        Write audio data to buffer

        Args:
            data: Audio data to write

        Returns:
            Number of samples actually written
        """
        with self.lock:
            samples_to_write = len(data)

            # Check for overflow
            if self.available_samples + samples_to_write > self.max_size:
                overflow = (self.available_samples + samples_to_write) - self.max_size
                self.overflow_count += 1
                logger.warning(f"Buffer overflow: {overflow} samples dropped")
                # Drop oldest data
                self.read_pos = (self.read_pos + overflow) % self.max_size
                self.available_samples = self.max_size - samples_to_write

            # Write data in chunks (handle wraparound)
            remaining = samples_to_write
            src_pos = 0

            while remaining > 0:
                # How much we can write before wrapping
                space_to_end = self.max_size - self.write_pos
                chunk_size = min(remaining, space_to_end)

                # Write chunk
                self.buffer[self.write_pos:self.write_pos + chunk_size] = \
                    data[src_pos:src_pos + chunk_size]

                # Update positions
                self.write_pos = (self.write_pos + chunk_size) % self.max_size
                src_pos += chunk_size
                remaining -= chunk_size

            self.available_samples += samples_to_write
            self.total_written += samples_to_write

            return samples_to_write

    def read(self, num_samples: int, remove: bool = True) -> Optional[np.ndarray]:
        """
        Read audio data from buffer

        Args:
            num_samples: Number of samples to read
            remove: If True, remove read data from buffer

        Returns:
            Audio data or None if not enough samples available
        """
        with self.lock:
            if self.available_samples < num_samples:
                return None

            # Read data in chunks (handle wraparound)
            result = np.zeros(num_samples, dtype=np.float32)
            remaining = num_samples
            dest_pos = 0
            temp_read_pos = self.read_pos

            while remaining > 0:
                # How much we can read before wrapping
                data_to_end = self.max_size - temp_read_pos
                chunk_size = min(remaining, data_to_end)

                # Read chunk
                result[dest_pos:dest_pos + chunk_size] = \
                    self.buffer[temp_read_pos:temp_read_pos + chunk_size]

                # Update positions
                temp_read_pos = (temp_read_pos + chunk_size) % self.max_size
                dest_pos += chunk_size
                remaining -= chunk_size

            if remove:
                self.read_pos = temp_read_pos
                self.available_samples -= num_samples
                self.total_read += num_samples

            return result

    def peek(self, num_samples: int) -> Optional[np.ndarray]:
        """Read without removing data from buffer"""
        return self.read(num_samples, remove=False)

    def clear(self):
        """Clear all data from buffer"""
        with self.lock:
            self.buffer.fill(0)
            self.write_pos = 0
            self.read_pos = 0
            self.available_samples = 0

    def get_stats(self) -> dict:
        """Get buffer statistics"""
        with self.lock:
            return {
                "max_size": self.max_size,
                "available_samples": self.available_samples,
                "utilization": self.available_samples / self.max_size,
                "total_written": self.total_written,
                "total_read": self.total_read,
                "overflow_count": self.overflow_count,
                "sample_rate": self.sample_rate,
                "channels": self.channels,
            }


class AudioBufferManager:
    """
    Manages multiple audio buffers with automatic processing

    Handles multiple simultaneous audio streams, automatically
    processes chunks, and invokes callbacks.

    Example:
        >>> manager = AudioBufferManager()
        >>> stream_id = manager.create_stream(sample_rate=44100)
        >>> manager.register_callback(stream_id, process_audio)
        >>> manager.write(stream_id, audio_data)
    """

    def __init__(self, chunk_size: int = 1024):
        """
        Initialize buffer manager

        Args:
            chunk_size: Size of processing chunks
        """
        self.chunk_size = chunk_size
        self.buffers: dict[str, AudioBuffer] = {}
        self.callbacks: dict[str, List[Callable]] = {}
        self.processing_tasks: dict[str, asyncio.Task] = {}
        self.active = True

        logger.info(f"AudioBufferManager initialized (chunk_size={chunk_size})")

    def create_stream(
        self,
        stream_id: str,
        sample_rate: int = 44100,
        channels: int = 1,
        buffer_size: int = 1024 * 1024
    ) -> str:
        """
        Create new audio stream

        Args:
            stream_id: Unique stream identifier
            sample_rate: Audio sample rate
            channels: Number of channels
            buffer_size: Buffer size in samples

        Returns:
            Stream ID
        """
        if stream_id in self.buffers:
            logger.warning(f"Stream {stream_id} already exists")
            return stream_id

        self.buffers[stream_id] = AudioBuffer(
            max_size=buffer_size,
            sample_rate=sample_rate,
            channels=channels
        )
        self.callbacks[stream_id] = []

        logger.info(f"Created stream: {stream_id} ({sample_rate}Hz, {channels}ch)")
        return stream_id

    def remove_stream(self, stream_id: str):
        """Remove audio stream"""
        if stream_id in self.buffers:
            # Stop processing task
            if stream_id in self.processing_tasks:
                self.processing_tasks[stream_id].cancel()
                del self.processing_tasks[stream_id]

            del self.buffers[stream_id]
            del self.callbacks[stream_id]
            logger.info(f"Removed stream: {stream_id}")

    def write(self, stream_id: str, data: np.ndarray) -> int:
        """Write data to stream buffer"""
        if stream_id not in self.buffers:
            raise ValueError(f"Stream {stream_id} not found")

        return self.buffers[stream_id].write(data)

    def read(self, stream_id: str, num_samples: int) -> Optional[np.ndarray]:
        """Read data from stream buffer"""
        if stream_id not in self.buffers:
            raise ValueError(f"Stream {stream_id} not found")

        return self.buffers[stream_id].read(num_samples)

    def register_callback(self, stream_id: str, callback: Callable):
        """
        Register callback for audio chunk processing

        Callback signature: async def callback(chunk: np.ndarray, sample_rate: int)
        """
        if stream_id not in self.callbacks:
            raise ValueError(f"Stream {stream_id} not found")

        self.callbacks[stream_id].append(callback)
        logger.info(f"Registered callback for stream {stream_id}")

    async def process_stream(self, stream_id: str):
        """
        Continuously process audio chunks from stream

        Reads chunks from buffer and invokes callbacks
        """
        buffer = self.buffers.get(stream_id)
        if not buffer:
            return

        logger.info(f"Started processing stream: {stream_id}")

        try:
            while self.active:
                # Read chunk if available
                chunk = buffer.read(self.chunk_size)

                if chunk is not None:
                    # Invoke all callbacks
                    for callback in self.callbacks.get(stream_id, []):
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(chunk, buffer.sample_rate)
                            else:
                                callback(chunk, buffer.sample_rate)
                        except Exception as e:
                            logger.error(f"Callback error: {e}")

                else:
                    # No data available, wait
                    await asyncio.sleep(0.01)

        except asyncio.CancelledError:
            logger.info(f"Stream processing cancelled: {stream_id}")
        except Exception as e:
            logger.error(f"Stream processing error: {e}")

    def start_processing(self, stream_id: str):
        """Start automatic processing for stream"""
        if stream_id not in self.buffers:
            raise ValueError(f"Stream {stream_id} not found")

        if stream_id in self.processing_tasks:
            logger.warning(f"Processing already running for {stream_id}")
            return

        task = asyncio.create_task(self.process_stream(stream_id))
        self.processing_tasks[stream_id] = task
        logger.info(f"Started processing task for {stream_id}")

    def stop_processing(self, stream_id: str):
        """Stop automatic processing for stream"""
        if stream_id in self.processing_tasks:
            self.processing_tasks[stream_id].cancel()
            del self.processing_tasks[stream_id]
            logger.info(f"Stopped processing task for {stream_id}")

    async def shutdown(self):
        """Shutdown all streams and processing"""
        self.active = False

        # Cancel all processing tasks
        for task in self.processing_tasks.values():
            task.cancel()

        # Wait for tasks to finish
        if self.processing_tasks:
            await asyncio.gather(*self.processing_tasks.values(), return_exceptions=True)

        self.processing_tasks.clear()
        self.buffers.clear()
        self.callbacks.clear()

        logger.info("AudioBufferManager shutdown complete")

    def get_stats(self, stream_id: Optional[str] = None) -> dict:
        """Get statistics for stream(s)"""
        if stream_id:
            if stream_id in self.buffers:
                return self.buffers[stream_id].get_stats()
            return {}

        # All streams
        return {
            sid: buffer.get_stats()
            for sid, buffer in self.buffers.items()
        }
