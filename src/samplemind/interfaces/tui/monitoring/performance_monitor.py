"""
Performance Monitoring System for SampleMind TUI
Real-time monitoring of CPU, memory, cache, and query performance
"""

import logging
import time
import psutil
from typing import Optional, Dict, Any, List, Deque
from dataclasses import dataclass, field
from collections import deque
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Performance metric types"""
    CPU = "cpu"
    MEMORY = "memory"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    QUERY_TIME = "query_time"
    ANALYSIS_TIME = "analysis_time"
    THREAD_COUNT = "thread_count"
    IO_READ = "io_read"
    IO_WRITE = "io_write"


@dataclass
class PerformanceMetric:
    """Single performance metric"""
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.now)
    value: float = 0.0
    label: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.metric_type.value}: {self.value:.2f} @ {self.timestamp.strftime('%H:%M:%S')}"


@dataclass
class PerformanceStats:
    """Aggregated performance statistics"""
    avg_cpu: float = 0.0
    max_cpu: float = 0.0
    avg_memory: float = 0.0
    max_memory: float = 0.0
    cache_hit_rate: float = 0.0  # 0-1
    total_cache_hits: int = 0
    total_cache_misses: int = 0
    avg_query_time: float = 0.0  # milliseconds
    max_query_time: float = 0.0
    avg_analysis_time: float = 0.0  # seconds
    max_analysis_time: float = 0.0
    current_threads: int = 0
    uptime_seconds: float = 0.0


class PerformanceMonitor:
    """Real-time performance monitoring system"""

    def __init__(self, max_history: int = 300):  # 5 minutes at 1 sample/sec
        """
        Initialize performance monitor

        Args:
            max_history: Maximum history size for deques
        """
        self.max_history = max_history
        self.metrics: Deque[PerformanceMetric] = deque(maxlen=max_history)
        self.cpu_samples: Deque[float] = deque(maxlen=60)  # 1 minute of CPU samples
        self.memory_samples: Deque[float] = deque(maxlen=60)
        self.cache_hits: Deque[PerformanceMetric] = deque(maxlen=300)
        self.cache_misses: Deque[PerformanceMetric] = deque(maxlen=300)
        self.query_times: Deque[float] = deque(maxlen=100)
        self.analysis_times: Deque[float] = deque(maxlen=100)

        self.start_time = time.time()
        self.process = psutil.Process()
        self.last_io_counters = self.process.io_counters()
        self.io_read_bytes = 0
        self.io_write_bytes = 0

    def record_metric(
        self,
        metric_type: MetricType,
        value: float,
        label: Optional[str] = None,
    ) -> None:
        """
        Record a performance metric

        Args:
            metric_type: Type of metric
            value: Metric value
            label: Optional label
        """
        metric = PerformanceMetric(metric_type=metric_type, value=value, label=label)
        self.metrics.append(metric)

        # Route to appropriate collection
        if metric_type == MetricType.CPU:
            self.cpu_samples.append(value)
        elif metric_type == MetricType.MEMORY:
            self.memory_samples.append(value)
        elif metric_type == MetricType.CACHE_HIT:
            self.cache_hits.append(metric)
        elif metric_type == MetricType.CACHE_MISS:
            self.cache_misses.append(metric)
        elif metric_type == MetricType.QUERY_TIME:
            self.query_times.append(value)
        elif metric_type == MetricType.ANALYSIS_TIME:
            self.analysis_times.append(value)

        logger.debug(f"Recorded {metric}")

    def record_cache_hit(self) -> None:
        """Record cache hit"""
        self.record_metric(MetricType.CACHE_HIT, 1.0)

    def record_cache_miss(self) -> None:
        """Record cache miss"""
        self.record_metric(MetricType.CACHE_MISS, 1.0)

    def record_query_time(self, duration_ms: float) -> None:
        """
        Record database query time

        Args:
            duration_ms: Query duration in milliseconds
        """
        self.record_metric(MetricType.QUERY_TIME, duration_ms)

    def record_analysis_time(self, duration_seconds: float) -> None:
        """
        Record analysis duration

        Args:
            duration_seconds: Analysis duration in seconds
        """
        self.record_metric(MetricType.ANALYSIS_TIME, duration_seconds)

    def sample_system_metrics(self) -> None:
        """Sample current system metrics"""
        try:
            cpu_percent = self.process.cpu_percent(interval=0.1)
            self.record_metric(MetricType.CPU, cpu_percent)

            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            self.record_metric(MetricType.MEMORY, memory_mb)

            thread_count = self.process.num_threads()
            self.record_metric(MetricType.THREAD_COUNT, float(thread_count))

            # Track I/O changes
            current_io = self.process.io_counters()
            io_read_delta = current_io.read_bytes - self.last_io_counters.read_bytes
            io_write_delta = current_io.write_bytes - self.last_io_counters.write_bytes
            self.last_io_counters = current_io

            if io_read_delta > 0:
                self.io_read_bytes += io_read_delta
            if io_write_delta > 0:
                self.io_write_bytes += io_write_delta

        except Exception as e:
            logger.error(f"Error sampling system metrics: {e}")

    def get_stats(self) -> PerformanceStats:
        """
        Get aggregated performance statistics

        Args:
            None

        Returns:
            PerformanceStats object
        """
        stats = PerformanceStats()

        # CPU stats
        if self.cpu_samples:
            stats.avg_cpu = sum(self.cpu_samples) / len(self.cpu_samples)
            stats.max_cpu = max(self.cpu_samples)

        # Memory stats
        if self.memory_samples:
            stats.avg_memory = sum(self.memory_samples) / len(self.memory_samples)
            stats.max_memory = max(self.memory_samples)

        # Cache stats
        total_cache = len(self.cache_hits) + len(self.cache_misses)
        if total_cache > 0:
            stats.total_cache_hits = len(self.cache_hits)
            stats.total_cache_misses = len(self.cache_misses)
            stats.cache_hit_rate = len(self.cache_hits) / total_cache

        # Query time stats
        if self.query_times:
            stats.avg_query_time = sum(self.query_times) / len(self.query_times)
            stats.max_query_time = max(self.query_times)

        # Analysis time stats
        if self.analysis_times:
            stats.avg_analysis_time = sum(self.analysis_times) / len(self.analysis_times)
            stats.max_analysis_time = max(self.analysis_times)

        # Thread count
        try:
            stats.current_threads = self.process.num_threads()
        except Exception:
            pass

        # Uptime
        stats.uptime_seconds = time.time() - self.start_time

        return stats

    def get_cpu_trend(self, points: int = 10) -> List[float]:
        """
        Get CPU trend as list

        Args:
            points: Number of data points to return

        Returns:
            List of CPU percentages
        """
        cpu_list = list(self.cpu_samples)
        if len(cpu_list) > points:
            # Sample evenly across history
            step = len(cpu_list) // points
            return [cpu_list[i * step] for i in range(points)]
        return cpu_list

    def get_memory_trend(self, points: int = 10) -> List[float]:
        """
        Get memory trend as list

        Args:
            points: Number of data points to return

        Returns:
            List of memory values in MB
        """
        mem_list = list(self.memory_samples)
        if len(mem_list) > points:
            step = len(mem_list) // points
            return [mem_list[i * step] for i in range(points)]
        return mem_list

    def get_query_performance(self) -> Dict[str, float]:
        """
        Get query performance metrics

        Returns:
            Dictionary with query stats
        """
        if not self.query_times:
            return {"avg": 0.0, "max": 0.0, "min": 0.0, "count": 0}

        query_list = list(self.query_times)
        return {
            "avg": sum(query_list) / len(query_list),
            "max": max(query_list),
            "min": min(query_list),
            "count": len(query_list),
        }

    def get_analysis_performance(self) -> Dict[str, float]:
        """
        Get analysis performance metrics

        Returns:
            Dictionary with analysis stats
        """
        if not self.analysis_times:
            return {"avg": 0.0, "max": 0.0, "min": 0.0, "count": 0}

        analysis_list = list(self.analysis_times)
        return {
            "avg": sum(analysis_list) / len(analysis_list),
            "max": max(analysis_list),
            "min": min(analysis_list),
            "count": len(analysis_list),
        }

    def format_uptime(self, seconds: float) -> str:
        """
        Format uptime nicely

        Args:
            seconds: Uptime in seconds

        Returns:
            Formatted uptime string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def get_health_score(self) -> Dict[str, Any]:
        """
        Calculate overall health score (0-100)

        Returns:
            Dictionary with health metrics
        """
        stats = self.get_stats()
        score = 100

        # CPU penalty (if >50%, -1 per percent)
        if stats.avg_cpu > 50:
            score -= (stats.avg_cpu - 50) / 2

        # Memory penalty (if >300MB, -0.1 per MB)
        if stats.avg_memory > 300:
            score -= (stats.avg_memory - 300) / 10

        # Cache hit penalty (if <70%, -0.5 per percent below)
        if stats.cache_hit_rate < 0.7:
            score -= (0.7 - stats.cache_hit_rate) * 100 * 0.5

        # Query time penalty (if >100ms avg, -1 per ms)
        if stats.avg_query_time > 100:
            score -= (stats.avg_query_time - 100) / 10

        score = max(0, min(100, score))

        # Determine health status
        if score >= 85:
            status = "🟢 EXCELLENT"
        elif score >= 70:
            status = "🟡 GOOD"
        elif score >= 50:
            status = "🟠 FAIR"
        else:
            status = "🔴 POOR"

        return {
            "score": score,
            "status": status,
            "cpu_ok": stats.avg_cpu < 50,
            "memory_ok": stats.avg_memory < 300,
            "cache_ok": stats.cache_hit_rate > 0.7,
            "queries_ok": stats.avg_query_time < 100,
        }

    def reset(self) -> None:
        """Reset all monitoring data"""
        self.metrics.clear()
        self.cpu_samples.clear()
        self.memory_samples.clear()
        self.cache_hits.clear()
        self.cache_misses.clear()
        self.query_times.clear()
        self.analysis_times.clear()
        self.start_time = time.time()
        logger.info("Performance monitor reset")


# Global singleton instance
_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get or create performance monitor singleton"""
    global _monitor
    if _monitor is None:
        _monitor = PerformanceMonitor()
    return _monitor
