"""Modal Dialog Widgets for SampleMind TUI — Textual ^0.87"""

from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label, ProgressBar, Static
from textual.containers import Container, Horizontal


class _BaseDialog(ModalScreen[bool]):
    DEFAULT_CSS = """
    _BaseDialog {
        align: center middle;
    }
    _BaseDialog > Container {
        width: 60;
        min-height: 8;
        max-height: 24;
        border: double $primary;
        background: $surface;
        padding: 1 2;
    }
    _BaseDialog #title {
        text-style: bold;
        color: $primary;
        width: 1fr;
        height: auto;
        margin-bottom: 1;
    }
    _BaseDialog #message {
        width: 1fr;
        height: auto;
        margin-bottom: 1;
    }
    _BaseDialog Horizontal {
        height: auto;
        align: center middle;
        margin-top: 1;
    }
    _BaseDialog Button {
        min-width: 10;
        margin: 0 1;
    }
    """

    def __init__(self, title: str, message: str) -> None:
        super().__init__()
        self._title = title
        self._message = message

    @property
    def title_text(self) -> str:
        return self._title

    @property
    def message_text(self) -> str:
        return self._message


class ErrorDialog(_BaseDialog):
    CSS = """
    ErrorDialog > Container {
        border: double $error;
    }
    """
    BINDINGS = [("escape", "cancel")]

    def compose(self) -> ComposeResult:
        with Container():
            yield Label(f"❌  {self._title}", id="title")
            yield Static(self._message, id="message")
            with Horizontal():
                yield Button("Close", id="close_btn", variant="error")

    @on(Button.Pressed, "#close_btn")
    def on_close(self, _: Button.Pressed) -> None:
        self.dismiss(False)

    def action_cancel(self) -> None:
        self.dismiss(False)


class InfoDialog(_BaseDialog):
    CSS = """
    InfoDialog > Container {
        border: double $accent;
    }
    """
    BINDINGS = [("escape", "cancel")]

    def compose(self) -> ComposeResult:
        with Container():
            yield Label(f"ℹ️   {self._title}", id="title")
            yield Static(self._message, id="message")
            with Horizontal():
                yield Button("OK", id="ok_btn", variant="primary")

    @on(Button.Pressed, "#ok_btn")
    def on_ok(self, _: Button.Pressed) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)


class WarningDialog(_BaseDialog):
    CSS = """
    WarningDialog > Container {
        border: double $warning;
    }
    """
    BINDINGS = [("escape", "cancel")]

    def compose(self) -> ComposeResult:
        with Container():
            yield Label(f"⚠️   {self._title}", id="title")
            yield Static(self._message, id="message")
            with Horizontal():
                yield Button("Acknowledge", id="ack_btn", variant="warning")

    @on(Button.Pressed, "#ack_btn")
    def on_ack(self, _: Button.Pressed) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)


class ConfirmDialog(_BaseDialog):
    CSS = """
    ConfirmDialog > Container {
        border: double $warning;
    }
    """
    BINDINGS = [("escape", "cancel")]

    def __init__(self, title: str, message: str) -> None:
        super().__init__(title, message)
        self.result: bool = False

    def compose(self) -> ComposeResult:
        with Container():
            yield Label(f"❓  {self._title}", id="title")
            yield Static(self._message, id="message")
            with Horizontal():
                yield Button("Confirm", id="confirm_btn", variant="success")
                yield Button("Cancel", id="cancel_btn", variant="error")

    @on(Button.Pressed, "#confirm_btn")
    def on_confirm(self, _: Button.Pressed) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#cancel_btn")
    def on_cancel_btn(self, _: Button.Pressed) -> None:
        self.dismiss(False)

    def on_button_pressed(self, event) -> None:
        """Handle button press events (legacy API for test compatibility)."""
        button_id = getattr(getattr(event, "button", None), "id", None)
        if button_id == "confirm_yes":
            self.result = True
        else:
            self.result = False
        self.app.pop_screen()

    def action_cancel(self) -> None:
        self.result = False
        self.app.pop_screen()


class LoadingDialog(ModalScreen[None]):
    CSS = """
    LoadingDialog {
        align: center middle;
    }
    LoadingDialog > Container {
        width: 40;
        height: 7;
        border: double $primary;
        background: $surface;
        padding: 1 2;
        align: center middle;
    }
    LoadingDialog Label { width: 1fr; text-align: center; margin-bottom: 1; }
    LoadingDialog ProgressBar { width: 1fr; }
    """

    def __init__(self, message: str = "Processing...") -> None:
        super().__init__()
        self._message = message

    @property
    def message_text(self) -> str:
        return self._message

    def compose(self) -> ComposeResult:
        with Container():
            yield Label(f"⏳  {self._message}", id="message")
            yield ProgressBar(total=None, show_eta=False)

    def update_message(self, message: str) -> None:
        self._message = message
        try:
            self.query_one("#message", Label).update(f"⏳  {message}")
        except Exception:
            pass


class ProgressDialog(ModalScreen[None]):
    CSS = """
    ProgressDialog {
        align: center middle;
    }
    ProgressDialog > Container {
        width: 52;
        height: 11;
        border: double $primary;
        background: $surface;
        padding: 1 2;
    }
    ProgressDialog #title { text-style: bold; color: $primary; margin-bottom: 1; }
    ProgressDialog #status { height: 1; color: $foreground 70%; margin-bottom: 1; }
    ProgressDialog ProgressBar { width: 1fr; margin-bottom: 1; }
    ProgressDialog Horizontal { height: auto; align: center middle; }
    """

    def __init__(self, title: str, total: int = 100) -> None:
        super().__init__()
        self._title = title
        self._total = total

    def compose(self) -> ComposeResult:
        with Container():
            yield Label(f"⏳  {self._title}", id="title")
            yield Label("", id="status")
            yield ProgressBar(total=self._total, id="progress", show_eta=True)
            with Horizontal():
                yield Button("Cancel", id="cancel_btn", variant="error")

    def advance(self, amount: int = 1, status: str = "") -> None:
        try:
            self.query_one("#progress", ProgressBar).advance(amount)
            if status:
                self.query_one("#status", Label).update(status)
        except Exception:
            pass

    @on(Button.Pressed, "#cancel_btn")
    def on_cancel(self, _: Button.Pressed) -> None:
        self.dismiss(None)
