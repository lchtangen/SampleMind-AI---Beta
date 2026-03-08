"""Progress Ring Widget — ASCII arc display for quality scores 0-100"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, Static
from textual.containers import Vertical


def _build_arc(score: int, width: int = 20) -> str:
    filled = int(max(0, min(100, score)) / 100 * width)
    arc = "█" * filled + "░" * (width - filled)
    return f"[{arc}] {score}%"


def _quality_label(score: int) -> str:
    if score >= 80:
        return "[bold green]★ Production Ready[/]"
    elif score >= 60:
        return "[bold cyan]◆ Good[/]"
    elif score >= 40:
        return "[bold yellow]◇ Fair[/]"
    else:
        return "[bold red]✗ Poor[/]"


class ProgressRing(Widget):
    """Visual quality score display with arc progress and category label."""

    DEFAULT_CSS = """
    ProgressRing {
        height: auto;
        min-height: 5;
        align: center middle;
        padding: 1;
        border: solid $primary 40%;
    }
    ProgressRing #ring_title { height: 1; color: $foreground 60%; text-align: center; margin-bottom: 1; }
    ProgressRing #ring_arc { height: 1; text-align: center; color: $primary; }
    ProgressRing #ring_label { height: 1; text-align: center; margin-top: 1; }
    """

    score: reactive[int] = reactive(0)

    def __init__(self, title: str = "Quality Score", **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._title = title

    def compose(self) -> ComposeResult:
        yield Label(self._title, id="ring_title")
        yield Static("", id="ring_arc", markup=True)
        yield Static("", id="ring_label", markup=True)

    def on_mount(self) -> None:
        self._render(self.score)

    def watch_score(self, value: int) -> None:
        self._render(value)

    def _render(self, score: int) -> None:
        try:
            self.query_one("#ring_arc", Static).update(_build_arc(score))
            self.query_one("#ring_label", Static).update(_quality_label(score))
        except Exception:
            pass
