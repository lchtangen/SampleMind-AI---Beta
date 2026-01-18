"""
Cache Warmer Service for background preloading.

Async background worker that preloads predicted files into cache
with thermal throttling and priority queue management.
"""

import asyncio
import psutil
import time
from typing import Dict, List, Optional, Callable, Coroutine
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class WarmupPriority(Enum):
    """Cache warmup priority levels"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


@dataclass
class WarmupTask:
    """Single cache warmup task"""
    file_id: str
    file_path: Path
    feature_type: str
    analysis_level: str
    priority: WarmupPriority
    confidence: float
    created_at: float = 0.0

    def __lt__(self, other: "WarmupTask") -> bool:
        """Enable sorting by priority and confidence"""
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.confidence > other.confidence

    def __eq__(self, other: "WarmupTask") -> bool:
        """Check equality"""
        return (
            self.file_id == other.file_id
            and self.feature_type == other.feature_type
            and self.analysis_level == other.analysis_level
        )


@dataclass
class WarmupStats:
    """Statistics for warmup process"""
    total_tasks: int = 0
    completed_tasks: int = 0
    skipped_tasks: int = 0
    failed_tasks: int = 0
    bytes_warmed: int = 0
    last_warmup_time: float = 0.0
    total_time: float = 0.0
    pause_count: int = 0
    resume_count: int = 0


class CacheWarmer:
    """
    Background cache warming service.

    Features:
    - Priority queue management
    - Thermal throttling (CPU/memory aware)
    - Background async operation
    - Progress tracking and statistics
    """

    def __init__(
        self,
        audio_engine=None,
        cache=None,
        markov_predictor=None,
        cpu_threshold: float = 0.60,
        memory_threshold: float = 0.70,
        max_concurrent_tasks: int = 2
    ):
        """
        Initialize cache warmer.

        Args:
            audio_engine: AudioEngine instance for analysis
            cache: Cache instance for storage
            markov_predictor: MarkovPredictor for predictions
            cpu_threshold: CPU usage threshold (0.0-1.0) before pause
            memory_threshold: Memory usage threshold (0.0-1.0) before pause
            max_concurrent_tasks: Maximum concurrent warmup tasks
        """
        self.audio_engine = audio_engine
        self.cache = cache
        self.markov_predictor = markov_predictor

        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.max_concurrent_tasks = max_concurrent_tasks

        # Task management
        self.task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.completed_tasks: set = set()

        # State
        self.is_running = False
        self._pause_event = asyncio.Event()
        self._pause_event.set()  # Start in running state
        self._stop_event = asyncio.Event()

        # Statistics
        self.stats = WarmupStats()

        # Callbacks
        self.on_warmup_start: Optional[Callable] = None
        self.on_warmup_complete: Optional[Callable] = None
        self.on_warmup_failed: Optional[Callable] = None

        logger.info(
            f"Cache warmer initialized "
            f"(cpu_threshold={cpu_threshold}, memory_threshold={memory_threshold})"
        )

    async def start(self) -> None:
        """Start the cache warmer service"""
        if self.is_running:
            logger.warning("Cache warmer already running")
            return

        self.is_running = True
        self._stop_event.clear()
        logger.info("Cache warmer started")

        try:
            await self._run_warmup_loop()
        finally:
            self.is_running = False
            logger.info("Cache warmer stopped")

    async def stop(self) -> None:
        """Stop the cache warmer service"""
        self.is_running = False
        self._stop_event.set()

        # Wait for active tasks to complete
        if self.active_tasks:
            logger.info(f"Waiting for {len(self.active_tasks)} active tasks to complete...")
            await asyncio.gather(*self.active_tasks.values(), return_exceptions=True)

        logger.info("Cache warmer stopped")

    async def pause(self) -> None:
        """Pause warmup operations"""
        self._pause_event.clear()
        logger.info("Cache warmer paused")

    async def resume(self) -> None:
        """Resume warmup operations"""
        self._pause_event.set()
        logger.info("Cache warmer resumed")

    async def add_task(
        self,
        file_id: str,
        file_path: Path,
        feature_type: str,
        analysis_level: str,
        priority: WarmupPriority = WarmupPriority.NORMAL,
        confidence: float = 0.5
    ) -> bool:
        """
        Add a task to the warmup queue.

        Args:
            file_id: File identifier
            file_path: Path to audio file
            feature_type: Feature type to analyze
            analysis_level: Analysis complexity level
            priority: Task priority
            confidence: Prediction confidence (for sorting)

        Returns:
            True if added successfully
        """
        # Skip if already completed
        task_key = f"{file_id}:{feature_type}:{analysis_level}"
        if task_key in self.completed_tasks:
            self.stats.skipped_tasks += 1
            return False

        task = WarmupTask(
            file_id=file_id,
            file_path=file_path,
            feature_type=feature_type,
            analysis_level=analysis_level,
            priority=priority,
            confidence=confidence,
            created_at=time.time()
        )

        try:
            await self.task_queue.put((priority.value, task_key, task))
            self.stats.total_tasks += 1
            return True
        except Exception as e:
            logger.error(f"Failed to add warmup task: {e}")
            return False

    async def _run_warmup_loop(self) -> None:
        """Main warmup loop"""
        while not self._stop_event.is_set():
            # Check thermal conditions
            if not self._should_warmup():
                self.stats.pause_count += 1
                await asyncio.sleep(1)
                continue

            # Ensure pause event is set (not paused)
            await self._pause_event.wait()

            # Check if we have room for more tasks
            if len(self.active_tasks) >= self.max_concurrent_tasks:
                await asyncio.sleep(0.5)
                continue

            # Get next task
            try:
                _, task_key, task = self.task_queue.get_nowait()
            except asyncio.QueueEmpty:
                await asyncio.sleep(0.5)
                continue

            # Create warmup task
            warmup_task = asyncio.create_task(self._warmup_task(task))
            self.active_tasks[task_key] = warmup_task

            # Clean up completed tasks
            self.active_tasks = {
                k: t for k, t in self.active_tasks.items()
                if not t.done()
            }

    async def _warmup_task(self, task: WarmupTask) -> None:
        """Execute a single warmup task"""
        task_key = f"{task.file_id}:{task.feature_type}:{task.analysis_level}"

        try:
            start_time = time.time()

            if self.on_warmup_start:
                await self.on_warmup_start(task)

            # Analyze file (this populates cache)
            if self.audio_engine:
                features = await self.audio_engine.analyze_audio_async(
                    task.file_path,
                    analysis_level=task.analysis_level
                )

                # Store in cache
                if self.cache:
                    cache_key = f"audio:{task.file_id}:{task.feature_type}:{task.analysis_level}"
                    await self.cache.set(cache_key, features, ttl=86400)  # 24 hours

                # Update statistics
                elapsed = time.time() - start_time
                self.stats.completed_tasks += 1
                self.stats.bytes_warmed += task.file_path.stat().st_size
                self.stats.last_warmup_time = elapsed
                self.stats.total_time += elapsed

                logger.debug(f"Warmed {task_key} in {elapsed:.2f}s")

                if self.on_warmup_complete:
                    await self.on_warmup_complete(task)

            # Mark as completed
            self.completed_tasks.add(task_key)

        except Exception as e:
            logger.error(f"Warmup failed for {task_key}: {e}")
            self.stats.failed_tasks += 1

            if self.on_warmup_failed:
                await self.on_warmup_failed(task, e)

    def _should_warmup(self) -> bool:
        """Check if system is healthy enough to warmup"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1) / 100.0
            if cpu_percent > self.cpu_threshold:
                logger.debug(f"CPU too high: {cpu_percent:.1%}")
                return False

            # Memory usage
            memory_percent = psutil.virtual_memory().percent / 100.0
            if memory_percent > self.memory_threshold:
                logger.debug(f"Memory too high: {memory_percent:.1%}")
                return False

            return True

        except Exception as e:
            logger.warning(f"Failed to check system resources: {e}")
            return True  # Continue on error

    def get_stats(self) -> Dict:
        """Get warmup statistics"""
        return {
            "total_tasks": self.stats.total_tasks,
            "completed_tasks": self.stats.completed_tasks,
            "skipped_tasks": self.stats.skipped_tasks,
            "failed_tasks": self.stats.failed_tasks,
            "bytes_warmed_mb": round(self.stats.bytes_warmed / 1024 / 1024, 2),
            "last_warmup_time_ms": round(self.stats.last_warmup_time * 1000, 2),
            "avg_warmup_time_ms": round(
                self.stats.total_time / max(1, self.stats.completed_tasks) * 1000, 2
            ),
            "active_tasks": len(self.active_tasks),
            "queue_size": self.task_queue.qsize(),
            "is_running": self.is_running,
            "pause_count": self.stats.pause_count
        }

    def clear_stats(self) -> None:
        """Clear statistics"""
        self.stats = WarmupStats()

    def clear_queue(self) -> None:
        """Clear the task queue"""
        while not self.task_queue.empty():
            try:
                self.task_queue.get_nowait()
            except asyncio.QueueEmpty:
                break

        logger.info("Cache warmup queue cleared")

    def get_queue_size(self) -> int:
        """Get current queue size"""
        return self.task_queue.qsize()


# Global instance
_warmer_instance: Optional[CacheWarmer] = None


def init_warmer(
    audio_engine=None,
    cache=None,
    markov_predictor=None,
    **kwargs
) -> CacheWarmer:
    """Initialize global cache warmer instance"""
    global _warmer_instance
    _warmer_instance = CacheWarmer(
        audio_engine=audio_engine,
        cache=cache,
        markov_predictor=markov_predictor,
        **kwargs
    )
    return _warmer_instance


def get_warmer() -> CacheWarmer:
    """Get global cache warmer instance"""
    if _warmer_instance is None:
        _warmer_instance = CacheWarmer()
    return _warmer_instance
