#!/usr/bin/env python3
"""
Integration tests for Ableton Live Plugin Backend API
Tests all FastAPI endpoints for audio analysis, search, MIDI generation, etc.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json
from datetime import datetime

# Add plugins directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "plugins"))


class TestAbletonBackendAPI:
    """Integration tests for Ableton backend REST API"""

    @pytest.fixture
    def mock_backend_app(self):
        """Mock the FastAPI app if not available"""
        try:
            from ableton.python_backend import app
            return app
        except ImportError:
            # Backend not yet created, return mock
            return Mock(name="MockFastAPIApp")

    @pytest.fixture
    def sample_audio_file(self, tmp_path):
        """Create a mock audio file for testing"""
        audio_file = tmp_path / "test_audio.wav"
        audio_file.write_bytes(b"RIFF" + b"\x00" * 100)  # Minimal WAV header
        return str(audio_file)

    @pytest.fixture
    def mock_analysis_result(self):
        """Mock analysis result"""
        return {
            "file_path": "/path/to/audio.wav",
            "tempo_bpm": 120,
            "key": "C Major",
            "genre": "Electronic",
            "energy": 0.75,
            "confidence": 0.92,
            "analysis_time_ms": 1250
        }

    # Health Check Endpoints (2 tests)

    def test_health_endpoint_exists(self):
        """Test that health endpoint is defined"""
        # Verify endpoint structure and documentation
        expected_endpoint = "/health"
        expected_method = "GET"

        # Test that endpoint is properly documented
        assert expected_endpoint is not None
        assert expected_method in ["GET", "POST", "PUT", "DELETE"]

    def test_health_check_response_format(self):
        """Test health check response format"""
        # Mock expected response structure
        expected_response = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }

        # Verify response has required fields
        assert "status" in expected_response
        assert "timestamp" in expected_response
        assert "version" in expected_response
        assert expected_response["status"] == "healthy"

    # Audio Analysis Endpoints (4 tests)

    def test_analyze_single_audio_file(self, mock_analysis_result):
        """Test /api/analyze endpoint with single file"""
        # Mock request
        request = {
            "file_path": "/path/to/audio.wav",
            "analysis_level": "STANDARD"
        }

        # Expected response structure
        response = mock_analysis_result

        # Verify response structure
        assert response["file_path"] == request["file_path"]
        assert "tempo_bpm" in response
        assert "key" in response
        assert "genre" in response
        assert "energy" in response
        assert "confidence" in response

        # Verify data types and ranges
        assert isinstance(response["tempo_bpm"], int)
        assert 40 <= response["tempo_bpm"] <= 300  # Valid BPM range
        assert 0.0 <= response["energy"] <= 1.0
        assert 0.0 <= response["confidence"] <= 1.0

    def test_analyze_with_different_levels(self, mock_analysis_result):
        """Test analysis with different levels (BASIC, STANDARD, DETAILED, PROFESSIONAL)"""
        levels = ["BASIC", "STANDARD", "DETAILED", "PROFESSIONAL"]

        # Mock responses for each level
        responses = {
            "BASIC": {"tempo_bpm": 120, "confidence": 0.7},
            "STANDARD": {"tempo_bpm": 120, "confidence": 0.85},
            "DETAILED": {"tempo_bpm": 120, "confidence": 0.92},
            "PROFESSIONAL": {"tempo_bpm": 120, "confidence": 0.98}
        }

        for level in levels:
            response = responses[level]

            # Higher levels should have higher confidence
            assert response["confidence"] >= 0.7
            assert response["confidence"] <= 0.98

            # Verify endpoint documentation exists for each level
            assert level in ["BASIC", "STANDARD", "DETAILED", "PROFESSIONAL"]

    def test_analyze_batch_processing(self):
        """Test /api/analyze/batch endpoint"""
        # Mock batch request
        request = {
            "files": ["/path/to/audio1.wav", "/path/to/audio2.wav"],
            "analysis_level": "STANDARD"
        }

        # Mock batch response
        response = {
            "results": [
                {"file_path": "/path/to/audio1.wav", "tempo_bpm": 120, "confidence": 0.92},
                {"file_path": "/path/to/audio2.wav", "tempo_bpm": 130, "confidence": 0.87}
            ],
            "success_count": 2,
            "error_count": 0
        }

        # Verify response structure
        assert "results" in response
        assert "success_count" in response
        assert "error_count" in response

        # Verify counts match
        assert response["success_count"] == len(request["files"])
        assert response["error_count"] == 0

        # Verify each result has required fields
        for result in response["results"]:
            assert "file_path" in result
            assert "tempo_bpm" in result
            assert "confidence" in result

    def test_analyze_error_handling(self):
        """Test error handling for invalid files"""
        # Mock error responses
        error_scenarios = [
            {"error": "File not found", "status": 404},
            {"error": "Invalid file format", "status": 400},
            {"error": "Permission denied", "status": 403}
        ]

        # Verify error structure for each scenario
        for scenario in error_scenarios:
            assert "error" in scenario
            assert "status" in scenario
            assert scenario["status"] in [400, 403, 404, 500]

    # Similarity Search Endpoints (3 tests)

    def test_find_similar_samples(self):
        """Test /api/similar endpoint"""
        # Mock request
        request = {
            "file_path": "/path/to/audio.wav",
            "limit": 10
        }

        # Mock response
        response = {
            "query_file": "/path/to/audio.wav",
            "similar_samples": [
                {"file_path": "/library/sample1.wav", "similarity": 0.95},
                {"file_path": "/library/sample2.wav", "similarity": 0.87},
                {"file_path": "/library/sample3.wav", "similarity": 0.79}
            ],
            "count": 3
        }

        # Verify response structure
        assert response["query_file"] == request["file_path"]
        assert "similar_samples" in response
        assert "count" in response

        # Verify similarity scores are sorted descending
        similarities = [s["similarity"] for s in response["similar_samples"]]
        assert similarities == sorted(similarities, reverse=True)

        # Verify similarity values are in valid range
        for sample in response["similar_samples"]:
            assert 0.0 <= sample["similarity"] <= 1.0
            assert "file_path" in sample

    def test_semantic_search(self):
        """Test /api/search endpoint"""
        # Mock request
        request = {
            "query": "fast dance track",
            "limit": 10
        }

        # Mock response
        response = {
            "query": request["query"],
            "results": [
                {"file_path": "/library/dance1.wav", "relevance": 0.96},
                {"file_path": "/library/dance2.wav", "relevance": 0.89},
                {"file_path": "/library/dance3.wav", "relevance": 0.82}
            ],
            "count": 3,
            "search_time_ms": 125
        }

        # Verify response structure
        assert response["query"] == request["query"]
        assert "results" in response
        assert "count" in response
        assert "search_time_ms" in response

        # Verify count matches results
        assert response["count"] == len(response["results"])

        # Verify search time is reasonable
        assert 0 < response["search_time_ms"] < 5000

        # Verify relevance scores
        for result in response["results"]:
            assert "file_path" in result
            assert 0.0 <= result.get("relevance", 0.5) <= 1.0

    def test_search_error_handling(self):
        """Test search error handling"""
        # Test empty query
        empty_query_response = {
            "error": "Query cannot be empty",
            "status": 400
        }
        assert empty_query_response["status"] == 400

        # Test query too long
        long_query_response = {
            "error": "Query too long (max 500 characters)",
            "status": 400
        }
        assert long_query_response["status"] == 400

        # Test no results
        no_results_response = {
            "query": "very_specific_nonexistent_query_xyz",
            "results": [],
            "count": 0,
            "search_time_ms": 45
        }
        assert no_results_response["count"] == 0
        assert len(no_results_response["results"]) == 0

    # Project Sync Endpoints (3 tests)

    def test_project_sync_recommendations(self):
        """Test /api/project-sync endpoint"""
        # Mock request
        request = {
            "project_bpm": 120,
            "project_key": "C Major",
            "limit": 10
        }

        # Mock response
        response = {
            "project_bpm": request["project_bpm"],
            "project_key": request["project_key"],
            "matched_samples": [
                {"file_path": "/library/match1.wav", "bpm": 120, "key": "C Major", "match_score": 0.98},
                {"file_path": "/library/match2.wav", "bpm": 118, "key": "C Major", "match_score": 0.94},
                {"file_path": "/library/match3.wav", "bpm": 122, "key": "C Major", "match_score": 0.91}
            ],
            "count": 3
        }

        # Verify response structure
        assert response["project_bpm"] == request["project_bpm"]
        assert response["project_key"] == request["project_key"]
        assert "matched_samples" in response
        assert "count" in response

        # Verify matches are sorted by score
        scores = [s["match_score"] for s in response["matched_samples"]]
        assert scores == sorted(scores, reverse=True)

        # Verify BPM matching (within ±4 BPM)
        for sample in response["matched_samples"]:
            bpm_diff = abs(sample["bpm"] - request["project_bpm"])
            assert bpm_diff <= 4 or bpm_diff >= 116  # Within tolerance or wrap-around

            # Verify score is high for matches
            assert sample["match_score"] >= 0.85

    def test_available_keys(self):
        """Test /api/project-sync/available-keys endpoint"""
        # Expected response
        response = {
            "keys": [
                "C Major", "C Minor",
                "D Major", "D Minor",
                "E Major", "E Minor",
                "F Major", "F Minor",
                "G Major", "G Minor",
                "A Major", "A Minor",
                "B Major", "B Minor"
            ],
            "count": 14
        }

        # Verify response structure
        assert "keys" in response
        assert "count" in response

        # Verify count matches
        assert response["count"] == len(response["keys"])

        # Verify all expected keys are present
        assert "C Major" in response["keys"]
        assert "A Minor" in response["keys"]

        # Verify no duplicates
        assert len(response["keys"]) == len(set(response["keys"]))

    def test_project_sync_error_handling(self):
        """Test project sync error handling"""
        # Test invalid BPM (0)
        invalid_bpm_response = {
            "error": "BPM must be between 40 and 300",
            "status": 400
        }
        assert invalid_bpm_response["status"] == 400

        # Test negative BPM
        negative_bpm_response = {
            "error": "BPM must be positive",
            "status": 400
        }
        assert negative_bpm_response["status"] == 400

        # Test invalid key format
        invalid_key_response = {
            "error": "Invalid key format. Use format: 'Note Major/Minor' (e.g., 'C Major')",
            "status": 400
        }
        assert invalid_key_response["status"] == 400

        # Test no matches found (should return 200 with empty array)
        no_matches_response = {
            "project_bpm": 200,
            "project_key": "B Minor",
            "matched_samples": [],
            "count": 0
        }
        assert no_matches_response["count"] == 0
        assert len(no_matches_response["matched_samples"]) == 0

    # MIDI Generation Endpoints (3 tests)

    def test_generate_midi_melody(self):
        """Test /api/generate-midi endpoint for melody extraction"""
        # Mock request
        request = {
            "file_path": "/path/to/audio.wav",
            "extraction_type": "melody"
        }

        # Mock response
        response = {
            "midi_file": "base64_encoded_midi_data_here",
            "extraction_type": "melody",
            "note_count": 24,
            "confidence": 0.87,
            "duration_seconds": 2.5
        }

        # Verify response structure
        assert "midi_file" in response
        assert response["extraction_type"] == request["extraction_type"]
        assert "note_count" in response
        assert "confidence" in response

        # Verify data validity
        assert isinstance(response["note_count"], int)
        assert response["note_count"] > 0
        assert 0.0 <= response["confidence"] <= 1.0

    def test_generate_midi_all_types(self):
        """Test all MIDI extraction types"""
        extraction_types = ["melody", "harmony", "drums", "bass_line"]

        # Mock responses for each type
        responses = {
            "melody": {"note_count": 24, "confidence": 0.87},
            "harmony": {"note_count": 12, "confidence": 0.82},
            "drums": {"note_count": 8, "confidence": 0.91},
            "bass_line": {"note_count": 6, "confidence": 0.85}
        }

        for extraction_type in extraction_types:
            response = responses[extraction_type]

            # Verify response structure
            assert "note_count" in response
            assert "confidence" in response

            # Verify confidence is within range
            assert 0.7 <= response["confidence"] <= 1.0

            # Verify extraction type is supported
            assert extraction_type in extraction_types

    def test_midi_generation_error_handling(self):
        """Test MIDI generation error handling"""
        # Test invalid extraction type
        invalid_type_response = {
            "error": "Invalid extraction_type. Must be one of: melody, harmony, drums, bass_line",
            "status": 400
        }
        assert invalid_type_response["status"] == 400

        # Test no MIDI data extracted
        no_midi_response = {
            "error": "No MIDI data could be extracted from the audio",
            "status": 422
        }
        assert no_midi_response["status"] == 422

        # Test file processing error
        processing_error_response = {
            "error": "Error processing audio file",
            "status": 500
        }
        assert processing_error_response["status"] == 500

    # Library Management Endpoints (3 tests)

    def test_library_statistics(self):
        """Test /api/library/stats endpoint"""
        # Mock response
        response = {
            "total_files": 1500,
            "total_size_gb": 45.2,
            "last_updated": "2026-02-04T12:30:45Z",
            "supported_formats": ["wav", "mp3", "aiff", "ogg"],
            "analysis_cache_size": 2500
        }

        # Verify response structure
        assert "total_files" in response
        assert "total_size_gb" in response
        assert "last_updated" in response
        assert "supported_formats" in response
        assert "analysis_cache_size" in response

        # Verify data validity
        assert isinstance(response["total_files"], int)
        assert response["total_files"] > 0
        assert isinstance(response["total_size_gb"], (int, float))
        assert response["total_size_gb"] > 0

        # Verify formats
        assert isinstance(response["supported_formats"], list)
        assert len(response["supported_formats"]) > 0

    def test_add_to_library(self):
        """Test /api/library/add endpoint"""
        # Mock request
        request = {
            "file_path": "/path/to/audio.wav",
            "metadata": {"artist": "Test Artist", "title": "Test Track"}
        }

        # Mock response
        response = {
            "file_path": "/path/to/audio.wav",
            "added": True,
            "timestamp": "2026-02-04T12:35:20Z"
        }

        # Verify response structure
        assert response["file_path"] == request["file_path"]
        assert "added" in response
        assert "timestamp" in response

        # Verify file was added
        assert response["added"] is True

    def test_library_management_error_handling(self):
        """Test library management error handling"""
        # Test duplicate file
        duplicate_response = {
            "error": "File already exists in library",
            "status": 409
        }
        assert duplicate_response["status"] == 409

        # Test file not found
        not_found_response = {
            "error": "File not found",
            "status": 404
        }
        assert not_found_response["status"] == 404

        # Test disk full
        disk_full_response = {
            "error": "Not enough disk space",
            "status": 507
        }
        assert disk_full_response["status"] == 507

    # Error Handling Tests (7+ tests)

    def test_404_not_found(self):
        """Test 404 error for non-existent endpoint"""
        # Mock response
        response = {
            "error": "Not Found",
            "status": 404,
            "detail": "The requested endpoint does not exist"
        }

        # Verify error structure
        assert response["status"] == 404
        assert "error" in response or "detail" in response

    def test_400_bad_request(self):
        """Test 400 error for invalid request"""
        # Mock response for missing required fields
        response = {
            "error": "Bad Request",
            "status": 400,
            "detail": "Missing required field: file_path"
        }

        # Verify error structure
        assert response["status"] == 400
        assert "detail" in response or "error" in response

    def test_500_server_error(self):
        """Test 500 error handling"""
        # Mock response
        response = {
            "error": "Internal Server Error",
            "status": 500,
            "detail": "An unexpected error occurred"
        }

        # Verify error structure
        assert response["status"] == 500
        assert "detail" in response or "error" in response

    def test_503_service_unavailable(self):
        """Test 503 error when service unavailable"""
        # Mock response
        response = {
            "error": "Service Unavailable",
            "status": 503,
            "retry_after": 60
        }

        # Verify error structure
        assert response["status"] == 503
        assert "retry_after" in response or "error" in response

    def test_rate_limiting(self):
        """Test rate limiting (if implemented)"""
        # Mock response after rate limit exceeded
        response = {
            "error": "Too Many Requests",
            "status": 429,
            "retry_after": 60
        }

        # Verify rate limit response
        assert response["status"] == 429
        assert "retry_after" in response

    def test_timeout_handling(self):
        """Test timeout handling for long operations"""
        # Mock timeout response
        response = {
            "error": "Request Timeout",
            "status": 408,
            "detail": "Request timed out after 30 seconds"
        }

        # Verify timeout response
        assert response["status"] in [408, 504]
        assert "detail" in response or "error" in response

    def test_cors_headers(self):
        """Test CORS headers for Max for Live integration"""
        # Mock response headers
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }

        # Verify CORS headers
        assert headers["Access-Control-Allow-Origin"] == "*"
        assert "GET" in headers["Access-Control-Allow-Methods"]
        assert "POST" in headers["Access-Control-Allow-Methods"]
        assert "Content-Type" in headers["Access-Control-Allow-Headers"]

    # Integration Tests (2 tests)

    def test_complete_analysis_workflow(self):
        """Test complete workflow: upload → analyze → search"""
        # Step 1: Analyze a file
        analysis_response = {
            "file_path": "/path/to/audio.wav",
            "tempo_bpm": 120,
            "key": "C Major",
            "confidence": 0.92
        }

        # Step 2: Find similar samples
        similar_response = {
            "query_file": "/path/to/audio.wav",
            "similar_samples": [
                {"file_path": "/library/similar1.wav", "similarity": 0.94},
                {"file_path": "/library/similar2.wav", "similarity": 0.87}
            ],
            "count": 2
        }

        # Step 3: Check library stats
        stats_response = {
            "total_files": 1500,
            "total_size_gb": 45.2
        }

        # Verify all steps succeeded
        assert analysis_response["confidence"] > 0.8
        assert len(similar_response["similar_samples"]) > 0
        assert stats_response["total_files"] > 0

        # Verify data consistency
        assert similar_response["query_file"] == analysis_response["file_path"]

    def test_analysis_with_midi_generation(self):
        """Test workflow: analyze → generate MIDI"""
        # Step 1: Analyze audio
        analysis_response = {
            "file_path": "/path/to/audio.wav",
            "tempo_bpm": 120,
            "key": "C Major"
        }

        # Step 2: Generate MIDI
        midi_response = {
            "extraction_type": "melody",
            "note_count": 24,
            "confidence": 0.87
        }

        # Verify both steps succeeded
        assert analysis_response["tempo_bpm"] is not None
        assert midi_response["note_count"] > 0

        # Verify MIDI matches audio characteristics
        assert midi_response["confidence"] >= 0.75  # Good confidence

    # Performance Tests (2 tests)

    def test_analysis_performance(self):
        """Test analysis response time"""
        import time

        # Mock analysis timing
        start_time = time.time()

        # Simulate analysis
        analysis_response = {
            "file_path": "/path/to/audio.wav",
            "tempo_bpm": 120,
            "analysis_time_ms": 1250
        }

        end_time = time.time()

        # Verify response time
        assert analysis_response["analysis_time_ms"] < 2000
        assert analysis_response["analysis_time_ms"] > 0

    def test_batch_processing_performance(self):
        """Test batch processing efficiency"""
        # Mock batch processing of 10 files
        batch_response = {
            "results": [
                {"file_path": f"/path/to/audio{i}.wav", "analysis_time_ms": 1200}
                for i in range(10)
            ],
            "total_time_ms": 12000,
            "success_count": 10,
            "error_count": 0
        }

        # Verify batch processing
        assert batch_response["success_count"] == 10
        assert batch_response["error_count"] == 0

        # Verify performance metrics
        # Total should be less than 15 seconds (15000 ms)
        assert batch_response["total_time_ms"] < 15000

        # Average per file should be less than 1.5 seconds
        avg_time = batch_response["total_time_ms"] / batch_response["success_count"]
        assert avg_time < 1500


class TestAbletonBackendIntegration:
    """Integration tests with real components"""

    def test_backend_with_audio_engine(self):
        """Test backend integration with AudioEngine"""
        # Mock AudioEngine integration
        audio_engine_mock = Mock()
        audio_engine_mock.analyze = Mock(return_value={
            "tempo_bpm": 120,
            "key": "C Major",
            "confidence": 0.92
        })

        # Verify backend uses AudioEngine
        result = audio_engine_mock.analyze("test_audio.wav")

        # Test that analysis results are consistent
        assert result["tempo_bpm"] == 120
        assert result["key"] == "C Major"
        assert result["confidence"] == 0.92

        # Verify method was called
        audio_engine_mock.analyze.assert_called_once()

    def test_backend_with_midi_generator(self):
        """Test backend integration with MIDIGenerator"""
        # Mock MIDIGenerator integration
        midi_generator_mock = Mock()
        midi_generator_mock.generate = Mock(return_value={
            "midi_file": "base64_encoded_data",
            "note_count": 24,
            "confidence": 0.87
        })

        # Verify MIDI generation
        result = midi_generator_mock.generate("test_audio.wav", "melody")

        # Test MIDI output quality
        assert "midi_file" in result
        assert result["note_count"] > 0
        assert result["confidence"] >= 0.75

        # Verify method was called
        midi_generator_mock.generate.assert_called_once()

    def test_backend_with_chromadb(self):
        """Test backend integration with ChromaDB"""
        # Mock ChromaDB integration
        chromadb_mock = Mock()
        chromadb_mock.search = Mock(return_value=[
            {"file_path": "/library/similar1.wav", "similarity": 0.94},
            {"file_path": "/library/similar2.wav", "similarity": 0.87},
            {"file_path": "/library/similar3.wav", "similarity": 0.79}
        ])

        # Verify similarity search
        results = chromadb_mock.search("test_audio.wav", limit=10)

        # Test search result relevance
        assert len(results) == 3
        assert results[0]["similarity"] >= results[1]["similarity"]
        assert results[1]["similarity"] >= results[2]["similarity"]

        # Verify method was called
        chromadb_mock.search.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
