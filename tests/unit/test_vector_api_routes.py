"""
Unit tests for Vector Search API Routes
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient


class TestVectorSearchRouteModels:
    """Test Pydantic models for vector search routes"""

    def test_index_file_request_model(self):
        """Test IndexFileRequest model"""
        from samplemind.interfaces.api.routes.vector_search import IndexFileRequest

        request = IndexFileRequest(
            file_path="/test/audio.wav",
            analysis_level="STANDARD",
            metadata={"genre": "electronic"}
        )

        assert request.file_path == "/test/audio.wav"
        assert request.analysis_level == "STANDARD"
        assert request.metadata["genre"] == "electronic"

    def test_index_directory_request_model(self):
        """Test IndexDirectoryRequest model"""
        from samplemind.interfaces.api.routes.vector_search import IndexDirectoryRequest

        request = IndexDirectoryRequest(
            directory="/test/samples",
            recursive=True,
            analysis_level="DETAILED"
        )

        assert request.directory == "/test/samples"
        assert request.recursive is True
        assert request.analysis_level == "DETAILED"

    def test_similar_search_request_model(self):
        """Test SimilarSearchRequest model"""
        from samplemind.interfaces.api.routes.vector_search import SimilarSearchRequest

        request = SimilarSearchRequest(
            file_path="/test/ref.wav",
            n_results=15,
            exclude_self=False
        )

        assert request.file_path == "/test/ref.wav"
        assert request.n_results == 15
        assert request.exclude_self is False

    def test_feature_search_request_model(self):
        """Test FeatureSearchRequest model"""
        from samplemind.interfaces.api.routes.vector_search import FeatureSearchRequest

        request = FeatureSearchRequest(
            features={"tempo": 120.0, "energy": 0.8},
            n_results=10,
            filter_metadata={"genre": "techno"}
        )

        assert request.features["tempo"] == 120.0
        assert request.n_results == 10
        assert request.filter_metadata["genre"] == "techno"

    def test_recommendation_request_model(self):
        """Test RecommendationRequest model"""
        from samplemind.interfaces.api.routes.vector_search import RecommendationRequest

        request = RecommendationRequest(
            file_path="/test/bass.wav",
            n_results=5,
            diversity=0.4
        )

        assert request.file_path == "/test/bass.wav"
        assert request.n_results == 5
        assert request.diversity == 0.4

    def test_similar_file_model(self):
        """Test SimilarFile response model"""
        from samplemind.interfaces.api.routes.vector_search import SimilarFile

        similar = SimilarFile(
            id="test_id",
            file_path="/test/similar.wav",
            metadata={"bpm": 128},
            distance=0.15,
            similarity=0.85
        )

        assert similar.id == "test_id"
        assert similar.file_path == "/test/similar.wav"
        assert similar.similarity == 0.85

    def test_recommendation_response_model(self):
        """Test RecommendationResponse model"""
        from samplemind.interfaces.api.routes.vector_search import RecommendationResponse, SimilarFile

        similar = [SimilarFile(
            id="1",
            file_path="/test/s1.wav",
            metadata={},
            distance=0.1,
            similarity=0.9
        )]

        response = RecommendationResponse(
            reference_file="/test/ref.wav",
            similar_samples=similar,
            complementary_samples=[],
            contrasting_samples=[],
            total_results=1
        )

        assert response.reference_file == "/test/ref.wav"
        assert len(response.similar_samples) == 1
        assert response.total_results == 1

    def test_n_results_validation(self):
        """Test n_results field validation"""
        from samplemind.interfaces.api.routes.vector_search import SimilarSearchRequest

        # Valid values
        request = SimilarSearchRequest(file_path="/test.wav", n_results=1)
        assert request.n_results == 1

        request = SimilarSearchRequest(file_path="/test.wav", n_results=50)
        assert request.n_results == 50

    def test_diversity_validation(self):
        """Test diversity field validation"""
        from samplemind.interfaces.api.routes.vector_search import RecommendationRequest

        # Valid values
        request = RecommendationRequest(file_path="/test.wav", diversity=0.0)
        assert request.diversity == 0.0

        request = RecommendationRequest(file_path="/test.wav", diversity=1.0)
        assert request.diversity == 1.0

        request = RecommendationRequest(file_path="/test.wav", diversity=0.5)
        assert request.diversity == 0.5


class TestVectorSearchAPIEndpoints:
    """Test vector search API endpoints with mocks"""

    @pytest.fixture
    def mock_embedding_service(self):
        """Mock embedding service"""
        with patch('samplemind.interfaces.api.routes.vector_search.get_embedding_service') as mock:
            service = Mock()
            service.index_audio_file = AsyncMock(return_value={
                'doc_id': 'test_doc',
                'file_path': '/test/audio.wav',
                'features': {},
                'status': 'indexed'
            })
            service.index_directory = AsyncMock(return_value={
                'total_files': 10,
                'indexed': 9,
                'failed': 1,
                'files': []
            })
            service.find_similar = AsyncMock(return_value=[])
            service.find_similar_by_features = AsyncMock(return_value=[])
            service.get_recommendations = AsyncMock(return_value={
                'reference_file': '/test/ref.wav',
                'similar_samples': [],
                'complementary_samples': [],
                'contrasting_samples': [],
                'total_results': 0
            })
            service.remove_from_index = AsyncMock(return_value=True)
            service.reindex_file = AsyncMock(return_value={'status': 'reindexed'})
            service.get_stats = Mock(return_value={'audio_count': 0})
            mock.return_value = service
            yield service

    def test_index_file_request_structure(self, mock_embedding_service):
        """Test index file request structure"""
        from samplemind.interfaces.api.routes.vector_search import IndexFileRequest

        request = IndexFileRequest(
            file_path="/test/audio.wav",
            analysis_level="STANDARD"
        )

        assert hasattr(request, 'file_path')
        assert hasattr(request, 'analysis_level')
        assert hasattr(request, 'metadata')

    def test_similar_file_response_structure(self):
        """Test similar file response structure"""
        from samplemind.interfaces.api.routes.vector_search import SimilarFile

        file = SimilarFile(
            id="test",
            file_path="/test.wav",
            metadata={},
            distance=0.1,
            similarity=0.9
        )

        # Verify all fields are accessible
        assert file.id
        assert file.file_path
        assert file.metadata is not None
        assert file.distance >= 0
        assert file.similarity >= 0
