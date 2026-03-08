"""Library Screen for SampleMind TUI v3.0"""

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
)


class LibraryScreen(Screen):
    """Browse the full sample library with filter and search."""

    BINDINGS = [
        Binding("escape", "action_back", "Back"),
        Binding("ctrl+f", "focus_filter", "Filter"),
        Binding("r", "reload_library", "Reload"),
    ]

    DEFAULT_CSS = """
    LibraryScreen { layout: vertical; }
    #library_body { height: 1fr; padding: 1 2; }
    .screen-title { color: $primary; text-style: bold; height: 1; margin-bottom: 1; }
    #filter_row { height: auto; margin-bottom: 1; }
    #filter_row Input { width: 1fr; margin-bottom: 0; }
    #filter_row Button { min-width: 10; margin-left: 1; }
    #lib_table { height: 1fr; }
    #log_area { height: 4; }
    #btn_row { height: 3; margin-top: 1; }
    #btn_row Button { margin-right: 1; }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="library_body"):
            yield Label("Sample Library", classes="screen-title")
            with Horizontal(id="filter_row"):
                yield Input(
                    placeholder="Filter by name, key, BPM, genre...", id="filter_input"
                )
                yield Button("Filter", id="btn_filter", variant="primary")
                yield Button("Reload", id="btn_reload", variant="default")
            yield Label("Loading...", id="count_label")
            yield DataTable(zebra_stripes=True, id="lib_table")
            yield RichLog(highlight=True, id="log_area", wrap=True)
            with Horizontal(id="btn_row"):
                yield Button("Analyze", id="btn_analyze", variant="primary")
                yield Button("Favorite", id="btn_fav", variant="success")
                yield Button("Back", id="btn_back", variant="warning")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#lib_table", DataTable)
        table.add_columns("File", "BPM", "Key", "Genre", "Duration", "Tags")
        self._load_library()

    @on(Input.Submitted, "#filter_input")
    def on_filter_submitted(self, _: Input.Submitted) -> None:
        self._apply_filter()

    @on(Button.Pressed, "#btn_filter")
    def on_filter_btn(self, _: Button.Pressed) -> None:
        self._apply_filter()

    @on(Button.Pressed, "#btn_reload")
    def on_reload(self, _: Button.Pressed) -> None:
        self._load_library()

    @on(Button.Pressed, "#btn_analyze")
    def on_analyze(self, _: Button.Pressed) -> None:
        try:
            table = self.query_one("#lib_table", DataTable)
            row = table.cursor_row
            if row is not None:
                _fp = str(table.get_cell_at(Coordinate(row, 0)))
                from .analyze_screen import AnalyzeScreen

                self.app.push_screen(AnalyzeScreen())
        except Exception as exc:
            self.notify(f"Cannot open: {exc}", severity="warning")

    @on(Button.Pressed, "#btn_fav")
    def on_fav(self, _: Button.Pressed) -> None:
        try:
            table = self.query_one("#lib_table", DataTable)
            row = table.cursor_row
            if row is not None:
                fp = str(table.get_cell_at(Coordinate(row, 0)))
                import asyncio

                from samplemind.services.favorites_service import (  # type: ignore[import]
                    get_favorites_manager,
                )

                mgr = get_favorites_manager()
                asyncio.get_event_loop().run_until_complete(mgr.add(fp))
                self.notify("Added to favorites")
        except Exception as exc:
            self.notify(f"Favorite failed: {exc}", severity="warning")

    @on(Button.Pressed, "#btn_back")
    def on_back(self, _: Button.Pressed) -> None:
        self.app.pop_screen()

    def _apply_filter(self) -> None:
        query = self.query_one("#filter_input", Input).value.strip()
        self._load_library(query)

    @work(thread=True)
    def _load_library(self, query: str = "") -> None:
        import asyncio

        try:
            from samplemind.services.library_service import (  # type: ignore[import]
                get_library_service,
            )

            svc = get_library_service()
            loop = asyncio.new_event_loop()
            items = loop.run_until_complete(svc.list(query=query, limit=500))
            loop.close()
            self.app.call_from_thread(self._populate, items)
        except Exception as exc:
            self.app.call_from_thread(
                self._log, f"[yellow]Library unavailable: {exc}[/]"
            )
            self.app.call_from_thread(
                self.query_one("#count_label", Label).update, "Library not available"
            )

    def _populate(self, items: list) -> None:
        table = self.query_one("#lib_table", DataTable)
        table.clear()
        for item in items:
            fp = getattr(item, "file_path", str(item))
            bpm = getattr(item, "tempo", "-")
            key = getattr(item, "key", "-")
            genre = getattr(item, "genre", "-")
            dur = getattr(item, "duration", "-")
            if isinstance(dur, float):
                dur = f"{dur:.1f}s"
            tags = ", ".join(getattr(item, "tags", []) or [])
            table.add_row(
                str(fp)[:60], str(bpm), str(key), str(genre), str(dur), tags[:30]
            )
        count = len(items)
        self.query_one("#count_label", Label).update(
            f"{count} sample{'s' if count != 1 else ''}"
        )

    def _log(self, msg: str) -> None:
        try:
            self.query_one("#log_area", RichLog).write(msg)
        except Exception:
            pass

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_focus_filter(self) -> None:
        self.query_one("#filter_input", Input).focus()

    def action_reload_library(self) -> None:
        self._load_library()
