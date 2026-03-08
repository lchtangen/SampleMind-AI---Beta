"""Favorites Screen for SampleMind TUI v3.0"""

from __future__ import annotations

from datetime import datetime

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.coordinate import Coordinate
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Label, RichLog


class FavoritesScreen(Screen):
    """Browse and manage favorited audio samples."""

    BINDINGS = [
        Binding("escape", "action_back", "Back"),
        Binding("d", "delete_selected", "Remove"),
        Binding("r", "refresh", "Refresh"),
    ]

    DEFAULT_CSS = """
    FavoritesScreen { layout: vertical; }
    #fav_body { height: 1fr; padding: 1 2; }
    .screen-title { color: $primary; text-style: bold; height: 1; margin-bottom: 1; }
    #table_panel { height: 1fr; }
    #log_area { height: 4; }
    #btn_row { height: 3; margin-top: 1; }
    #btn_row Button { margin-right: 1; }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="fav_body"):
            yield Label("Favorites", classes="screen-title")
            yield Label("0 favorites", id="count_label")
            yield DataTable(zebra_stripes=True, id="fav_table")
            yield RichLog(highlight=True, id="log_area", wrap=True)
            with Horizontal(id="btn_row"):
                yield Button("Analyze", id="btn_analyze", variant="primary")
                yield Button("Remove", id="btn_remove", variant="error")
                yield Button("Refresh", id="btn_refresh", variant="default")
                yield Button("Back", id="btn_back", variant="warning")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#fav_table", DataTable)
        table.add_columns("File", "BPM", "Key", "Genre", "Added")
        self._load_favorites()

    @on(Button.Pressed, "#btn_analyze")
    def on_analyze(self, _: Button.Pressed) -> None:
        try:
            table = self.query_one("#fav_table", DataTable)
            row = table.cursor_row
            if row is not None:
                _fp = table.get_cell_at(Coordinate(row, 0))
                from .analyze_screen import AnalyzeScreen

                scr = AnalyzeScreen()
                self.app.push_screen(scr)
        except Exception as exc:
            self.notify(f"Cannot open file: {exc}", severity="warning")

    @on(Button.Pressed, "#btn_remove")
    def on_remove(self, _: Button.Pressed) -> None:
        self.action_delete_selected()

    @on(Button.Pressed, "#btn_refresh")
    def on_refresh(self, _: Button.Pressed) -> None:
        self._load_favorites()

    @on(Button.Pressed, "#btn_back")
    def on_back(self, _: Button.Pressed) -> None:
        self.app.pop_screen()

    @work(thread=True)
    def _load_favorites(self) -> None:
        import asyncio

        try:
            from samplemind.services.favorites_service import (  # type: ignore[import]
                get_favorites_manager,
            )

            mgr = get_favorites_manager()
            loop = asyncio.new_event_loop()
            favorites = loop.run_until_complete(mgr.list_all())
            loop.close()
            self.app.call_from_thread(self._populate, favorites)
        except Exception as exc:
            self.app.call_from_thread(
                self._log, f"[yellow]Favorites unavailable: {exc}[/]"
            )

    def _populate(self, favorites: list) -> None:
        table = self.query_one("#fav_table", DataTable)
        table.clear()
        for item in favorites:
            fp = getattr(item, "file_path", str(item))
            bpm = getattr(item, "tempo", "-")
            key = getattr(item, "key", "-")
            genre = getattr(item, "genre", "-")
            added = getattr(item, "added_at", "")
            if isinstance(added, datetime):
                added = added.strftime("%Y-%m-%d")
            table.add_row(
                str(fp)[:60], str(bpm), str(key), str(genre), str(added), key=str(fp)
            )
        count = len(favorites)
        self.query_one("#count_label", Label).update(
            f"{count} favorite{'s' if count != 1 else ''}"
        )

    def _log(self, msg: str) -> None:
        try:
            self.query_one("#log_area", RichLog).write(msg)
        except Exception:
            pass

    def action_delete_selected(self) -> None:
        try:
            table = self.query_one("#fav_table", DataTable)
            row = table.cursor_row
            if row is None:
                return
            fp = table.get_cell_at(Coordinate(row, 0))
            from samplemind.services.favorites_service import (  # type: ignore[import]
                get_favorites_manager,
            )

            mgr = get_favorites_manager()
            import asyncio

            asyncio.get_event_loop().run_until_complete(mgr.remove(str(fp)))
            self._load_favorites()
            self.notify("Removed from favorites")
        except Exception as exc:
            self.notify(f"Remove failed: {exc}", severity="error")

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_refresh(self) -> None:
        self._load_favorites()
