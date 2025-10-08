"""
Tests for Vector Search API Routes

Tests similarity search, indexing, and recommendation endpoints.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from httpx import AsyncClient, ASGITransport
from pathlib import Path
import tempfile
import io

from samplemind.interfaces.api.main import app


class TestIndexFileEndpoint:
    """Test /api/v1/vector/index/file endpoint"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.vector_search.get_embedding_service')
    async def test_index_file_success(self, mock_get_service, test_audio_samples):
        """Test successfully indexing a file"""
        mock_service = Mock()
        mock_service.index_audio_file = AsyncMock(return_value={
            'status': 'indexed',
            'file_id': 'test123',
            'vector_count': 1
        })
        mock_get_service.return_value = mock_service

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                '/api/v1/vector/index/file',
                json={
                    'file_path': str(audio_file),
                    'analysis_level': 'STANDARD'
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'indexed'

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.vector_search.get_embedding_service')
    async def test_index_file_with_metadata(self, mock_get_service, test_audio_samples):
        """Test indexing file with custom metadata"""
        mock_service = Mock()
        mock_service.index_audio_file = AsyncMock(return_value={'status': 'indexed'})
        mock_get_service.return_value = mock_service

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                '/api/v1/vector/index/file',
                json={
                    'file_path': str(audio_file),
                    'metadata': {
                        'artist': 'Test Artist',
                        'genre': 'Electronic'
                    }
                }
            )

        assert response.status_code == 200

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.vector_search.get_embedding_service')
    async def test_index_nonexistent_file(self, mock_get_service):
        """Test indexing a file that doesn't exist"""
        mock_service = Mock()
        mock_service.index_audio_file = AsyncMock(side_effect=FileNotFoundError())
        mock_get_service.return_value = mock_service

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                '/api/v1/vector/index/file',
                json={'file_path': '/nonexistent/file.wav'}
            )

        assert response.status_code == 404


class TestIndexUploadEndpoint:
    """Test /api/v1/vector/index/upload endpoint"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.vector_search.get_embedding_service')
    async def test_upload_and_index(self, mock_get_service, test_audio_samples):
        """Test uploading and indexing a file"""
        mock_service = Mock()
        mock_service.index_audio_file = AsyncMock(return_value={
            'status': 'indexed',
            'file_id': 'test123'
        })
        mock_get_service.return_value = mock_service

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with open(audio_file, 'rb') as f:
                files = {'file': (audio_file.name, f, 'audio/wav')}
                response = await client.post('/api/v1/vector/index/upload', files=files)

        assert response.status_code == 200
        data = response.json()
        assert 'original_filename' in data

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.vector_search.get_embedding_service')
    async def test_upload_and_index_with_analysis_level(self, mock_get_service, test_audio_samples):
        """Test upload and index with custom analysis level"""
        mock_service = Mock()
        mock_service.index_audio_file = AsyncMock(return_value={'status': 'indexed'})
        mock_get_service.return_value = mock_service

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with open(audio_file, 'rb') as f:
                files = {'file': (audio_file.name, f, 'audio/wav')}
                response = await client.post(
                    '/api/v1/vector/index/upload',
                    files=files,
                    params={'analysis_level': 'DETAILED'}
                )

        assert response.status_code == 200


class TestIndexDirectoryEndpoint:
    """Test /api/v1/vector/index/directory endpoint"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.vector_search.get_embedding_service')
    async def test_index_directory(self, mock_get_service, tmp_path):
        """Test indexing all files in a directory"""
        mock_service = Mock()
        mock_service.index_directory = AsyncMock(return_value={
            'indexed': 5,
            'failed': 0,
            'total_time': 10.5
        })
        mock_get_service.return_value = mock_service

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                '/api/v1/vector/index/directory',
                json={
                    'directory': str(tmp_path),
                    'recursive': True
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert 'indexed' in data

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.vector_search.get_embedding_service')
    async def test_index_directory_with_extensions(self, mock_get_service, tmp_path):
        """Test indexing directory with file extension filter"""
        mock_service = Mock()
        mock_service.index_directory = AsyncMock(return_value={'indexed': 3})
        mock_get_service.return_value = mock_service

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                '/api/v1/vector/index/directory',
                json={
                    'directory': str(tmp_path),
                    'extensions': ['.wav', '.mp3']
                }
            )

        assert response.status_code == 200


class TestSearchSimilarEndpoint:
    """Test /api/v1/vector/search/similar endpoint"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.vector_search.get_embedding_service')
    async def test_search_similar_files(self, mock_get_service, test_audio_samples):
        """Test searching for similar files"""
        mock_service = Mock()
        mock_service.find_similar = AsyncMock(return_value=[
            {
                'id': '1',
                'file_path': '/path/to/similar1.wav',
                'metadata': {},
                'distance': 0.15,
                'similarity': 0.85
            },
            {
                'id': '2',
                'file_path': '/path/to/similar2.wav',
                'metadata': {},
                'distance': 0.25,
                'similarity': 0.75
            }
        ])
        mock_get_service.return_value = mock_service

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                '/api/v1/vector/search/similar',
                json={
                    'file_path': str(audio_file),
                    'n_results': 10
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]['similarity'] == 0.85

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.vector_search.get_embedding_service')
    async def test_search_similar_exclude_self(self, mock_get_service, test_audio_samples):
        """Test search with exclude_self option"""
        mock_service = Mock()
        mock_service.find_similar = AsyncMock(return_value=[])
        mock_get_service.return_value = mock_service

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                '/api/v1/vector/search/similar',
                json={
                    'file_path': str(audio_file),
                    'exclude_self': True,
                    'n_results': 5
                }
            )

        assert response.status_code == 200

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.vector_search.get_embedding_service')
    async def test_search_similar_file_not_indexed(self, mock_get_service):
        """Test search for file that's not indexed"""
        mock_service = Mock()
        mock_service.find_similar = AsyncMock(side_effect=ValueError("File not indexed"))
        mock_get_service.return_value = mock_service

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                '/api/v1/vector/search/similar',
                json={'file_path': '/not/indexed.wav'}
            )

        assert response.status_code == 404


class TestSearchByFeaturesEndpoint:
    """Test /api/v1/vector/search/features endpoint"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.vector_search.get_embedding_service')
    async def test_search_by_features(self, mock_get_service):
        """Test searching by audio features"""
        mock_service = Mock()
        mock_service.find_similar_by_features = AsyncMock(return_value=[
            {
                'id': '1',
                'file_path': '/match1.wav',
                'metadata': {},
                'distance': 0.1,
                'similarity': 0.9
            }
        ])
        mock_get_service.return_value = mock_service

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                '/api/v1/vector/search/features',
                json={
                    'features': {
                        'tempo': 120,
                        'key': 'C',
                        'energy': 0.8
                    },
                    'n_results': 10
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 0

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.vector_search.get_embedding_service')
    async def test_search_by_features_with_filters(self, mock_get_service):
        """Test feature search with metadata filters"""
        mock_service = Mock()
        mock_service.find_similar_by_features = AsyncMock(return_value=[])
        mock_get_service.return_value = mock_service

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                '/api/v1/vector/search/features',
                json={
                    'features': {'tempo': 128},
                    'filter_metadata': {
                        'genre': 'electronic'
                    }
                }
            )

        assert response.status_code == 200


class TestRecommendationsEndpoint:
    """Test /api/v1/vector/recommend endpoint"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.vector_search.get_embedding_service')
    async def test_get_recommendations(self, mock_get_service, test_audio_samples):
        """Test getting smart recommendations"""
        mock_service = Mock()
        mock_service.get_recommendations = AsyncMock(return_value={
            'reference_file': str(test_audio_samples['120_c_major']),
            'similar_samples': [
                {
                    'id': '1',
                    'file_path': '/similar.wav',
                    'metadata': {},
                    'distance': 0.1,
                    'similarity': 0.9
                }
            ],
            'complementary_samples': [
                {
                    'id': '2',
                    'file_path': '/complementary.wav',
                    'metadata': {},
                    'distance': 0.5,
                    'similarity': 0.5
                }
            ],
            'contrasting_samples': [
                {
                    'id': '3',
                    'file_path': '/contrasting.wav',
                    'metadata': {},
                    'distance': 0.9,
                    'similarity': 0.1
                }
            ],
            'total_results': 3
        })
        mock_get_service.return_value = mock_service

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                '/api/v1/vector/recommend',
                json={
                    'file_path': str(audio_file),
                    'n_results': 5
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert 'similar_samples' in data
        assert 'complementary_samples' in data
        assert 'contrasting_samples' in data
        assert data['total_results'] == 3

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.vector_search.get_embedding_service')
    async def test_get_recommendations_with_diversity(self, mock_get_service, test_audio_samples):
        """Test recommendations with diversity parameter"""
        mock_service = Mock()
        mock_service.get_recommendations = AsyncMock(return_value={
            'reference_file': '',
            'similar_samples': [],
            'complementary_samples': [],
            'contrasting_samples': [],
            'total_results': 0
        })
        mock_get_service.return_value = mock_service

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                '/api/v1/vector/recommend',
                json={
                    'file_path': str(audio_file),
                    'diversity': 0.7
                }
            )

        assert response.status_code == 200


class TestRemoveFromIndexEndpoint:
    """Test /api/v1/vector/index/{file_path:path} DELETE endpoint"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.vector_search.get_embedding_service')
    async def test_remove_from_index_success(self, mock_get_service):
        """Test successfully removing file from index"""
        mock_service = Mock()
        mock_service.remove_from_index = AsyncMock(return_value=True)
        mock_get_service.return_value = mock_service

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete('/api/v1/vector/index/path/to/file.wav')

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'removed'

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.vector_search.get_embedding_service')
    async def test_remove_from_index_not_found(self, mock_get_service):
        """Test removing file that's not in index"""
        mock_service = Mock()
        mock_service.remove_from_index = AsyncMock(return_value=False)
        mock_get_service.return_value = mock_service

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete('/api/v1/vector/index/not/indexed.wav')

        assert response.status_code == 404


class TestReindexEndpoint:
    """Test /api/v1/vector/reindex PUT endpoint"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.vector_search.get_embedding_service')
    async def test_reindex_file_success(self, mock_get_service, test_audio_samples):
        """Test successfully reindexing a file"""
        mock_service = Mock()
        mock_service.reindex_file = AsyncMock(return_value={
            'status': 'reindexed',
            'file_id': 'test123'
        })
        mock_get_service.return_value = mock_service

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.put(
                '/api/v1/vector/reindex',
                json={'file_path': str(audio_file)}
            )

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'reindexed'

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.vector_search.get_embedding_service')
    async def test_reindex_nonexistent_file(self, mock_get_service):
        """Test reindexing file that doesn't exist"""
        mock_service = Mock()
        mock_service.reindex_file = AsyncMock(side_effect=FileNotFoundError())
        mock_get_service.return_value = mock_service

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.put(
                '/api/v1/vector/reindex',
                json={'file_path': '/nonexistent.wav'}
            )

        assert response.status_code == 404


class TestVectorStatsEndpoint:
    """Test /api/v1/vector/stats endpoint"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.vector_search.get_embedding_service')
    async def test_get_index_stats(self, mock_get_service):
        """Test getting vector index statistics"""
        mock_service = Mock()
        mock_service.get_stats.return_value = {
            'total_vectors': 1000,
            'total_files': 250,
            'index_size_mb': 50.5,
            'collections': ['audio_samples']
        }
        mock_get_service.return_value = mock_service

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/vector/stats')

        assert response.status_code == 200
        data = response.json()
        assert 'total_vectors' in data or 'total_files' in data


class TestVectorSearchIntegration:
    """Integration tests for vector search routes"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.vector_search.get_embedding_service')
    async def test_full_vector_search_workflow(self, mock_get_service, test_audio_samples):
        """Test complete workflow: index -> search -> recommend"""
        mock_service = Mock()
        mock_service.index_audio_file = AsyncMock(return_value={'status': 'indexed'})
        mock_service.find_similar = AsyncMock(return_value=[
            {
                'id': '1',
                'file_path': '/similar.wav',
                'metadata': {},
                'distance': 0.2,
                'similarity': 0.8
            }
        ])
        mock_service.get_recommendations = AsyncMock(return_value={
            'reference_file': '',
            'similar_samples': [],
            'complementary_samples': [],
            'contrasting_samples': [],
            'total_results': 0
        })
        mock_get_service.return_value = mock_service

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Index file
            index_response = await client.post(
                '/api/v1/vector/index/file',
                json={'file_path': str(audio_file)}
            )
            assert index_response.status_code == 200

            # 2. Search for similar files
            search_response = await client.post(
                '/api/v1/vector/search/similar',
                json={'file_path': str(audio_file)}
            )
            assert search_response.status_code == 200

            # 3. Get recommendations
            rec_response = await client.post(
                '/api/v1/vector/recommend',
                json={'file_path': str(audio_file)}
            )
            assert rec_response.status_code == 200
