"""Results Screen for SampleMind TUI v3.0"""

from __future__ import annotations

from typing import Any

from textual import on
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
    Static,
    TabbedContent,
    TabPane,
)

from ..widgets.bpm_wheel import BPMWheel
from ..widgets.progress_ring import ProgressRing
from ..widgets.spectral_viz import SpectralViz
from ..widgets.waveform import WaveformWidget


class ResultsScreen(Screen):
    """Display audio analysis results with tabbed layout."""

    BINDINGS = [
        Binding("escape", "action_back", "Back"),
        Binding("e", "export", "Export"),
        Binding("f", "add_favorite", "Favorite"),
    ]

    DEFAULT_CSS = """
    ResultsScreen { layout: vertical; }
    #results_body { height: 1fr; padding: 1 2; }
    .screen-title { color: $primary; text-style: bold; height: 1; margin-bottom: 1; }
    .section-label { text-style: bold; color: $accent; margin-bottom: 1; }
    #summary_row { height: auto; margin-bottom: 1; }
    #data_table { height: 12; }
    #ai_text { height: 1fr; }
    #btn_row { height: 3; margin-top: 1; }
    #btn_row Button { margin-right: 1; }
    """

    def __init__(self, features: Any = None, file_path: str = "") -> None:
        super().__init__()
        self._features = features
        self._file_path = file_path

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="results_body"):
            yield Label("Analysis Results", classes="screen-title")
            yield Label(self._file_path or "No file", id="file_label")
            with TabbedContent(initial="tab_overview"):
                with TabPane("Overview", id="tab_overview"):
                    with Horizontal(id="summary_row"):
                        yield BPMWheel(id="bpm_wheel")
                        with Vertical():
                            yield Label("Key / Scale", classes="section-label")
                            yield Label("", id="lbl_key")
                            yield Label("Genre", classes="section-label")
                            yield Label("", id="lbl_genre")
                            yield Label("Duration", classes="section-label")
                            yield Label("", id="lbl_duration")
                    yield ProgressRing(id="quality_ring")
                with TabPane("Audio", id="tab_audio"):
                    yield WaveformWidget(id="waveform_widget")
                with TabPane("Spectral", id="tab_spectral"):
                    yield SpectralViz(id="spectral_viz")
                with TabPane("AI Analysis", id="tab_ai"):
                    yield Static("", id="ai_text", expand=True)
                with TabPane("Features", id="tab_features"):
                    yield DataTable(zebra_stripes=True, id="data_table")
                with TabPane("Export", id="tab_export"):
                    with Vertical():
                        yield Button("Export JSON", id="btn_json", variant="primary")
                        yield Button("Export CSV", id="btn_csv", variant="primary")
                        yield Button(
                            "Add to Library", id="btn_library", variant="success"
                        )
            with Horizontal(id="btn_row"):
                yield Button("Back", id="btn_back", variant="warning")
                yield Button("Favorite", id="btn_fav", variant="success")
                yield Button("Analyze Another", id="btn_another", variant="primary")
        yield Footer()

    def on_mount(self) -> None:
        self._populate()

    def _populate(self) -> None:
        f = self._features
        if not f:
            return
        try:
            from ..widgets.bpm_wheel import BPMWheel as BPMWheelWidget

            self.query_one("#bpm_wheel", BPMWheelWidget).bpm = float(
                getattr(f, "tempo", 0)
            )
        except Exception:
            pass
        try:
            self.query_one("#lbl_key", Label).update(str(getattr(f, "key", "?")))
            self.query_one("#lbl_genre", Label).update(str(getattr(f, "genre", "?")))
            dur = getattr(f, "duration", 0)
            m, s = divmod(int(dur), 60)
            self.query_one("#lbl_duration", Label).update(f"{m}:{s:02d}")
        except Exception:
            pass
        try:
            table = self.query_one("#data_table", DataTable)
            table.add_columns("Feature", "Value")
            for attr in (
                "tempo",
                "key",
                "loudness",
                "spectral_centroid",
                "zero_crossing_rate",
                "duration",
                "genre",
                "mood",
            ):
                val = getattr(f, attr, None)
                if val is not None:
                    table.add_row(
                        attr.replace("_", " ").title(),
                        str(round(val, 3) if isinstance(val, float) else val),
                    )
        except Exception:
            pass
        try:
            ai = getattr(f, "ai_analysis", None) or "No AI analysis available."
            self.query_one("#ai_text", Static).update(str(ai))
        except Exception:
            pass
        try:
            score = getattr(f, "quality_score", 0)
            self.query_one("#quality_ring", ProgressRing).score = int(score)
        except Exception:
            pass

    @on(Button.Pressed, "#btn_back")
    def on_back(self, _: Button.Pressed) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#btn_fav")
    def on_fav(self, _: Button.Pressed) -> None:
        self.action_add_favorite()

    @on(Button.Pressed, "#btn_another")
    def on_another(self, _: Button.Pressed) -> None:
        from .analyze_screen import AnalyzeScreen

        self.app.pop_screen()
        self.app.push_screen(AnalyzeScreen())

    @on(Button.Pressed, "#btn_json")
    def on_export_json(self, _: Button.Pressed) -> None:
        self._export("json")

    @on(Button.Pressed, "#btn_csv")
    def on_export_csv(self, _: Button.Pressed) -> None:
        self._export("csv")

    @on(Button.Pressed, "#btn_library")
    def on_add_library(self, _: Button.Pressed) -> None:
        self.notify("Added to library")

    def _export(self, fmt: str) -> None:
        if not self._features:
            self.notify("No results to export", severity="warning")
            return
        try:
            import csv
            import json
            import time

            out = f"samplemind_export_{int(time.time())}.{fmt}"
            if fmt == "json":
                data = {
                    k: v
                    for k, v in vars(self._features).items()
                    if not k.startswith("_")
                }
                with open(out, "w") as fh:
                    json.dump(data, fh, indent=2, default=str)
            else:
                data = {
                    k: v
                    for k, v in vars(self._features).items()
                    if not k.startswith("_")
                }
                with open(out, "w", newline="") as fh:
                    w = csv.writer(fh)
                    for k, v in data.items():
                        w.writerow([k, v])
            self.notify(f"Exported to {out}")
        except Exception as exc:
            self.notify(f"Export failed: {exc}", severity="error")

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_export(self) -> None:
        self._export("json")

    def action_add_favorite(self) -> None:
        if not self._file_path:
            self.notify("No file to favorite", severity="warning")
            return
        try:
            from samplemind.services.favorites_service import (  # type: ignore[import]
                get_favorites_manager,
            )

            mgr = get_favorites_manager()
            mgr.add(self._file_path)
            self.notify("Added to favorites", severity="information")
        except Exception as exc:
            self.notify(f"Could not add favorite: {exc}", severity="warning")
