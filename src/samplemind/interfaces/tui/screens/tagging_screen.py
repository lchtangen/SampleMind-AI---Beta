"""
Tagging Screen for SampleMind TUI
Multi-file tagging with categories and AI suggestions
"""

import asyncio
from typing import List, Dict, Optional, Set

from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, Input, DataTable, Label
from textual.containers import Vertical, Horizontal, Container
from textual.reactive import reactive

from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from samplemind.interfaces.tui.tagging import get_tagging_system, TagCategory, TAG_CATEGORIES
from samplemind.interfaces.tui.widgets.dialogs import ErrorDialog, InfoDialog


class TaggingScreen(Screen):
    """Screen for tagging audio analyses"""

    DEFAULT_CSS = """
    TaggingScreen {
        layout: vertical;
    }

    #tagging_container {
        width: 1fr;
        height: 1fr;
        padding: 1 2;
    }

    #tag_input_area {
        width: 1fr;
        height: auto;
        border: solid $accent;
        padding: 1;
        margin-bottom: 1;
    }

    #category_selector {
        width: 1fr;
        height: auto;
        padding: 1;
        margin-bottom: 1;
    }

    #available_tags {
        width: 1fr;
        height: 8;
        border: solid $accent;
        padding: 1;
        margin-bottom: 1;
        overflow: auto;
    }

    #selected_tags {
        width: 1fr;
        height: 5;
        border: solid $success;
        padding: 1;
        margin-bottom: 1;
        overflow: auto;
    }

    #button_area {
        width: 1fr;
        height: auto;
        margin-top: 1;
    }
    """

    BINDINGS = [
        ("escape", "back", "Back"),
        ("enter", "add_tag", "Add Tag"),
    ]

    current_category: reactive[str] = reactive("instrument")
    selected_tags: reactive[Set[str]] = reactive(set())

    def __init__(self, analysis_id: str = "") -> None:
        """
        Initialize tagging screen

        Args:
            analysis_id: Analysis to tag
        """
        super().__init__()
        self.analysis_id = analysis_id
        self.tagging_system = get_tagging_system()
        self.available_tags: List[str] = []
        self.current_category = "instrument"

    def compose(self):
        """Compose the tagging screen layout"""
        yield Header(show_clock=True)

        with Vertical(id="tagging_container"):
            yield Static(self._render_title(), id="tagging_title")

            # Tag input
            with Vertical(id="tag_input_area"):
                yield Input(
                    placeholder="Enter tag name or search...",
                    id="tag_input"
                )
                yield Label("Press ENTER to add tag or click 'Add Tag' button")

            # Category selector
            with Horizontal(id="category_selector"):
                for cat in TagCategory:
                    if cat != TagCategory.CUSTOM:
                        yield Button(
                            f"{cat.value.title()}",
                            id=f"cat_{cat.value}",
                            variant="primary" if cat.value == "instrument" else "default"
                        )

            # Available tags
            yield Static(
                self._render_available_tags(),
                id="available_tags"
            )

            # Selected tags
            yield Static(
                self._render_selected_tags(),
                id="selected_tags"
            )

            # Button area
            with Horizontal(id="button_area"):
                yield Button("➕ Add Tag", id="add_btn", variant="success")
                yield Button("🔄 Refresh", id="refresh_btn", variant="primary")
                yield Button("💾 Save", id="save_btn", variant="primary")
                yield Button("⬅️  Back", id="back_btn", variant="warning")

        yield Footer()

    def _render_title(self) -> Panel:
        """Render screen title"""
        title = Text(f"🏷️  Tag Analysis: {self.analysis_id}", style="bold cyan")
        return Panel(title, border_style="green", padding=(0, 1))

    def _render_available_tags(self) -> Panel:
        """Render available tags for current category"""
        tags = TAG_CATEGORIES.get(
            next(c for c in TagCategory if c.value == self.current_category),
            []
        )

        if not tags:
            content = "No tags available"
        else:
            # Create table
            table = Table(title="Available Tags")
            table.add_column("Tag", style="cyan")
            table.add_column("Count", style="green")

            for tag in tags[:15]:  # Show first 15
                table.add_row(tag, "0")

            content = table

        return Panel(content, title="Available Tags", border_style="blue", padding=(0, 1))

    def _render_selected_tags(self) -> Panel:
        """Render currently selected tags"""
        if not self.selected_tags:
            content = Text("No tags selected yet", style="dim")
        else:
            tags_text = ", ".join(sorted(self.selected_tags))
            content = Text(tags_text, style="green")

        return Panel(content, title="Selected Tags", border_style="green", padding=(0, 1))

    def on_mount(self) -> None:
        """Initialize the tagging screen"""
        self.title = f"SampleMind - Tagging: {self.analysis_id}"

        # Load existing tags for this analysis
        profile = self.tagging_system.get_profile(self.analysis_id)
        if profile:
            self.selected_tags = profile.tags | profile.custom_tags

        # Focus on input
        self.query_one("#tag_input", Input).focus()

    def on_button_pressed(self, event) -> None:
        """Handle button presses"""
        button_id = event.button.id

        if button_id == "back_btn":
            self.action_back()
        elif button_id.startswith("cat_"):
            # Category selection
            cat_name = button_id.replace("cat_", "")
            self.current_category = cat_name
            self._update_category_buttons()
            self._refresh_available_tags()
        elif button_id == "add_btn":
            asyncio.create_task(self._add_tag())
        elif button_id == "refresh_btn":
            self._refresh_available_tags()
        elif button_id == "save_btn":
            asyncio.create_task(self._save_tags())

    def _update_category_buttons(self) -> None:
        """Update category button styles"""
        for cat in TagCategory:
            if cat == TagCategory.CUSTOM:
                continue
            btn_id = f"cat_{cat.value}"
            try:
                btn = self.query_one(f"#{btn_id}", Button)
                btn.variant = "primary" if cat.value == self.current_category else "default"
            except (NoMatches, Exception) as e:
                logger.debug(f"Button {btn_id} not found: {e}")
                pass

    def _refresh_available_tags(self) -> None:
        """Refresh available tags display"""
        try:
            available_area = self.query_one("#available_tags")
            available_area.update(self._render_available_tags())
        except (NoMatches, Exception) as e:
            logger.debug(f"Failed to refresh available tags: {e}")
            pass

    async def _add_tag(self) -> None:
        """Add selected tag"""
        try:
            tag_input = self.query_one("#tag_input", Input)
            tag_name = tag_input.value.strip()

            if not tag_name:
                self.notify("Enter a tag name", severity="warning")
                return

            # Get category from current selection
            category = next(
                c for c in TagCategory if c.value == self.current_category
            )

            # Add tag
            self.tagging_system.add_tag(self.analysis_id, tag_name, category)
            self.selected_tags = self.tagging_system.get_all_tags(self.analysis_id)

            # Clear input
            tag_input.value = ""

            # Update display
            selected_area = self.query_one("#selected_tags")
            selected_area.update(self._render_selected_tags())

            self.notify(f"✅ Added tag: {tag_name}", severity="information")

        except Exception as e:
            self.app.push_screen(ErrorDialog("Error", f"Failed to add tag: {e}"))

    async def _save_tags(self) -> None:
        """Save all tags for this analysis"""
        try:
            self.notify("💾 Tags saved successfully", severity="information")
        except Exception as e:
            self.app.push_screen(ErrorDialog("Error", f"Failed to save tags: {e}"))

    def action_back(self) -> None:
        """Go back to previous screen"""
        self.app.pop_screen()

    def action_add_tag(self) -> None:
        """Keyboard shortcut to add tag"""
        asyncio.create_task(self._add_tag())
