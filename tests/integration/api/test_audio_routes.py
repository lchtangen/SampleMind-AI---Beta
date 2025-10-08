"""
Tests for Audio API Routes

Tests audio file upload, analysis, and listing endpoints.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pathlib import Path
from httpx import AsyncClient, ASGITransport
from fastapi import UploadFile
import tempfile
import io

from samplemind.interfaces.api.main import app
from samplemind.core.engine.audio_engine import AnalysisLevel


class TestAudioUploadEndpoint:
    """Test /api/v1/audio/upload endpoint"""

    @pytest.mark.asyncio
    async def test_upload_valid_audio_file(self, test_audio_samples):
        """Test uploading a valid audio file"""
        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with open(audio_file, 'rb') as f:
                files = {'file': (audio_file.name, f, 'audio/wav')}
                response = await client.post('/api/v1/audio/upload', files=files)

        assert response.status_code == 200
        data = response.json()
        assert 'file_id' in data
        assert data['filename'] == audio_file.name
        assert data['file_size'] > 0

    @pytest.mark.asyncio
    async def test_upload_invalid_file_type(self):
        """Test uploading an invalid file type"""
        # Create fake text file
        fake_file = io.BytesIO(b"This is not an audio file")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            files = {'file': ('test.txt', fake_file, 'text/plain')}
            response = await client.post('/api/v1/audio/upload', files=files)

        assert response.status_code in [400, 422]  # Validation error

    @pytest.mark.asyncio
    async def test_upload_file_too_large(self):
        """Test uploading a file that exceeds size limit"""
        # Create large fake file (simulate 200MB)
        large_data = b'0' * (200 * 1024 * 1024)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            files = {'file': ('large.wav', io.BytesIO(large_data), 'audio/wav')}
            response = await client.post('/api/v1/audio/upload', files=files)

        assert response.status_code in [400, 422]  # Should reject large files

    @pytest.mark.asyncio
    async def test_upload_multiple_files_sequentially(self, test_audio_samples):
        """Test uploading multiple files"""
        files_to_upload = [
            test_audio_samples['120_c_major'],
            test_audio_samples['140_a_minor']
        ]

        file_ids = []

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            for audio_file in files_to_upload:
                with open(audio_file, 'rb') as f:
                    files = {'file': (audio_file.name, f, 'audio/wav')}
                    response = await client.post('/api/v1/audio/upload', files=files)

                    assert response.status_code == 200
                    data = response.json()
                    file_ids.append(data['file_id'])

        # All file IDs should be unique
        assert len(file_ids) == len(set(file_ids))

    @pytest.mark.asyncio
    async def test_upload_without_file(self):
        """Test upload endpoint without providing a file"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post('/api/v1/audio/upload')

        assert response.status_code in [400, 422]  # Validation error

    @pytest.mark.asyncio
    async def test_upload_mp3_file(self, tmp_path):
        """Test uploading MP3 file"""
        # Create minimal MP3-like file
        mp3_file = tmp_path / "test.mp3"
        mp3_file.write_bytes(b"fake mp3 data")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with open(mp3_file, 'rb') as f:
                files = {'file': ('test.mp3', f, 'audio/mp3')}
                response = await client.post('/api/v1/audio/upload', files=files)

        # MP3 might be allowed or rejected depending on settings
        assert response.status_code in [200, 422]


class TestAudioAnalysisEndpoint:
    """Test /api/v1/audio/analyze/{file_id} endpoint"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.audio.get_app_state')
    async def test_analyze_uploaded_file_basic(self, mock_get_app_state, test_audio_samples):
        """Test basic analysis of uploaded file"""
        # Mock audio engine
        mock_engine = Mock()
        mock_features = Mock()
        mock_features.duration = 10.0
        mock_features.tempo = 120.0
        mock_features.key = 'C'
        mock_features.mode = 'major'
        mock_features.time_signature = (4, 4)
        mock_features.spectral_centroid = 1500.0
        mock_features.spectral_bandwidth = 2000.0
        mock_features.to_dict.return_value = {}
        mock_engine.analyze_audio.return_value = mock_features

        mock_get_app_state.side_effect = lambda key: mock_engine if key == 'audio_engine' else None

        # First upload file
        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Upload
            with open(audio_file, 'rb') as f:
                files = {'file': (audio_file.name, f, 'audio/wav')}
                upload_response = await client.post('/api/v1/audio/upload', files=files)

            file_id = upload_response.json()['file_id']

            # Analyze
            response = await client.post(
                f'/api/v1/audio/analyze/{file_id}',
                params={'analysis_level': 'basic'}
            )

        assert response.status_code == 200
        data = response.json()
        assert data['file_id'] == file_id
        assert data['tempo'] == 120.0
        assert data['key'] == 'C'
        assert data['mode'] == 'major'

    @pytest.mark.asyncio
    async def test_analyze_nonexistent_file(self):
        """Test analyzing a file that doesn't exist"""
        fake_file_id = 'nonexistent-file-id'

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f'/api/v1/audio/analyze/{fake_file_id}',
                params={'analysis_level': 'basic'}
            )

        assert response.status_code == 404

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.audio.get_app_state')
    async def test_analyze_with_ai_integration(self, mock_get_app_state, test_audio_samples):
        """Test analysis with AI integration"""
        # Mock audio engine
        mock_engine = Mock()
        mock_features = Mock()
        mock_features.duration = 10.0
        mock_features.tempo = 120.0
        mock_features.key = 'C'
        mock_features.mode = 'major'
        mock_features.time_signature = (4, 4)
        mock_features.spectral_centroid = 1500.0
        mock_features.spectral_bandwidth = 2000.0
        mock_features.to_dict.return_value = {}
        mock_engine.analyze_audio.return_value = mock_features

        # Mock AI manager
        mock_ai_manager = Mock()
        # Create a simple object with to_dict method
        class MockAIResult:
            def to_dict(self):
                return {
                    'summary': 'Upbeat track',
                    'production_tips': ['Add compression']
                }

        mock_ai_result = MockAIResult()
        mock_ai_manager.analyze_music = AsyncMock(return_value=mock_ai_result)

        def state_getter(key):
            if key == 'audio_engine':
                return mock_engine
            elif key == 'ai_manager':
                return mock_ai_manager
            return None

        mock_get_app_state.side_effect = state_getter

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Upload
            with open(audio_file, 'rb') as f:
                files = {'file': (audio_file.name, f, 'audio/wav')}
                upload_response = await client.post('/api/v1/audio/upload', files=files)

            file_id = upload_response.json()['file_id']

            # Analyze with AI
            response = await client.post(
                f'/api/v1/audio/analyze/{file_id}',
                params={
                    'analysis_level': 'detailed',
                    'include_ai': True,
                    'ai_provider': 'openai'
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert 'ai_analysis' in data
        assert data['ai_analysis'] is not None

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.audio.get_app_state')
    async def test_analyze_different_levels(self, mock_get_app_state, test_audio_samples):
        """Test analysis with different analysis levels"""
        mock_engine = Mock()
        mock_features = Mock()
        mock_features.duration = 10.0
        mock_features.tempo = 120.0
        mock_features.key = 'C'
        mock_features.mode = 'major'
        mock_features.time_signature = (4, 4)
        mock_features.spectral_centroid = 1500.0
        mock_features.spectral_bandwidth = 2000.0
        mock_features.to_dict.return_value = {}
        mock_engine.analyze_audio.return_value = mock_features

        mock_get_app_state.side_effect = lambda key: mock_engine if key == 'audio_engine' else None

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Upload once
            with open(audio_file, 'rb') as f:
                files = {'file': (audio_file.name, f, 'audio/wav')}
                upload_response = await client.post('/api/v1/audio/upload', files=files)

            file_id = upload_response.json()['file_id']

            # Test each analysis level
            for level in ['basic', 'standard', 'detailed']:
                response = await client.post(
                    f'/api/v1/audio/analyze/{file_id}',
                    params={'analysis_level': level}
                )

                assert response.status_code == 200
                data = response.json()
                assert data['analysis_level'] == level


class TestListAudioFilesEndpoint:
    """Test /api/v1/audio/files endpoint"""

    @pytest.mark.asyncio
    async def test_list_empty_files(self):
        """Test listing files when no files uploaded"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/audio/files')

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_list_files_with_pagination(self, test_audio_samples):
        """Test file listing with pagination"""
        # Upload several files first
        file_ids = []

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            for i in range(5):
                audio_file = test_audio_samples['120_c_major']
                with open(audio_file, 'rb') as f:
                    files = {'file': (f'test_{i}.wav', f, 'audio/wav')}
                    upload_response = await client.post('/api/v1/audio/upload', files=files)
                    file_ids.append(upload_response.json()['file_id'])

            # List with pagination
            response = await client.get('/api/v1/audio/files', params={'page': 1, 'page_size': 2})

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 2  # Should respect page_size

    @pytest.mark.asyncio
    async def test_list_files_page_size_limits(self):
        """Test that page_size is limited"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Try with very large page size
            response = await client.get('/api/v1/audio/files', params={'page': 1, 'page_size': 1000})

        # Should either limit to max or return validation error
        assert response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_list_files_invalid_page(self):
        """Test listing files with invalid page number"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/audio/files', params={'page': 0, 'page_size': 10})

        # Page must be >= 1
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_files_metadata(self, test_audio_samples):
        """Test that file listing includes metadata"""
        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Upload
            with open(audio_file, 'rb') as f:
                files = {'file': (audio_file.name, f, 'audio/wav')}
                await client.post('/api/v1/audio/upload', files=files)

            # List and check metadata
            response = await client.get('/api/v1/audio/files')

        assert response.status_code == 200
        data = response.json()

        if len(data) > 0:
            file_info = data[0]
            assert 'file_id' in file_info
            assert 'filename' in file_info
            assert 'file_size' in file_info
            assert 'uploaded_at' in file_info


class TestAudioRoutesErrorHandling:
    """Test error handling in audio routes"""

    @pytest.mark.asyncio
    async def test_upload_corrupted_file(self):
        """Test uploading corrupted audio file"""
        # Create fake corrupted WAV file
        corrupted_data = b'RIFF' + b'\x00' * 100  # Incomplete WAV header

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            files = {'file': ('corrupted.wav', io.BytesIO(corrupted_data), 'audio/wav')}
            response = await client.post('/api/v1/audio/upload', files=files)

        # Should either accept (just stores bytes) or reject
        assert response.status_code in [200, 422, 500]

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.audio.get_app_state')
    async def test_analyze_with_engine_error(self, mock_get_app_state, test_audio_samples):
        """Test analysis when audio engine throws error"""
        mock_engine = Mock()
        mock_engine.analyze_audio.side_effect = Exception("Analysis failed")

        mock_get_app_state.side_effect = lambda key: mock_engine if key == 'audio_engine' else None

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Upload
            with open(audio_file, 'rb') as f:
                files = {'file': (audio_file.name, f, 'audio/wav')}
                upload_response = await client.post('/api/v1/audio/upload', files=files)

            file_id = upload_response.json()['file_id']

            # Analyze - should handle error gracefully
            response = await client.post(
                f'/api/v1/audio/analyze/{file_id}',
                params={'analysis_level': 'basic'}
            )

        assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_analyze_invalid_file_id_format(self):
        """Test analysis with malformed file ID"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                '/api/v1/audio/analyze/invalid-id-format',
                params={'analysis_level': 'basic'}
            )

        assert response.status_code == 404


class TestAudioRoutesIntegration:
    """Integration tests for audio routes"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.audio.get_app_state')
    async def test_full_upload_analyze_workflow(self, mock_get_app_state, test_audio_samples):
        """Test complete workflow: upload -> analyze -> list"""
        # Setup mocks
        mock_engine = Mock()
        mock_features = Mock()
        mock_features.duration = 10.0
        mock_features.tempo = 120.0
        mock_features.key = 'C'
        mock_features.mode = 'major'
        mock_features.time_signature = (4, 4)
        mock_features.spectral_centroid = 1500.0
        mock_features.spectral_bandwidth = 2000.0
        mock_features.to_dict.return_value = {}
        mock_engine.analyze_audio.return_value = mock_features

        mock_get_app_state.side_effect = lambda key: mock_engine if key == 'audio_engine' else None

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Upload
            with open(audio_file, 'rb') as f:
                files = {'file': (audio_file.name, f, 'audio/wav')}
                upload_response = await client.post('/api/v1/audio/upload', files=files)

            assert upload_response.status_code == 200
            file_id = upload_response.json()['file_id']

            # 2. Analyze
            analyze_response = await client.post(
                f'/api/v1/audio/analyze/{file_id}',
                params={'analysis_level': 'standard'}
            )

            assert analyze_response.status_code == 200
            analysis_data = analyze_response.json()
            assert analysis_data['file_id'] == file_id

            # 3. List files
            list_response = await client.get('/api/v1/audio/files')

            assert list_response.status_code == 200
            files_list = list_response.json()
            assert isinstance(files_list, list)
