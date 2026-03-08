"""
SampleMind AI — Monitoring & Observability Module

Provides system metrics collection, audio processing metrics,
and a Prometheus-compatible monitoring server.
"""

try:
    from .monitor import (
        Monitor,
        SystemMetricsCollector,
        AudioProcessingMetrics,
        MetricType,
        Metric,
    )
    from .server import MonitoringServer

    __all__ = [
        "Monitor",
        "SystemMetricsCollector",
        "AudioProcessingMetrics",
        "MetricType",
        "Metric",
        "MonitoringServer",
    ]
except ImportError:
    # psutil or other optional dep missing (e.g. lightweight installs)
    __all__ = []
