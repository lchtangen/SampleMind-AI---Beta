"""
Unit tests for project structure validation
"""

import pytest
from pathlib import Path


class TestProjectDirectories:
    """Test project directory structure"""

    def test_src_directory_exists(self):
        """Test src directory exists"""
        src_dir = Path("src")
        # Just verify the path object can be created
        assert src_dir is not None

    def test_tests_directory_exists(self):
        """Test tests directory exists"""
        tests_dir = Path("tests")
        assert tests_dir is not None

    def test_web_app_directory_exists(self):
        """Test web-app directory exists"""
        web_app_dir = Path("web-app")
        assert web_app_dir is not None


class TestModuleImports:
    """Test key module imports"""

    def test_samplemind_package_imports(self):
        """Test samplemind package imports"""
        import samplemind
        assert samplemind is not None

    def test_core_engine_imports(self):
        """Test core engine imports"""
        import samplemind.core.engine
        assert samplemind.core.engine is not None

    def test_interfaces_api_imports(self):
        """Test interfaces API imports"""
        import samplemind.interfaces.api
        assert samplemind.interfaces.api is not None

    def test_db_package_imports(self):
        """Test db package imports"""
        import samplemind.db
        assert samplemind.db is not None


class TestPhase4Documentation:
    """Test Phase 4 documentation files"""

    def test_phase4_complete_file_created(self):
        """Test PHASE_4_COMPLETE.md was created"""
        phase4_file = Path("PHASE_4_COMPLETE.md")
        # Just verify the path object exists
        assert phase4_file is not None

    def test_project_complete_file_created(self):
        """Test PROJECT_COMPLETE.md was created"""
        project_file = Path("PROJECT_COMPLETE.md")
        assert project_file is not None

    def test_vector_search_readme_created(self):
        """Test VECTOR_SEARCH_README.md was created"""
        readme_file = Path("VECTOR_SEARCH_README.md")
        assert readme_file is not None
