"""Visualizer Screen for SampleMind TUI v3.0 — PlotextPlot waveform + spectrum"""

from __future__ import annotations

from typing import Any

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    Select,
    Sparkline,
)

_VIZ_TYPES = [
    ("waveform", "Waveform"),
    ("spectrum", "Frequency Spectrum"),
    ("mel", "Mel Spectrogram"),
    ("chroma", "Chromagram"),
]

_PLOTEXT_AVAILABLE = False
try:
    from textual_plotext import PlotextPlot

    _PLOTEXT_AVAILABLE = True
except ImportError:
    pass


class VisualizerScreen(Screen):
    """Interactive audio visualizer with multiple plot modes."""

    BINDINGS = [
        Binding("escape", "action_back", "Back"),
        Binding("r", "action_reload", "Reload"),
    ]

    DEFAULT_CSS = """
    VisualizerScreen { layout: vertical; }
    #viz_body { height: 1fr; padding: 1 2; layout: vertical; }
    .screen-title { color: $primary; text-style: bold; height: 1; margin-bottom: 1; }
    #file_row { height: 3; margin-bottom: 1; }
    #file_row Input { width: 1fr; }
    #file_row Button { min-width: 12; margin-left: 1; }
    #controls_row { height: auto; margin-bottom: 1; }
    #controls_row Select { width: 30; margin-right: 1; }
    #main_plot { height: 1fr; border: solid $accent 30%; }
    #rms_sparkline { height: 4; }
    #btn_row { height: auto; margin-top: 1; }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="viz_body"):
            yield Label("📊 Audio Visualizer", classes="screen-title")
            with Horizontal(id="file_row"):
                yield Input(
                    placeholder="Audio file path (WAV, MP3, FLAC)…", id="file_input"
                )
                yield Button("📁 Browse", id="btn_browse", variant="primary")
            with Horizontal(id="controls_row"):
                yield Select(
                    [(label, val) for val, label in _VIZ_TYPES],
                    id="sel_viz",
                    value="waveform",
                )
                yield Button("🔄 Load", id="btn_load", variant="primary")
            if _PLOTEXT_AVAILABLE:
                yield PlotextPlot(id="main_plot")
            else:
                yield Label(
                    "[yellow]textual-plotext not installed — install with: pip install textual-plotext[/]",
                    id="main_plot",
                    markup=True,
                )
            yield Label("RMS (loudness over time):", classes="screen-title")
            yield Sparkline(data=[0.0] * 60, id="rms_sparkline", summary_function=max)
            with Horizontal(id="btn_row"):
                yield Button("⬅️  Back", id="btn_back", variant="warning")
        yield Footer()

    @on(Button.Pressed, "#btn_browse")
    def on_browse(self, _: Button.Pressed) -> None:
        try:
            from samplemind.utils.file_picker import CrossPlatformFilePicker

            picker = CrossPlatformFilePicker()
            f = picker.choose_file(
                file_types=["wav", "mp3", "flac"],
                title="Select Audio File",
            )
            if f:
                self.query_one("#file_input", Input).value = str(f)
        except Exception as exc:
            self.notify(f"Picker unavailable: {exc}", severity="warning")

    @on(Button.Pressed, "#btn_load")
    def on_load(self, _: Button.Pressed) -> None:
        path = self.query_one("#file_input", Input).value.strip()
        if not path:
            self.notify("Enter a file path first", severity="warning")
            return
        viz_sel = self.query_one("#sel_viz", Select)
        viz_type = str(viz_sel.value) if viz_sel.value != Select.BLANK else "waveform"
        self._load_audio(path, viz_type)

    @on(Input.Submitted, "#file_input")
    def on_path_submitted(self, _: Input.Submitted) -> None:
        path = self.query_one("#file_input", Input).value.strip()
        if not path:
            return
        viz_sel = self.query_one("#sel_viz", Select)
        viz_type = str(viz_sel.value) if viz_sel.value != Select.BLANK else "waveform"
        self._load_audio(path, viz_type)

    @work(thread=True)
    def _load_audio(self, file_path: str, viz_type: str) -> None:
        try:
            import soundfile as sf  # type: ignore[import-untyped]

            y, sr = sf.read(file_path, dtype="float32", always_2d=False)
            if y.ndim == 2:
                y = y.mean(axis=1)
            self.app.call_from_thread(self._render_plot, y, sr, viz_type)
        except Exception as exc:
            self.app.call_from_thread(self.notify, f"Load failed: {exc}", "error")

    def _render_plot(self, y: Any, sr: int, viz_type: str) -> None:
        # Update RMS sparkline regardless of plotext availability
        try:
            import numpy as np

            chunk = max(1, len(y) // 60)
            rms = [
                float(np.sqrt(np.mean(y[i : i + chunk] ** 2)))
                for i in range(0, len(y), chunk)
            ][:60]
            while len(rms) < 60:
                rms.append(0.0)
            self.query_one("#rms_sparkline", Sparkline).data = rms
        except Exception:
            pass

        if not _PLOTEXT_AVAILABLE:
            return
        try:
            import numpy as np
            from textual_plotext import PlotextPlot

            plot = self.query_one("#main_plot", PlotextPlot)
            plt = plot.plt
            plt.clear_figure()

            if viz_type == "waveform":
                t = np.linspace(0, len(y) / sr, num=min(len(y), 2048))
                step = max(1, len(y) // 2048)
                plt.plot(list(t), list(y[::step][: len(t)]))
                plt.title("Waveform")
                plt.xlabel("Time (s)")
                plt.ylabel("Amplitude")
            elif viz_type == "spectrum":
                import scipy.fft as fft  # type: ignore[import-untyped]

                n = min(len(y), 4096)
                mag = np.abs(fft.rfft(y[:n]))  # type: ignore[arg-type]
                freqs = fft.rfftfreq(n, 1 / sr)
                plt.plot(list(freqs[:512]), list(mag[:512]))
                plt.title("Frequency Spectrum")
                plt.xlabel("Frequency (Hz)")
                plt.ylabel("Magnitude")
            elif viz_type in ("mel", "chroma"):
                try:
                    import librosa

                    if viz_type == "mel":
                        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=64)
                        S_db = librosa.power_to_db(S, ref=np.max)
                        mean_per_band = S_db.mean(axis=1)
                        plt.bar(list(range(64)), list(mean_per_band))
                        plt.title("Mel Spectrogram (band averages)")
                    else:
                        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
                        notes = [
                            "C",
                            "C#",
                            "D",
                            "D#",
                            "E",
                            "F",
                            "F#",
                            "G",
                            "G#",
                            "A",
                            "A#",
                            "B",
                        ]
                        plt.bar(notes, list(chroma.mean(axis=1)))
                        plt.title("Chromagram")
                except ImportError:
                    plt.plot([0, 1], [0, 0])
                    plt.title("librosa not available")
            plot.refresh()
        except Exception as exc:
            self.notify(f"Plot error: {exc}", severity="warning")

    @on(Button.Pressed, "#btn_back")
    def on_back(self, _: Button.Pressed) -> None:
        self.app.pop_screen()

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_reload(self) -> None:
        path = self.query_one("#file_input", Input).value.strip()
        if path:
            viz_sel = self.query_one("#sel_viz", Select)
            viz_type = (
                str(viz_sel.value) if viz_sel.value != Select.BLANK else "waveform"
            )
            self._load_audio(path, viz_type)
