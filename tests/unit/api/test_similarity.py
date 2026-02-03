"""
Tests for Similarity Search API
"""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from samplemind.interfaces.api.routes.similarity import router
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestSimilarityAPI:
    """Test similarity search endpoints"""
    
    @patch('samplemind.interfaces.api.routes.similarity.audio_engine')
    @patch('samplemind.interfaces.api.routes.similarity.query_similar')
    def test_find_similar_audio(self, mock_query, mock_engine):
        """Test similarity search endpoint"""
        # Mock audio engine
        mock_features = Mock()
        mock_features.to_dict.return_value = {"tempo": 120, "key": "C"}
        mock_engine.analyze_audio.return_value = mock_features
        
        # Mock query results
        mock_query.return_value = [
            {
                "id": "file1",
                "file_path": "/path/to/file1.wav",
                "similarity": 0.95,
                "metadata": {"tempo": 120}
            },
            {
                "id": "file2",
                "file_path": "/path/to/file2.wav",
                "similarity": 0.85,
                "metadata": {"tempo": 118}
            }
        ]
        
        # Create test file
        test_file = ("test.wav", b"fake audio data", "audio/wav")
        
        # Make request
        response = client.post(
            "/similarity/search",
            files={"file": test_file},
            params={"limit": 10, "min_similarity": 0.7}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["query_file"] == "test.wav"
        assert data["total_results"] == 2
        assert len(data["results"]) == 2
        assert data["results"][0]["similarity_score"] == 0.95
    
    @patch('samplemind.interfaces.api.routes.similarity.audio_engine')
    @patch('samplemind.interfaces.api.routes.similarity.add_audio_to_collection')
    def test_index_audio_file(self, mock_add, mock_engine):
        """Test audio indexing endpoint"""
        # Mock audio engine
        mock_features = Mock()
        mock_features.to_dict.return_value = {"tempo": 120}
        mock_engine.analyze_audio.return_value = mock_features
        
        # Mock add to collection
        mock_add.return_value = "file_id_123"
        
        # Create test file
        test_file = ("test.wav", b"fake audio data", "audio/wav")
        
        # Make request
        response = client.post(
            "/similarity/index",
            files={"file": test_file}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "indexed"
        assert data["file_id"] == "file_id_123"
        assert data["file_name"] == "test.wav"
    
    @patch('samplemind.interfaces.api.routes.similarity.get_collection_stats')
    def test_get_stats(self, mock_stats):
        """Test stats endpoint"""
        mock_stats.return_value = {
            "count": 100,
            "name": "audio_features",
            "dimensions": 128
        }
        
        response = client.get("/similarity/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_indexed"] == 100
        assert data["collection_name"] == "audio_features"
        assert data["dimensions"] == 128
