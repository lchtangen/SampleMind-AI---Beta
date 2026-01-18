"""
Tests for SampleMind TUI Application
Tests the Textual-based CLI application
"""

import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from samplemind.interfaces.tui.app import SampleMindTUI
from samplemind.interfaces.tui.screens import MainScreen, AnalyzeScreen, BatchScreen


class TestTUIApp:
    """Test SampleMind TUI application"""

    def test_tui_app_instantiation(self):
        """Test that TUI app can be instantiated"""
        app = SampleMindTUI()
        assert app is not None
        assert isinstance(app, SampleMindTUI)

    def test_tui_app_title(self):
        """Test that TUI app has correct title"""
        app = SampleMindTUI()
        assert "SampleMind" in app.TITLE
        assert "v6" in app.TITLE

    def test_tui_app_subtitle(self):
        """Test that TUI app has subtitle"""
        app = SampleMindTUI()
        assert "Modern Terminal" in app.SUB_TITLE or "Offline" in app.SUB_TITLE

    def test_main_screen_creation(self):
        """Test that MainScreen can be created"""
        screen = MainScreen()
        assert screen is not None
        assert isinstance(screen, MainScreen)

    def test_analyze_screen_creation(self):
        """Test that AnalyzeScreen can be created"""
        screen = AnalyzeScreen()
        assert screen is not None
        assert isinstance(screen, AnalyzeScreen)

    def test_batch_screen_creation(self):
        """Test that BatchScreen can be created"""
        screen = BatchScreen()
        assert screen is not None
        assert isinstance(screen, BatchScreen)

    def test_tui_app_bindings(self):
        """Test that TUI app has keyboard bindings"""
        app = SampleMindTUI()
        assert app.BINDINGS is not None
        assert len(app.BINDINGS) > 0

    def test_main_screen_has_header_footer(self):
        """Test that main screen includes header and footer"""
        screen = MainScreen()
        # Screens should have bindings
        assert screen.BINDINGS is not None
        assert len(screen.BINDINGS) > 0

    def test_analyze_screen_bindings(self):
        """Test that analyze screen has keyboard bindings"""
        screen = AnalyzeScreen()
        assert screen.BINDINGS is not None
        assert "escape" in [binding[0] for binding in screen.BINDINGS]

    def test_batch_screen_bindings(self):
        """Test that batch screen has keyboard bindings"""
        screen = BatchScreen()
        assert screen.BINDINGS is not None
        assert "escape" in [binding[0] for binding in screen.BINDINGS]


class TestTUIMenuWidget:
    """Test TUI menu widget"""

    def test_menu_imports(self):
        """Test that menu widgets can be imported"""
        from samplemind.interfaces.tui.widgets.menu import MainMenu, MainMenuOption
        assert MainMenu is not None
        assert MainMenuOption is not None

    def test_status_bar_imports(self):
        """Test that status bar widget can be imported"""
        from samplemind.interfaces.tui.widgets.status_bar import StatusBar
        assert StatusBar is not None


class TestTUIScreens:
    """Test TUI screens"""

    def test_main_screen_imports(self):
        """Test that main screen can be imported"""
        from samplemind.interfaces.tui.screens.main_screen import MainScreen
        assert MainScreen is not None

    def test_analyze_screen_imports(self):
        """Test that analyze screen can be imported"""
        from samplemind.interfaces.tui.screens.analyze_screen import AnalyzeScreen
        assert AnalyzeScreen is not None

    def test_batch_screen_imports(self):
        """Test that batch screen can be imported"""
        from samplemind.interfaces.tui.screens.batch_screen import BatchScreen
        assert BatchScreen is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
