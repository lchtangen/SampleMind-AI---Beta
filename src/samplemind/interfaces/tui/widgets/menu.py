"""
Main Menu Widget for SampleMind TUI
Provides a modern interactive menu interface
"""

from textual.widget import Widget
from textual.widgets import Static, ListItem, Label
from textual.containers import Container, Vertical
from textual.message import Message
from rich.text import Text
from rich.panel import Panel
from rich.align import Align


class MainMenuOption(Message):
    """Custom message for menu selection"""

    def __init__(self, option_id: str, option_label: str) -> None:
        super().__init__()
        self.option_id = option_id
        self.option_label = option_label


class MainMenu(Static):
    """Main menu widget with 5 core options"""

    DEFAULT_CSS = """
    MainMenu {
        width: 1fr;
        height: auto;
        padding: 1 2;
    }

    MainMenu > Vertical {
        width: 1fr;
        height: auto;
    }

    MainMenu .menu-option {
        padding: 1 2;
        background: $surface;
    }

    MainMenu .menu-option:hover {
        background: $primary;
        color: $text;
    }

    MainMenu .menu-option.focused {
        background: $accent;
        color: $panel;
    }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.menu_items = [
            ("analyze", "🎯 Analyze Single File"),
            ("batch", "📁 Batch Process Folder"),
            ("scan", "🔍 Scan & Preview"),
            ("settings", "⚙️  Settings"),
            ("analytics", "📊 Session Analytics"),
        ]
        self.selected_index = 0

    def compose(self):
        """Compose the menu layout"""
        with Vertical():
            yield Static(
                self._render_title(),
                id="menu_title"
            )

            # Add menu options
            for idx, (option_id, label) in enumerate(self.menu_items):
                yield Label(
                    label,
                    id=f"menu_{option_id}",
                    classes="menu-option"
                )

    def _render_title(self) -> Panel:
        """Render the menu title"""
        title = Text("🎵 SampleMind AI v6 - Main Menu", style="bold cyan")
        subtitle = Text("Press UP/DOWN to navigate, ENTER to select, Q to quit", style="dim")

        content = Text()
        content.append(title)
        content.append("\n")
        content.append(subtitle)

        return Panel(
            Align.center(content),
            border_style="green",
            padding=(1, 2)
        )
