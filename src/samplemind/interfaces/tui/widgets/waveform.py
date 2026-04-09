"""Waveform Visualization Widget — Textual ^0.87, uses textual-plotext (KP 44)"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget

if TYPE_CHECKING:
    import numpy as np

logger = logging.getLogger(__name__)

try:
    from textual_plotext import PlotextPlot  # type: ignore[import-untyped]

    _PLOTEXT_AVAILABLE = True
except ImportError:
    _PLOTEXT_AVAILABLE = False


class WaveformWidget(Widget):
    """Audio waveform visualization using textual-plotext."""

    DEFAULT_CSS = """
    WaveformWidget {
        width: 1fr;
        height: 10;
        border: solid $accent;
        padding: 0;
    }
    WaveformWidget > Static {
        height: 1fr;
        content-align: center middle;
        color: $foreground 50%;
    }
    """

    playback_position: reactive[float] = reactive(0.0)
    _waveform_data: np.ndarray | None = None
    _waveform_sr: int = 44100

    def compose(self) -> ComposeResult:
        if _PLOTEXT_AVAILABLE:
            yield PlotextPlot(id="waveform_plot")
        else:
            from textual.widgets import Static

            yield Static(
                "📊 Waveform (install textual-plotext for visualization)",
                id="waveform_fallback",
            )

    def update_waveform(self, y: np.ndarray, sr: int) -> None:
        if not _PLOTEXT_AVAILABLE:
            return
        try:
            self._waveform_data = y
            self._waveform_sr = sr
            self._render_plot()
        except Exception as exc:
            logger.debug("Waveform render failed: %s", exc)

    def _render_plot(self) -> None:
        if not _PLOTEXT_AVAILABLE or self._waveform_data is None:
            return
        try:
            y = self._waveform_data
            sr = self._waveform_sr
            plot = self.query_one("#waveform_plot", PlotextPlot)
            duration = len(y) / max(sr, 1)
            step = max(1, len(y) // 400)
            x = [i / sr for i in range(0, len(y), step)]
            ydata = y[::step].tolist()
            plot.plt.clear_data()
            plot.plt.clear_figure()
            plot.plt.plot(x, ydata, color="cyan", marker="braille")
            plot.plt.xlabel("Time (s)")
            plot.plt.yticks([])
            plot.plt.title(f"Waveform  [{duration:.1f}s  ·  {sr / 1000:.1f} kHz]")
            if self.playback_position > 0:
                plot.plt.vertical_line(self.playback_position, color="red")
            plot.refresh()
        except Exception as exc:
            logger.debug("Waveform plot update failed: %s", exc)

    def watch_playback_position(self, pos: float) -> None:
        self._render_plot()

    def clear(self) -> None:
        self._waveform_data = None
        if not _PLOTEXT_AVAILABLE:
            return
        try:
            plot = self.query_one("#waveform_plot", PlotextPlot)
            plot.plt.clear_data()
            plot.plt.clear_figure()
            plot.refresh()
        except Exception:
            pass
