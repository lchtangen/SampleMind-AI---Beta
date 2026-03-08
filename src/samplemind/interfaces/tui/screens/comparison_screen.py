"""Comparison Screen for SampleMind TUI v3.0"""

from __future__ import annotations

from typing import Any

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
    Input,
    Label,
    RichLog,
)


class ComparisonScreen(Screen):
    """Side-by-side comparison of two audio samples."""

    BINDINGS = [
        Binding("escape", "action_back", "Back"),
        Binding("ctrl+r", "run_comparison", "Compare"),
    ]

    DEFAULT_CSS = """
    ComparisonScreen { layout: vertical; }
    #comp_body { height: 1fr; padding: 1 2; }
    .screen-title { color: $primary; text-style: bold; height: 1; margin-bottom: 1; }
    .file-row { height: auto; margin-bottom: 1; }
    .file-row Label { min-width: 10; content-align: center middle; height: 1; }
    .file-row Input { width: 1fr; }
    .file-row Button { min-width: 12; margin-left: 1; }
    #comp_table { height: 1fr; }
    #log_area { height: 4; }
    #btn_row { height: 3; margin-top: 1; }
    #btn_row Button { margin-right: 1; }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="comp_body"):
            yield Label("Compare Two Audio Samples", classes="screen-title")
            with Horizontal(classes="file-row"):
                yield Label("Sample A:")
                yield Input(placeholder="Path to first audio file...", id="path_a")
                yield Button("Browse A", id="btn_browse_a", variant="primary")
            with Horizontal(classes="file-row"):
                yield Label("Sample B:")
                yield Input(placeholder="Path to second audio file...", id="path_b")
                yield Button("Browse B", id="btn_browse_b", variant="primary")
            with Horizontal(id="btn_row"):
                yield Button("Compare", id="btn_compare", variant="success")
                yield Button("Back", id="btn_back", variant="warning")
            yield DataTable(zebra_stripes=True, id="comp_table")
            yield RichLog(highlight=True, id="log_area", wrap=True)
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#comp_table", DataTable)
        table.add_columns("Feature", "Sample A", "Sample B", "Delta")
        self.query_one("#path_a", Input).focus()

    @on(Button.Pressed, "#btn_browse_a")
    def on_browse_a(self, _: Button.Pressed) -> None:
        self._browse("#path_a")

    @on(Button.Pressed, "#btn_browse_b")
    def on_browse_b(self, _: Button.Pressed) -> None:
        self._browse("#path_b")

    @on(Button.Pressed, "#btn_compare")
    def on_compare(self, _: Button.Pressed) -> None:
        self.action_run_comparison()

    @on(Button.Pressed, "#btn_back")
    def on_back(self, _: Button.Pressed) -> None:
        self.app.pop_screen()

    def _browse(self, target_id: str) -> None:
        try:
            from samplemind.utils.file_picker import CrossPlatformFilePicker

            picker = CrossPlatformFilePicker()
            selected = picker.choose_file(
                file_types=["wav", "mp3", "flac", "m4a", "ogg"],
            )
            if selected:
                self.query_one(target_id, Input).value = str(selected)
        except Exception as exc:
            self.notify(f"File picker unavailable: {exc}", severity="warning")

    @work(exclusive=True, thread=True)
    def _compare(self, path_a: str, path_b: str) -> None:
        import asyncio

        try:
            from samplemind.core.engine.audio_engine import AnalysisLevel
            from samplemind.interfaces.tui.audio_engine_bridge import get_tui_engine

            engine = get_tui_engine()
            level = AnalysisLevel.DETAILED
            self.app.call_from_thread(self._log, "[cyan]Analyzing sample A...[/]")
            loop = asyncio.new_event_loop()
            feat_a = loop.run_until_complete(engine.analyze_file(path_a, None, level))
            self.app.call_from_thread(self._log, "[cyan]Analyzing sample B...[/]")
            feat_b = loop.run_until_complete(engine.analyze_file(path_b, None, level))
            loop.close()
            self.app.call_from_thread(self._populate_comparison, feat_a, feat_b)
        except Exception as exc:
            self.app.call_from_thread(self._log, f"[red]Comparison error: {exc}[/]")

    def _populate_comparison(self, feat_a: Any, feat_b: Any) -> None:
        table = self.query_one("#comp_table", DataTable)
        table.clear()
        attrs = [
            "tempo",
            "key",
            "loudness",
            "spectral_centroid",
            "duration",
            "genre",
            "zero_crossing_rate",
            "mood",
        ]
        for attr in attrs:
            val_a = getattr(feat_a, attr, "-") if feat_a else "-"
            val_b = getattr(feat_b, attr, "-") if feat_b else "-"
            if isinstance(val_a, float) and isinstance(val_b, float):
                delta = f"{val_b - val_a:+.2f}"
                val_a_s = f"{val_a:.2f}"
                val_b_s = f"{val_b:.2f}"
            else:
                delta = "" if str(val_a) == str(val_b) else "differs"
                val_a_s = str(val_a)
                val_b_s = str(val_b)
            table.add_row(attr.replace("_", " ").title(), val_a_s, val_b_s, delta)
        self._log("[green]Comparison complete![/]")

    def _log(self, msg: str) -> None:
        try:
            self.query_one("#log_area", RichLog).write(msg)
        except Exception:
            pass

    def action_run_comparison(self) -> None:
        path_a = self.query_one("#path_a", Input).value.strip()
        path_b = self.query_one("#path_b", Input).value.strip()
        if not path_a or not path_b:
            self.notify("Enter both file paths first", severity="warning")
            return
        self._compare(path_a, path_b)

    def action_back(self) -> None:
        self.app.pop_screen()
