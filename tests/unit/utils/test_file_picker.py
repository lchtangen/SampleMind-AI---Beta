#!/usr/bin/env python3
"""
Unit tests for Cross-Platform File Picker
Tests platform detection, file picker selection, and fallback logic
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from samplemind.utils.file_picker import (
    PlatformDetector,
    CrossPlatformFilePicker,
    MacOSFilePicker,
    LinuxFilePicker,
    TkinterFilePicker,
    get_file_picker,
    select_audio_file,
    select_directory
)


class TestPlatformDetector:
    """Test platform detection logic"""

    @patch('platform.system')
    def test_detect_macos(self, mock_system):
        """Test macOS detection"""
        mock_system.return_value = 'Darwin'
        detector = PlatformDetector()

        assert detector.get_os() == 'macos'

    @patch('platform.system')
    def test_detect_linux(self, mock_system):
        """Test Linux detection"""
        mock_system.return_value = 'Linux'
        detector = PlatformDetector()

        assert detector.get_os() == 'linux'

    @patch('platform.system')
    def test_detect_windows(self, mock_system):
        """Test Windows detection"""
        mock_system.return_value = 'Windows'
        detector = PlatformDetector()

        assert detector.get_os() == 'windows'

    @patch('shutil.which')
    def test_has_zenity(self, mock_which):
        """Test zenity detection"""
        mock_which.return_value = '/usr/bin/zenity'
        detector = PlatformDetector()

        assert detector.has_zenity() == True

    @patch('shutil.which')
    def test_no_zenity(self, mock_which):
        """Test zenity not available"""
        mock_which.return_value = None
        detector = PlatformDetector()

        assert detector.has_zenity() == False

    @patch('shutil.which')
    def test_has_kdialog(self, mock_which):
        """Test kdialog detection"""
        mock_which.return_value = '/usr/bin/kdialog'
        detector = PlatformDetector()

        assert detector.has_kdialog() == True

    def test_has_tkinter(self):
        """Test tkinter detection"""
        detector = PlatformDetector()
        # Should return True in test environment
        result = detector.has_tkinter()
        assert isinstance(result, bool)

    @patch.dict('os.environ', {'XDG_CURRENT_DESKTOP': 'GNOME'})
    def test_detect_gnome(self):
        """Test GNOME desktop detection"""
        import os
        detector = PlatformDetector()
        desktop = detector.get_desktop_environment()

        assert desktop == 'gnome'

    @patch.dict('os.environ', {'XDG_CURRENT_DESKTOP': 'KDE'})
    def test_detect_kde(self):
        """Test KDE desktop detection"""
        detector = PlatformDetector()
        desktop = detector.get_desktop_environment()

        assert desktop == 'kde'


class TestMacOSFilePicker:
    """Test macOS file picker"""

    @patch('subprocess.run')
    def test_choose_file_success(self, mock_run):
        """Test successful file selection on macOS"""
        # Mock successful AppleScript response
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "/Users/test/Music/song.wav\n"
        mock_run.return_value = mock_result

        result = MacOSFilePicker.choose_file(title="Test")

        assert result == Path("/Users/test/Music/song.wav")
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_choose_file_cancelled(self, mock_run):
        """Test cancelled file selection"""
        # Mock cancelled operation
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        result = MacOSFilePicker.choose_file()

        assert result is None

    @patch('subprocess.run')
    def test_choose_folder_success(self, mock_run):
        """Test successful folder selection"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "/Users/test/Music\n"
        mock_run.return_value = mock_result

        result = MacOSFilePicker.choose_folder()

        assert result == Path("/Users/test/Music")


class TestLinuxFilePicker:
    """Test Linux file picker"""

    @patch('subprocess.run')
    def test_zenity_file_selection(self, mock_run):
        """Test Zenity file selection"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "/home/user/music/song.wav\n"
        mock_run.return_value = mock_result

        result = LinuxFilePicker.choose_file_zenity(title="Test")

        assert result == Path("/home/user/music/song.wav")
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_zenity_folder_selection(self, mock_run):
        """Test Zenity folder selection"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "/home/user/music\n"
        mock_run.return_value = mock_result

        result = LinuxFilePicker.choose_folder_zenity()

        assert result == Path("/home/user/music")

    @patch('subprocess.run')
    def test_kdialog_file_selection(self, mock_run):
        """Test KDialog file selection"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "/home/user/music/song.flac\n"
        mock_run.return_value = mock_result

        result = LinuxFilePicker.choose_file_kdialog(title="Test")

        assert result == Path("/home/user/music/song.flac")


class TestCrossPlatformFilePicker:
    """Test main cross-platform file picker"""

    def test_initialization(self):
        """Test picker initializes correctly"""
        picker = CrossPlatformFilePicker()

        assert picker is not None
        assert hasattr(picker, 'os')
        assert hasattr(picker, 'detector')

    def test_get_platform_info(self):
        """Test getting platform information"""
        picker = CrossPlatformFilePicker()
        info = picker.get_platform_info()

        assert isinstance(info, dict)
        assert 'os' in info
        assert 'platform' in info
        assert 'has_tkinter' in info

    @patch('platform.system')
    @patch('subprocess.run')
    def test_macos_file_selection(self, mock_run, mock_system):
        """Test file selection on macOS"""
        mock_system.return_value = 'Darwin'

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "/Users/test/song.mp3\n"
        mock_run.return_value = mock_result

        picker = CrossPlatformFilePicker()
        result = picker.choose_file(title="Test")

        assert result is not None

    @patch('platform.system')
    @patch('shutil.which')
    @patch('subprocess.run')
    def test_linux_zenity_selection(self, mock_run, mock_which, mock_system):
        """Test file selection on Linux with Zenity"""
        mock_system.return_value = 'Linux'
        mock_which.return_value = '/usr/bin/zenity'

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "/home/user/song.wav\n"
        mock_run.return_value = mock_result

        picker = CrossPlatformFilePicker()
        result = picker.choose_file(title="Test")

        # Should attempt Zenity
        assert mock_run.called

    def test_text_input_fallback_file(self):
        """Test text input fallback for file"""
        picker = CrossPlatformFilePicker()

        with patch('builtins.input', return_value='/tmp/test.wav'):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('pathlib.Path.is_file', return_value=True):
                    result = picker._text_input_file("Test")

                    assert result is not None
                    assert isinstance(result, Path)

    def test_text_input_fallback_folder(self):
        """Test text input fallback for folder"""
        picker = CrossPlatformFilePicker()

        with patch('builtins.input', return_value='/tmp'):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('pathlib.Path.is_dir', return_value=True):
                    result = picker._text_input_folder("Test")

                    assert result is not None
                    assert isinstance(result, Path)


class TestConvenienceFunctions:
    """Test convenience wrapper functions"""

    def test_get_file_picker_singleton(self):
        """Test file picker singleton"""
        picker1 = get_file_picker()
        picker2 = get_file_picker()

        assert picker1 is picker2  # Same instance

    @patch.object(CrossPlatformFilePicker, 'choose_file')
    def test_select_audio_file(self, mock_choose):
        """Test select_audio_file wrapper"""
        mock_choose.return_value = Path("/test/audio.wav")

        result = select_audio_file(title="Test")

        assert result == Path("/test/audio.wav")
        mock_choose.assert_called_once()

    @patch.object(CrossPlatformFilePicker, 'choose_folder')
    def test_select_directory(self, mock_choose):
        """Test select_directory wrapper"""
        mock_choose.return_value = Path("/test/music")

        result = select_directory(title="Test")

        assert result == Path("/test/music")
        mock_choose.assert_called_once()


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_file_types(self):
        """Test with no file types specified"""
        picker = CrossPlatformFilePicker()

        # Should not raise error
        try:
            # This will use fallback in test environment
            result = picker.choose_file(file_types=None)
            # Result might be None (cancelled) but shouldn't error
            assert result is None or isinstance(result, Path)
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")

    def test_nonexistent_initial_directory(self):
        """Test with nonexistent initial directory"""
        picker = CrossPlatformFilePicker()

        # Should handle gracefully
        try:
            result = picker.choose_file(
                initial_directory="/nonexistent/path/12345"
            )
            assert result is None or isinstance(result, Path)
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
