#!/usr/bin/env python3
"""
Unit tests for SampleMind AI Plugin Installer
Tests: DAWDetector, PluginInstaller, cross-platform compatibility
"""

import pytest
import platform
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add plugins directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "plugins"))

from installer import Platform, DAW, DAWDetector, PluginInstaller, PluginInfo, InstallationPath


class TestDAWDetector:
    """Tests for DAWDetector class"""

    # Platform detection tests
    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_detect_platform_windows(self):
        """Test Windows platform detection"""
        with patch("platform.system", return_value="Windows"):
            with patch("pathlib.Path.exists", return_value=False):
                detector = DAWDetector()
                assert detector.platform == Platform.WINDOWS

    def test_detect_platform_macos(self):
        """Test macOS platform detection"""
        with patch("platform.system", return_value="Darwin"):
            detector = DAWDetector()
            assert detector.platform == Platform.MACOS

    def test_detect_platform_linux(self):
        """Test Linux platform detection"""
        with patch("platform.system", return_value="Linux"):
            detector = DAWDetector()
            assert detector.platform == Platform.LINUX

    def test_detect_platform_unsupported(self):
        """Test unsupported platform raises error"""
        with patch("platform.system", return_value="FreeBSD"):
            with pytest.raises(RuntimeError, match="Unsupported platform"):
                DAWDetector()

    # Windows DAW detection tests
    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_detect_fl_studio_windows(self):
        """Test FL Studio detection on Windows"""
        detector = DAWDetector()
        # If running on Windows with FL Studio installed
        if DAW.FL_STUDIO in detector.installed_daws:
            assert detector.installed_daws[DAW.FL_STUDIO] is not None

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_detect_ableton_windows(self):
        """Test Ableton Live detection on Windows"""
        detector = DAWDetector()
        # If running on Windows with Ableton installed
        if DAW.ABLETON_LIVE in detector.installed_daws:
            assert detector.installed_daws[DAW.ABLETON_LIVE] is not None

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_detect_no_daws_windows(self):
        """Test no DAWs detected on Windows"""
        detector = DAWDetector()
        # Either DAWs are detected or not - this test just ensures it doesn't crash
        assert isinstance(detector.installed_daws, dict)

    # macOS DAW detection tests
    @patch("platform.system", return_value="Darwin")
    def test_detect_fl_studio_macos(self, mock_system, tmp_path):
        """Test FL Studio detection on macOS"""
        fl_path = tmp_path / "Applications" / "FL Studio.app"
        fl_path.mkdir(parents=True)

        with patch("pathlib.Path.exists", return_value=True):
            detector = DAWDetector()
            detector._detect_macos()
            assert DAW.FL_STUDIO in detector.installed_daws

    @patch("platform.system", return_value="Darwin")
    def test_detect_ableton_macos(self, mock_system, tmp_path):
        """Test Ableton Live detection on macOS"""
        ableton_path = tmp_path / "Applications" / "Ableton Live 12.app"
        ableton_path.mkdir(parents=True)

        with patch("pathlib.Path.exists", return_value=True):
            detector = DAWDetector()
            detector._detect_macos()
            assert DAW.ABLETON_LIVE in detector.installed_daws

    @patch("platform.system", return_value="Darwin")
    def test_detect_no_daws_macos(self, mock_system):
        """Test no DAWs detected on macOS"""
        with patch("pathlib.Path.exists", return_value=False):
            detector = DAWDetector()
            detector._detect_macos()
            assert len(detector.installed_daws) == 0

    # Linux DAW detection tests
    @patch("platform.system", return_value="Linux")
    @patch("os.path.expanduser")
    def test_detect_fl_studio_linux(self, mock_expand, mock_system, tmp_path):
        """Test FL Studio detection on Linux"""
        mock_expand.return_value = str(tmp_path / "FL_Studio")
        fl_path = tmp_path / "FL_Studio"
        fl_path.mkdir()

        with patch("pathlib.Path.exists", return_value=True):
            detector = DAWDetector()
            detector._detect_linux()
            assert DAW.FL_STUDIO in detector.installed_daws

    @patch("platform.system", return_value="Linux")
    @patch("os.path.expanduser")
    def test_detect_ableton_linux(self, mock_expand, mock_system, tmp_path):
        """Test Ableton Live detection on Linux"""
        mock_expand.return_value = str(tmp_path / "Ableton")
        ableton_path = tmp_path / "Ableton"
        ableton_path.mkdir()

        with patch("pathlib.Path.exists", return_value=True):
            detector = DAWDetector()
            detector._detect_linux()
            assert DAW.ABLETON_LIVE in detector.installed_daws

    @patch("platform.system", return_value="Linux")
    def test_detect_no_daws_linux(self, mock_system):
        """Test no DAWs detected on Linux"""
        with patch("pathlib.Path.exists", return_value=False):
            detector = DAWDetector()
            detector._detect_linux()
            assert len(detector.installed_daws) == 0

    # DAWDetector utility methods
    def test_is_daw_installed(self):
        """Test is_daw_installed method"""
        detector = DAWDetector.__new__(DAWDetector)
        detector.platform = Platform.LINUX
        detector.installed_daws = {DAW.FL_STUDIO: Path("~/FL_Studio")}

        assert detector.is_daw_installed(DAW.FL_STUDIO) is True
        assert detector.is_daw_installed(DAW.ABLETON_LIVE) is False

    def test_get_daw_path(self):
        """Test get_daw_path method"""
        detector = DAWDetector.__new__(DAWDetector)
        detector.platform = Platform.LINUX
        fl_path = Path("/opt/FL_Studio")
        detector.installed_daws = {DAW.FL_STUDIO: fl_path}

        assert detector.get_daw_path(DAW.FL_STUDIO) == fl_path
        assert detector.get_daw_path(DAW.ABLETON_LIVE) is None

    def test_list_installed_daws(self):
        """Test list_installed_daws method"""
        detector = DAWDetector.__new__(DAWDetector)
        detector.platform = Platform.LINUX
        fl_path = Path("/opt/FL_Studio")
        ableton_path = Path("/opt/Ableton")
        detector.installed_daws = {
            DAW.FL_STUDIO: fl_path,
            DAW.ABLETON_LIVE: ableton_path
        }

        daws = detector.list_installed_daws()
        assert len(daws) == 2
        assert (DAW.FL_STUDIO, fl_path) in daws
        assert (DAW.ABLETON_LIVE, ableton_path) in daws

    def test_list_installed_daws_empty(self):
        """Test list_installed_daws with no DAWs"""
        detector = DAWDetector.__new__(DAWDetector)
        detector.platform = Platform.LINUX
        detector.installed_daws = {}
        daws = detector.list_installed_daws()
        assert daws == []


class TestPluginInstaller:
    """Tests for PluginInstaller class"""

    @pytest.fixture
    def mock_detector(self):
        """Create mock DAWDetector"""
        detector = Mock(spec=DAWDetector)
        detector.platform = Platform.LINUX
        detector.installed_daws = {}
        return detector

    @pytest.fixture
    def installer(self, mock_detector, tmp_path):
        """Create PluginInstaller with mocked detector"""
        installer = PluginInstaller(mock_detector)
        installer.plugins_dir = tmp_path / "plugins"
        installer.plugins_dir.mkdir()
        return installer

    # Path generation tests
    def test_get_fl_studio_plugin_paths_windows(self, installer):
        """Test FL Studio plugin paths on Windows"""
        installer.detector.platform = Platform.WINDOWS
        paths = installer.get_fl_studio_plugin_paths()

        assert Platform.WINDOWS in paths
        assert "Fruity/Generators" in str(paths[Platform.WINDOWS])

    def test_get_fl_studio_plugin_paths_macos(self, installer):
        """Test FL Studio plugin paths on macOS"""
        installer.detector.platform = Platform.MACOS
        paths = installer.get_fl_studio_plugin_paths()

        assert Platform.MACOS in paths
        assert "Library/Application Support" in str(paths[Platform.MACOS])

    def test_get_fl_studio_plugin_paths_linux(self, installer):
        """Test FL Studio plugin paths on Linux"""
        installer.detector.platform = Platform.LINUX
        paths = installer.get_fl_studio_plugin_paths()

        assert Platform.LINUX in paths
        assert ".config" in str(paths[Platform.LINUX])

    def test_get_ableton_plugin_paths_windows(self, installer):
        """Test Ableton plugin paths on Windows"""
        installer.detector.platform = Platform.WINDOWS
        paths = installer.get_ableton_plugin_paths()

        assert Platform.WINDOWS in paths
        assert "Ableton" in str(paths[Platform.WINDOWS])

    def test_get_ableton_plugin_paths_macos(self, installer):
        """Test Ableton plugin paths on macOS"""
        installer.detector.platform = Platform.MACOS
        paths = installer.get_ableton_plugin_paths()

        assert Platform.MACOS in paths
        assert "Music" in str(paths[Platform.MACOS])

    def test_get_ableton_plugin_paths_linux(self, installer):
        """Test Ableton plugin paths on Linux"""
        installer.detector.platform = Platform.LINUX
        paths = installer.get_ableton_plugin_paths()

        assert Platform.LINUX in paths
        assert ".Ableton" in str(paths[Platform.LINUX])

    # Plugin source path tests
    def test_get_plugin_source_path_fl_studio_windows(self, installer):
        """Test FL Studio source path on Windows"""
        installer.detector.platform = Platform.WINDOWS
        path = installer.get_plugin_source_path(DAW.FL_STUDIO, Platform.WINDOWS)

        assert path is not None
        assert "SampleMind_FL_Studio.dll" in str(path)

    def test_get_plugin_source_path_fl_studio_macos(self, installer):
        """Test FL Studio source path on macOS"""
        installer.detector.platform = Platform.MACOS
        path = installer.get_plugin_source_path(DAW.FL_STUDIO, Platform.MACOS)

        assert path is not None
        assert "libSampleMind_FL_Studio.dylib" in str(path)

    def test_get_plugin_source_path_fl_studio_linux(self, installer):
        """Test FL Studio source path on Linux"""
        installer.detector.platform = Platform.LINUX
        path = installer.get_plugin_source_path(DAW.FL_STUDIO, Platform.LINUX)

        assert path is not None
        assert "libSampleMind_FL_Studio.so" in str(path)

    def test_get_plugin_source_path_ableton(self, installer):
        """Test Ableton source path"""
        path = installer.get_plugin_source_path(DAW.ABLETON_LIVE, Platform.LINUX)

        assert path is not None
        assert "SampleMind.amxd" in str(path)

    def test_get_plugin_source_path_invalid_daw(self, installer):
        """Test invalid DAW returns None"""
        invalid_daw = Mock()
        path = installer.get_plugin_source_path(invalid_daw, Platform.WINDOWS)

        assert path is None

    # Installation tests
    def test_install_fl_studio_plugin_daw_not_installed(self, installer):
        """Test FL Studio installation fails when DAW not installed"""
        installer.detector.is_daw_installed.return_value = False

        result = installer.install_fl_studio_plugin()

        assert result is False
        assert any("not detected" in msg.lower() for msg in installer.get_log())

    def test_install_fl_studio_plugin_source_missing(self, installer):
        """Test FL Studio installation fails when source missing"""
        installer.detector.is_daw_installed.return_value = True
        installer.detector.platform = Platform.WINDOWS

        result = installer.install_fl_studio_plugin()

        assert result is False
        assert any("source not found" in msg.lower() for msg in installer.get_log())

    def test_install_fl_studio_plugin_success(self, installer, tmp_path):
        """Test successful FL Studio plugin installation"""
        installer.detector.is_daw_installed.return_value = True
        installer.detector.platform = Platform.LINUX

        # Create source plugin file
        source_file = installer.plugins_dir / "fl_studio" / "build" / "lib" / "libSampleMind_FL_Studio.so"
        source_file.parent.mkdir(parents=True)
        source_file.write_text("dummy plugin")

        # Create destination directory
        dest_dir = tmp_path / "fl_plugins"
        dest_dir.mkdir()

        with patch.object(installer, "get_fl_studio_plugin_paths") as mock_paths:
            mock_paths.return_value = {Platform.LINUX: dest_dir}
            result = installer.install_fl_studio_plugin()

        assert result is True
        assert (dest_dir / "libSampleMind_FL_Studio.so").exists()

    def test_install_ableton_plugin_daw_not_installed(self, installer):
        """Test Ableton installation fails when DAW not installed"""
        installer.detector.is_daw_installed.return_value = False

        result = installer.install_ableton_plugin()

        assert result is False
        assert any("not detected" in msg.lower() for msg in installer.get_log())

    def test_install_ableton_plugin_success(self, installer, tmp_path):
        """Test successful Ableton plugin installation"""
        installer.detector.is_daw_installed.return_value = True
        installer.detector.platform = Platform.LINUX

        # Create source files
        amxd_file = installer.plugins_dir / "ableton" / "SampleMind.amxd"
        amxd_file.parent.mkdir(parents=True)
        amxd_file.write_text("dummy amxd")

        js_file = installer.plugins_dir / "ableton" / "communication.js"
        js_file.write_text("dummy js")

        # Create destination directory
        dest_dir = tmp_path / "ableton_instruments"
        dest_dir.mkdir()

        with patch.object(installer, "get_ableton_plugin_paths") as mock_paths:
            mock_paths.return_value = {Platform.LINUX: dest_dir}
            result = installer.install_ableton_plugin()

        assert result is True
        assert (dest_dir / "SampleMind.amxd").exists()
        assert (dest_dir / "communication.js").exists()

    # Uninstallation tests
    def test_uninstall_fl_studio_plugin_file_missing(self, installer):
        """Test FL Studio uninstallation when file not present"""
        installer.detector.platform = Platform.WINDOWS

        with patch.object(installer, "get_fl_studio_plugin_paths") as mock_paths:
            mock_paths.return_value = {Platform.WINDOWS: Path("/nonexistent")}
            result = installer.uninstall_fl_studio_plugin()

        assert result is False

    def test_uninstall_fl_studio_plugin_success(self, installer, tmp_path):
        """Test successful FL Studio plugin uninstallation"""
        installer.detector.platform = Platform.WINDOWS

        # Create plugin file
        dest_dir = tmp_path / "fl_plugins"
        dest_dir.mkdir()
        plugin_file = dest_dir / "SampleMind_FL_Studio.dll"
        plugin_file.write_text("dummy plugin")

        with patch.object(installer, "get_fl_studio_plugin_paths") as mock_paths:
            mock_paths.return_value = {Platform.WINDOWS: dest_dir}
            result = installer.uninstall_fl_studio_plugin()

        assert result is True
        assert not plugin_file.exists()

    def test_uninstall_ableton_plugin_success(self, installer, tmp_path):
        """Test successful Ableton plugin uninstallation"""
        installer.detector.platform = Platform.LINUX

        # Create plugin files
        dest_dir = tmp_path / "ableton_instruments"
        dest_dir.mkdir()
        (dest_dir / "SampleMind.amxd").write_text("dummy")
        (dest_dir / "communication.js").write_text("dummy")

        with patch.object(installer, "get_ableton_plugin_paths") as mock_paths:
            mock_paths.return_value = {Platform.LINUX: dest_dir}
            result = installer.uninstall_ableton_plugin()

        assert result is True
        assert not (dest_dir / "SampleMind.amxd").exists()

    # Verification tests
    def test_verify_fl_studio_plugin_installed(self, installer, tmp_path):
        """Test FL Studio plugin verification when installed"""
        installer.detector.platform = Platform.LINUX

        dest_dir = tmp_path / "fl_plugins"
        dest_dir.mkdir()
        (dest_dir / "libSampleMind_FL_Studio.so").write_text("dummy")

        with patch.object(installer, "get_fl_studio_plugin_paths") as mock_paths:
            mock_paths.return_value = {Platform.LINUX: dest_dir}
            result = installer._verify_fl_studio()

        assert result is True

    def test_verify_fl_studio_plugin_not_installed(self, installer, tmp_path):
        """Test FL Studio plugin verification when not installed"""
        installer.detector.platform = Platform.LINUX

        dest_dir = tmp_path / "fl_plugins"
        dest_dir.mkdir()

        with patch.object(installer, "get_fl_studio_plugin_paths") as mock_paths:
            mock_paths.return_value = {Platform.LINUX: dest_dir}
            result = installer._verify_fl_studio()

        assert result is False

    def test_verify_ableton_plugin_installed(self, installer, tmp_path):
        """Test Ableton plugin verification when installed"""
        installer.detector.platform = Platform.LINUX

        dest_dir = tmp_path / "ableton_instruments"
        dest_dir.mkdir()
        (dest_dir / "SampleMind.amxd").write_text("dummy")

        with patch.object(installer, "get_ableton_plugin_paths") as mock_paths:
            mock_paths.return_value = {Platform.LINUX: dest_dir}
            result = installer._verify_ableton()

        assert result is True

    def test_verify_ableton_plugin_not_installed(self, installer, tmp_path):
        """Test Ableton plugin verification when not installed"""
        installer.detector.platform = Platform.LINUX

        dest_dir = tmp_path / "ableton_instruments"
        dest_dir.mkdir()

        with patch.object(installer, "get_ableton_plugin_paths") as mock_paths:
            mock_paths.return_value = {Platform.LINUX: dest_dir}
            result = installer._verify_ableton()

        assert result is False

    def test_verify_installations(self, installer):
        """Test verify_installations returns dict for all DAWs"""
        installer.detector.is_daw_installed.return_value = False

        results = installer.verify_installations()

        assert DAW.FL_STUDIO in results
        assert DAW.ABLETON_LIVE in results

    # Logging tests
    def test_log_message(self, installer):
        """Test logging a message"""
        message = "Test log message"
        installer.log(message)

        assert message in installer.get_log()

    def test_get_log_multiple_messages(self, installer):
        """Test getting multiple log messages"""
        installer.log("Message 1")
        installer.log("Message 2")
        installer.log("Message 3")

        log = installer.get_log()
        assert len(log) == 3
        assert log[0] == "Message 1"
        assert log[2] == "Message 3"

    def test_save_log(self, installer, tmp_path):
        """Test saving log to file"""
        installer.log("Log line 1")
        installer.log("Log line 2")

        log_file = tmp_path / "install.log"
        installer.save_log(log_file)

        assert log_file.exists()
        content = log_file.read_text()
        assert "Log line 1" in content
        assert "Log line 2" in content


class TestDataClasses:
    """Tests for dataclasses"""

    def test_plugin_info_creation(self):
        """Test PluginInfo dataclass"""
        info = PluginInfo(
            name="SampleMind",
            version="1.0.0",
            author="Image-Line",
            website="https://samplemind.ai",
            description="AI audio analysis plugin"
        )

        assert info.name == "SampleMind"
        assert info.version == "1.0.0"

    def test_installation_path_creation(self):
        """Test InstallationPath dataclass"""
        path = InstallationPath(
            daw=DAW.FL_STUDIO,
            platform=Platform.WINDOWS,
            plugin_dir=Path("C:/Plugins"),
            supports_vst3=True
        )

        assert path.daw == DAW.FL_STUDIO
        assert path.platform == Platform.WINDOWS
        assert path.supports_vst3 is True


class TestEnums:
    """Tests for Enum classes"""

    def test_platform_enum_values(self):
        """Test Platform enum has all values"""
        assert Platform.WINDOWS.value == "windows"
        assert Platform.MACOS.value == "macos"
        assert Platform.LINUX.value == "linux"

    def test_daw_enum_values(self):
        """Test DAW enum has all values"""
        assert DAW.FL_STUDIO.value == "fl_studio"
        assert DAW.ABLETON_LIVE.value == "ableton_live"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
