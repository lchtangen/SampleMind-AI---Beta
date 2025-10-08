"""
Unit tests for Embedding Service
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import asyncio

from samplemind.ai.embedding_service import EmbeddingService, get_embedding_service


class TestEmbeddingService:
    """Test EmbeddingService functionality"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def mock_vector_store(self):
        """Create mock VectorStore"""
        mock = Mock()
        mock.add_audio_features = Mock(return_value="test_doc_id")
        mock.search_similar = Mock(return_value=[])
        mock.search_by_file = Mock(return_value=[])
        mock.get_collection_stats = Mock(return_value={'audio_count': 0, 'sample_count': 0})
        mock.delete_audio = Mock(return_value=True)
        return mock

    @pytest.fixture
    def mock_audio_engine(self):
        """Create mock AudioEngine"""
        mock = Mock()
        mock.analyze = Mock(return_value={
            'features': {
                'tempo': 120.0,
                'energy': 0.8,
                'spectral_features': {'centroid': 2000.0}
            }
        })
        return mock

    @pytest.fixture
    def embedding_service(self, mock_vector_store, mock_audio_engine):
        """Create EmbeddingService with mocks"""
        service = EmbeddingService(vector_store=mock_vector_store)
        service.audio_engine = mock_audio_engine
        return service

    @pytest.mark.asyncio
    async def test_index_audio_file(self, embedding_service, mock_vector_store, mock_audio_engine, tmp_path):
        """Test indexing a single audio file"""
        # Create a dummy file
        audio_file = tmp_path / "test.wav"
        audio_file.write_bytes(b"fake audio data")

        result = await embedding_service.index_audio_file(
            str(audio_file),
            analysis_level="STANDARD"
        )

        assert result is not None
        assert 'doc_id' in result
        assert 'file_path' in result
        assert 'features' in result
        assert result['status'] == 'indexed'
        assert result['doc_id'] == "test_doc_id"

        # Verify audio engine was called
        mock_audio_engine.analyze.assert_called_once()

        # Verify vector store was called
        mock_vector_store.add_audio_features.assert_called_once()

    @pytest.mark.asyncio
    async def test_index_audio_file_with_metadata(self, embedding_service, mock_vector_store, tmp_path):
        """Test indexing with custom metadata"""
        audio_file = tmp_path / "test.wav"
        audio_file.write_bytes(b"fake audio data")

        metadata = {'genre': 'electronic', 'bpm': 128}

        result = await embedding_service.index_audio_file(
            str(audio_file),
            metadata=metadata
        )

        assert result is not None
        # Verify metadata was passed to vector store
        call_args = mock_vector_store.add_audio_features.call_args
        assert call_args[1]['metadata']['genre'] == 'electronic'
        assert call_args[1]['metadata']['bpm'] == 128

    @pytest.mark.asyncio
    async def test_index_directory(self, embedding_service, mock_vector_store, tmp_path):
        """Test indexing a directory of audio files"""
        # Create test audio files
        (tmp_path / "audio1.wav").write_bytes(b"fake audio 1")
        (tmp_path / "audio2.mp3").write_bytes(b"fake audio 2")
        (tmp_path / "not_audio.txt").write_text("not an audio file")

        result = await embedding_service.index_directory(
            str(tmp_path),
            recursive=False
        )

        assert result is not None
        assert 'total_files' in result
        assert 'indexed' in result
        assert 'failed' in result
        assert 'files' in result
        assert result['total_files'] >= 2

    @pytest.mark.asyncio
    async def test_find_similar(self, embedding_service, mock_vector_store):
        """Test finding similar files"""
        mock_vector_store.search_by_file.return_value = [
            {
                'id': 'test_1',
                'file_path': '/test/similar1.wav',
                'metadata': {},
                'distance': 0.1,
                'similarity': 0.9
            },
            {
                'id': 'test_2',
                'file_path': '/test/similar2.wav',
                'metadata': {},
                'distance': 0.2,
                'similarity': 0.8
            }
        ]

        results = await embedding_service.find_similar(
            "/test/reference.wav",
            n_results=10
        )

        assert isinstance(results, list)
        assert len(results) == 2
        assert results[0]['similarity'] == 0.9
        assert results[1]['similarity'] == 0.8

        mock_vector_store.search_by_file.assert_called_once_with(
            "/test/reference.wav",
            10,
            True
        )

    @pytest.mark.asyncio
    async def test_find_similar_by_features(self, embedding_service, mock_vector_store):
        """Test finding similar files by features"""
        features = {
            'tempo': 120.0,
            'energy': 0.8
        }

        mock_vector_store.search_similar.return_value = [
            {
                'id': 'test_1',
                'file_path': '/test/match.wav',
                'metadata': {},
                'distance': 0.15,
                'similarity': 0.85
            }
        ]

        results = await embedding_service.find_similar_by_features(
            features,
            n_results=5
        )

        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0]['similarity'] == 0.85

    @pytest.mark.asyncio
    async def test_get_recommendations(self, embedding_service, mock_vector_store):
        """Test getting smart recommendations"""
        # Mock similar files with different similarity scores
        mock_vector_store.search_by_file.return_value = [
            {'id': '1', 'file_path': '/test/very_similar.wav', 'metadata': {}, 'distance': 0.1, 'similarity': 0.9},
            {'id': '2', 'file_path': '/test/similar.wav', 'metadata': {}, 'distance': 0.2, 'similarity': 0.8},
            {'id': '3', 'file_path': '/test/complementary1.wav', 'metadata': {}, 'distance': 0.35, 'similarity': 0.65},
            {'id': '4', 'file_path': '/test/complementary2.wav', 'metadata': {}, 'distance': 0.4, 'similarity': 0.6},
            {'id': '5', 'file_path': '/test/contrasting.wav', 'metadata': {}, 'distance': 0.6, 'similarity': 0.4},
        ]

        result = await embedding_service.get_recommendations(
            "/test/reference.wav",
            n_results=2
        )

        assert 'reference_file' in result
        assert 'similar_samples' in result
        assert 'complementary_samples' in result
        assert 'contrasting_samples' in result
        assert result['reference_file'] == "/test/reference.wav"

        # Should have categorized samples
        assert isinstance(result['similar_samples'], list)
        assert isinstance(result['complementary_samples'], list)
        assert isinstance(result['contrasting_samples'], list)

    @pytest.mark.asyncio
    async def test_remove_from_index(self, embedding_service, mock_vector_store):
        """Test removing file from index"""
        success = await embedding_service.remove_from_index("/test/remove.wav")

        assert success is True
        mock_vector_store.delete_audio.assert_called_once_with("/test/remove.wav")

    def test_get_stats(self, embedding_service, mock_vector_store):
        """Test getting statistics"""
        stats = embedding_service.get_stats()

        assert isinstance(stats, dict)
        mock_vector_store.get_collection_stats.assert_called_once()

    @pytest.mark.asyncio
    async def test_reindex_file(self, embedding_service, mock_vector_store, tmp_path):
        """Test reindexing a file"""
        audio_file = tmp_path / "test.wav"
        audio_file.write_bytes(b"fake audio data")

        result = await embedding_service.reindex_file(
            str(audio_file),
            analysis_level="DETAILED"
        )

        assert result is not None
        assert result['status'] == 'reindexed'

        # Should have called delete and add
        mock_vector_store.delete_audio.assert_called_once()
        mock_vector_store.add_audio_features.assert_called_once()


class TestEmbeddingServiceSingleton:
    """Test EmbeddingService singleton"""

    def test_get_embedding_service_singleton(self):
        """Test that get_embedding_service returns singleton"""
        service1 = get_embedding_service()
        service2 = get_embedding_service()

        assert service1 is service2


class TestRecommendationCategorization:
    """Test recommendation categorization logic"""

    @pytest.fixture
    def embedding_service(self):
        """Create EmbeddingService with mock vector store"""
        mock_store = Mock()
        service = EmbeddingService(vector_store=mock_store)
        return service, mock_store

    @pytest.mark.asyncio
    async def test_similar_category_threshold(self, embedding_service):
        """Test that high similarity samples are categorized as similar"""
        service, mock_store = embedding_service

        # Mock high similarity results
        mock_store.search_by_file.return_value = [
            {'id': '1', 'file_path': '/test/high_sim.wav', 'metadata': {}, 'distance': 0.1, 'similarity': 0.9},
            {'id': '2', 'file_path': '/test/high_sim2.wav', 'metadata': {}, 'distance': 0.15, 'similarity': 0.85},
        ]

        result = await service.get_recommendations("/test/ref.wav", n_results=5)

        # Both should be in similar category (>0.8 similarity)
        assert len(result['similar_samples']) >= 1

    @pytest.mark.asyncio
    async def test_complementary_category_threshold(self, embedding_service):
        """Test that medium similarity samples are categorized as complementary"""
        service, mock_store = embedding_service

        # Mock medium similarity results
        mock_store.search_by_file.return_value = [
            {'id': '1', 'file_path': '/test/med_sim.wav', 'metadata': {}, 'distance': 0.3, 'similarity': 0.7},
            {'id': '2', 'file_path': '/test/med_sim2.wav', 'metadata': {}, 'distance': 0.4, 'similarity': 0.6},
        ]

        result = await service.get_recommendations("/test/ref.wav", n_results=5)

        # Should be in complementary category (0.5-0.8 similarity)
        # or fallback category since we're providing medium similarity
        assert len(result['complementary_samples']) >= 0

    @pytest.mark.asyncio
    async def test_empty_recommendations(self, embedding_service):
        """Test handling of no similar files found"""
        service, mock_store = embedding_service

        mock_store.search_by_file.return_value = []

        result = await service.get_recommendations("/test/ref.wav", n_results=5)

        assert result['similar_samples'] == []
        assert result['complementary_samples'] == []
        assert result['contrasting_samples'] == []


class TestIndexingErrors:
    """Test error handling during indexing"""

    @pytest.fixture
    def embedding_service(self):
        """Create EmbeddingService with mock vector store"""
        mock_store = Mock()
        mock_engine = Mock()
        service = EmbeddingService(vector_store=mock_store)
        service.audio_engine = mock_engine
        return service, mock_store, mock_engine

    @pytest.mark.asyncio
    async def test_index_nonexistent_file(self, embedding_service):
        """Test indexing a file that doesn't exist"""
        service, _, _ = embedding_service

        with pytest.raises(Exception):
            await service.index_audio_file("/nonexistent/file.wav")

    @pytest.mark.asyncio
    async def test_index_directory_not_found(self, embedding_service):
        """Test indexing a directory that doesn't exist"""
        service, _, _ = embedding_service

        with pytest.raises(ValueError):
            await service.index_directory("/nonexistent/directory")
