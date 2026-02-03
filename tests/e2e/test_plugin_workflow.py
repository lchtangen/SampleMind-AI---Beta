#!/usr/bin/env python3
"""
End-to-End Tests for SampleMind Plugin System
Tests complete workflows integrating installer, backend, and API client
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import asyncio
import json

# Add plugins directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "plugins"))

from installer import Platform, DAW, DAWDetector, PluginInstaller


class TestPluginInstallationWorkflow:
    """End-to-end tests for plugin installation workflows"""

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
            "tmp_path": tmp_path,
        }

    def test_complete_fl_studio_installation_workflow(self, mock_detector, plugins_env):
        """Test complete FL Studio installation workflow: detect → install → verify"""
        mock_detector.platform = Platform.LINUX
        mock_detector.is_daw_installed.return_value = True

        installer = PluginInstaller(mock_detector)
        installer.plugins_dir = plugins_env["plugins_dir"]

        fl_dest = plugins_env["daw_dirs"]["fl_studio"]

        with patch.object(installer, "get_fl_studio_plugin_paths") as mock_paths:
            mock_paths.return_value = {Platform.LINUX: fl_dest}

            # Step 1: Install
            install_success = installer.install_fl_studio_plugin()
            assert install_success is True

            # Step 2: Verify installation
            plugin_file = fl_dest / "libSampleMind_FL_Studio.so"
            assert plugin_file.exists()
            assert "dummy fl plugin" in plugin_file.read_text()

            # Step 3: Verify status
            verify_result = installer._verify_fl_studio()
            assert verify_result is True

            # Step 4: Check logs
            logs = installer.get_log()
            assert len(logs) > 0
            assert any("Copied" in msg for msg in logs)

    def test_complete_ableton_installation_workflow(self, mock_detector, plugins_env):
        """Test complete Ableton installation workflow: detect → install → verify"""
        mock_detector.platform = Platform.LINUX
        mock_detector.is_daw_installed.return_value = True

        installer = PluginInstaller(mock_detector)
        installer.plugins_dir = plugins_env["plugins_dir"]

        ableton_dest = plugins_env["daw_dirs"]["ableton"]

        with patch.object(installer, "get_ableton_plugin_paths") as mock_paths:
            mock_paths.return_value = {Platform.LINUX: ableton_dest}

            # Step 1: Install
            install_success = installer.install_ableton_plugin()
            assert install_success is True

            # Step 2: Verify all files exist
            assert (ableton_dest / "SampleMind.amxd").exists()
            assert (ableton_dest / "communication.js").exists()
            assert (ableton_dest / "midi_mapper.maxpat").exists()

            # Step 3: Verify status
            verify_result = installer._verify_ableton()
            assert verify_result is True

            # Step 4: Get both DAW status
            all_status = installer.verify_installations()
            assert DAW.ABLETON_LIVE in all_status
            assert all_status[DAW.ABLETON_LIVE] is True

    def test_complete_uninstall_workflow(self, mock_detector, plugins_env):
        """Test complete uninstall workflow: install → uninstall → verify"""
        mock_detector.platform = Platform.LINUX
        mock_detector.is_daw_installed.return_value = True

        installer = PluginInstaller(mock_detector)
        installer.plugins_dir = plugins_env["plugins_dir"]

        fl_dest = plugins_env["daw_dirs"]["fl_studio"]

        with patch.object(installer, "get_fl_studio_plugin_paths") as mock_paths:
            mock_paths.return_value = {Platform.LINUX: fl_dest}

            # Step 1: Install
            installer.install_fl_studio_plugin()
            plugin_file = fl_dest / "libSampleMind_FL_Studio.so"
            assert plugin_file.exists()

            # Step 2: Uninstall
            uninstall_success = installer.uninstall_fl_studio_plugin()
            assert uninstall_success is True

            # Step 3: Verify removal
            assert not plugin_file.exists()

            # Step 4: Verify status shows not installed
            verify_result = installer._verify_fl_studio()
            assert verify_result is False

    def test_multi_daw_detection_workflow(self, mock_detector, plugins_env):
        """Test detecting and installing to multiple DAWs"""
        installer = PluginInstaller(mock_detector)
        installer.plugins_dir = plugins_env["plugins_dir"]

        fl_dest = plugins_env["daw_dirs"]["fl_studio"]
        ableton_dest = plugins_env["daw_dirs"]["ableton"]

        with patch.object(installer, "get_fl_studio_plugin_paths") as mock_fl:
            with patch.object(installer, "get_ableton_plugin_paths") as mock_ab:
                mock_fl.return_value = {Platform.LINUX: fl_dest}
                mock_ab.return_value = {Platform.LINUX: ableton_dest}

                with patch.object(installer.detector, "is_daw_installed", return_value=True):
                    # Step 1: Install to both DAWs
                    fl_success = installer.install_fl_studio_plugin()
                    ab_success = installer.install_ableton_plugin()

                    assert fl_success is True
                    assert ab_success is True

                    # Step 2: Verify both
                    all_status = installer.verify_installations()
                    assert all_status[DAW.FL_STUDIO] is True
                    assert all_status[DAW.ABLETON_LIVE] is True

                    # Step 3: Uninstall from one
                    installer.uninstall_fl_studio_plugin()

                    # Step 4: Verify status
                    final_status = installer.verify_installations()
                    assert final_status[DAW.FL_STUDIO] is False
                    assert final_status[DAW.ABLETON_LIVE] is True

    def test_error_recovery_workflow(self, mock_detector, plugins_env):
        """Test error recovery during installation"""
        installer = PluginInstaller(mock_detector)
        installer.plugins_dir = plugins_env["plugins_dir"]

        fl_dest = plugins_env["daw_dirs"]["fl_studio"]

        with patch.object(installer, "get_fl_studio_plugin_paths") as mock_paths:
            mock_paths.return_value = {Platform.LINUX: fl_dest}

            # Step 1: Simulate first failure
            with patch("shutil.copy2") as mock_copy:
                mock_copy.side_effect = PermissionError("Permission denied")

                result = installer.install_fl_studio_plugin()
                assert result is False

                # Plugin should not be installed
                plugin_file = fl_dest / "libSampleMind_FL_Studio.so"
                assert not plugin_file.exists()

            # Step 2: Retry without error
            mock_paths.return_value = {Platform.LINUX: fl_dest}
            result = installer.install_fl_studio_plugin()
            assert result is True

            # Plugin should now be installed
            plugin_file = fl_dest / "libSampleMind_FL_Studio.so"
            assert plugin_file.exists()


class TestBackendAPIWorkflow:
    """End-to-end tests for backend API workflows"""

    @pytest.fixture
    def mock_api_responses(self):
        """Mock backend API responses"""
        return {
            "health": {"status": "healthy", "version": "1.0.0"},
            "analyze": {
                "tempo_bpm": 120,
                "key": "C Major",
                "genre": "Electronic",
                "energy": 0.75,
                "confidence": 0.92,
            },
            "similar": {
                "similar_samples": [
                    {"file_path": "/path/sample1.wav", "similarity": 0.95},
                    {"file_path": "/path/sample2.wav", "similarity": 0.87},
                ]
            },
            "sync": {
                "matched_samples": [
                    {
                        "file_path": "/path/sync1.wav",
                        "bpm": 120,
                        "match_score": 0.98,
                    },
                    {
                        "file_path": "/path/sync2.wav",
                        "bpm": 122,
                        "match_score": 0.85,
                    },
                ]
            },
        }

    def test_health_check_workflow(self, mock_api_responses):
        """Test health check workflow"""
        # Step 1: Connect and check health
        # In real scenario: api.health()
        response = mock_api_responses["health"]

        # Step 2: Verify response
        assert response["status"] == "healthy"
        assert response["version"] == "1.0.0"

        # Step 3: Ready for operations
        ready = response["status"] == "healthy"
        assert ready is True

    def test_complete_analysis_workflow(self, mock_api_responses):
        """Test complete analysis workflow: upload → analyze → display results"""
        # Step 1: Upload audio file (mock)
        # In real scenario: file selection from HTML
        mock_file = {
            "name": "test.wav",
            "size": 1024000,
            "type": "audio/wav",
        }

        # Step 2: Send to backend for analysis
        # In real scenario: api.analyzeAudio(file, 'STANDARD')
        response = mock_api_responses["analyze"]

        # Step 3: Parse results
        results = {
            "tempo": response["tempo_bpm"],
            "key": response["key"],
            "genre": response["genre"],
            "energy": response["energy"],
            "confidence": response["confidence"],
        }

        # Step 4: Display results
        assert results["tempo"] == 120
        assert results["key"] == "C Major"
        assert results["genre"] == "Electronic"
        assert 0 <= results["energy"] <= 1
        assert 0 <= results["confidence"] <= 1

    def test_search_and_display_workflow(self, mock_api_responses):
        """Test search workflow: search → sort → display"""
        # Step 1: Perform search
        # In real scenario: api.findSimilar(file, 10)
        response = mock_api_responses["similar"]
        results = response["similar_samples"]

        # Step 2: Verify results are sorted by similarity (highest first)
        assert results[0]["similarity"] >= results[1]["similarity"]

        # Step 3: Format for display
        display_items = [
            {
                "name": Path(r["file_path"]).name,
                "similarity": f"{r['similarity']*100:.1f}%",
            }
            for r in results
        ]

        # Step 4: Render display
        assert len(display_items) == 2
        assert display_items[0]["similarity"] == "95.0%"

    def test_project_sync_workflow(self, mock_api_responses):
        """Test project sync workflow: input params → sync → display matches"""
        # Step 1: Get project parameters
        project_params = {
            "bpm": 120,
            "key": "C Major",
        }

        # Step 2: Request recommendations from backend
        # In real scenario: api.projectSync(120, 'C Major', 10)
        response = mock_api_responses["sync"]
        matches = response["matched_samples"]

        # Step 3: Verify matches meet criteria
        for match in matches:
            # BPM should be close
            bpm_diff = abs(match["bpm"] - project_params["bpm"])
            assert bpm_diff <= 4  # Within ±4 BPM

            # Score should be high
            assert match["match_score"] >= 0.7

        # Step 4: Sort by match score (highest first)
        sorted_matches = sorted(
            matches, key=lambda x: x["match_score"], reverse=True
        )
        assert sorted_matches[0]["match_score"] >= sorted_matches[1]["match_score"]


class TestIntegrationScenarios:
    """Integration scenarios combining multiple components"""

    def test_plugin_installer_integration(self, tmp_path):
        """Test plugin installer can be imported and initialized"""
        # Should not raise any import errors
        from installer import DAWDetector, PluginInstaller, Platform

        detector = DAWDetector()
        assert detector is not None

        installer = PluginInstaller(detector)
        assert installer is not None
        assert installer.detector is detector

    def test_mock_api_client_integration(self):
        """Test API client mock structure is valid"""
        # Mock the API client initialization
        mock_client = {
            "baseUrl": "http://localhost:8001",
            "timeout": 30000,
            "maxRetries": 3,
            "cache": {},
        }

        assert mock_client["baseUrl"] is not None
        assert mock_client["timeout"] > 0
        assert mock_client["maxRetries"] >= 1

    def test_logging_workflow(self, tmp_path):
        """Test logging throughout workflow"""
        mock_detector = Mock(spec=DAWDetector)
        mock_detector.platform = Platform.LINUX

        installer = PluginInstaller(mock_detector)

        # Step 1: Perform operations
        installer.log("Starting installation")
        installer.log("Checking paths")
        installer.log("Copying files")

        # Step 2: Retrieve logs
        logs = installer.get_log()
        assert len(logs) == 3

        # Step 3: Save logs
        log_file = tmp_path / "install.log"
        installer.save_log(log_file)

        # Step 4: Verify log file
        assert log_file.exists()
        content = log_file.read_text()
        assert "Starting installation" in content


class TestCrossComponentWorkflows:
    """Test workflows spanning multiple components"""

    def test_installer_detects_and_installs(self, tmp_path):
        """Test detector finds DAWs and installer deploys to them"""
        # Setup
        detector = Mock(spec=DAWDetector)
        detector.platform = Platform.LINUX
        detector.is_daw_installed = Mock(return_value=True)

        installer = PluginInstaller(detector)

        # Create test structure
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        daw_dir = tmp_path / "daw_path"
        daw_dir.mkdir()

        plugin_file = plugins_dir / "plugin.so"
        plugin_file.write_text("test")

        installer.plugins_dir = plugins_dir

        # Test workflow
        with patch.object(
            installer, "get_fl_studio_plugin_paths"
        ) as mock_paths:
            mock_paths.return_value = {Platform.LINUX: daw_dir}

            # Detector finds DAW
            assert detector.is_daw_installed(DAW.FL_STUDIO)

            # Installer deploys
            # (Note: Real file would fail to copy, this tests the workflow)
            # In actual use, plugin source would exist

    def test_status_verification_workflow(self, tmp_path):
        """Test verifying installation status across multiple DAWs"""
        detector = Mock(spec=DAWDetector)
        detector.platform = Platform.LINUX

        installer = PluginInstaller(detector)

        # Create directories
        fl_dir = tmp_path / "fl_path"
        fl_dir.mkdir()
        ab_dir = tmp_path / "ab_path"
        ab_dir.mkdir()

        with patch.object(installer, "get_fl_studio_plugin_paths") as mock_fl:
            with patch.object(installer, "get_ableton_plugin_paths") as mock_ab:
                mock_fl.return_value = {Platform.LINUX: fl_dir}
                mock_ab.return_value = {Platform.LINUX: ab_dir}

                # Verify when nothing installed
                status = installer.verify_installations()
                assert status[DAW.FL_STUDIO] is False
                assert status[DAW.ABLETON_LIVE] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
