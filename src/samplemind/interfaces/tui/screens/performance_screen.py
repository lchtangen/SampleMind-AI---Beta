"""
Performance Monitoring Dashboard Screen for SampleMind TUI
Real-time CPU, memory, cache, and query performance visualization
"""

import logging
from typing import Optional

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, DataTable, Static
from textual.containers import Container, Vertical, Horizontal
from rich.table import Table
from rich.console import Console
from rich.text import Text

from samplemind.interfaces.tui.monitoring import get_performance_monitor

logger = logging.getLogger(__name__)


class PerformanceSummaryWidget(Static):
    """Widget showing performance summary and health score"""

    def __init__(self):
        super().__init__()
        self.monitor = get_performance_monitor()

    def render(self) -> str:
        """Render performance summary"""
        stats = self.monitor.get_stats()
        health = self.monitor.get_health_score()

        lines = [
            "╔══════════════════════════════════════════════════════╗",
            "║             📊 PERFORMANCE SUMMARY                  ║",
            "╠══════════════════════════════════════════════════════╣",
            f"║ Health Score:  {health['status']:<47} ║",
            f"║ Uptime:        {self.monitor.format_uptime(stats.uptime_seconds):<47} ║",
            "╠══════════════════════════════════════════════════════╣",
            "║ SYSTEM RESOURCES                                   ║",
            f"║   CPU:         {stats.avg_cpu:>6.1f}% (max: {stats.max_cpu:>6.1f}%)         ║",
            f"║   Memory:      {stats.avg_memory:>6.1f}MB (max: {stats.max_memory:>6.1f}MB)      ║",
            f"║   Threads:     {stats.current_threads:<47} ║",
            "╠══════════════════════════════════════════════════════╣",
            "║ CACHE PERFORMANCE                                  ║",
            f"║   Hit Rate:    {stats.cache_hit_rate*100:>6.1f}%    (Total: {stats.total_cache_hits:<8})   ║",
            f"║   Misses:      {stats.total_cache_misses:<47} ║",
            "╠══════════════════════════════════════════════════════╣",
            "║ QUERY PERFORMANCE                                  ║",
            f"║   Avg Time:    {stats.avg_query_time:>6.1f}ms  (max: {stats.max_query_time:>6.1f}ms)   ║",
            "╠══════════════════════════════════════════════════════╣",
            "║ ANALYSIS PERFORMANCE                               ║",
            f"║   Avg Time:    {stats.avg_analysis_time:>6.2f}s   (max: {stats.max_analysis_time:>6.2f}s)    ║",
            "╠══════════════════════════════════════════════════════╣",
            "║ HEALTH INDICATORS:                                 ║",
            f"║   CPU OK:      {self._bool_indicator(health['cpu_ok']):<47} ║",
            f"║   Memory OK:   {self._bool_indicator(health['memory_ok']):<47} ║",
            f"║   Cache OK:    {self._bool_indicator(health['cache_ok']):<47} ║",
            f"║   Queries OK:  {self._bool_indicator(health['queries_ok']):<47} ║",
            "╚══════════════════════════════════════════════════════╝",
        ]
        return "\n".join(lines)

    @staticmethod
    def _bool_indicator(value: bool) -> str:
        """Convert bool to indicator"""
        return "🟢 YES" if value else "🔴 NO"


class CPUTrendWidget(Static):
    """Widget showing CPU trend"""

    def __init__(self):
        super().__init__()
        self.monitor = get_performance_monitor()

    def render(self) -> str:
        """Render CPU trend graph"""
        trend = self.monitor.get_cpu_trend(points=20)

        if not trend:
            return "╔══════════════════════╗\n║ No CPU data yet      ║\n╚══════════════════════╝"

        # Normalize to 0-100
        max_val = max(trend) if trend else 1
        normalized = [int((v / max(max_val, 1)) * 10) for v in trend]

        # Create graph
        graph_chars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        graph = "".join([graph_chars[min(v, 7)] for v in normalized])

        lines = [
            "╔════════════════════════════════════════════╗",
            "║         📈 CPU USAGE TREND                ║",
            "╠════════════════════════════════════════════╣",
            f"║ {graph:<42} ║",
            f"║ Current: {self.monitor.cpu_samples[-1] if self.monitor.cpu_samples else 0:>6.1f}% " f"{"│" * int((self.monitor.cpu_samples[-1] if self.monitor.cpu_samples else 0) / 10):<20} ║",
            "╚════════════════════════════════════════════╝",
        ]
        return "\n".join(lines)


class MemoryTrendWidget(Static):
    """Widget showing memory trend"""

    def __init__(self):
        super().__init__()
        self.monitor = get_performance_monitor()

    def render(self) -> str:
        """Render memory trend graph"""
        trend = self.monitor.get_memory_trend(points=20)

        if not trend:
            return "╔══════════════════════╗\n║ No memory data yet   ║\n╚══════════════════════╝"

        # Normalize to 0-100
        max_val = max(trend) if trend else 1
        normalized = [int((v / max(max_val, 1)) * 10) for v in trend]

        # Create graph
        graph_chars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        graph = "".join([graph_chars[min(v, 7)] for v in normalized])

        current_mem = self.monitor.memory_samples[-1] if self.monitor.memory_samples else 0

        lines = [
            "╔════════════════════════════════════════════╗",
            "║       💾 MEMORY USAGE TREND (MB)          ║",
            "╠════════════════════════════════════════════╣",
            f"║ {graph:<42} ║",
            f"║ Current: {current_mem:>6.1f}MB " f"{'█' * int(current_mem / 30):<20} ║",
            "╚════════════════════════════════════════════╝",
        ]
        return "\n".join(lines)


class CacheStatsWidget(Static):
    """Widget showing cache statistics"""

    def __init__(self):
        super().__init__()
        self.monitor = get_performance_monitor()

    def render(self) -> str:
        """Render cache statistics"""
        stats = self.monitor.get_stats()
        hit_rate_pct = stats.cache_hit_rate * 100

        # Create pie chart representation
        pie_segments = int(hit_rate_pct / 10)
        pie = "🟢" * pie_segments + "🔴" * (10 - pie_segments)

        lines = [
            "╔════════════════════════════════════════════╗",
            "║        💾 CACHE PERFORMANCE METRICS        ║",
            "╠════════════════════════════════════════════╣",
            f"║ Hit Rate: {hit_rate_pct:>5.1f}%                         ║",
            f"║ {pie:<42} ║",
            f"║ Hits:     {stats.total_cache_hits:<37} ║",
            f"║ Misses:   {stats.total_cache_misses:<37} ║",
            "╠════════════════════════════════════════════╣",
            "║ Status:                                    ║",
            f"║ {'✓ Cache working efficiently' if stats.cache_hit_rate > 0.8 else '◐ Cache performance fair' if stats.cache_hit_rate > 0.6 else '✗ Cache hit rate low':<42} ║",
            "╚════════════════════════════════════════════╝",
        ]
        return "\n".join(lines)


class QueryStatsWidget(Static):
    """Widget showing query performance"""

    def __init__(self):
        super().__init__()
        self.monitor = get_performance_monitor()

    def render(self) -> str:
        """Render query statistics"""
        perf = self.monitor.get_query_performance()

        lines = [
            "╔════════════════════════════════════════════╗",
            "║       📝 DATABASE QUERY PERFORMANCE        ║",
            "╠════════════════════════════════════════════╣",
            f"║ Avg Time:  {perf['avg']:>6.1f}ms                        ║",
            f"║ Max Time:  {perf['max']:>6.1f}ms                        ║",
            f"║ Min Time:  {perf['min']:>6.1f}ms                        ║",
            f"║ Queries:   {perf['count']:<37} ║",
            "╠════════════════════════════════════════════╣",
            "║ Performance Status:                        ║",
            f"║ {'✓ Excellent' if perf['avg'] < 50 else '◐ Acceptable' if perf['avg'] < 100 else '✗ Slow':<42} ║",
            "╚════════════════════════════════════════════╝",
        ]
        return "\n".join(lines)


class AnalysisStatsWidget(Static):
    """Widget showing analysis performance"""

    def __init__(self):
        super().__init__()
        self.monitor = get_performance_monitor()

    def render(self) -> str:
        """Render analysis statistics"""
        perf = self.monitor.get_analysis_performance()

        lines = [
            "╔════════════════════════════════════════════╗",
            "║       🎵 AUDIO ANALYSIS PERFORMANCE        ║",
            "╠════════════════════════════════════════════╣",
            f"║ Avg Time:  {perf['avg']:>6.2f}s                         ║",
            f"║ Max Time:  {perf['max']:>6.2f}s                         ║",
            f"║ Min Time:  {perf['min']:>6.2f}s                         ║",
            f"║ Analyses:  {perf['count']:<37} ║",
            "╠════════════════════════════════════════════╣",
            "║ Performance Status:                        ║",
            f"║ {'✓ Fast' if perf['avg'] < 2 else '◐ Moderate' if perf['avg'] < 5 else '✗ Slow':<42} ║",
            "╚════════════════════════════════════════════╝",
        ]
        return "\n".join(lines)


class PerformanceScreen(Screen):
    """Performance monitoring dashboard screen"""

    BINDINGS = [
        ("r", "reset_monitor", "Reset"),
        ("e", "export_stats", "Export"),
        ("q", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the screen layout"""
        yield Header(show_clock=True)

        with Container(id="performance-main"):
            with Vertical():
                yield PerformanceSummaryWidget(id="perf-summary")

                with Horizontal():
                    yield CPUTrendWidget(id="cpu-trend")
                    yield MemoryTrendWidget(id="mem-trend")

                with Horizontal():
                    yield CacheStatsWidget(id="cache-stats")
                    yield QueryStatsWidget(id="query-stats")

                with Horizontal():
                    yield AnalysisStatsWidget(id="analysis-stats")

        yield Footer()

    def on_mount(self) -> None:
        """Set up auto-refresh"""
        self.set_interval(1.0, self._refresh_widgets)

    def _refresh_widgets(self) -> None:
        """Refresh all widgets"""
        monitor = get_performance_monitor()
        monitor.sample_system_metrics()

        # Update all widgets
        for widget_id in [
            "perf-summary",
            "cpu-trend",
            "mem-trend",
            "cache-stats",
            "query-stats",
            "analysis-stats",
        ]:
            widget = self.query_one(f"#{widget_id}", Static)
            widget.update(widget.render())

    def action_reset_monitor(self) -> None:
        """Reset monitoring data"""
        monitor = get_performance_monitor()
        monitor.reset()
        self._refresh_widgets()

    def action_export_stats(self) -> None:
        """Export statistics to file"""
        monitor = get_performance_monitor()
        stats = monitor.get_stats()
        health = monitor.get_health_score()

        # Create export string
        export_lines = [
            "=== SampleMind Performance Report ===",
            f"Generated: {monitor.metrics[-1].timestamp if monitor.metrics else 'N/A'}",
            "",
            f"Health Score: {health['score']:.1f}/100 - {health['status']}",
            f"Uptime: {monitor.format_uptime(stats.uptime_seconds)}",
            "",
            "System Resources:",
            f"  CPU Avg: {stats.avg_cpu:.1f}%",
            f"  CPU Max: {stats.max_cpu:.1f}%",
            f"  Memory Avg: {stats.avg_memory:.1f}MB",
            f"  Memory Max: {stats.max_memory:.1f}MB",
            f"  Thread Count: {stats.current_threads}",
            "",
            "Cache Performance:",
            f"  Hit Rate: {stats.cache_hit_rate*100:.1f}%",
            f"  Total Hits: {stats.total_cache_hits}",
            f"  Total Misses: {stats.total_cache_misses}",
            "",
            "Query Performance:",
            f"  Avg Time: {stats.avg_query_time:.1f}ms",
            f"  Max Time: {stats.max_query_time:.1f}ms",
            "",
            "Analysis Performance:",
            f"  Avg Time: {stats.avg_analysis_time:.2f}s",
            f"  Max Time: {stats.max_analysis_time:.2f}s",
        ]

        report = "\n".join(export_lines)
        logger.info(f"Performance report:\n{report}")

    def action_back(self) -> None:
        """Go back to previous screen"""
        self.app.pop_screen()
