"""
Error Handling and Dialog Widgets for SampleMind TUI

Provides modal dialogs for user notifications:
- ErrorDialog: Display error messages with OK button
- InfoDialog: Display informational messages
- ConfirmDialog: Get user confirmation (Yes/No)
- LoadingDialog: Show loading/processing state
"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Label, Button, Static
from rich.panel import Panel
from rich.text import Text


class ErrorDialog(ModalScreen):
    """Modal dialog for displaying error messages."""

    BINDINGS = [("escape", "cancel")]

    CSS = """
    ErrorDialog {
        align: center middle;
    }

    #error_dialog {
        width: 60;
        height: auto;
        background: $surface;
        border: solid $error;
    }

    #error_title {
        width: 1fr;
        height: auto;
        content-align: center middle;
        background: $error;
        color: $text;
        padding: 1 2;
        text-style: bold;
    }

    #error_content {
        width: 1fr;
        height: auto;
        padding: 2;
    }

    #error_buttons {
        width: 1fr;
        height: auto;
        align: center middle;
        padding: 1 2;
    }

    Button {
        margin: 0 1;
    }
    """

    def __init__(self, title: str, message: str) -> None:
        """Initialize error dialog.

        Args:
            title: Error title/heading
            message: Error message body
        """
        super().__init__()
        self.title_text = title
        self.message_text = message

    def compose(self) -> ComposeResult:
        """Compose error dialog layout."""
        with Vertical(id="error_dialog"):
            yield Label(f"❌ {self.title_text}", id="error_title")

            with Container(id="error_content"):
                yield Label(self.message_text)

            with Horizontal(id="error_buttons"):
                yield Button("OK", variant="error", id="error_ok")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "error_ok":
            self.app.pop_screen()

    def action_cancel(self) -> None:
        """Close dialog on escape."""
        self.app.pop_screen()


class InfoDialog(ModalScreen):
    """Modal dialog for displaying informational messages."""

    BINDINGS = [("escape", "cancel")]

    CSS = """
    InfoDialog {
        align: center middle;
    }

    #info_dialog {
        width: 60;
        height: auto;
        background: $surface;
        border: solid $accent;
    }

    #info_title {
        width: 1fr;
        height: auto;
        content-align: center middle;
        background: $accent;
        color: $text;
        padding: 1 2;
        text-style: bold;
    }

    #info_content {
        width: 1fr;
        height: auto;
        padding: 2;
    }

    #info_buttons {
        width: 1fr;
        height: auto;
        align: center middle;
        padding: 1 2;
    }

    Button {
        margin: 0 1;
    }
    """

    def __init__(self, title: str, message: str) -> None:
        """Initialize info dialog.

        Args:
            title: Info title/heading
            message: Info message body
        """
        super().__init__()
        self.title_text = title
        self.message_text = message

    def compose(self) -> ComposeResult:
        """Compose info dialog layout."""
        with Vertical(id="info_dialog"):
            yield Label(f"ℹ️  {self.title_text}", id="info_title")

            with Container(id="info_content"):
                yield Label(self.message_text)

            with Horizontal(id="info_buttons"):
                yield Button("OK", variant="primary", id="info_ok")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "info_ok":
            self.app.pop_screen()

    def action_cancel(self) -> None:
        """Close dialog on escape."""
        self.app.pop_screen()


class ConfirmDialog(ModalScreen):
    """Modal dialog for getting user confirmation (Yes/No)."""

    BINDINGS = [("escape", "cancel")]

    CSS = """
    ConfirmDialog {
        align: center middle;
    }

    #confirm_dialog {
        width: 60;
        height: auto;
        background: $surface;
        border: solid $warning;
    }

    #confirm_title {
        width: 1fr;
        height: auto;
        content-align: center middle;
        background: $warning;
        color: $text;
        padding: 1 2;
        text-style: bold;
    }

    #confirm_content {
        width: 1fr;
        height: auto;
        padding: 2;
    }

    #confirm_buttons {
        width: 1fr;
        height: auto;
        align: center middle;
        padding: 1 2;
    }

    Button {
        margin: 0 1;
    }
    """

    def __init__(self, title: str, message: str) -> None:
        """Initialize confirmation dialog.

        Args:
            title: Confirmation title/heading
            message: Confirmation message body
        """
        super().__init__()
        self.title_text = title
        self.message_text = message
        self.result = False

    def compose(self) -> ComposeResult:
        """Compose confirmation dialog layout."""
        with Vertical(id="confirm_dialog"):
            yield Label(f"❓ {self.title_text}", id="confirm_title")

            with Container(id="confirm_content"):
                yield Label(self.message_text)

            with Horizontal(id="confirm_buttons"):
                yield Button("Yes", variant="success", id="confirm_yes")
                yield Button("No", variant="error", id="confirm_no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "confirm_yes":
            self.result = True
            self.app.pop_screen()
        elif event.button.id == "confirm_no":
            self.result = False
            self.app.pop_screen()

    def action_cancel(self) -> None:
        """Close dialog on escape (default to No)."""
        self.result = False
        self.app.pop_screen()


class LoadingDialog(ModalScreen):
    """Modal dialog for displaying loading/processing state."""

    CSS = """
    LoadingDialog {
        align: center middle;
    }

    #loading_dialog {
        width: 50;
        height: auto;
        background: $surface;
        border: solid $accent;
    }

    #loading_content {
        width: 1fr;
        height: auto;
        padding: 2;
        content-align: center middle;
    }

    .spinner {
        text-align: center;
    }
    """

    def __init__(self, message: str = "Processing...") -> None:
        """Initialize loading dialog.

        Args:
            message: Message to display while loading
        """
        super().__init__()
        self.message_text = message

    def compose(self) -> ComposeResult:
        """Compose loading dialog layout."""
        with Vertical(id="loading_dialog"):
            with Container(id="loading_content"):
                yield Label(
                    "⏳ " + self.message_text,
                    classes="spinner"
                )

    def update_message(self, message: str) -> None:
        """Update the loading message.

        Args:
            message: New message to display
        """
        label = self.query_one(Label)
        label.update("⏳ " + message)


class WarningDialog(ModalScreen):
    """Modal dialog for displaying warning messages."""

    BINDINGS = [("escape", "cancel")]

    CSS = """
    WarningDialog {
        align: center middle;
    }

    #warning_dialog {
        width: 60;
        height: auto;
        background: $surface;
        border: solid $warning;
    }

    #warning_title {
        width: 1fr;
        height: auto;
        content-align: center middle;
        background: $warning;
        color: $text;
        padding: 1 2;
        text-style: bold;
    }

    #warning_content {
        width: 1fr;
        height: auto;
        padding: 2;
    }

    #warning_buttons {
        width: 1fr;
        height: auto;
        align: center middle;
        padding: 1 2;
    }

    Button {
        margin: 0 1;
    }
    """

    def __init__(self, title: str, message: str) -> None:
        """Initialize warning dialog.

        Args:
            title: Warning title/heading
            message: Warning message body
        """
        super().__init__()
        self.title_text = title
        self.message_text = message

    def compose(self) -> ComposeResult:
        """Compose warning dialog layout."""
        with Vertical(id="warning_dialog"):
            yield Label(f"⚠️  {self.title_text}", id="warning_title")

            with Container(id="warning_content"):
                yield Label(self.message_text)

            with Horizontal(id="warning_buttons"):
                yield Button("OK", variant="warning", id="warning_ok")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "warning_ok":
            self.app.pop_screen()

    def action_cancel(self) -> None:
        """Close dialog on escape."""
        self.app.pop_screen()
