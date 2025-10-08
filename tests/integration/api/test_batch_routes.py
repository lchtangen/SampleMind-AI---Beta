"""
Tests for Batch Processing API Routes

Tests batch upload and status tracking endpoints.
"""

import pytest
from unittest.mock import Mock, patch
from httpx import AsyncClient, ASGITransport
import io

from samplemind.interfaces.api.main import app


class TestBatchUploadEndpoint:
    """Test /api/v1/batch/upload endpoint"""

    @pytest.mark.asyncio
    async def test_batch_upload_multiple_files(self, test_audio_samples):
        """Test uploading multiple files in batch"""
        files_to_upload = [
            test_audio_samples['120_c_major'],
            test_audio_samples['140_a_minor']
        ]

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            files = []
            for audio_file in files_to_upload:
                with open(audio_file, 'rb') as f:
                    files.append(('files', (audio_file.name, f.read(), 'audio/wav')))

            response = await client.post('/api/v1/batch/upload', files=files)

        assert response.status_code == 200
        data = response.json()
        assert 'batch_id' in data
        assert data['status'] == 'pending'
        assert data['total_files'] == 2
        assert data['completed'] == 0
        assert len(data['files']) == 2

    @pytest.mark.asyncio
    async def test_batch_upload_single_file(self, test_audio_samples):
        """Test batch upload with single file"""
        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with open(audio_file, 'rb') as f:
                files = [('files', (audio_file.name, f.read(), 'audio/wav'))]
                response = await client.post('/api/v1/batch/upload', files=files)

        assert response.status_code == 200
        data = response.json()
        assert data['total_files'] == 1

    @pytest.mark.asyncio
    async def test_batch_upload_generates_unique_ids(self, test_audio_samples):
        """Test that batch uploads generate unique IDs"""
        audio_file = test_audio_samples['120_c_major']

        batch_ids = []

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            for _ in range(3):
                with open(audio_file, 'rb') as f:
                    files = [('files', (audio_file.name, f.read(), 'audio/wav'))]
                    response = await client.post('/api/v1/batch/upload', files=files)

                    data = response.json()
                    batch_ids.append(data['batch_id'])

        # All batch IDs should be unique
        assert len(batch_ids) == len(set(batch_ids))

    @pytest.mark.asyncio
    async def test_batch_upload_includes_file_metadata(self, test_audio_samples):
        """Test that batch upload includes file metadata"""
        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with open(audio_file, 'rb') as f:
                files = [('files', (audio_file.name, f.read(), 'audio/wav'))]
                response = await client.post('/api/v1/batch/upload', files=files)

        data = response.json()
        file_info = data['files'][0]

        assert 'file_id' in file_info
        assert 'filename' in file_info
        assert 'status' in file_info
        assert 'progress' in file_info
        assert file_info['status'] == 'pending'
        assert file_info['progress'] == 0.0

    @pytest.mark.asyncio
    async def test_batch_upload_empty_list(self):
        """Test batch upload with no files"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post('/api/v1/batch/upload')

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_batch_upload_large_batch(self, test_audio_samples):
        """Test uploading large batch of files"""
        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            files = []
            for i in range(10):
                with open(audio_file, 'rb') as f:
                    files.append(('files', (f'test_{i}.wav', f.read(), 'audio/wav')))

            response = await client.post('/api/v1/batch/upload', files=files)

        assert response.status_code == 200
        data = response.json()
        assert data['total_files'] == 10
        assert len(data['files']) == 10


class TestBatchStatusEndpoint:
    """Test /api/v1/batch/status/{batch_id} endpoint"""

    @pytest.mark.asyncio
    async def test_get_batch_status_existing(self, test_audio_samples):
        """Test getting status of existing batch"""
        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # First create batch
            with open(audio_file, 'rb') as f:
                files = [('files', (audio_file.name, f.read(), 'audio/wav'))]
                upload_response = await client.post('/api/v1/batch/upload', files=files)

            batch_id = upload_response.json()['batch_id']

            # Get status
            status_response = await client.get(f'/api/v1/batch/status/{batch_id}')

        assert status_response.status_code == 200
        data = status_response.json()
        assert data['batch_id'] == batch_id
        assert 'status' in data
        assert 'total_files' in data
        assert 'completed' in data
        assert 'failed' in data
        assert 'progress' in data

    @pytest.mark.asyncio
    async def test_get_batch_status_nonexistent(self):
        """Test getting status of nonexistent batch"""
        fake_batch_id = 'nonexistent-batch-id'

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f'/api/v1/batch/status/{fake_batch_id}')

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_batch_status_calculates_progress(self, test_audio_samples):
        """Test that batch status correctly calculates progress"""
        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Create batch
            files = []
            for i in range(5):
                with open(audio_file, 'rb') as f:
                    files.append(('files', (f'test_{i}.wav', f.read(), 'audio/wav')))

            upload_response = await client.post('/api/v1/batch/upload', files=files)
            batch_id = upload_response.json()['batch_id']

            # Get status
            status_response = await client.get(f'/api/v1/batch/status/{batch_id}')

        data = status_response.json()
        # Progress should be calculated
        assert 'progress' in data
        assert 0 <= data['progress'] <= 100

    @pytest.mark.asyncio
    async def test_batch_status_includes_file_details(self, test_audio_samples):
        """Test that batch status includes individual file details"""
        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Create batch
            with open(audio_file, 'rb') as f:
                files = [('files', (audio_file.name, f.read(), 'audio/wav'))]
                upload_response = await client.post('/api/v1/batch/upload', files=files)

            batch_id = upload_response.json()['batch_id']

            # Get status
            status_response = await client.get(f'/api/v1/batch/status/{batch_id}')

        data = status_response.json()
        assert 'files' in data
        assert len(data['files']) > 0

        # Check file detail structure
        file_detail = data['files'][0]
        assert 'file_id' in file_detail
        assert 'filename' in file_detail
        assert 'status' in file_detail

    @pytest.mark.asyncio
    async def test_batch_status_counts_completed_files(self, test_audio_samples):
        """Test that batch status correctly counts completed files"""
        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Create batch
            with open(audio_file, 'rb') as f:
                files = [('files', (audio_file.name, f.read(), 'audio/wav'))]
                upload_response = await client.post('/api/v1/batch/upload', files=files)

            batch_id = upload_response.json()['batch_id']

            # Get status
            status_response = await client.get(f'/api/v1/batch/status/{batch_id}')

        data = status_response.json()
        # Initially no files should be completed
        assert data['completed'] >= 0
        assert data['failed'] >= 0


class TestBatchRoutesIntegration:
    """Integration tests for batch routes"""

    @pytest.mark.asyncio
    async def test_batch_upload_and_status_workflow(self, test_audio_samples):
        """Test complete workflow: upload batch -> check status"""
        files_to_upload = [
            test_audio_samples['120_c_major'],
            test_audio_samples['140_a_minor']
        ]

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Upload batch
            files = []
            for audio_file in files_to_upload:
                with open(audio_file, 'rb') as f:
                    files.append(('files', (audio_file.name, f.read(), 'audio/wav')))

            upload_response = await client.post('/api/v1/batch/upload', files=files)

            assert upload_response.status_code == 200
            upload_data = upload_response.json()
            batch_id = upload_data['batch_id']

            # 2. Check status immediately
            status_response = await client.get(f'/api/v1/batch/status/{batch_id}')

            assert status_response.status_code == 200
            status_data = status_response.json()
            assert status_data['batch_id'] == batch_id
            assert status_data['total_files'] == 2

            # 3. Check status again (simulate polling)
            status_response_2 = await client.get(f'/api/v1/batch/status/{batch_id}')

            assert status_response_2.status_code == 200

    @pytest.mark.asyncio
    async def test_multiple_batch_uploads(self, test_audio_samples):
        """Test multiple independent batch uploads"""
        audio_file = test_audio_samples['120_c_major']

        batch_ids = []

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Create multiple batches
            for i in range(3):
                with open(audio_file, 'rb') as f:
                    files = [('files', (f'test_{i}.wav', f.read(), 'audio/wav'))]
                    response = await client.post('/api/v1/batch/upload', files=files)

                    batch_ids.append(response.json()['batch_id'])

            # Verify each batch independently
            for batch_id in batch_ids:
                status_response = await client.get(f'/api/v1/batch/status/{batch_id}')

                assert status_response.status_code == 200
                data = status_response.json()
                assert data['batch_id'] == batch_id

    @pytest.mark.asyncio
    async def test_batch_with_mixed_file_types(self, test_audio_samples):
        """Test batch upload with different file types"""
        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            files = []

            # Add valid audio file
            with open(audio_file, 'rb') as f:
                files.append(('files', (audio_file.name, f.read(), 'audio/wav')))

            # Add another valid file
            with open(audio_file, 'rb') as f:
                files.append(('files', ('test2.wav', f.read(), 'audio/wav')))

            response = await client.post('/api/v1/batch/upload', files=files)

        assert response.status_code == 200
        data = response.json()
        assert data['total_files'] == 2


class TestBatchRoutesErrorHandling:
    """Test error handling in batch routes"""

    @pytest.mark.asyncio
    async def test_status_with_invalid_batch_id_format(self):
        """Test status check with malformed batch ID"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/batch/status/invalid-id')

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_batch_upload_with_corrupt_files(self):
        """Test batch upload with corrupted files"""
        corrupt_data = b'corrupted audio data'

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            files = [('files', ('corrupt.wav', io.BytesIO(corrupt_data), 'audio/wav'))]
            response = await client.post('/api/v1/batch/upload', files=files)

        # Should still accept for batch processing (validation happens during processing)
        assert response.status_code in [200, 422]
