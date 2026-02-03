#!/usr/bin/env python3
"""
Integration tests for Plugin Installer
Tests complete installation workflows with real file system interactions
"""

import pytest
import platform
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import shutil

# Add plugins directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "plugins"))

from installer import Platform, DAW, DAWDetector, PluginInstaller


class TestPluginInstallerIntegration:
    """Integration tests for complete installation workflows"""

    @pytest.fixture
    def mock_detector(self):
        """Create mock DAWDetector"""
        detector = Mock(spec=DAWDetector)
        detector.platform = Platform.LINUX
        detector.installed_daws = {}
        return detector

    @pytest.fixture
    def plugins_env(self, tmp_path):
        """Create complete plugin environment"""
        # Plugin source directory
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        # FL Studio plugin
        fl_studio_dir = plugins_dir / "fl_studio" / "build" / "lib"
        fl_studio_dir.mkdir(parents=True)
        (fl_studio_dir / "libSampleMind_FL_Studio.so").write_text("dummy fl plugin")

        # Ableton plugin
        ableton_dir = plugins_dir / "ableton"
        ableton_dir.mkdir()
        (ableton_dir / "SampleMind.amxd").write_text("dummy amxd")
        (ableton_dir / "communication.js").write_text("dummy js")
        (ableton_dir / "midi_mapper.maxpat").write_text("dummy midi")

        # DAW install directories
        daw_dirs = {
            "fl_studio": tmp_path / "daw_fl" / "Plugins" / "Fruity" / "Generators",
            "ableton": tmp_path / "daw_ableton" / "Presets" / "Instruments" / "Max Instrument",
        }

        for daw_type, daw_path in daw_dirs.items():
            daw_path.mkdir(parents=True)

        return {
            "plugins_dir": plugins_dir,
            "daw_dirs": daw_dirs,
        }

    def test_full_installation_workflow_fl_studio(self, mock_detector, plugins_env):
        """Test complete FL Studio installation workflow"""
        mock_detector.platform = Platform.LINUX
        mock_detector.is_daw_installed.return_value = True

        installer = PluginInstaller(mock_detector)
        installer.plugins_dir = plugins_env["plugins_dir"]

        fl_dest = plugins_env["daw_dirs"]["fl_studio"]

        with patch.object(installer, "get_fl_studio_plugin_paths") as mock_paths:
            mock_paths.return_value = {Platform.LINUX: fl_dest}

            # Install
            success = installer.install_fl_studio_plugin()
            assert success is True

            # Verify file exists
            plugin_file = fl_dest / "libSampleMind_FL_Studio.so"
            assert plugin_file.exists()
            assert "dummy fl plugin" in plugin_file.read_text()

            # Verify log
            log = installer.get_log()
            assert any("Copied" in msg for msg in log)

    def test_full_installation_workflow_ableton(self, mock_detector, plugins_env):
        """Test complete Ableton installation workflow"""
        mock_detector.platform = Platform.LINUX
        mock_detector.is_daw_installed.return_value = True

        installer = PluginInstaller(mock_detector)
        installer.plugins_dir = plugins_env["plugins_dir"]

        ableton_dest = plugins_env["daw_dirs"]["ableton"]

        with patch.object(installer, "get_ableton_plugin_paths") as mock_paths:
            mock_paths.return_value = {Platform.LINUX: ableton_dest}

            # Install
            success = installer.install_ableton_plugin()
            assert success is True

            # Verify all files exist
            assert (ableton_dest / "SampleMind.amxd").exists()
            assert (ableton_dest / "communication.js").exists()

            # Verify log
            log = installer.get_log()
            assert any("Copied" in msg for msg in log)

    def test_install_verify_uninstall_cycle(self, mock_detector, plugins_env):
        """Test complete install -> verify -> uninstall cycle"""
        mock_detector.platform = Platform.LINUX
        mock_detector.is_daw_installed.return_value = True

        installer = PluginInstaller(mock_detector)
        installer.plugins_dir = plugins_env["plugins_dir"]

        fl_dest = plugins_env["daw_dirs"]["fl_studio"]

        with patch.object(installer, "get_fl_studio_plugin_paths") as mock_paths:
            mock_paths.return_value = {Platform.LINUX: fl_dest}

            # 1. Install
            install_success = installer.install_fl_studio_plugin()
            assert install_success is True
            assert (fl_dest / "libSampleMind_FL_Studio.so").exists()

            # 2. Verify
            verify_success = installer._verify_fl_studio()
            assert verify_success is True

            # 3. Uninstall
            uninstall_success = installer.uninstall_fl_studio_plugin()
            assert uninstall_success is True
            assert not (fl_dest / "libSampleMind_FL_Studio.so").exists()

            # 4. Verify again
            verify_after = installer._verify_fl_studio()
            assert verify_after is False

    def test_reinstallation_overwrites(self, mock_detector, plugins_env):
        """Test that reinstalling overwrites previous version"""
        mock_detector.platform = Platform.LINUX
        mock_detector.is_daw_installed.return_value = True

        installer = PluginInstaller(mock_detector)
        installer.plugins_dir = plugins_env["plugins_dir"]

        fl_dest = plugins_env["daw_dirs"]["fl_studio"]

        with patch.object(installer, "get_fl_studio_plugin_paths") as mock_paths:
            mock_paths.return_value = {Platform.LINUX: fl_dest}

            # Install first time
            success1 = installer.install_fl_studio_plugin()
            assert success1 is True

            plugin_file = fl_dest / "libSampleMind_FL_Studio.so"
            original_size = plugin_file.stat().st_size

            # Modify the plugin file
            plugin_file.write_text("modified content - much longer than before")
            modified_size = plugin_file.stat().st_size
            assert modified_size > original_size

            # Reinstall
            success2 = installer.install_fl_studio_plugin()
            assert success2 is True

            # File should be back to original size
            new_size = plugin_file.stat().st_size
            assert new_size == original_size

    def test_install_creates_directory(self, mock_detector, plugins_env, tmp_path):
        """Test that installation creates destination directory if missing"""
        mock_detector.platform = Platform.LINUX
        mock_detector.is_daw_installed.return_value = True

        installer = PluginInstaller(mock_detector)
        installer.plugins_dir = plugins_env["plugins_dir"]

        # Use non-existent destination
        fl_dest = tmp_path / "nonexistent" / "path" / "to" / "plugins"
        assert not fl_dest.exists()

        with patch.object(installer, "get_fl_studio_plugin_paths") as mock_paths:
            mock_paths.return_value = {Platform.LINUX: fl_dest}

            success = installer.install_fl_studio_plugin()
            assert success is True

            # Directory should be created
            assert fl_dest.exists()
            assert (fl_dest / "libSampleMind_FL_Studio.so").exists()

    def test_install_preserves_existing_files(self, mock_detector, plugins_env):
        """Test that installation preserves other files in directory"""
        mock_detector.platform = Platform.LINUX
        mock_detector.is_daw_installed.return_value = True

        installer = PluginInstaller(mock_detector)
        installer.plugins_dir = plugins_env["plugins_dir"]

        fl_dest = plugins_env["daw_dirs"]["fl_studio"]

        # Create existing file
        existing_file = fl_dest / "existing_plugin.dll"
        existing_file.write_text("existing content")

        with patch.object(installer, "get_fl_studio_plugin_paths") as mock_paths:
            mock_paths.return_value = {Platform.LINUX: fl_dest}

            success = installer.install_fl_studio_plugin()
            assert success is True

            # Both files should exist
            assert existing_file.exists()
            assert existing_file.read_text() == "existing content"
            assert (fl_dest / "libSampleMind_FL_Studio.so").exists()

    def test_uninstall_removes_only_plugin_files(self, mock_detector, plugins_env):
        """Test that uninstall only removes plugin files, not other files"""
        mock_detector.platform = Platform.LINUX

        installer = PluginInstaller(mock_detector)
        installer.plugins_dir = plugins_env["plugins_dir"]

        ableton_dest = plugins_env["daw_dirs"]["ableton"]

        # Install Ableton
        with patch.object(installer, "get_ableton_plugin_paths") as mock_paths:
            with patch.object(installer.detector, "is_daw_installed", return_value=True):
                mock_paths.return_value = {Platform.LINUX: ableton_dest}
                installer.install_ableton_plugin()

                # Create additional file
                other_file = ableton_dest / "other_preset.amxd"
                other_file.write_text("other content")

                # Uninstall (within same mocked context so path is consistent)
                success = installer.uninstall_ableton_plugin()
                assert success is True

                # Other file should remain
                assert other_file.exists()
                assert other_file.read_text() == "other content"

                # Plugin files should be removed
                assert not (ableton_dest / "SampleMind.amxd").exists()
                assert not (ableton_dest / "communication.js").exists()

    def test_error_handling_permission_denied(self, mock_detector, plugins_env):
        """Test graceful handling of permission errors"""
        mock_detector.platform = Platform.LINUX
        mock_detector.is_daw_installed.return_value = True

        installer = PluginInstaller(mock_detector)
        installer.plugins_dir = plugins_env["plugins_dir"]

        fl_dest = plugins_env["daw_dirs"]["fl_studio"]

        # Mock file copy to raise PermissionError
        with patch("shutil.copy2") as mock_copy:
            mock_copy.side_effect = PermissionError("Permission denied")

            with patch.object(installer, "get_fl_studio_plugin_paths") as mock_paths:
                mock_paths.return_value = {Platform.LINUX: fl_dest}

                success = installer.install_fl_studio_plugin()
                assert success is False

                # Should log error
                log = installer.get_log()
                assert any("Permission denied" in msg for msg in log)

    def test_error_handling_missing_source(self, mock_detector):
        """Test graceful handling of missing source files"""
        mock_detector.platform = Platform.LINUX
        mock_detector.is_daw_installed.return_value = True

        installer = PluginInstaller(mock_detector)
        installer.plugins_dir = Path("/nonexistent/plugins")  # Missing

        with patch("pathlib.Path.exists", return_value=False):
            success = installer.install_fl_studio_plugin()
            assert success is False

            log = installer.get_log()
            assert any("source not found" in msg.lower() for msg in log)

    def test_logging_captures_all_operations(self, mock_detector, plugins_env):
        """Test that logging captures all operations"""
        mock_detector.platform = Platform.LINUX
        mock_detector.is_daw_installed.return_value = True

        installer = PluginInstaller(mock_detector)
        installer.plugins_dir = plugins_env["plugins_dir"]

        fl_dest = plugins_env["daw_dirs"]["fl_studio"]

        with patch.object(installer, "get_fl_studio_plugin_paths") as mock_paths:
            mock_paths.return_value = {Platform.LINUX: fl_dest}

            installer.install_fl_studio_plugin()

            log = installer.get_log()
            assert len(log) > 0

            # Should contain verification messages
            log_text = " ".join(log)
            assert "directory" in log_text.lower() or "copied" in log_text.lower()

    def test_log_persistence_across_operations(self, mock_detector, plugins_env):
        """Test that log persists across multiple operations"""
        mock_detector.platform = Platform.LINUX
        mock_detector.is_daw_installed.return_value = True

        installer = PluginInstaller(mock_detector)
        installer.plugins_dir = plugins_env["plugins_dir"]

        fl_dest = plugins_env["daw_dirs"]["fl_studio"]
        ableton_dest = plugins_env["daw_dirs"]["ableton"]

        with patch.object(installer, "get_fl_studio_plugin_paths") as mock_fl_paths:
            with patch.object(installer, "get_ableton_plugin_paths") as mock_ab_paths:
                mock_fl_paths.return_value = {Platform.LINUX: fl_dest}
                mock_ab_paths.return_value = {Platform.LINUX: ableton_dest}

                installer.install_fl_studio_plugin()
                log1 = len(installer.get_log())

                installer.install_ableton_plugin()
                log2 = len(installer.get_log())

                # Log should grow with each operation
                assert log2 > log1

    def test_save_log_creates_file(self, mock_detector, plugins_env, tmp_path):
        """Test that save_log creates a file with log contents"""
        mock_detector.platform = Platform.LINUX
        mock_detector.is_daw_installed.return_value = True

        installer = PluginInstaller(mock_detector)
        installer.plugins_dir = plugins_env["plugins_dir"]

        installer.log("Test log line 1")
        installer.log("Test log line 2")

        log_file = tmp_path / "test_install.log"
        installer.save_log(log_file)

        assert log_file.exists()
        content = log_file.read_text()
        assert "Test log line 1" in content
        assert "Test log line 2" in content
        assert "\n" in content  # Lines should be separated


class TestPluginInstallerCLI:
    """Tests for CLI interface"""

    @pytest.fixture
    def plugins_env(self, tmp_path):
        """Create complete plugin environment"""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        # FL Studio plugin
        fl_studio_dir = plugins_dir / "fl_studio" / "build" / "lib"
        fl_studio_dir.mkdir(parents=True)
        (fl_studio_dir / "libSampleMind_FL_Studio.so").write_text("dummy")

        # Ableton
        ableton_dir = plugins_dir / "ableton"
        ableton_dir.mkdir()
        (ableton_dir / "SampleMind.amxd").write_text("dummy")

        return plugins_dir

    def test_verify_workflow(self, tmp_path):
        """Test verify workflow returns correct status"""
        mock_detector = Mock(spec=DAWDetector)
        mock_detector.platform = Platform.LINUX
        mock_detector.is_daw_installed.side_effect = lambda daw: daw == DAW.FL_STUDIO

        installer = PluginInstaller(mock_detector)

        # Create mock plugin file
        fl_dest = tmp_path / "plugins"
        fl_dest.mkdir()
        (fl_dest / "libSampleMind_FL_Studio.so").write_text("dummy")

        with patch.object(installer, "get_fl_studio_plugin_paths") as mock_paths:
            mock_paths.return_value = {Platform.LINUX: fl_dest}

            results = installer.verify_installations()

            assert DAW.FL_STUDIO in results
            assert DAW.ABLETON_LIVE in results
            # FL Studio should be verified as installed
            assert results[DAW.FL_STUDIO] is True
            # Ableton not installed
            assert results[DAW.ABLETON_LIVE] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
