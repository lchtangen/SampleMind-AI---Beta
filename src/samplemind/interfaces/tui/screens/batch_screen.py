"""Batch Process Screen for SampleMind TUI v3.0"""

from __future__ import annotations

from pathlib import Path
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
    ProgressBar,
    RichLog,
)

from ..widgets.dialogs import ErrorDialog

_VALID_EXT = {".wav", ".mp3", ".flac", ".m4a", ".ogg", ".aiff"}


class BatchScreen(Screen):
    """Batch processing for folders of audio files."""

    BINDINGS = [
        Binding("escape", "action_back", "Back"),
    ]

    DEFAULT_CSS = """
    BatchScreen { layout: vertical; }
    #batch_body { height: 1fr; padding: 1 2; }
    .screen-title { color: $primary; text-style: bold; height: 1; margin-bottom: 1; }
    #folder_row { height: 3; margin-bottom: 1; }
    #folder_row Input { width: 1fr; margin-bottom: 0; }
    #folder_row Button { min-width: 12; margin-left: 1; }
    #btn_row { height: auto; margin: 1 0; }
    #btn_row Button { margin-right: 1; }
    #progress_bar { margin-bottom: 1; }
    #files_table { height: 8; margin-bottom: 1; }
    #log_out { height: 1fr; }
    """

    def __init__(self) -> None:
        super().__init__()
        self._audio_files: list[str] = []
        self._results: list[Any] = []
        self._cancel_requested = False
        self._level = "STANDARD"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="batch_body"):
            yield Label("Batch Process Audio Files", classes="screen-title")
            with Horizontal(id="folder_row"):
                yield Input(
                    placeholder="Folder path to batch process...", id="folder_input"
                )
                yield Button("Browse", id="btn_browse", variant="primary")
            with Horizontal(id="btn_row"):
                yield Button("Scan", id="btn_scan", variant="primary")
                yield Button("Process All", id="btn_process", variant="success")
                yield Button("Cancel", id="btn_cancel", variant="error")
                yield Button("Back", id="btn_back", variant="warning")
            yield Label("", id="status_label")
            yield ProgressBar(total=100, id="progress_bar", show_eta=True)
            yield DataTable(zebra_stripes=True, id="files_table")
            yield RichLog(highlight=True, markup=True, id="log_out", wrap=True)
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#files_table", DataTable)
        table.add_columns("File", "Size", "Duration", "BPM", "Key", "Status")
        self._update_buttons()
        self.query_one("#folder_input", Input).focus()

    @on(Button.Pressed, "#btn_browse")
    def on_browse(self, _: Button.Pressed) -> None:
        try:
            from samplemind.utils.file_picker import CrossPlatformFilePicker

            picker = CrossPlatformFilePicker()
            folder = picker.choose_folder(title="Select Folder for Batch Processing")
            if folder:
                self.query_one("#folder_input", Input).value = str(folder)
        except Exception as exc:
            self.notify(f"Folder picker unavailable: {exc}", severity="warning")

    @on(Button.Pressed, "#btn_scan")
    def on_scan(self, _: Button.Pressed) -> None:
        self._do_scan()

    @on(Button.Pressed, "#btn_process")
    def on_process(self, _: Button.Pressed) -> None:
        self._start_processing()

    @on(Button.Pressed, "#btn_cancel")
    def on_cancel_btn(self, _: Button.Pressed) -> None:
        self._cancel_requested = True
        self._log("[yellow]Cancel requested...[/]")

    @on(Button.Pressed, "#btn_back")
    def on_back(self, _: Button.Pressed) -> None:
        self.app.pop_screen()

    @on(Input.Submitted, "#folder_input")
    def on_folder_submitted(self, _: Input.Submitted) -> None:
        self._do_scan()

    @work(thread=True)
    def _do_scan(self) -> None:
        folder_str = self.query_one("#folder_input", Input).value.strip()
        if not folder_str:
            self.app.call_from_thread(
                lambda: self.app.push_screen(
                    ErrorDialog("No Folder", "Enter a folder path first.")
                )
            )
            return
        folder = Path(folder_str)
        if not folder.is_dir():
            self.app.call_from_thread(
                lambda: self.app.push_screen(
                    ErrorDialog("Not Found", f"Folder not found: {folder_str}")
                )
            )
            return
        found: list[str] = []
        for ext in _VALID_EXT:
            found.extend(str(p) for p in folder.rglob(f"*{ext}"))
        self._audio_files = sorted(found)
        self.app.call_from_thread(self._populate_table)
        self.app.call_from_thread(
            self._log, f"[green]Found {len(self._audio_files)} audio files[/]"
        )

    def _populate_table(self) -> None:
        table = self.query_one("#files_table", DataTable)
        table.clear()
        for fp in self._audio_files:
            p = Path(fp)
            try:
                size = f"{p.stat().st_size / 1024:.0f} KB"
            except Exception:
                size = "?"
            table.add_row(p.name[:50], size, "-", "-", "-", "Pending", key=fp)
        self._update_buttons()

    def _start_processing(self) -> None:
        if not self._audio_files:
            self.app.push_screen(
                ErrorDialog("Nothing to Process", "Scan a folder first.")
            )
            return
        self._cancel_requested = False
        self._results.clear()
        self._run_batch()

    @work(exclusive=True, thread=True)
    def _run_batch(self) -> None:
        import asyncio

        try:
            from samplemind.core.engine.audio_engine import AnalysisLevel
            from samplemind.interfaces.tui.audio_engine_bridge import get_tui_engine

            engine = get_tui_engine()
            level = getattr(AnalysisLevel, self._level, AnalysisLevel.STANDARD)
            total = len(self._audio_files)
            self.app.call_from_thread(self._set_busy, True)
            for i, fp in enumerate(self._audio_files):
                if self._cancel_requested:
                    self.app.call_from_thread(
                        self._log, "[yellow]Processing cancelled.[/]"
                    )
                    break
                self.app.call_from_thread(
                    self._log, f"[dim]({i+1}/{total})[/] {Path(fp).name}"
                )
                try:
                    loop = asyncio.new_event_loop()
                    features = loop.run_until_complete(
                        engine.analyze_file(fp, None, level)
                    )
                    loop.close()
                    self._results.append((fp, features))
                    self.app.call_from_thread(self._update_row, fp, features)
                    pct = int((i + 1) / total * 100)
                    self.app.call_from_thread(self._set_progress, pct)
                except Exception as exc:
                    self.app.call_from_thread(
                        self._log, f"[red]{Path(fp).name}: {exc}[/]"
                    )
            self.app.call_from_thread(
                self._log,
                f"[green]Done - {len(self._results)}/{total} files processed[/]",
            )
        except Exception as exc:
            self.app.call_from_thread(self._log, f"[red]Batch error: {exc}[/]")
        finally:
            self.app.call_from_thread(self._set_busy, False)

    def _update_row(self, fp: str, features: Any) -> None:
        try:
            table = self.query_one("#files_table", DataTable)
            bpm = f"{getattr(features, 'tempo', 0):.0f}" if features else "?"
            key = getattr(features, "key", "?") if features else "?"
            dur = f"{getattr(features, 'duration', 0):.1f}s" if features else "?"
            table.update_cell(fp, "Duration", dur)
            table.update_cell(fp, "BPM", bpm)
            table.update_cell(fp, "Key", key)
            table.update_cell(fp, "Status", "[green]Done[/]")
        except Exception:
            pass

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

    def _update_buttons(self) -> None:
        try:
            self.query_one("#btn_process", Button).disabled = not bool(
                self._audio_files
            )
        except Exception:
            pass

    def action_back(self) -> None:
        self.app.pop_screen()
