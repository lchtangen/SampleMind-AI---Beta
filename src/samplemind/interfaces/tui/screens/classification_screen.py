"""Classification Screen for SampleMind TUI v3.0"""

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
    Input,
    Label,
    ProgressBar,
    RichLog,
)


class ClassificationScreen(Screen):
    """BEATs-powered audio classification with confidence scores."""

    BINDINGS = [
        Binding("escape", "action_back", "Back"),
        Binding("ctrl+r", "run_classification", "Classify"),
    ]

    DEFAULT_CSS = """
    ClassificationScreen { layout: vertical; }
    #class_body { height: 1fr; padding: 1 2; }
    .screen-title { color: $primary; text-style: bold; height: 1; margin-bottom: 1; }
    .row { height: auto; margin-bottom: 1; }
    .row Label { min-width: 12; content-align: center middle; height: 1; }
    .row Input { width: 1fr; }
    .row Button { min-width: 12; margin-left: 1; }
    #progress_bar { margin-bottom: 1; }
    #class_table { height: 1fr; }
    #log_area { height: 5; }
    #btn_row { height: 3; margin-top: 1; }
    #btn_row Button { margin-right: 1; }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="class_body"):
            yield Label("Audio Classification (BEATs / AI)", classes="screen-title")
            with Horizontal(classes="row"):
                yield Label("Audio file:")
                yield Input(placeholder="Path to audio file...", id="file_input")
                yield Button("Browse", id="btn_browse", variant="primary")
            with Horizontal(id="btn_row"):
                yield Button("Classify", id="btn_classify", variant="success")
                yield Button("Back", id="btn_back", variant="warning")
            yield ProgressBar(total=100, id="progress_bar", show_eta=False)
            yield Label("0 categories detected", id="count_label")
            yield DataTable(zebra_stripes=True, id="class_table")
            yield RichLog(highlight=True, id="log_area", wrap=True)
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#class_table", DataTable)
        table.add_columns("Category", "Label", "Confidence", "Source")
        self.query_one("#file_input", Input).focus()

    @on(Button.Pressed, "#btn_browse")
    def on_browse(self, _: Button.Pressed) -> None:
        try:
            from samplemind.utils.file_picker import CrossPlatformFilePicker

            picker = CrossPlatformFilePicker()
            selected = picker.choose_file(
                file_types=["wav", "mp3", "flac", "m4a"],
            )
            if selected:
                self.query_one("#file_input", Input).value = str(selected)
        except Exception as exc:
            self.notify(f"File picker unavailable: {exc}", severity="warning")

    @on(Button.Pressed, "#btn_classify")
    def on_classify(self, _: Button.Pressed) -> None:
        self.action_run_classification()

    @on(Button.Pressed, "#btn_back")
    def on_back(self, _: Button.Pressed) -> None:
        self.app.pop_screen()

    @on(Input.Submitted, "#file_input")
    def on_submitted(self, _: Input.Submitted) -> None:
        self.action_run_classification()

    @work(exclusive=True, thread=True)
    def _classify(self, file_path: str) -> None:
        import asyncio

        try:
            from samplemind.core.engine.audio_engine import AnalysisLevel
            from samplemind.interfaces.tui.audio_engine_bridge import get_tui_engine

            engine = get_tui_engine()
            self.app.call_from_thread(self._log, f"[cyan]Classifying {file_path}...[/]")
            self.app.call_from_thread(self._set_progress, 25)
            loop = asyncio.new_event_loop()
            features = loop.run_until_complete(
                engine.analyze_file(file_path, None, AnalysisLevel.PROFESSIONAL)
            )
            loop.close()
            self.app.call_from_thread(self._set_progress, 100)
            self.app.call_from_thread(self._populate, features)
        except Exception as exc:
            self.app.call_from_thread(self._log, f"[red]Error: {exc}[/]")
            self.app.call_from_thread(self._set_progress, 0)

    def _populate(self, features: object) -> None:
        table = self.query_one("#class_table", DataTable)
        table.clear()
        rows: list[tuple[str, str, str, str]] = []
        genre = getattr(features, "genre", None)
        if genre:
            rows.append(("Genre", str(genre), "primary", "ML model"))
        mood = getattr(features, "mood", None)
        if mood:
            rows.append(("Mood", str(mood), "-", "ML model"))
        instrument = getattr(features, "instrument", None)
        if instrument:
            rows.append(("Instrument", str(instrument), "-", "BEATs"))
        beats_labels = getattr(features, "beats_labels", None)
        if beats_labels and isinstance(beats_labels, list):
            for label in beats_labels[:10]:
                lbl = (
                    label.get("label", str(label))
                    if isinstance(label, dict)
                    else str(label)
                )
                conf = label.get("confidence", "-") if isinstance(label, dict) else "-"
                rows.append(("BEATs", lbl, str(conf), "microsoft/BEATs"))
        for row in rows:
            table.add_row(*row)
        count = len(rows)
        self.query_one("#count_label", Label).update(
            f"{count} categor{'ies' if count != 1 else 'y'} detected"
        )
        self._log("[green]Classification complete![/]")

    def _set_progress(self, pct: int) -> None:
        try:
            self.query_one("#progress_bar", ProgressBar).progress = float(pct)
        except Exception:
            pass

    def _log(self, msg: str) -> None:
        try:
            self.query_one("#log_area", RichLog).write(msg)
        except Exception:
            pass

    def action_run_classification(self) -> None:
        fp = self.query_one("#file_input", Input).value.strip()
        if not fp:
            self.notify("Enter a file path first", severity="warning")
            return
        self._classify(fp)

    def action_back(self) -> None:
        self.app.pop_screen()
