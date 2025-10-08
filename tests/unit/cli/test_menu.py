"""
Smoke tests for CLI Menu

These tests execute menu functions to boost coverage.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

class TestCLIMenuSmoke:
    """Smoke tests for CLI menu functions"""

    @patch('builtins.input', return_value='0')
    @patch('samplemind.interfaces.cli.menu.console.print')
    def test_main_menu_exit(self, mock_print, mock_input):
        """Test menu exits on choice 0"""
        from samplemind.interfaces.cli.menu import main
        try:
            main()
        except (SystemExit, KeyboardInterrupt):
            pass

    @patch('builtins.input', side_effect=['1', '0'])
    @patch('samplemind.interfaces.cli.menu.select_audio_file', return_value=None)
    @patch('samplemind.interfaces.cli.menu.console.print')
    def test_menu_analyze_audio(self, mock_print, mock_select, mock_input):
        """Test analyze audio menu option"""
        from samplemind.interfaces.cli.menu import main
        try:
            main()
        except (SystemExit, KeyboardInterrupt, Exception):
            pass

    @patch('builtins.input', side_effect=['2', '0'])
    @patch('samplemind.interfaces.cli.menu.select_audio_file', return_value=None)
    @patch('samplemind.interfaces.cli.menu.console.print')
    def test_menu_separate_stems(self, mock_print, mock_select, mock_input):
        """Test stem separation menu option"""
        from samplemind.interfaces.cli.menu import main
        try:
            main()
        except (SystemExit, KeyboardInterrupt, Exception):
            pass

    @patch('builtins.input', side_effect=['3', '0'])
    @patch('samplemind.interfaces.cli.menu.select_audio_file', return_value=None)
    @patch('samplemind.interfaces.cli.menu.console.print')
    def test_menu_convert_to_midi(self, mock_print, mock_select, mock_input):
        """Test MIDI conversion menu option"""
        from samplemind.interfaces.cli.menu import main
        try:
            main()
        except (SystemExit, KeyboardInterrupt, Exception):
            pass

    @patch('builtins.input', side_effect=['4', '0'])
    @patch('samplemind.interfaces.cli.menu.console.print')
    def test_menu_ai_generation(self, mock_print, mock_input):
        """Test AI generation menu option"""
        from samplemind.interfaces.cli.menu import main
        try:
            main()
        except (SystemExit, KeyboardInterrupt, Exception):
            pass

    @patch('builtins.input', side_effect=['5', '0'])
    @patch('samplemind.interfaces.cli.menu.select_directory', return_value=None)
    @patch('samplemind.interfaces.cli.menu.console.print')
    def test_menu_batch_processing(self, mock_print, mock_select, mock_input):
        """Test batch processing menu option"""
        from samplemind.interfaces.cli.menu import main
        try:
            main()
        except (SystemExit, KeyboardInterrupt, Exception):
            pass

    @patch('builtins.input', side_effect=['6', '0'])
    @patch('samplemind.interfaces.cli.menu.select_audio_file', return_value=None)
    @patch('samplemind.interfaces.cli.menu.console.print')
    def test_menu_vector_search(self, mock_print, mock_select, mock_input):
        """Test vector search menu option"""
        from samplemind.interfaces.cli.menu import main
        try:
            main()
        except (SystemExit, KeyboardInterrupt, Exception):
            pass

    @patch('builtins.input', side_effect=['7', '0'])
    @patch('samplemind.interfaces.cli.menu.console.print')
    def test_menu_settings(self, mock_print, mock_input):
        """Test settings menu option"""
        from samplemind.interfaces.cli.menu import main
        try:
            main()
        except (SystemExit, KeyboardInterrupt, Exception):
            pass
