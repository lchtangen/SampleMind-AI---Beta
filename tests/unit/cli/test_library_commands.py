"""
Comprehensive unit tests for library management commands (25+ tests)

Tests cover:
- Library organization (scan, import, organize, export)
- Search and filtering (search, filter by BPM, key, genre, tag)
- Collections (create, add, list, export)
- Library cleanup (dedupe, cleanup, verify)
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typer.testing import CliRunner

pytestmark = [pytest.mark.unit, pytest.mark.cli]


class TestLibraryOrganizationCommands:
    """Test library organization commands (scan, import, organize, export)"""

    def test_library_scan_directory(self, typer_runner, test_audio_samples):
        """Test library:scan command - Scan and index directory"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.scan_library_async') as mock_scan:
            mock_scan.return_value = {
                'total_files': 2,
                'indexed': 2,
                'skipped': 0
            }

            result = runner.invoke(app, ["library:scan", str(test_audio_samples["120_c_major"].parent)])

        assert result.exit_code == 0

    def test_library_scan_empty_directory(self, typer_runner, temp_directory):
        """Test library:scan with empty directory"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.scan_library_async') as mock_scan:
            mock_scan.return_value = {
                'total_files': 0,
                'indexed': 0,
                'skipped': 0
            }

            result = runner.invoke(app, ["library:scan", str(temp_directory)])

        assert result.exit_code == 0

    def test_library_organize_by_metadata(self, typer_runner, test_audio_samples):
        """Test library:organize command - Auto-organize by metadata"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.organize_library_async') as mock_org:
            mock_org.return_value = {
                'organized': 2,
                'failed': 0,
                'structure': 'by_genre/by_bpm'
            }

            result = runner.invoke(app, [
                "library:organize", str(test_audio_samples["120_c_major"].parent),
                "--structure", "by_genre"
            ])

        assert result.exit_code == 0

    def test_library_import_with_metadata(self, typer_runner, test_audio_samples):
        """Test library:import command - Import with metadata"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.import_library_async') as mock_import:
            mock_import.return_value = {
                'imported': 2,
                'with_metadata': 2,
                'without_metadata': 0
            }

            result = runner.invoke(app, ["library:import", str(test_audio_samples["120_c_major"].parent)])

        assert result.exit_code == 0

    def test_library_export_with_metadata(self, typer_runner, test_audio_samples, temp_directory):
        """Test library:export command - Export with metadata"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        output_dir = temp_directory / "export"

        with patch('samplemind.interfaces.cli.commands.utils.export_library_async') as mock_export:
            mock_export.return_value = {
                'exported': 2,
                'format': 'json',
                'location': str(output_dir)
            }

            result = runner.invoke(app, [
                "library:export", str(test_audio_samples["120_c_major"].parent),
                "--output", str(output_dir)
            ])

        assert result.exit_code == 0

    def test_library_sync_cloud(self, typer_runner):
        """Test library:sync command - Cloud sync"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.sync_library_async') as mock_sync:
            mock_sync.return_value = {
                'synced': 5,
                'conflicts': 0,
                'timestamp': '2025-01-19T12:00:00Z'
            }

            result = runner.invoke(app, ["library:sync"])

        assert result.exit_code == 0


class TestLibrarySearchAndFilterCommands:
    """Test search and filtering commands"""

    def test_library_search_query(self, typer_runner):
        """Test library:search command - Full-text search"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.search_library_async') as mock_search:
            mock_search.return_value = {
                'query': 'drum',
                'results': 5,
                'matches': [
                    {'file': 'drum_loop_1.wav', 'score': 0.95},
                    {'file': 'drum_hit.wav', 'score': 0.87}
                ]
            }

            result = runner.invoke(app, ["library:search", "drum"])

        assert result.exit_code == 0

    def test_library_filter_by_bpm(self, typer_runner):
        """Test library:filter:bpm command - Filter by BPM range"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.filter_by_bpm_async') as mock_filter:
            mock_filter.return_value = {
                'min_bpm': 100,
                'max_bpm': 130,
                'matches': 3
            }

            result = runner.invoke(app, [
                "library:filter:bpm",
                "--min", "100",
                "--max", "130"
            ])

        assert result.exit_code == 0

    def test_library_filter_by_key(self, typer_runner):
        """Test library:filter:key command - Filter by key"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.filter_by_key_async') as mock_filter:
            mock_filter.return_value = {
                'key': 'C',
                'mode': 'major',
                'matches': 4
            }

            result = runner.invoke(app, [
                "library:filter:key",
                "--key", "C",
                "--mode", "major"
            ])

        assert result.exit_code == 0

    def test_library_filter_by_genre(self, typer_runner):
        """Test library:filter:genre command - Filter by genre"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.filter_by_genre_async') as mock_filter:
            mock_filter.return_value = {
                'genre': 'electronic',
                'matches': 7,
                'confidence_threshold': 0.8
            }

            result = runner.invoke(app, [
                "library:filter:genre",
                "--genre", "electronic"
            ])

        assert result.exit_code == 0

    def test_library_filter_by_tag(self, typer_runner):
        """Test library:filter:tag command - Filter by tag"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.filter_by_tag_async') as mock_filter:
            mock_filter.return_value = {
                'tag': 'favorites',
                'matches': 10
            }

            result = runner.invoke(app, [
                "library:filter:tag",
                "--tag", "favorites"
            ])

        assert result.exit_code == 0

    def test_library_search_similar_samples(self, typer_runner, test_audio_samples):
        """Test library:find-similar command - Find similar samples"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.find_similar_async') as mock_similar:
            mock_similar.return_value = {
                'query_file': audio_file.name,
                'similar_count': 3,
                'threshold': 0.8
            }

            result = runner.invoke(app, [
                "library:find-similar", str(audio_file),
                "--limit", "10"
            ])

        assert result.exit_code == 0


class TestLibraryCollectionCommands:
    """Test collection management commands"""

    def test_collection_create(self, typer_runner):
        """Test collection:create command - Create new collection"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.create_collection_async') as mock_create:
            mock_create.return_value = {
                'collection_name': 'my_collection',
                'id': 'coll_123',
                'created': '2025-01-19T12:00:00Z'
            }

            result = runner.invoke(app, [
                "collection:create",
                "--name", "my_collection",
                "--description", "My sample collection"
            ])

        assert result.exit_code == 0

    def test_collection_add_sample(self, typer_runner, test_audio_samples):
        """Test collection:add command - Add sample to collection"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.add_to_collection_async') as mock_add:
            mock_add.return_value = {
                'collection': 'my_collection',
                'added': 1,
                'total': 5
            }

            result = runner.invoke(app, [
                "collection:add",
                "--collection", "my_collection",
                str(audio_file)
            ])

        assert result.exit_code == 0

    def test_collection_list(self, typer_runner):
        """Test collection:list command - List collections"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.list_collections_async') as mock_list:
            mock_list.return_value = {
                'total': 3,
                'collections': [
                    {'name': 'favorites', 'size': 10},
                    {'name': 'my_collection', 'size': 5}
                ]
            }

            result = runner.invoke(app, ["collection:list"])

        assert result.exit_code == 0

    def test_collection_export(self, typer_runner, temp_directory):
        """Test collection:export command - Export collection"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        output_file = temp_directory / "collection_export.zip"

        with patch('samplemind.interfaces.cli.commands.utils.export_collection_async') as mock_export:
            mock_export.return_value = {
                'collection': 'my_collection',
                'exported_files': 5,
                'location': str(output_file)
            }

            result = runner.invoke(app, [
                "collection:export",
                "--collection", "my_collection",
                "--output", str(output_file)
            ])

        assert result.exit_code == 0


class TestLibraryCleanupCommands:
    """Test library cleanup and maintenance commands"""

    def test_library_deduplicate(self, typer_runner, test_audio_samples):
        """Test library:dedupe command - Find duplicates"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.dedupe_library_async') as mock_dedupe:
            mock_dedupe.return_value = {
                'total_files': 10,
                'duplicates_found': 2,
                'suggested_removals': 2
            }

            result = runner.invoke(app, [
                "library:dedupe",
                str(test_audio_samples["120_c_major"].parent)
            ])

        assert result.exit_code == 0

    def test_library_cleanup_broken_files(self, typer_runner, test_audio_samples):
        """Test library:cleanup command - Remove broken files"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.cleanup_library_async') as mock_cleanup:
            mock_cleanup.return_value = {
                'scanned': 10,
                'broken_files': 1,
                'removed': 1
            }

            result = runner.invoke(app, [
                "library:cleanup",
                str(test_audio_samples["120_c_major"].parent)
            ])

        assert result.exit_code == 0

    def test_library_verify_integrity(self, typer_runner, test_audio_samples):
        """Test library:verify command - Verify file integrity"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.verify_library_async') as mock_verify:
            mock_verify.return_value = {
                'total_files': 10,
                'valid': 10,
                'corrupted': 0,
                'integrity_score': 1.0
            }

            result = runner.invoke(app, [
                "library:verify",
                str(test_audio_samples["120_c_major"].parent)
            ])

        assert result.exit_code == 0

    def test_library_rebuild_index(self, typer_runner, test_audio_samples):
        """Test library:rebuild-index command - Rebuild library index"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.rebuild_index_async') as mock_rebuild:
            mock_rebuild.return_value = {
                'files_indexed': 10,
                'index_entries': 10,
                'rebuild_time': 1.23
            }

            result = runner.invoke(app, ["library:rebuild-index"])

        assert result.exit_code == 0


class TestLibraryErrorHandling:
    """Test error handling in library commands"""

    def test_library_scan_invalid_directory(self, typer_runner):
        """Test library:scan with invalid directory"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        result = runner.invoke(app, ["library:scan", "/nonexistent/directory"])

        assert result.exit_code != 0

    def test_library_search_empty_query(self, typer_runner):
        """Test library:search with empty query"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        result = runner.invoke(app, ["library:search", ""])

        assert result.exit_code != 0 or "empty" in result.stdout.lower()

    def test_library_collection_not_found(self, typer_runner, test_audio_samples):
        """Test collection:add with non-existent collection"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.add_to_collection_async') as mock_add:
            mock_add.side_effect = Exception("Collection not found")

            result = runner.invoke(app, [
                "collection:add",
                "--collection", "nonexistent",
                str(audio_file)
            ])

        assert result.exit_code != 0

    def test_library_filter_invalid_bpm_range(self, typer_runner):
        """Test library:filter:bpm with invalid range"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        result = runner.invoke(app, [
            "library:filter:bpm",
            "--min", "200",
            "--max", "100"  # min > max
        ])

        # Should fail or warn about invalid range
        assert result.exit_code != 0 or "invalid" in result.stdout.lower()


class TestLibraryPerformance:
    """Test performance characteristics of library commands"""

    @pytest.mark.performance
    def test_library_scan_performance(self, typer_runner, test_audio_samples, performance_timer):
        """Test library:scan completes quickly"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.scan_library_async') as mock_scan:
            mock_scan.return_value = {'total_files': 10, 'indexed': 10, 'skipped': 0}

            result, elapsed = performance_timer.time_operation(
                runner.invoke,
                app, ["library:scan", str(test_audio_samples["120_c_major"].parent)]
            )

        # Scanning should be reasonably fast
        assert elapsed < 30.0, f"Scan took {elapsed:.2f}s, target <30s"

    @pytest.mark.performance
    def test_library_search_performance(self, typer_runner, performance_timer):
        """Test library:search completes quickly"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.search_library_async') as mock_search:
            mock_search.return_value = {'query': 'drum', 'results': 5}

            result, elapsed = performance_timer.time_operation(
                runner.invoke,
                app, ["library:search", "drum"]
            )

        # Search should be instant
        assert elapsed < 2.0, f"Search took {elapsed:.2f}s, target <2s"
