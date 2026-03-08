"""BPM Wheel Widget — large Digits display, color-coded by tempo range"""

from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Digits, Label
from textual.containers import Horizontal, Vertical


class BPMWheel(Widget):
    """Large BPM display using Textual's Digits widget."""

    DEFAULT_CSS = """
    BPMWheel {
        height: auto;
        min-height: 6;
        align: center middle;
        padding: 0 1;
        border: solid $primary 50%;
    }
    BPMWheel Digits { text-style: bold; width: auto; }
    BPMWheel .bpm-label { height: 1; color: $foreground 70%; width: 1fr; text-align: center; }
    BPMWheel .bpm-controls { height: 1; align: center middle; margin-top: 1; }
    BPMWheel .bpm-controls Button { min-width: 14; margin: 0 1; }
    BPMWheel .dim { color: $foreground 40%; }
    """

    bpm: reactive[float] = reactive(0.0)
    _halved: reactive[bool] = reactive(False)

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Digits("0", id="bpm_digits")
            yield Label("BPM", classes="bpm-label")
            with Horizontal(classes="bpm-controls"):
                yield Button("½ Half-time", id="btn_half")
                yield Button("×2 Double", id="btn_double")
            yield Label("", id="bpm_range_label", classes="bpm-label dim")

    def watch_bpm(self, value: float) -> None:
        self._render(value)

    def _render(self, value: float) -> None:
        try:
            display = value / 2 if self._halved else value
            digits = self.query_one("#bpm_digits", Digits)
            digits.update(f"{display:.0f}")
            if value < 80:
                digits.styles.color = "green"
            elif value < 120:
                digits.styles.color = "cyan"
            elif value < 145:
                digits.styles.color = "yellow"
            else:
                digits.styles.color = "red"
            if value < 80:
                range_name = "Ambient / Slow"
            elif value < 100:
                range_name = "Downtempo / Hip-Hop"
            elif value < 128:
                range_name = "House / Pop"
            elif value < 145:
                range_name = "Techno / Trance"
            else:
                range_name = "Drum & Bass / Hardcore"
            half_indicator = " [½ time]" if self._halved else ""
            self.query_one("#bpm_range_label", Label).update(
                f"{range_name}{half_indicator}"
            )
        except Exception:
            pass

    @on(Button.Pressed, "#btn_half")
    def on_half(self, _: Button.Pressed) -> None:
        self._halved = not self._halved
        self._render(self.bpm)

    @on(Button.Pressed, "#btn_double")
    def on_double(self, _: Button.Pressed) -> None:
        self._halved = False
        self.bpm = self.bpm * 2
