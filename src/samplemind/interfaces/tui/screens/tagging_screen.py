"""Tagging Screen for SampleMind TUI v3.0"""

from __future__ import annotations

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
    RichLog,
    TextArea,
)


class TaggingScreen(Screen):
    """Attach metadata tags and notes to audio samples."""

    BINDINGS = [
        Binding("escape", "action_back", "Back"),
        Binding("ctrl+s", "save_tags", "Save"),
    ]

    DEFAULT_CSS = """
    TaggingScreen { layout: vertical; }
    #tagging_body { height: 1fr; padding: 1 2; }
    .screen-title { color: $primary; text-style: bold; height: 1; margin-bottom: 1; }
    .row { height: auto; margin-bottom: 1; }
    .row Label { min-width: 18; content-align: center middle; height: 1; }
    #notes_area { height: 6; margin-bottom: 1; }
    #log_area { height: 4; }
    #btn_row { height: 3; margin-top: 1; }
    #btn_row Button { margin-right: 1; }
    """

    def __init__(self, file_path: str = "") -> None:
        super().__init__()
        self._file_path = file_path

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="tagging_body"):
            yield Label("Tag Audio Sample", classes="screen-title")
            with Horizontal(classes="row"):
                yield Label("File path:")
                yield Input(
                    value=self._file_path,
                    placeholder="Path to audio file...",
                    id="file_input",
                )
            with Horizontal(classes="row"):
                yield Label("Tags (comma-sep):")
                yield Input(
                    placeholder="ambient, 120bpm, C major, drum loop...",
                    id="tags_input",
                )
            with Horizontal(classes="row"):
                yield Label("Genre:")
                yield Input(placeholder="Override genre...", id="genre_input")
            with Horizontal(classes="row"):
                yield Label("Mood:")
                yield Input(placeholder="dark, energetic, chill...", id="mood_input")
            yield Label("Notes:")
            yield TextArea(id="notes_area")
            yield RichLog(highlight=True, id="log_area", wrap=True)
            with Horizontal(id="btn_row"):
                yield Button("Save Tags", id="btn_save", variant="success")
                yield Button("Clear", id="btn_clear", variant="default")
                yield Button("Back", id="btn_back", variant="warning")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#file_input", Input).focus()

    @on(Button.Pressed, "#btn_save")
    def on_save(self, _: Button.Pressed) -> None:
        self.action_save_tags()

    @on(Button.Pressed, "#btn_clear")
    def on_clear(self, _: Button.Pressed) -> None:
        for inp_id in ("#tags_input", "#genre_input", "#mood_input"):
            self.query_one(inp_id, Input).value = ""
        self.query_one("#notes_area", TextArea).clear()

    @on(Button.Pressed, "#btn_back")
    def on_back_btn(self, _: Button.Pressed) -> None:
        self.app.pop_screen()

    @work(thread=True)
    def _save_async(
        self, fp: str, tags: list[str], genre: str, mood: str, notes: str
    ) -> None:
        import asyncio

        try:
            from samplemind.services.tagging_service import (  # type: ignore[import]
                TaggingService,
            )

            svc = TaggingService()
            loop = asyncio.new_event_loop()
            loop.run_until_complete(
                svc.save_tags(
                    file_path=fp,
                    tags=tags,
                    genre=genre,
                    mood=mood,
                    notes=notes,
                )
            )
            loop.close()
            self.app.call_from_thread(self._log, "[green]Tags saved successfully![/]")
            self.app.call_from_thread(
                lambda: self.notify("Tags saved", severity="information")
            )
        except Exception as exc:
            self.app.call_from_thread(self._log, f"[red]Save error: {exc}[/]")
            self.app.call_from_thread(
                lambda e=exc: self.notify(f"Save failed: {e}", severity="error")
            )

    def _log(self, msg: str) -> None:
        try:
            self.query_one("#log_area", RichLog).write(msg)
        except Exception:
            pass

    def action_save_tags(self) -> None:
        fp = self.query_one("#file_input", Input).value.strip()
        if not fp:
            self.notify("Enter a file path first", severity="warning")
            return
        raw_tags = self.query_one("#tags_input", Input).value
        tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
        genre = self.query_one("#genre_input", Input).value.strip()
        mood = self.query_one("#mood_input", Input).value.strip()
        notes = self.query_one("#notes_area", TextArea).text
        self._save_async(fp, tags, genre, mood, notes)

    def action_back(self) -> None:
        self.app.pop_screen()
