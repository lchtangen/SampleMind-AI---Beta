"""Settings Screen for SampleMind TUI v3.0"""

from __future__ import annotations

from textual import on
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
    Select,
    Switch,
    TabbedContent,
    TabPane,
)

_THEMES = [
    ("samplemind_dark", "SampleMind Dark (default)"),
    ("samplemind_light", "SampleMind Light"),
    ("midnight_pro", "Midnight Pro"),
    ("neon_synthwave", "Neon Synthwave"),
    ("forest_green", "Forest Green"),
    ("high_contrast", "High Contrast"),
    ("textual-dark", "Textual Dark"),
    ("textual-light", "Textual Light"),
]

_AI_MODELS = [
    ("auto", "Auto (recommended)"),
    ("claude-3-7-sonnet-20250219", "Claude 3.7 Sonnet"),
    ("gpt-4o", "GPT-4o"),
    ("gemini-2.0-flash-exp", "Gemini 2.0 Flash"),
    ("qwen2.5:7b-instruct", "Qwen 2.5 7B (Ollama / offline)"),
]


class SettingsScreen(Screen):
    """Application settings with tabbed layout."""

    BINDINGS = [
        Binding("escape", "action_back", "Back"),
        Binding("ctrl+s", "save_settings", "Save"),
    ]

    DEFAULT_CSS = """
    SettingsScreen { layout: vertical; }
    #settings_body { height: 1fr; padding: 1 2; }
    .screen-title { color: $primary; text-style: bold; height: 1; margin-bottom: 1; }
    .setting-row { height: auto; margin-bottom: 1; }
    .setting-label { height: 1; content-align: center middle; width: auto; min-width: 20; }
    #btn_row { height: 3; margin-top: 1; }
    #btn_row Button { margin-right: 1; }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="settings_body"):
            yield Label("Settings", classes="screen-title")
            with TabbedContent(initial="tab_theme"):
                with TabPane("Themes", id="tab_theme"):
                    with Horizontal(classes="setting-row"):
                        yield Label("Theme:", classes="setting-label")
                        yield Select(
                            [(lbl, v) for v, lbl in _THEMES],
                            id="sel_theme",
                            value="samplemind_dark",
                        )
                with TabPane("AI", id="tab_ai"):
                    with Horizontal(classes="setting-row"):
                        yield Label("Default model:", classes="setting-label")
                        yield Select(
                            [(lbl, v) for v, lbl in _AI_MODELS],
                            id="sel_model",
                            value="auto",
                        )
                    with Horizontal(classes="setting-row"):
                        yield Label("Anthropic API key:", classes="setting-label")
                        yield Input(
                            password=True, placeholder="sk-ant-...", id="inp_anthropic"
                        )
                    with Horizontal(classes="setting-row"):
                        yield Label("OpenAI API key:", classes="setting-label")
                        yield Input(
                            password=True, placeholder="sk-...", id="inp_openai"
                        )
                    with Horizontal(classes="setting-row"):
                        yield Label("Gemini API key:", classes="setting-label")
                        yield Input(
                            password=True, placeholder="AIza...", id="inp_gemini"
                        )
                with TabPane("Audio", id="tab_audio"):
                    with Horizontal(classes="setting-row"):
                        yield Label("Sample rate:", classes="setting-label")
                        yield Select(
                            [
                                ("22 050 Hz", "22050"),
                                ("44 100 Hz", "44100"),
                                ("48 000 Hz", "48000"),
                            ],
                            id="sel_sr",
                            value="22050",
                        )
                    with Horizontal(classes="setting-row"):
                        yield Label("Preview audio:", classes="setting-label")
                        yield Switch(id="sw_preview", value=True)
                with TabPane("Library", id="tab_library"):
                    with Horizontal(classes="setting-row"):
                        yield Label("Library root:", classes="setting-label")
                        yield Input(placeholder="/path/to/samples", id="inp_library")
                    with Horizontal(classes="setting-row"):
                        yield Label("Auto-scan on start:", classes="setting-label")
                        yield Switch(id="sw_autoscan", value=False)
            with Horizontal(id="btn_row"):
                yield Button("Save", id="btn_save", variant="success")
                yield Button("Reset", id="btn_reset", variant="warning")
                yield Button("Back", id="btn_back", variant="default")
        yield Footer()

    def on_mount(self) -> None:
        self._load_settings()

    def _load_settings(self) -> None:
        try:
            import os

            current_theme = getattr(self.app, "theme", "samplemind_dark")
            self.query_one("#sel_theme", Select).value = str(current_theme)
            for env_key, inp_id in [
                ("ANTHROPIC_API_KEY", "#inp_anthropic"),
                ("OPENAI_API_KEY", "#inp_openai"),
                ("GOOGLE_API_KEY", "#inp_gemini"),
            ]:
                val = os.environ.get(env_key, "")
                if val:
                    inp = self.query_one(inp_id, Input)
                    inp.value = val[:8] + "..." if len(val) > 8 else val
        except Exception:
            pass

    @on(Select.Changed, "#sel_theme")
    def on_theme_changed(self, event: Select.Changed) -> None:
        if event.value and event.value is not Select.BLANK:
            self.app.theme = str(event.value)
            self.notify(f"Theme changed to {event.value}")

    @on(Button.Pressed, "#btn_save")
    def on_save(self, _: Button.Pressed) -> None:
        self.action_save_settings()

    @on(Button.Pressed, "#btn_reset")
    def on_reset(self, _: Button.Pressed) -> None:
        self._load_settings()
        self.notify("Settings reset")

    @on(Button.Pressed, "#btn_back")
    def on_back_btn(self, _: Button.Pressed) -> None:
        self.app.pop_screen()

    def action_save_settings(self) -> None:
        import os

        try:
            for inp_id, env_key in [
                ("#inp_anthropic", "ANTHROPIC_API_KEY"),
                ("#inp_openai", "OPENAI_API_KEY"),
                ("#inp_gemini", "GOOGLE_API_KEY"),
            ]:
                val = self.query_one(inp_id, Input).value.strip()
                if val and not val.endswith("..."):
                    os.environ[env_key] = val
            self.notify("Settings saved", severity="information")
        except Exception as exc:
            self.notify(f"Save error: {exc}", severity="error")

    def action_back(self) -> None:
        self.app.pop_screen()
