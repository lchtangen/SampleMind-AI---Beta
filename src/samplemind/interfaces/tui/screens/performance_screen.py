"""Performance Screen for SampleMind TUI v3.0"""

from __future__ import annotations

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Label,
    Sparkline,
)


class PerformanceScreen(Screen):
    """Real-time system performance metrics and diagnostics."""

    BINDINGS = [
        Binding("escape", "action_back", "Back"),
        Binding("r", "refresh_metrics", "Refresh"),
    ]

    DEFAULT_CSS = """
    PerformanceScreen { layout: vertical; }
    #perf_body { height: 1fr; padding: 1 2; }
    .screen-title { color: $primary; text-style: bold; height: 1; margin-bottom: 1; }
    #cpu_chart { height: 3; margin-bottom: 1; }
    #mem_chart { height: 3; margin-bottom: 1; }
    #metrics_table { height: 1fr; }
    #btn_row { height: 3; margin-top: 1; }
    #btn_row Button { margin-right: 1; }
    .chart-label { color: $accent; height: 1; }
    """

    def __init__(self) -> None:
        super().__init__()
        self._cpu_history: list[float] = [0.0] * 30
        self._mem_history: list[float] = [0.0] * 30

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="perf_body"):
            yield Label("System Performance", classes="screen-title")
            yield Label("CPU Usage", classes="chart-label")
            yield Sparkline(data=self._cpu_history, id="cpu_chart")
            yield Label("Memory Usage", classes="chart-label")
            yield Sparkline(data=self._mem_history, id="mem_chart")
            yield Label("Metrics", classes="chart-label")
            yield DataTable(zebra_stripes=True, id="metrics_table")
            with Horizontal(id="btn_row"):
                yield Button("Refresh", id="btn_refresh", variant="primary")
                yield Button("Start Monitor", id="btn_monitor", variant="success")
                yield Button("Stop", id="btn_stop", variant="warning")
                yield Button("Back", id="btn_back", variant="default")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#metrics_table", DataTable)
        table.add_columns("Metric", "Value", "Target", "Status")
        self._refresh_metrics()

    @on(Button.Pressed, "#btn_refresh")
    def on_refresh_btn(self, _: Button.Pressed) -> None:
        self.action_refresh_metrics()

    @on(Button.Pressed, "#btn_monitor")
    def on_monitor_btn(self, _: Button.Pressed) -> None:
        self._start_monitor()

    @on(Button.Pressed, "#btn_stop")
    def on_stop_btn(self, _: Button.Pressed) -> None:
        self._monitoring = False
        self.notify("Monitoring stopped")

    @on(Button.Pressed, "#btn_back")
    def on_back(self, _: Button.Pressed) -> None:
        self.app.pop_screen()

    @work(thread=True)
    def _fetch_metrics(self) -> None:
        try:
            import psutil

            cpu = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            self._cpu_history.append(cpu / 100.0)
            self._cpu_history = self._cpu_history[-30:]
            self._mem_history.append(mem.percent / 100.0)
            self._mem_history = self._mem_history[-30:]
            metrics = [
                (
                    "CPU Usage",
                    f"{cpu:.1f}%",
                    "<80%",
                    "[green]OK[/]" if cpu < 80 else "[red]HIGH[/]",
                ),
                (
                    "Memory Used",
                    f"{mem.percent:.1f}%",
                    "<85%",
                    "[green]OK[/]" if mem.percent < 85 else "[red]HIGH[/]",
                ),
                ("Memory Total", f"{mem.total / 1024**3:.1f} GB", "-", "-"),
                (
                    "Disk Used",
                    f"{disk.percent:.1f}%",
                    "<90%",
                    "[green]OK[/]" if disk.percent < 90 else "[yellow]WARN[/]",
                ),
                ("Disk Free", f"{disk.free / 1024**3:.1f} GB", "-", "-"),
            ]
            self.app.call_from_thread(self._update_table, metrics)
            self.app.call_from_thread(self._update_sparklines)
        except ImportError:
            metrics = [("psutil", "Not installed", "-", "[yellow]UNAVAILABLE[/]")]
            self.app.call_from_thread(self._update_table, metrics)
        except Exception as exc:
            self.app.call_from_thread(
                lambda: self.notify(f"Metrics error: {exc}", severity="warning")
            )

    def _update_table(self, metrics: list[tuple[str, str, str, str]]) -> None:
        table = self.query_one("#metrics_table", DataTable)
        table.clear()
        for row in metrics:
            table.add_row(*row)

    def _update_sparklines(self) -> None:
        try:
            self.query_one("#cpu_chart", Sparkline).data = list(self._cpu_history)
            self.query_one("#mem_chart", Sparkline).data = list(self._mem_history)
        except Exception:
            pass

    def _start_monitor(self) -> None:
        self._monitoring = True
        self._monitor_loop()

    @work(exclusive=True, thread=True)
    def _monitor_loop(self) -> None:
        import time

        self._monitoring = True
        while getattr(self, "_monitoring", False):
            self.app.call_from_thread(self.action_refresh_metrics)
            time.sleep(2.0)

    def action_refresh_metrics(self) -> None:
        self._fetch_metrics()

    def action_back(self) -> None:
        self._monitoring = False
        self.app.pop_screen()

    def _refresh_metrics(self) -> None:
        self._fetch_metrics()
