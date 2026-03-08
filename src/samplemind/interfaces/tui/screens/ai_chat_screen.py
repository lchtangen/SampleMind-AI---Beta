"""AI Chat Screen for SampleMind TUI v3.0 — multi-provider conversation"""

from __future__ import annotations

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, RichLog, Select

_MODEL_OPTIONS = [
    ("auto", "Auto (best available)"),
    ("claude-3-7-sonnet-20250219", "Claude 3.7 Sonnet"),
    ("gpt-4o", "GPT-4o"),
    ("gemini-2.0-flash", "Gemini 2.0 Flash"),
    ("qwen2.5:7b-instruct", "Qwen 2.5 7B (Offline)"),
]


class AIChatScreen(Screen):
    """Multi-provider AI chat with streaming responses."""

    BINDINGS = [
        Binding("escape", "action_back", "Back"),
        Binding("ctrl+l", "action_clear", "Clear"),
    ]

    DEFAULT_CSS = """
    AIChatScreen { layout: vertical; }
    #chat_body { height: 1fr; padding: 1 2; layout: vertical; }
    .screen-title { color: $primary; text-style: bold; height: 1; margin-bottom: 1; }
    #model_row { height: auto; margin-bottom: 1; }
    #model_row Label { width: 14; content-align: left middle; }
    #model_row Select { width: 1fr; }
    #chat_log { height: 1fr; border: solid $accent 30%; }
    #input_row { height: auto; margin-top: 1; }
    #input_row Input { width: 1fr; }
    #input_row Button { min-width: 10; margin-left: 1; }
    #btn_row { height: auto; margin-top: 1; }
    #btn_row Button { margin-right: 1; }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="chat_body"):
            yield Label("🤖 AI Chat — SampleMind AI", classes="screen-title")
            with Horizontal(id="model_row"):
                yield Label("AI Model:")
                yield Select(
                    [(label, val) for val, label in _MODEL_OPTIONS],
                    id="sel_model",
                    value="auto",
                )
            yield RichLog(highlight=True, markup=True, id="chat_log", wrap=True)
            with Horizontal(id="input_row"):
                yield Input(
                    placeholder="Ask about music production, samples, mixing…",
                    id="chat_input",
                )
                yield Button("Send", id="btn_send", variant="primary")
            with Horizontal(id="btn_row"):
                yield Button("🗑️  Clear", id="btn_clear")
                yield Button("⬅️  Back", id="btn_back", variant="warning")
        yield Footer()

    def on_mount(self) -> None:
        log = self.query_one("#chat_log", RichLog)
        log.write("[dim]Welcome to SampleMind AI Chat![/]")
        log.write(
            "[dim]Ask anything about music production, sample analysis, mixing, or mastering.[/]"
        )
        log.write("")
        self.query_one("#chat_input", Input).focus()

    @on(Input.Submitted, "#chat_input")
    def on_input_submitted(self, _: Input.Submitted) -> None:
        self._send_message()

    @on(Button.Pressed, "#btn_send")
    def on_send(self, _: Button.Pressed) -> None:
        self._send_message()

    @on(Button.Pressed, "#btn_clear")
    def on_clear_btn(self, _: Button.Pressed) -> None:
        self.action_clear()

    @on(Button.Pressed, "#btn_back")
    def on_back(self, _: Button.Pressed) -> None:
        self.app.pop_screen()

    def _send_message(self) -> None:
        msg = self.query_one("#chat_input", Input).value.strip()
        if not msg:
            return
        self.query_one("#chat_input", Input).clear()
        model_sel = self.query_one("#sel_model", Select)
        model = str(model_sel.value) if model_sel.value != Select.BLANK else "auto"
        log = self.query_one("#chat_log", RichLog)
        log.write(f"[bold cyan]You:[/] {msg}")
        self._run_ai_query(msg, model)

    @work(thread=True)
    def _run_ai_query(self, message: str, model: str) -> None:
        try:
            import asyncio

            from samplemind.integrations.ai_manager import (
                AnalysisType,
                SampleMindAIManager,
            )

            loop = asyncio.new_event_loop()
            mgr = SampleMindAIManager()
            result = loop.run_until_complete(
                mgr.analyze_music(
                    audio_features={"user_message": message},
                    analysis_type=AnalysisType.QUICK_ANALYSIS,
                    user_context={"prompt": message, "model": model},
                )
            )
            loop.close()
            response = (
                result.summary if result and result.summary else "No response from AI."
            )
            self.app.call_from_thread(self._post_response, response)
        except Exception as exc:
            self.app.call_from_thread(
                self._post_response, f"[red]AI unavailable: {exc}[/]"
            )

    def _post_response(self, response: str) -> None:
        log = self.query_one("#chat_log", RichLog)
        log.write(f"[bold green]AI:[/] {response}")
        log.write("")

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_clear(self) -> None:
        self.query_one("#chat_log", RichLog).clear()
