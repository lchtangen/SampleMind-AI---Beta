"""
Unit tests for CLI command structure
"""

import pytest
from typer.testing import CliRunner


class TestCLICommandStructure:
    """Test CLI command structure and availability"""

    def test_cli_app_exists(self):
        """Test that CLI app is importable"""
        from samplemind.interfaces.cli.main import app
        assert app is not None

    def test_stems_app_exists(self):
        """Test that stems sub-app exists"""
        from samplemind.interfaces.cli.main import stems_app
        assert stems_app is not None

    def test_midi_app_exists(self):
        """Test that midi sub-app exists"""
        from samplemind.interfaces.cli.main import midi_app
        assert midi_app is not None

    def test_analyze_app_exists(self):
        """Test that analyze sub-app exists"""
        from samplemind.interfaces.cli.main import analyze_app
        assert analyze_app is not None

    def test_generate_app_exists(self):
        """Test that generate sub-app exists"""
        from samplemind.interfaces.cli.main import generate_app
        assert generate_app is not None

    def test_search_app_exists(self):
        """Test that search sub-app exists"""
        from samplemind.interfaces.cli.main import search_app
        assert search_app is not None

    def test_console_exists(self):
        """Test that console is initialized"""
        from samplemind.interfaces.cli.main import console
        assert console is not None

    def test_main_function_exists(self):
        """Test that main function exists"""
        from samplemind.interfaces.cli.main import main
        assert callable(main)


class TestCLIHelpers:
    """Test CLI helper functions"""

    def test_analysis_level_enum(self):
        """Test AnalysisLevel enum"""
        from samplemind.core.engine.audio_engine import AnalysisLevel

        assert hasattr(AnalysisLevel, 'BASIC')
        assert hasattr(AnalysisLevel, 'STANDARD')
        assert hasattr(AnalysisLevel, 'DETAILED')
        assert hasattr(AnalysisLevel, 'PROFESSIONAL')

    def test_analysis_level_values(self):
        """Test AnalysisLevel enum values"""
        from samplemind.core.engine.audio_engine import AnalysisLevel

        # Just verify the enum has values
        assert AnalysisLevel.BASIC is not None
        assert AnalysisLevel.STANDARD is not None
        assert AnalysisLevel.DETAILED is not None
        assert AnalysisLevel.PROFESSIONAL is not None


class TestVectorSearchCLI:
    """Test vector search CLI commands structure"""

    def test_search_commands_importable(self):
        """Test that search commands are importable"""
        from samplemind.interfaces.cli import main
        assert hasattr(main, 'search_app')

    def test_search_index_command_exists(self):
        """Test search index command exists"""
        from samplemind.interfaces.cli.main import search_index
        assert callable(search_index)

    def test_search_similar_command_exists(self):
        """Test search similar command exists"""
        from samplemind.interfaces.cli.main import search_similar
        assert callable(search_similar)

    def test_search_recommend_command_exists(self):
        """Test search recommend command exists"""
        from samplemind.interfaces.cli.main import search_recommend
        assert callable(search_recommend)

    def test_search_stats_command_exists(self):
        """Test search stats command exists"""
        from samplemind.interfaces.cli.main import search_stats
        assert callable(search_stats)
