"""Spectral Visualization Widget — Textual ^0.87, uses Sparkline per freq band"""

from __future__ import annotations

import logging
from enum import auto, Enum
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, Sparkline
from textual.containers import Horizontal, Vertical

if TYPE_CHECKING:
    import numpy as np

logger = logging.getLogger(__name__)

_BAND_NAMES = ["Sub", "Bass", "LowMid", "Mid", "HighMid", "High"]


class SpectralType(Enum):
    WAVEFORM = auto()
    CHROMAGRAM = auto()
    MEL_SPECTROGRAM = auto()
    MFCC = auto()


class SpectralViz(Widget):
    """Six Sparkline widgets (one per frequency band) for real-time spectral display."""

    DEFAULT_CSS = """
    SpectralViz {
        width: 1fr;
        height: 14;
        border: solid $accent;
        padding: 1;
    }
    SpectralViz #viz_label {
        color: $primary;
        text-style: bold;
        height: 1;
        margin-bottom: 1;
    }
    SpectralViz .band-row {
        height: 2;
    }
    SpectralViz .band-label {
        width: 8;
        height: 2;
        content-align: left middle;
        color: $foreground 60%;
    }
    SpectralViz .band-sparkline {
        width: 1fr;
        height: 2;
    }
    """

    viz_type: reactive[SpectralType] = reactive(SpectralType.CHROMAGRAM)

    def compose(self) -> ComposeResult:
        yield Label("📈 Spectral Analysis", id="viz_label")
        with Vertical(id="band_container"):
            for i, name in enumerate(_BAND_NAMES):
                with Horizontal(classes="band-row"):
                    yield Label(name, classes="band-label")
                    yield Sparkline(
                        data=[0.0] * 20,
                        id=f"band_{i}",
                        summary_function=max,
                        classes="band-sparkline",
                    )

    def update_spectral(self, spectral_contrast: list[float] | None = None) -> None:
        if not spectral_contrast:
            return
        n = min(len(spectral_contrast), 6)
        for i in range(n):
            try:
                sparkline = self.query_one(f"#band_{i}", Sparkline)
                val = max(0.0, float(spectral_contrast[i]))
                current = list(sparkline.data)[-19:] if sparkline.data else [0.0] * 19
                sparkline.data = current + [val]
            except Exception as exc:
                logger.debug("SpectralViz band %d update failed: %s", i, exc)

    def update_chromagram(self, chroma: "np.ndarray | None" = None) -> None:
        if chroma is None:
            return
        try:
            import numpy as np

            means = np.abs(chroma).mean(axis=1).tolist()
            paired = [float(means[i * 2] + means[i * 2 + 1]) / 2 for i in range(6)]
            self.update_spectral(paired)
        except Exception as exc:
            logger.debug("Chromagram update failed: %s", exc)

    def clear(self) -> None:
        for i in range(6):
            try:
                self.query_one(f"#band_{i}", Sparkline).data = [0.0] * 20
            except Exception:
                pass
