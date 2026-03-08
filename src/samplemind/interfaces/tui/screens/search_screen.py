"""Search Screen for SampleMind TUI v3.0"""

from __future__ import annotations

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.coordinate import Coordinate
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    RichLog,
    Select,
)

_SEARCH_TYPES = [
    ("semantic", "Semantic (AI similarity)"),
    ("bpm", "By BPM range"),
    ("key", "By Key"),
    ("genre", "By Genre"),
    ("filename", "Filename"),
]


class SearchScreen(Screen):
    """Vector + metadata based search across the sample library."""

    BINDINGS = [
        Binding("escape", "action_back", "Back"),
        Binding("ctrl+f", "focus_search", "Focus"),
    ]

    DEFAULT_CSS = """
    SearchScreen { layout: vertical; }
    #search_body { height: 1fr; padding: 1 2; }
    .screen-title { color: $primary; text-style: bold; height: 1; margin-bottom: 1; }
    #search_row { height: auto; margin-bottom: 1; }
    #search_row Input { width: 1fr; }
    #search_row Button { min-width: 12; margin-left: 1; }
    #results_table { height: 1fr; }
    #status_log { height: 4; }
    #btn_row { height: 3; margin-top: 1; }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="search_body"):
            yield Label("Search Sample Library", classes="screen-title")
            with Horizontal(id="search_row"):
                yield Input(placeholder="Search query...", id="search_input")
                yield Select(
                    [(lbl, v) for v, lbl in _SEARCH_TYPES],
                    id="search_type",
                    value="semantic",
                )
                yield Button("Search", id="btn_search", variant="primary")
            yield Label("0 results", id="result_count")
            yield DataTable(zebra_stripes=True, id="results_table")
            yield RichLog(highlight=True, id="status_log", wrap=True)
            with Horizontal(id="btn_row"):
                yield Button("Open", id="btn_open", variant="success")
                yield Button("Back", id="btn_back", variant="warning")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#results_table", DataTable)
        table.add_columns("File", "BPM", "Key", "Genre", "Duration", "Score")
        self.query_one("#search_input", Input).focus()

    @on(Input.Submitted, "#search_input")
    def on_submitted(self, _: Input.Submitted) -> None:
        self._start_search()

    @on(Button.Pressed, "#btn_search")
    def on_search(self, _: Button.Pressed) -> None:
        self._start_search()

    @on(Button.Pressed, "#btn_open")
    def on_open_selected(self, _: Button.Pressed) -> None:
        try:
            row = self.query_one("#results_table", DataTable).cursor_row
            if row is not None:
                _cell = self.query_one("#results_table", DataTable).get_cell_at(
                    Coordinate(row, 0)
                )
                from .analyze_screen import AnalyzeScreen

                scr = AnalyzeScreen()
                self.app.push_screen(scr)
        except Exception as exc:
            self.notify(f"Open failed: {exc}", severity="warning")

    @on(Button.Pressed, "#btn_back")
    def on_back(self, _: Button.Pressed) -> None:
        self.app.pop_screen()

    def _start_search(self) -> None:
        query = self.query_one("#search_input", Input).value.strip()
        if not query:
            self.notify("Enter search query first", severity="warning")
            return
        search_type = str(self.query_one("#search_type", Select).value)
        self._run_search(query, search_type)

    @work(exclusive=True, thread=True)
    def _run_search(self, query: str, search_type: str) -> None:
        import asyncio

        try:
            self.app.call_from_thread(
                self._log, f"[cyan]Searching: {query!r} ({search_type})[/]"
            )
            loop = asyncio.new_event_loop()
            if search_type == "semantic":
                from samplemind.core.database.chroma import get_collection

                collection = get_collection()
                raw = collection.query(query_texts=[query], n_results=20)
                results = [
                    {"file_path": mid, "score": 1 - dist}
                    for mid, dist in zip(
                        (raw["ids"] or [[]])[0],
                        (raw["distances"] or [[]])[0],
                        strict=False,
                    )
                ]
            else:
                from samplemind.services.library_service import (  # type: ignore[import]
                    get_library_service,
                )

                svc = get_library_service()
                results = loop.run_until_complete(
                    svc.search(query=query, search_type=search_type, limit=20)
                )
            loop.close()
            self.app.call_from_thread(self._populate_results, results)
        except Exception as exc:
            self.app.call_from_thread(self._log, f"[red]Search error: {exc}[/]")

    def _populate_results(self, results: list) -> None:
        table = self.query_one("#results_table", DataTable)
        table.clear()
        for r in results:
            fp = getattr(r, "file_path", None) or (
                r.get("file_path") if isinstance(r, dict) else str(r)
            )
            bpm = getattr(r, "tempo", getattr(r, "bpm", "-"))
            key = getattr(r, "key", "-")
            genre = getattr(r, "genre", "-")
            dur = getattr(r, "duration", "-")
            score = getattr(r, "score", getattr(r, "distance", "-"))
            if isinstance(score, float):
                score = f"{score:.3f}"
            table.add_row(
                str(fp or "")[:60], str(bpm), str(key), str(genre), str(dur), str(score)
            )
        count = len(results)
        self.query_one("#result_count", Label).update(
            f"{count} result{'s' if count != 1 else ''}"
        )
        self._log(f"[green]{count} results found[/]")

    def _log(self, msg: str) -> None:
        try:
            self.query_one("#status_log", RichLog).write(msg)
        except Exception:
            pass

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_focus_search(self) -> None:
        self.query_one("#search_input", Input).focus()
