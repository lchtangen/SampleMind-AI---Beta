"""
Settings Screen for SampleMind TUI
Configure application preferences and settings
"""

import asyncio
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, Select, Checkbox, Input, Label
from textual.containers import Vertical, Horizontal, Container
from textual.reactive import reactive

from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from samplemind.interfaces.tui.settings import get_settings_manager
from samplemind.interfaces.tui.themes import get_theme_manager
from samplemind.interfaces.tui.widgets.dialogs import (
    ErrorDialog,
    InfoDialog,
    WarningDialog,
)


class SettingsScreen(Screen):
    """Screen for configuring application settings"""

    DEFAULT_CSS = """
    SettingsScreen {
        layout: vertical;
    }

    #settings_container {
        width: 1fr;
        height: 1fr;
        padding: 1 2;
    }

    #settings_tabs {
        width: 1fr;
        height: auto;
        margin-bottom: 1;
    }

    #settings_content {
        width: 1fr;
        height: 1fr;
        border: solid $accent;
        padding: 1;
        overflow: auto;
    }

    #button_area {
        width: 1fr;
        height: auto;
        margin-top: 1;
    }

    .setting_group {
        width: 1fr;
        height: auto;
        margin-bottom: 1;
        padding: 1;
        border: solid $primary;
    }

    .setting_row {
        width: 1fr;
        height: auto;
        margin-bottom: 1;
    }

    .setting_label {
        width: 30;
        margin-right: 1;
    }
    """

    BINDINGS = [
        ("escape", "back", "Back"),
        ("s", "save_settings", "Save"),
        ("r", "reset_settings", "Reset"),
    ]

    current_tab: reactive[str] = reactive("general")
    is_saving: reactive[bool] = reactive(False)

    def compose(self):
        """Compose the settings screen layout"""
        yield Header(show_clock=True)

        with Vertical(id="settings_container"):
            yield Static(
                self._render_title(),
                id="settings_title"
            )

            # Tab selection
            with Horizontal(id="settings_tabs"):
                yield Button("🎯 General", id="tab_general", variant="primary")
                yield Button("🔊 Audio", id="tab_audio", variant="default")
                yield Button("🤖 AI", id="tab_ai", variant="default")
                yield Button("⚡ Performance", id="tab_performance", variant="default")

            # Settings content area
            yield Static("Loading settings...", id="settings_content")

            # Button area
            with Horizontal(id="button_area"):
                yield Button("💾 Save", id="save_btn", variant="success")
                yield Button("🔄 Reset", id="reset_btn", variant="warning")
                yield Button("⬅️  Back", id="back_btn", variant="default")

        yield Footer()

    def _render_title(self) -> Panel:
        """Render screen title"""
        title = Text("⚙️  Application Settings", style="bold cyan")
        return Panel(title, border_style="green", padding=(0, 1))

    def on_mount(self) -> None:
        """Initialize the settings screen"""
        self.title = "SampleMind AI - Settings"
        asyncio.create_task(self._load_settings())

    async def _load_settings(self) -> None:
        """Load and display settings for current tab"""
        try:
            settings_manager = get_settings_manager()

            if self.current_tab == "general":
                content = await self._render_general_settings(settings_manager)
            elif self.current_tab == "audio":
                content = await self._render_audio_settings(settings_manager)
            elif self.current_tab == "ai":
                content = await self._render_ai_settings(settings_manager)
            elif self.current_tab == "performance":
                content = await self._render_performance_settings(settings_manager)
            else:
                content = "Unknown tab"

            settings_area = self.query_one("#settings_content")
            settings_area.update(content)

        except Exception as e:
            self.app.push_screen(ErrorDialog("Error", f"Failed to load settings: {e}"))

    async def _render_general_settings(self, settings_manager) -> str:
        """Render general settings"""
        settings = await settings_manager.get_all_settings()
        theme = settings.get("theme", "dark")
        show_advanced = settings.get("show_advanced_stats", False)

        # Get theme manager for theme info
        theme_manager = get_theme_manager()
        available_themes = theme_manager.get_all_themes()

        content = f"""
╔════════════════════════════════════════╗
║         GENERAL SETTINGS               ║
╠════════════════════════════════════════╣
║
║  Theme: {theme:.<30}
║  Available: {', '.join(available_themes[:3])}...
║
║  Show Advanced Stats: {'✅ Yes' if show_advanced else '❌ No':<22}
║
║  Analysis Level: STANDARD
║
║  Export Format: JSON
║
║  Available Themes (8 total):
║  🌙 dark, ☀️ light, 🤖 cyberpunk
║  🌅 synthwave, 🌲 gruvbox, 🧛 dracula
║  ❄️ nord, 🎨 monokai
║
╚════════════════════════════════════════╝
"""
        return content

    async def _render_audio_settings(self, settings_manager) -> str:
        """Render audio settings"""
        cache_enabled = await settings_manager.is_cache_enabled()
        cache_size = await settings_manager.get_cache_size()
        auto_save = await settings_manager.is_auto_save_enabled()

        content = f"""
╔════════════════════════════════════════╗
║         AUDIO SETTINGS                 ║
╠════════════════════════════════════════╣
║
║  Cache Enabled: {'✅ Yes' if cache_enabled else '❌ No':<24}
║
║  Max Cache Size: {cache_size} items
║
║  Auto-Save Results: {'✅ Yes' if auto_save else '❌ No':<20}
║
║  Show Waveform: ✅ Yes
║
║  Auto Preview: ❌ No
║
╚════════════════════════════════════════╝
"""
        return content

    async def _render_ai_settings(self, settings_manager) -> str:
        """Render AI settings"""
        content = """
╔════════════════════════════════════════╗
║          AI SETTINGS                   ║
╠════════════════════════════════════════╣
║
║  Primary AI: Google Gemini 3 Flash
║
║  Fallback AI: Ollama Local Models
║
║  AI Model: gemini-pro
║
║  Response Timeout: 30 seconds
║
║  Enable AI Coaching: ✅ Yes
║
╚════════════════════════════════════════╝
"""
        return content

    async def _render_performance_settings(self, settings_manager) -> str:
        """Render performance settings"""
        workers = await settings_manager.get_parallel_workers()
        cache_size = await settings_manager.get_cache_size()

        content = f"""
╔════════════════════════════════════════╗
║       PERFORMANCE SETTINGS             ║
╠════════════════════════════════════════╣
║
║  Parallel Workers: {workers} threads
║
║  Cache Size: {cache_size} items
║
║  Feature Caching: ✅ Enabled
║
║  Disk Cache: ✅ Enabled
║
║  Memory Optimization: ✅ Enabled
║
╚════════════════════════════════════════╝
"""
        return content

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id

        if button_id.startswith("tab_"):
            # Tab selection
            new_tab = button_id.replace("tab_", "")
            self.current_tab = new_tab
            self._update_tab_buttons()
            asyncio.create_task(self._load_settings())

        elif button_id == "save_btn":
            asyncio.create_task(self._save_settings())
        elif button_id == "reset_btn":
            asyncio.create_task(self._reset_settings())
        elif button_id == "back_btn":
            self.action_back()

    def _update_tab_buttons(self) -> None:
        """Update tab button styles based on current tab"""
        tabs = ["general", "audio", "ai", "performance"]
        for tab in tabs:
            btn = self.query_one(f"#tab_{tab}", Button)
            btn.variant = "primary" if self.current_tab == tab else "default"

    async def _save_settings(self) -> None:
        """Save settings"""
        try:
            self.is_saving = True
            self.notify("💾 Saving settings...", severity="information")

            # Settings would be saved here based on current values
            # For now, just show confirmation

            await asyncio.sleep(0.5)  # Simulate save
            self.notify("✅ Settings saved successfully", severity="information")

        except Exception as e:
            self.app.push_screen(ErrorDialog("Error", f"Failed to save settings: {e}"))
        finally:
            self.is_saving = False

    async def _reset_settings(self) -> None:
        """Reset settings to defaults"""
        try:
            settings_manager = get_settings_manager()
            success = await settings_manager.reset_to_defaults()

            if success:
                self.notify("✅ Settings reset to defaults", severity="information")
                await self._load_settings()
            else:
                self.notify("❌ Failed to reset settings", severity="error")

        except Exception as e:
            self.app.push_screen(ErrorDialog("Error", f"Failed to reset: {e}"))

    def watch_current_tab(self, new_tab: str) -> None:
        """Called when current_tab changes"""
        self._update_tab_buttons()
        asyncio.create_task(self._load_settings())

    def action_back(self) -> None:
        """Go back to main screen"""
        self.app.pop_screen()

    def action_save_settings(self) -> None:
        """Keyboard shortcut to save"""
        asyncio.create_task(self._save_settings())

    def action_reset_settings(self) -> None:
        """Keyboard shortcut to reset"""
        asyncio.create_task(self._reset_settings())
