"""Sample Card Widget — compact/expanded metadata display"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Collapsible, Label, Static


class SampleCard(Widget):
    """Compact-or-expanded display card for a single audio sample."""

    DEFAULT_CSS = """
    SampleCard {
        height: auto;
        border: solid $primary 30%;
        padding: 0 1;
        margin-bottom: 1;
    }
    SampleCard:focus { border: solid $accent; }
    SampleCard .card-header { height: 1; }
    SampleCard .badge {
        min-width: 8;
        height: 1;
        padding: 0 1;
        margin: 0 1 0 0;
        background: $primary 30%;
        color: $foreground;
        text-style: bold;
    }
    SampleCard .badge-bpm { background: $primary 40%; }
    SampleCard .badge-key { background: $secondary 40%; }
    SampleCard .badge-genre { background: $accent 30%; color: $background; }
    SampleCard .detail-label { color: $foreground 70%; margin-bottom: 1; }
    """

    class Clicked(Message):
        def __init__(self, card: SampleCard) -> None:
            super().__init__()
            self.card = card

    def __init__(
        self,
        filename: str = "",
        bpm: float | None = None,
        key: str | None = None,
        genre: str | None = None,
        quality_score: int | None = None,
        duration: float | None = None,
        compact: bool = True,
        **kwargs: object,
    ) -> None:
        super().__init__(**kwargs)
        self.filename = filename
        self.bpm = bpm
        self.key = key
        self.genre = genre
        self.quality_score = quality_score
        self.duration = duration
        self.compact = compact

    def compose(self) -> ComposeResult:
        name = self.filename[:35] + "…" if len(self.filename) > 35 else self.filename
        with Horizontal(classes="card-header"):
            yield Label(f"[bold]{name}[/]", classes="badge", markup=True)
            if self.bpm:
                yield Label(f"♩ {self.bpm:.0f}", classes="badge badge-bpm")
            if self.key:
                yield Label(self.key, classes="badge badge-key")
            if self.genre:
                yield Label(self.genre[:12], classes="badge badge-genre")
            if self.quality_score is not None:
                color = (
                    "green"
                    if self.quality_score >= 70
                    else "yellow" if self.quality_score >= 40 else "red"
                )
                yield Label(
                    f"[{color}]★ {self.quality_score}[/]",
                    classes="badge",
                    markup=True,
                )
        if not self.compact:
            lines: list[str] = []
            if self.duration:
                lines.append(f"Duration: {self.duration:.1f}s")
            if self.bpm:
                lines.append(f"BPM: {self.bpm:.1f}")
            if self.key:
                lines.append(f"Key: {self.key}")
            if self.genre:
                lines.append(f"Genre: {self.genre}")
            if self.quality_score is not None:
                lines.append(f"Quality: {self.quality_score}/100")
            with Collapsible(title="Details", collapsed=False):
                yield Static(
                    "\n".join(lines) if lines else "No metadata available",
                    classes="detail-label",
                )

    def on_click(self) -> None:
        self.post_message(self.Clicked(self))
