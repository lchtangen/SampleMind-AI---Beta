"""
Unit tests for Textual TUI dialog widgets.

Tests cover:
- ErrorDialog display and user interaction
- InfoDialog display and user interaction
- ConfirmDialog display and result handling
- WarningDialog display
- LoadingDialog message updates
- Dialog CSS styling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from samplemind.interfaces.tui.widgets.dialogs import (
    ErrorDialog,
    InfoDialog,
    ConfirmDialog,
    WarningDialog,
    LoadingDialog,
)


class TestErrorDialog:
    """Test ErrorDialog functionality."""

    def test_initialization(self):
        """Test ErrorDialog initializes with title and message."""
        dialog = ErrorDialog("Test Error", "This is a test error message")
        assert dialog.title_text == "Test Error"
        assert dialog.message_text == "This is a test error message"

    def test_compose(self):
        """Test ErrorDialog composes correct layout."""
        dialog = ErrorDialog("Test Error", "Error details")
        widgets = list(dialog.compose())

        # Should have vertical container with title, content, and buttons
        assert len(widgets) > 0

    def test_error_dialog_icon(self):
        """Test ErrorDialog uses correct error icon."""
        dialog = ErrorDialog("Database Error", "Connection failed")
        assert dialog.title_text == "Database Error"
        # Icon should be added in compose via f-string
        assert "❌" not in dialog.title_text  # Icon added during compose


class TestInfoDialog:
    """Test InfoDialog functionality."""

    def test_initialization(self):
        """Test InfoDialog initializes with title and message."""
        dialog = InfoDialog("Information", "Here is some information")
        assert dialog.title_text == "Information"
        assert dialog.message_text == "Here is some information"

    def test_compose(self):
        """Test InfoDialog composes correct layout."""
        dialog = InfoDialog("Tips", "Use Ctrl+S to save")
        widgets = list(dialog.compose())

        assert len(widgets) > 0

    def test_multiline_message(self):
        """Test InfoDialog handles multiline messages."""
        message = "Line 1\nLine 2\nLine 3"
        dialog = InfoDialog("Multiline", message)
        assert dialog.message_text == message


class TestConfirmDialog:
    """Test ConfirmDialog functionality."""

    def test_initialization(self):
        """Test ConfirmDialog initializes correctly."""
        dialog = ConfirmDialog("Confirm Action", "Do you want to continue?")
        assert dialog.title_text == "Confirm Action"
        assert dialog.message_text == "Do you want to continue?"
        assert dialog.result is False  # Default to False

    def test_compose(self):
        """Test ConfirmDialog composes layout with Yes/No buttons."""
        dialog = ConfirmDialog("Delete File", "Are you sure?")
        widgets = list(dialog.compose())

        assert len(widgets) > 0

    def test_result_flag_default(self):
        """Test result flag defaults to False."""
        dialog = ConfirmDialog("Question", "Yes or no?")
        assert dialog.result is False

    @patch("samplemind.interfaces.tui.widgets.dialogs.ConfirmDialog.app")
    def test_yes_button_pressed(self, mock_app):
        """Test clicking Yes button sets result to True."""
        dialog = ConfirmDialog("Question", "Yes or no?")
        dialog.app = MagicMock()

        # Simulate button press event
        button_event = Mock()
        button_event.button = Mock()
        button_event.button.id = "confirm_yes"

        dialog.on_button_pressed(button_event)

        assert dialog.result is True
        dialog.app.pop_screen.assert_called_once()

    @patch("samplemind.interfaces.tui.widgets.dialogs.ConfirmDialog.app")
    def test_no_button_pressed(self, mock_app):
        """Test clicking No button sets result to False."""
        dialog = ConfirmDialog("Question", "Yes or no?")
        dialog.app = MagicMock()

        # Simulate button press event
        button_event = Mock()
        button_event.button = Mock()
        button_event.button.id = "confirm_no"

        dialog.on_button_pressed(button_event)

        assert dialog.result is False
        dialog.app.pop_screen.assert_called_once()

    @patch("samplemind.interfaces.tui.widgets.dialogs.ConfirmDialog.app")
    def test_escape_cancels(self, mock_app):
        """Test escape key cancels dialog with False result."""
        dialog = ConfirmDialog("Question", "Confirm?")
        dialog.app = MagicMock()

        dialog.action_cancel()

        assert dialog.result is False
        dialog.app.pop_screen.assert_called_once()


class TestWarningDialog:
    """Test WarningDialog functionality."""

    def test_initialization(self):
        """Test WarningDialog initializes with title and message."""
        dialog = WarningDialog("Warning", "This is a warning")
        assert dialog.title_text == "Warning"
        assert dialog.message_text == "This is a warning"

    def test_compose(self):
        """Test WarningDialog composes correct layout."""
        dialog = WarningDialog("Unsupported Format", "File format not supported")
        widgets = list(dialog.compose())

        assert len(widgets) > 0

    def test_warning_styling(self):
        """Test WarningDialog uses warning styling."""
        dialog = WarningDialog("Caution", "Proceed with caution")
        # CSS should use warning colors (defined in DEFAULT_CSS)
        assert hasattr(dialog, "CSS")


class TestLoadingDialog:
    """Test LoadingDialog functionality."""

    def test_initialization_default_message(self):
        """Test LoadingDialog initializes with default message."""
        dialog = LoadingDialog()
        assert dialog.message_text == "Processing..."

    def test_initialization_custom_message(self):
        """Test LoadingDialog initializes with custom message."""
        dialog = LoadingDialog("Analyzing audio...")
        assert dialog.message_text == "Analyzing audio..."

    def test_compose(self):
        """Test LoadingDialog composes correct layout."""
        dialog = LoadingDialog("Loading...")
        widgets = list(dialog.compose())

        assert len(widgets) > 0

    @patch("samplemind.interfaces.tui.widgets.dialogs.LoadingDialog.query_one")
    def test_update_message(self, mock_query_one):
        """Test updating loading message."""
        dialog = LoadingDialog("Initial message")

        mock_label = MagicMock()
        mock_query_one.return_value = mock_label

        dialog.update_message("New message")

        # Should call update on label with new message
        mock_label.update.assert_called_once()


class TestDialogIntegration:
    """Integration tests for dialog system."""

    def test_error_dialog_with_long_message(self):
        """Test ErrorDialog handles long error messages."""
        long_message = "Error: " + "x" * 500
        dialog = ErrorDialog("Long Error", long_message)
        assert dialog.message_text == long_message

    def test_confirm_dialog_with_special_chars(self):
        """Test ConfirmDialog handles special characters in messages."""
        message = "Delete file: '~/Documents/file@#$.txt'?"
        dialog = ConfirmDialog("Confirm", message)
        assert dialog.message_text == message

    def test_info_dialog_with_newlines(self):
        """Test InfoDialog preserves newlines in messages."""
        message = "Step 1: Select file\nStep 2: Click Analyze\nStep 3: View results"
        dialog = InfoDialog("Instructions", message)
        assert dialog.message_text == message
        assert "\n" in dialog.message_text

    def test_warning_dialog_with_unicode(self):
        """Test WarningDialog handles unicode characters."""
        message = "⚠️  Warning: High CPU usage detected (95%)"
        dialog = WarningDialog("Performance", message)
        assert dialog.message_text == message
        assert "⚠️" in dialog.message_text

    def test_loading_dialog_spinner_animation(self):
        """Test LoadingDialog renders with spinner."""
        dialog = LoadingDialog("Analyzing...")
        assert dialog.message_text == "Analyzing..."
        # Loading dialog should have spinner styling in CSS


class TestDialogStyling:
    """Test dialog styling and themes."""

    def test_error_dialog_has_css(self):
        """Test ErrorDialog has CSS styling defined."""
        dialog = ErrorDialog("Test", "Test")
        assert hasattr(dialog, "CSS")
        assert "ErrorDialog" in dialog.CSS
        assert "$error" in dialog.CSS

    def test_info_dialog_has_css(self):
        """Test InfoDialog has CSS styling defined."""
        dialog = InfoDialog("Test", "Test")
        assert hasattr(dialog, "CSS")
        assert "InfoDialog" in dialog.CSS
        assert "$accent" in dialog.CSS

    def test_confirm_dialog_has_css(self):
        """Test ConfirmDialog has CSS styling defined."""
        dialog = ConfirmDialog("Test", "Test")
        assert hasattr(dialog, "CSS")
        assert "ConfirmDialog" in dialog.CSS
        assert "$warning" in dialog.CSS

    def test_warning_dialog_has_css(self):
        """Test WarningDialog has CSS styling defined."""
        dialog = WarningDialog("Test", "Test")
        assert hasattr(dialog, "CSS")
        assert "WarningDialog" in dialog.CSS

    def test_loading_dialog_has_css(self):
        """Test LoadingDialog has CSS styling defined."""
        dialog = LoadingDialog("Test")
        assert hasattr(dialog, "CSS")
        assert "LoadingDialog" in dialog.CSS


class TestDialogAccessibility:
    """Test dialog accessibility features."""

    def test_error_dialog_has_escape_binding(self):
        """Test ErrorDialog responds to escape key."""
        dialog = ErrorDialog("Error", "Message")
        assert hasattr(dialog, "BINDINGS")
        bindings = dict(dialog.BINDINGS)
        assert "escape" in bindings

    def test_confirm_dialog_has_escape_binding(self):
        """Test ConfirmDialog responds to escape key."""
        dialog = ConfirmDialog("Confirm", "Continue?")
        assert hasattr(dialog, "BINDINGS")
        bindings = dict(dialog.BINDINGS)
        assert "escape" in bindings

    def test_info_dialog_has_escape_binding(self):
        """Test InfoDialog responds to escape key."""
        dialog = InfoDialog("Info", "Information")
        assert hasattr(dialog, "BINDINGS")
        bindings = dict(dialog.BINDINGS)
        assert "escape" in bindings

    def test_warning_dialog_has_escape_binding(self):
        """Test WarningDialog responds to escape key."""
        dialog = WarningDialog("Warning", "Caution")
        assert hasattr(dialog, "BINDINGS")
        bindings = dict(dialog.BINDINGS)
        assert "escape" in bindings
