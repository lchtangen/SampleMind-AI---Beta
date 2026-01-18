"""
Favorites Screen for SampleMind TUI
Display and manage favorite analyses
"""

import asyncio
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, DataTable
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive

from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from samplemind.interfaces.tui.favorites import get_favorites_manager
from samplemind.interfaces.tui.widgets.dialogs import (
    ErrorDialog,
    InfoDialog,
    WarningDialog,
)


class FavoritesScreen(Screen):
    """Screen for managing favorited analyses"""

    DEFAULT_CSS = """
    FavoritesScreen {
        layout: vertical;
    }

    #favorites_container {
        width: 1fr;
        height: 1fr;
        padding: 1 2;
    }

    #favorites_table {
        width: 1fr;
        height: 1fr;
        border: solid $accent;
        margin-bottom: 1;
    }

    #button_area {
        width: 1fr;
        height: auto;
        margin-top: 1;
    }

    #stats_area {
        width: 1fr;
        height: auto;
        border: solid $success;
        padding: 1;
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        ("escape", "back", "Back"),
        ("d", "delete_favorite", "Delete"),
        ("e", "export_favorites", "Export"),
        ("r", "refresh", "Refresh"),
    ]

    is_loading: reactive[bool] = reactive(False)

    def compose(self):
        """Compose the favorites screen layout"""
        yield Header(show_clock=True)

        with Vertical(id="favorites_container"):
            yield Static(
                self._render_title(),
                id="favorites_title"
            )

            yield Static(
                self._render_stats(),
                id="stats_area"
            )

            # Create DataTable for favorites
            table = DataTable(id="favorites_table")
            table.add_columns("", "File Name", "Analysis ID", "Rating", "Notes", "Added")
            yield table

            with Horizontal(id="button_area"):
                yield Button("🔄 Refresh", id="refresh_btn", variant="primary")
                yield Button("📤 Export", id="export_btn", variant="success")
                yield Button("🗑️  Delete", id="delete_btn", variant="warning")
                yield Button("⬅️  Back", id="back_btn", variant="default")

        yield Footer()

    def _render_title(self) -> Panel:
        """Render screen title"""
        title = Text("⭐ Favorite Analyses", style="bold cyan")
        return Panel(title, border_style="green", padding=(0, 1))

    def _render_stats(self) -> Panel:
        """Render statistics panel"""
        stats_text = "Loading statistics..."
        panel = Panel(stats_text, border_style="blue", padding=(0, 1))
        return panel

    def on_mount(self) -> None:
        """Initialize the favorites screen"""
        self.title = "SampleMind AI - Favorites"
        asyncio.create_task(self._load_favorites())

    async def _load_favorites(self) -> None:
        """Load and display favorites"""
        try:
            self.is_loading = True

            # Get favorites manager
            fav_manager = get_favorites_manager()

            # Load all favorites
            favorites = await fav_manager.get_all_favorites(limit=100)

            if not favorites:
                stats_area = self.query_one("#stats_area")
                stats_area.update(Panel(
                    "No favorites yet. Star your favorite analyses!",
                    border_style="yellow",
                    padding=(0, 1)
                ))
                self.is_loading = False
                return

            # Get statistics
            stats = await fav_manager.get_favorite_stats()

            # Update stats panel
            stats_text = (
                f"Total: {stats['total']} | "
                f"Rated: {stats['rated']} | "
                f"With Notes: {stats['with_notes']} | "
                f"Avg Rating: {stats['average_rating']}⭐"
            )
            stats_area = self.query_one("#stats_area")
            stats_area.update(Panel(stats_text, border_style="blue", padding=(0, 1)))

            # Populate table
            table = self.query_one("#favorites_table", DataTable)

            for idx, favorite in enumerate(favorites, 1):
                # Format rating as stars
                rating = "⭐" * favorite.rating if favorite.rating > 0 else "Unrated"
                notes = favorite.notes or "-"
                added_date = favorite.added_at.strftime("%Y-%m-%d")

                table.add_row(
                    str(idx),
                    favorite.file_name,
                    favorite.analysis_id[:8] + "...",
                    rating,
                    notes if len(notes) < 20 else notes[:17] + "...",
                    added_date,
                    key=favorite.favorite_id
                )

            self.notify(f"✅ Loaded {len(favorites)} favorites", severity="information")

        except Exception as e:
            self.app.push_screen(ErrorDialog("Error", f"Failed to load favorites: {e}"))
        finally:
            self.is_loading = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        if button_id == "back_btn":
            self.action_back()
        elif button_id == "refresh_btn":
            asyncio.create_task(self._refresh_favorites())
        elif button_id == "export_btn":
            asyncio.create_task(self._export_favorites())
        elif button_id == "delete_btn":
            asyncio.create_task(self._delete_selected())

    async def _refresh_favorites(self) -> None:
        """Refresh the favorites list"""
        try:
            table = self.query_one("#favorites_table", DataTable)
            table.clear()
            await self._load_favorites()
            self.notify("✅ Favorites refreshed", severity="information")
        except Exception as e:
            self.app.push_screen(ErrorDialog("Error", f"Failed to refresh: {e}"))

    async def _export_favorites(self) -> None:
        """Export favorites to JSON"""
        try:
            fav_manager = get_favorites_manager()
            export_data = await fav_manager.export_favorites()

            self.notify("📤 Export functionality coming soon!", severity="information")

        except Exception as e:
            self.app.push_screen(ErrorDialog("Error", f"Failed to export: {e}"))

    async def _delete_selected(self) -> None:
        """Delete selected favorite"""
        try:
            table = self.query_one("#favorites_table", DataTable)
            cursor_row = table.cursor_row

            if cursor_row is None:
                self.notify("Please select a favorite to delete", severity="warning")
                return

            # Get the favorite ID from the row key
            row_key = table.get_row_at(cursor_row)[0]
            for row_index in range(table.row_count):
                if table.get_row_at(row_index)[0] == row_key:
                    favorite_id = table.get_row_key(row_index)
                    break

            fav_manager = get_favorites_manager()
            success = await fav_manager.remove_from_favorites(favorite_id)

            if success:
                table.remove_row(table.cursor_row)
                self.notify("✅ Favorite removed", severity="information")
            else:
                self.notify("❌ Failed to remove favorite", severity="error")

        except Exception as e:
            self.app.push_screen(ErrorDialog("Error", f"Failed to delete: {e}"))

    def action_back(self) -> None:
        """Go back to main screen"""
        self.app.pop_screen()

    def action_delete_favorite(self) -> None:
        """Keyboard shortcut to delete favorite"""
        asyncio.create_task(self._delete_selected())

    def action_export_favorites(self) -> None:
        """Keyboard shortcut to export"""
        asyncio.create_task(self._export_favorites())

    def action_refresh(self) -> None:
        """Keyboard shortcut to refresh"""
        asyncio.create_task(self._refresh_favorites())
