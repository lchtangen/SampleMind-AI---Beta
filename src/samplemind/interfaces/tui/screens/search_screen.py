"""
Search Screen for SampleMind TUI
Advanced search with filters, fuzzy matching, and saved searches
"""

import asyncio
from typing import List, Dict, Optional, Any

from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, Input, DataTable
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive

from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from samplemind.interfaces.tui.search import get_search_engine, QueryBuilder
from samplemind.interfaces.tui.widgets.dialogs import ErrorDialog, InfoDialog


class SearchScreen(Screen):
    """Screen for advanced search with filters"""

    DEFAULT_CSS = """
    SearchScreen {
        layout: vertical;
    }

    #search_container {
        width: 1fr;
        height: 1fr;
        padding: 1 2;
    }

    #search_input_area {
        width: 1fr;
        height: auto;
        border: solid $accent;
        padding: 1;
        margin-bottom: 1;
    }

    #filter_suggestions {
        width: 1fr;
        height: auto;
        padding: 1;
        margin-bottom: 1;
    }

    #results_table {
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

    Input {
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        ("escape", "back", "Back"),
        ("enter", "search", "Search"),
    ]

    current_query: reactive[str] = reactive("")
    is_searching: reactive[bool] = reactive(False)

    def __init__(self, initial_query: str = "", sample_data: Optional[List[Dict]] = None):
        """
        Initialize search screen

        Args:
            initial_query: Initial query string
            sample_data: Sample data to search (for demo)
        """
        super().__init__()
        self.current_query = initial_query
        self.search_engine = get_search_engine()
        self.sample_data = sample_data or []
        self.search_results: List[Dict[str, Any]] = []

    def compose(self):
        """Compose the search screen layout"""
        yield Header(show_clock=True)

        with Vertical(id="search_container"):
            yield Static(self._render_title(), id="search_title")

            # Search input
            with Vertical(id="search_input_area"):
                yield Input(
                    placeholder="Search query (e.g., tempo:120-130 key:C mood:dark)",
                    value=self.current_query,
                    id="search_input"
                )

                yield Static(
                    "💡 Tips: Use tempo:120-130, key:C, duration:<5, or text search",
                    id="search_tips"
                )

            # Filter suggestions
            yield Static(self._render_filter_suggestions(), id="filter_suggestions")

            # Results table
            table = DataTable(id="results_table")
            table.add_columns("File", "Tempo", "Key", "Duration", "Match Score")
            yield table

            # Button area
            with Horizontal(id="button_area"):
                yield Button("🔍 Search", id="search_btn", variant="success")
                yield Button("💾 Save", id="save_btn", variant="primary")
                yield Button("⬅️  Back", id="back_btn", variant="warning")

        yield Footer()

    def _render_title(self) -> Panel:
        """Render screen title"""
        title = Text("🔍 Advanced Search", style="bold cyan")
        return Panel(title, border_style="green", padding=(0, 1))

    def _render_filter_suggestions(self) -> Panel:
        """Render filter suggestions"""
        suggestions = """
Available Filters:
  • tempo:MIN-MAX    (e.g., tempo:120-130)
  • key:NOTE          (e.g., key:C, key:D♯)
  • duration:MIN-MAX  (e.g., duration:3-5)
  • mood:MOOD        (e.g., mood:dark)
  • energy:LEVEL     (e.g., energy:high)

Examples:
  tempo:100-120 AND key:C
  mood:dark mood:aggressive
  duration:<5 energy:high
"""
        return Panel(suggestions, border_style="blue", padding=(0, 1))

    def on_mount(self) -> None:
        """Initialize the search screen"""
        self.title = "SampleMind - Search"
        # Focus on search input
        self.query_one("#search_input", Input).focus()

        # Perform initial search if query provided
        if self.current_query:
            asyncio.create_task(self._perform_search())

    def on_button_pressed(self, event) -> None:
        """Handle button presses"""
        button_id = event.button.id

        if button_id == "back_btn":
            self.action_back()
        elif button_id == "search_btn":
            asyncio.create_task(self._perform_search())
        elif button_id == "save_btn":
            asyncio.create_task(self._save_search())

    async def _perform_search(self) -> None:
        """Perform search with current query"""
        try:
            self.is_searching = True

            # Get query from input
            search_input = self.query_one("#search_input", Input)
            query = search_input.value.strip()

            if not query:
                self.notify("Please enter a search query", severity="warning")
                return

            self.current_query = query

            # Perform search
            results = self.search_engine.search(
                self.sample_data,
                query,
                fuzzy=False,
                threshold=0.8
            )

            # Update results table
            table = self.query_one("#results_table", DataTable)
            table.clear()

            for result in results[:50]:  # Limit to 50 results
                file_name = result.get("file_name", "Unknown")
                tempo = f"{result.get('tempo', 0):.0f}"
                key = result.get("key", "?")
                duration = f"{result.get('duration', 0):.1f}s"
                match_score = "100%"

                table.add_row(file_name, tempo, key, duration, match_score)

            count = len(results)
            self.notify(
                f"✅ Found {count} results",
                severity="information"
            )

        except Exception as e:
            self.app.push_screen(
                ErrorDialog("Search Error", f"Failed to search: {e}")
            )
        finally:
            self.is_searching = False

    async def _save_search(self) -> None:
        """Save current search"""
        try:
            if not self.current_query:
                self.notify("No search query to save", severity="warning")
                return

            # In a real implementation, would show a dialog for search name
            search_name = f"search_{len(self.search_engine.saved_searches) + 1}"
            self.search_engine.save_search(search_name, self.current_query)

            self.notify(
                f"✅ Search saved as '{search_name}'",
                severity="information"
            )

        except Exception as e:
            self.app.push_screen(
                ErrorDialog("Save Error", f"Failed to save search: {e}")
            )

    def action_back(self) -> None:
        """Go back to previous screen"""
        self.app.pop_screen()

    def action_search(self) -> None:
        """Keyboard shortcut to search"""
        asyncio.create_task(self._perform_search())
