"""Analyze Screen for SampleMind TUI v3.0"""

from __future__ import annotations

import os
from pathlib import Path

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    Collapsible,
    Footer,
    Header,
    Input,
    Label,
    ProgressBar,
    RadioButton,
    RadioSet,
    RichLog,
)

from ..widgets.dialogs import ErrorDialog

_VALID_EXT = {".wav", ".mp3", ".flac", ".m4a", ".ogg", ".aiff", ".opus"}
_LEVELS: list[tuple[str, str]] = [
    ("basic", "BASIC - BPM+Key only (~0.5s)"),
    ("standard", "STANDARD - +MFCC+Chroma (~1.5s)"),
    ("detailed", "DETAILED - +Harmonic/Percussive (~2.5s)"),
    ("professional", "PROFESSIONAL - +AI analysis (~4s)"),
]


class AnalyzeScreen(Screen):
    """Single-file audio analysis with RichLog streaming and @work background."""

    BINDINGS = [
        Binding("escape", "action_back", "Back"),
        Binding("ctrl+r", "start_analysis", "Analyze"),
    ]

    DEFAULT_CSS = """
    AnalyzeScreen { layout: vertical; }
    #analyze_body { height: 1fr; padding: 1 2; }
    .screen-title { color: $primary; text-style: bold; height: 1; margin-bottom: 1; }
    #file_row { height: 3; margin-bottom: 1; }
    #file_row Input { width: 1fr; margin-bottom: 0; }
    #file_row Button { min-width: 12; margin-left: 1; }
    #btn_row { height: auto; margin: 1 0; }
    #btn_row Button { margin-right: 1; }
    #progress_bar { margin-bottom: 1; }
    #log_out { height: 1fr; }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="analyze_body"):
            yield Label("Analyze Single Audio File", classes="screen-title")
            with Horizontal(id="file_row"):
                yield Input(
                    placeholder="Audio file path (WAV, MP3, FLAC, M4A, OGG, AIFF)...",
                    id="file_input",
                )
                yield Button("Browse", id="btn_browse", variant="primary")
            with Collapsible(title="Analysis Options", collapsed=True):
                with RadioSet(id="level_set"):
                    for value, label in _LEVELS:
                        yield RadioButton(label, id=f"lev_{value}")
            with Horizontal(id="btn_row"):
                yield Button("Analyze", id="btn_analyze", variant="success")
                yield Button("Back", id="btn_back", variant="warning")
            yield ProgressBar(total=100, id="progress_bar", show_eta=False)
            yield RichLog(highlight=True, markup=True, id="log_out", wrap=True)
        yield Footer()

    def on_mount(self) -> None:
        self._level = "STANDARD"
        try:
            self.query_one("#lev_standard", RadioButton).value = True
        except Exception:
            pass
        self.query_one("#file_input", Input).focus()

    @on(RadioSet.Changed, "#level_set")
    def on_level_changed(self, event: RadioSet.Changed) -> None:
        if event.pressed and event.pressed.id:
            self._level = event.pressed.id.replace("lev_", "").upper()

    @on(Button.Pressed, "#btn_browse")
    def on_browse(self, _: Button.Pressed) -> None:
        try:
            from samplemind.utils.file_picker import CrossPlatformFilePicker

            picker = CrossPlatformFilePicker()
            selected = picker.choose_file(
                file_types=["wav", "mp3", "flac", "m4a", "ogg", "aiff"],
                title="Select Audio File",
            )
            if selected:
                self.query_one("#file_input", Input).value = str(selected)
        except Exception as exc:
            self.notify(f"File picker unavailable: {exc}", severity="warning")

    @on(Button.Pressed, "#btn_analyze")
    async def on_analyze(self, _: Button.Pressed) -> None:
        await self._validate_and_run()

    @on(Button.Pressed, "#btn_back")
    def on_back(self, _: Button.Pressed) -> None:
        self.app.pop_screen()

    @on(Input.Submitted, "#file_input")
    async def on_path_submitted(self, _: Input.Submitted) -> None:
        await self._validate_and_run()

    async def _validate_and_run(self) -> None:
        path_str = self.query_one("#file_input", Input).value.strip()
        if not path_str:
            self.app.push_screen(ErrorDialog("No File", "Enter a file path first."))
            return
        p = Path(path_str)
        if not p.exists():
            self.app.push_screen(
                ErrorDialog("Not Found", f"File not found: {path_str}")
            )
            return
        if not p.is_file():
            self.app.push_screen(
                ErrorDialog("Not a File", f"Path is a directory: {path_str}")
            )
            return
        if not os.access(path_str, os.R_OK):
            self.app.push_screen(
                ErrorDialog("Permission", "Cannot read file - check permissions.")
            )
            return
        self._run_analysis(path_str)

    @work(exclusive=True, thread=True)
    def _run_analysis(self, file_path: str) -> None:
        import asyncio

        try:
            from samplemind.core.engine.audio_engine import AnalysisLevel
            from samplemind.interfaces.tui.audio_engine_bridge import get_tui_engine

            engine = get_tui_engine()
            level = getattr(AnalysisLevel, self._level, AnalysisLevel.STANDARD)
            self.app.call_from_thread(self._set_busy, True)
            self.app.call_from_thread(
                self._log, f"[cyan]Starting {self._level} analysis...[/]"
            )
            loop = asyncio.new_event_loop()
            features = loop.run_until_complete(
                engine.analyze_file(file_path, self._progress_cb, level)
            )
            loop.close()
            self.app.call_from_thread(self._log, "[green]Analysis complete![/]")
            self.app.call_from_thread(self._push_results, features, file_path)
        except Exception as exc:
            self.app.call_from_thread(self._log, f"[red]Error: {exc}[/]")
            self.app.call_from_thread(self._set_busy, False)

    def _progress_cb(self, pct: float) -> None:
        self.app.call_from_thread(self._set_progress, int(pct * 100))

    def _set_busy(self, busy: bool) -> None:
        for btn in self.query("Button"):
            btn.disabled = busy

    def _set_progress(self, pct: int) -> None:
        try:
            self.query_one("#progress_bar", ProgressBar).progress = float(pct)
        except Exception:
            pass

    def _log(self, msg: str) -> None:
        try:
            self.query_one("#log_out", RichLog).write(msg)
        except Exception:
            pass

    def _push_results(self, features: object, file_path: str) -> None:
        self._set_busy(False)
        from .results_screen import ResultsScreen

        self.app.push_screen(ResultsScreen(features, file_path))

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_start_analysis(self) -> None:
        import asyncio

        asyncio.get_event_loop().create_task(self._validate_and_run())
