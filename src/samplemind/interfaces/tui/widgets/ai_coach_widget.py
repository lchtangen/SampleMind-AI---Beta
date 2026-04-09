"""AI Coach Widget — Textual ^0.87 (Collapsible + RichLog + @work)"""

from __future__ import annotations

import logging

from textual import on, work
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Collapsible, Input, RichLog

logger = logging.getLogger(__name__)


class AICoachWidget(Widget):
    """Collapsible AI coaching panel with background queries via @work."""

    DEFAULT_CSS = """
    AICoachWidget {
        height: auto;
        min-height: 4;
    }
    AICoachWidget Collapsible {
        background: $panel;
        border: solid $primary;
        margin: 0;
        padding: 0 1;
    }
    AICoachWidget RichLog {
        height: 8;
        border: none;
        padding: 0 1;
        background: $surface;
    }
    AICoachWidget Input {
        margin-top: 1;
        margin-bottom: 0;
    }
    AICoachWidget Button {
        margin-top: 1;
    }
    """

    is_active: reactive[bool] = reactive(False)

    def compose(self) -> ComposeResult:
        with Collapsible(title="🤖 AI Coach", id="coach_panel", collapsed=True):
            yield RichLog(highlight=True, markup=True, id="coach_log", wrap=True)
            yield Input(placeholder="Ask about this sample...", id="coach_input")
            yield Button("Send", id="send_btn", variant="primary")

    @on(Button.Pressed, "#send_btn")
    async def on_send_pressed(self, event: Button.Pressed) -> None:
        await self._send_message()

    @on(Input.Submitted, "#coach_input")
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        await self._send_message()

    async def _send_message(self) -> None:
        inp = self.query_one("#coach_input", Input)
        message = inp.value.strip()
        if not message:
            return
        log = self.query_one("#coach_log", RichLog)
        log.write(f"[bold cyan]You:[/] {message}")
        inp.value = ""
        self._query_ai(message)

    @work(thread=True)
    def _query_ai(self, message: str) -> None:
        try:
            import asyncio

            from samplemind.integrations.ai_manager import SampleMindAIManager

            loop = asyncio.new_event_loop()
            manager = SampleMindAIManager()
            response = loop.run_until_complete(manager.chat(message))
            loop.close()
            self.app.call_from_thread(self._post_response, str(response))
        except Exception as exc:
            logger.debug("AI coach query failed: %s", exc)
            self.app.call_from_thread(
                self._post_response, f"[red]Error — AI unavailable: {exc}[/]"
            )

    def _post_response(self, text: str) -> None:
        try:
            self.query_one("#coach_log", RichLog).write(f"[bold green]AI:[/] {text}")
        except Exception:
            pass

    def add_tip(self, tip: str) -> None:
        try:
            self.query_one("#coach_log", RichLog).write(
                f"[bold yellow]💡 Tip:[/] {tip}"
            )
        except Exception:
            pass

    def clear_log(self) -> None:
        try:
            self.query_one("#coach_log", RichLog).clear()
        except Exception:
            pass
