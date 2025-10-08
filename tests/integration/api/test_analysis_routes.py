"""
Tests for Analysis API Routes

Tests BPM/key detection, loop segmentation, audio identification, and duplicate detection endpoints.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
from httpx import AsyncClient, ASGITransport
import io
import tempfile

from samplemind.interfaces.api.main import app


class TestBPMKeyDetectionEndpoint:
    """Test /api/v1/analysis/bpm-key endpoint"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.analysis.BPMKeyDetector')
    async def test_detect_bpm_key_success(self, mock_detector_class, test_audio_samples):
        """Test successful BPM and key detection"""
        # Setup mock
        mock_detector = Mock()
        mock_detector.detect_bpm.return_value = {
            'bpm': 120.5,
            'confidence': 0.95,
            'librosa_bpm': 120.0,
            'madmom_bpm': 121.0
        }
        mock_detector.detect_key.return_value = 'C major'
        mock_detector_class.return_value = mock_detector

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with open(audio_file, 'rb') as f:
                files = {'file': (audio_file.name, f, 'audio/wav')}
                response = await client.post('/api/v1/analysis/bpm-key', files=files)

        assert response.status_code == 200
        data = response.json()
        assert data['bpm'] == 120.5
        assert data['confidence'] == 0.95
        assert data['key'] == 'C major'
        assert data['file'] == audio_file.name

    @pytest.mark.asyncio
    async def test_detect_bpm_key_invalid_file(self):
        """Test BPM/key detection with invalid file"""
        fake_file = io.BytesIO(b"not an audio file")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            files = {'file': ('test.txt', fake_file, 'text/plain')}
            response = await client.post('/api/v1/analysis/bpm-key', files=files)

        # Should handle gracefully
        assert response.status_code in [422, 500]

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.analysis.BPMKeyDetector')
    async def test_detect_bpm_key_with_error(self, mock_detector_class, test_audio_samples):
        """Test BPM/key detection when detector fails"""
        mock_detector = Mock()
        mock_detector.detect_bpm.side_effect = Exception("Detection failed")
        mock_detector_class.return_value = mock_detector

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with open(audio_file, 'rb') as f:
                files = {'file': (audio_file.name, f, 'audio/wav')}
                response = await client.post('/api/v1/analysis/bpm-key', files=files)

        assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_detect_bpm_key_without_file(self):
        """Test BPM/key detection without providing file"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post('/api/v1/analysis/bpm-key')

        assert response.status_code == 422


class TestBatchBPMKeyDetection:
    """Test /api/v1/analysis/bpm-key/batch endpoint"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.analysis.BPMKeyDetector')
    async def test_batch_detect_multiple_files(self, mock_detector_class, test_audio_samples):
        """Test batch BPM/key detection with multiple files"""
        mock_detector = Mock()
        mock_detector.detect_bpm.return_value = {
            'bpm': 120.0,
            'confidence': 0.9
        }
        mock_detector.detect_key.return_value = 'C major'
        mock_detector_class.return_value = mock_detector

        files_to_test = [
            test_audio_samples['120_c_major'],
            test_audio_samples['140_a_minor']
        ]

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            files = []
            for audio_file in files_to_test:
                with open(audio_file, 'rb') as f:
                    files.append(('files', (audio_file.name, f.read(), 'audio/wav')))

            response = await client.post('/api/v1/analysis/bpm-key/batch', files=files)

        assert response.status_code == 200
        data = response.json()
        assert 'results' in data
        assert data['total'] == 2
        assert len(data['results']) == 2

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.analysis.BPMKeyDetector')
    async def test_batch_detect_with_errors(self, mock_detector_class):
        """Test batch detection when some files fail"""
        mock_detector = Mock()
        mock_detector.detect_bpm.side_effect = Exception("Detection failed")
        mock_detector_class.return_value = mock_detector

        fake_file = io.BytesIO(b"fake audio")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            files = [
                ('files', ('test1.wav', fake_file, 'audio/wav')),
            ]
            response = await client.post('/api/v1/analysis/bpm-key/batch', files=files)

        assert response.status_code == 200
        data = response.json()
        # Should include error in results
        assert 'results' in data

    @pytest.mark.asyncio
    async def test_batch_detect_empty_list(self):
        """Test batch detection with empty file list"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post('/api/v1/analysis/bpm-key/batch')

        assert response.status_code == 422


class TestLoopExtractionEndpoint:
    """Test /api/v1/analysis/loops endpoint"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.analysis.LoopSegmenter')
    async def test_extract_loops_default_bars(self, mock_segmenter_class, test_audio_samples):
        """Test loop extraction with default 8 bars"""
        mock_segmenter = Mock()
        mock_segmenter.segment_8bars.return_value = [
            {
                'start_bar': 0,
                'end_bar': 8,
                'start_sample': 0,
                'end_sample': 44100 * 4,
                'duration': 4.0,
                'bpm': 120.0,
                'segment_index': 0,
                'audio': None,
                'sample_rate': 44100
            }
        ]
        mock_segmenter._score_segment.return_value = 0.85
        mock_segmenter_class.return_value = mock_segmenter

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with open(audio_file, 'rb') as f:
                files = {'file': (audio_file.name, f, 'audio/wav')}
                response = await client.post('/api/v1/analysis/loops', files=files)

        assert response.status_code == 200
        data = response.json()
        assert 'segments' in data
        assert data['total_segments'] >= 0
        assert data['file'] == audio_file.name

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.analysis.LoopSegmenter')
    async def test_extract_loops_custom_bars(self, mock_segmenter_class, test_audio_samples):
        """Test loop extraction with custom bar count"""
        mock_segmenter = Mock()
        mock_segmenter.segment_8bars.return_value = []
        mock_segmenter_class.return_value = mock_segmenter

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with open(audio_file, 'rb') as f:
                files = {'file': (audio_file.name, f, 'audio/wav')}
                response = await client.post(
                    '/api/v1/analysis/loops',
                    files=files,
                    params={'bars': 16}
                )

        assert response.status_code == 200
        # Verify segmenter was called with bars=16
        mock_segmenter.segment_8bars.assert_called_once()

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.analysis.LoopSegmenter')
    async def test_extract_loops_with_quality_scores(self, mock_segmenter_class, test_audio_samples):
        """Test that loop segments include quality scores"""
        mock_segmenter = Mock()
        mock_segmenter.segment_8bars.return_value = [
            {
                'start_bar': 0,
                'end_bar': 8,
                'start_sample': 0,
                'end_sample': 44100 * 4,
                'duration': 4.0,
                'bpm': 120.0,
                'segment_index': 0,
                'audio': None,
                'sample_rate': 44100
            }
        ]
        mock_segmenter._score_segment.return_value = 0.92
        mock_segmenter_class.return_value = mock_segmenter

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with open(audio_file, 'rb') as f:
                files = {'file': (audio_file.name, f, 'audio/wav')}
                response = await client.post('/api/v1/analysis/loops', files=files)

        assert response.status_code == 200
        data = response.json()
        if len(data['segments']) > 0:
            segment = data['segments'][0]
            assert 'quality_score' in segment


class TestBestLoopExtraction:
    """Test /api/v1/analysis/loops/best endpoint"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.analysis.LoopSegmenter')
    async def test_extract_best_loop(self, mock_segmenter_class, test_audio_samples):
        """Test extracting best quality loop"""
        mock_segmenter = Mock()
        mock_segmenter.extract_best_loop.return_value = {
            'start_bar': 8,
            'end_bar': 16,
            'start_sample': 44100 * 4,
            'end_sample': 44100 * 8,
            'duration': 4.0,
            'bpm': 120.0,
            'segment_index': 1,
            'audio': None,
            'sample_rate': 44100
        }
        mock_segmenter._score_segment.return_value = 0.95
        mock_segmenter_class.return_value = mock_segmenter

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with open(audio_file, 'rb') as f:
                files = {'file': (audio_file.name, f, 'audio/wav')}
                response = await client.post('/api/v1/analysis/loops/best', files=files)

        assert response.status_code == 200
        data = response.json()
        assert 'segment' in data
        assert data['file'] == audio_file.name

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.analysis.LoopSegmenter')
    async def test_extract_best_loop_no_loops_found(self, mock_segmenter_class, test_audio_samples):
        """Test when no suitable loops are found"""
        mock_segmenter = Mock()
        mock_segmenter.extract_best_loop.return_value = None
        mock_segmenter_class.return_value = mock_segmenter

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with open(audio_file, 'rb') as f:
                files = {'file': (audio_file.name, f, 'audio/wav')}
                response = await client.post('/api/v1/analysis/loops/best', files=files)

        assert response.status_code == 404


class TestAudioIdentification:
    """Test /api/v1/analysis/identify endpoint"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.analysis.AcoustIDClient')
    async def test_identify_audio_with_matches(self, mock_client_class, test_audio_samples):
        """Test audio identification with matches found"""
        mock_client = Mock()
        mock_client.identify.return_value = [
            {
                'score': 0.95,
                'recording_id': 'abc123',
                'title': 'Test Song',
                'artist': 'Test Artist',
                'metadata': {'year': 2024}
            }
        ]
        mock_client_class.return_value = mock_client

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with open(audio_file, 'rb') as f:
                files = {'file': (audio_file.name, f, 'audio/wav')}
                response = await client.post('/api/v1/analysis/identify', files=files)

        assert response.status_code == 200
        data = response.json()
        assert 'matches' in data
        assert data['total_matches'] == 1
        assert data['matches'][0]['title'] == 'Test Song'

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.analysis.AcoustIDClient')
    async def test_identify_audio_no_matches(self, mock_client_class, test_audio_samples):
        """Test audio identification with no matches"""
        mock_client = Mock()
        mock_client.identify.return_value = []
        mock_client_class.return_value = mock_client

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with open(audio_file, 'rb') as f:
                files = {'file': (audio_file.name, f, 'audio/wav')}
                response = await client.post('/api/v1/analysis/identify', files=files)

        assert response.status_code == 200
        data = response.json()
        assert data['total_matches'] == 0

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.analysis.AcoustIDClient')
    async def test_identify_audio_custom_threshold(self, mock_client_class, test_audio_samples):
        """Test audio identification with custom confidence threshold"""
        mock_client = Mock()
        mock_client.identify.return_value = []
        mock_client_class.return_value = mock_client

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with open(audio_file, 'rb') as f:
                files = {'file': (audio_file.name, f, 'audio/wav')}
                response = await client.post(
                    '/api/v1/analysis/identify',
                    files=files,
                    params={'threshold': 0.9}
                )

        assert response.status_code == 200
        # Verify threshold was passed
        mock_client.identify.assert_called_once()


class TestDuplicateDetection:
    """Test /api/v1/analysis/dedupe endpoint"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.analysis.AcoustIDClient')
    async def test_dedupe_with_duplicates(self, mock_client_class, test_audio_samples):
        """Test duplicate detection with duplicates found"""
        mock_client = Mock()
        mock_client.find_duplicates.return_value = [
            (Path('file1.wav'), Path('file2.wav')),
            (Path('file3.wav'), Path('file4.wav'))
        ]
        mock_client_class.return_value = mock_client

        files_to_test = [
            test_audio_samples['120_c_major'],
            test_audio_samples['140_a_minor']
        ]

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            files = []
            for audio_file in files_to_test:
                with open(audio_file, 'rb') as f:
                    files.append(('files', (audio_file.name, f.read(), 'audio/wav')))

            response = await client.post('/api/v1/analysis/dedupe', files=files)

        assert response.status_code == 200
        data = response.json()
        assert 'duplicates' in data
        assert data['total_duplicates'] == 2

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.analysis.AcoustIDClient')
    async def test_dedupe_no_duplicates(self, mock_client_class, test_audio_samples):
        """Test duplicate detection with no duplicates"""
        mock_client = Mock()
        mock_client.find_duplicates.return_value = []
        mock_client_class.return_value = mock_client

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with open(audio_file, 'rb') as f:
                files = [('files', (audio_file.name, f.read(), 'audio/wav'))]
                response = await client.post('/api/v1/analysis/dedupe', files=files)

        assert response.status_code == 200
        data = response.json()
        assert data['total_duplicates'] == 0

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.analysis.AcoustIDClient')
    async def test_dedupe_custom_threshold(self, mock_client_class, test_audio_samples):
        """Test duplicate detection with custom similarity threshold"""
        mock_client = Mock()
        mock_client.find_duplicates.return_value = []
        mock_client_class.return_value = mock_client

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with open(audio_file, 'rb') as f:
                files = [('files', (audio_file.name, f.read(), 'audio/wav'))]
                response = await client.post(
                    '/api/v1/analysis/dedupe',
                    files=files,
                    params={'threshold': 0.99}
                )

        assert response.status_code == 200
        # Verify threshold was passed
        mock_client.find_duplicates.assert_called_once()


class TestAnalysisHealthEndpoint:
    """Test /api/v1/analysis/health endpoint"""

    @pytest.mark.asyncio
    async def test_analysis_health_check(self):
        """Test analysis service health check"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/analysis/health')

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'analysis'
        assert 'features' in data
        assert len(data['features']) > 0


class TestAnalysisRoutesErrorHandling:
    """Test error handling in analysis routes"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.analysis.LoopSegmenter')
    async def test_loop_extraction_with_error(self, mock_segmenter_class, test_audio_samples):
        """Test loop extraction when segmenter fails"""
        mock_segmenter = Mock()
        mock_segmenter.segment_8bars.side_effect = Exception("Segmentation failed")
        mock_segmenter_class.return_value = mock_segmenter

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with open(audio_file, 'rb') as f:
                files = {'file': (audio_file.name, f, 'audio/wav')}
                response = await client.post('/api/v1/analysis/loops', files=files)

        assert response.status_code == 500

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.analysis.AcoustIDClient')
    async def test_identify_with_error(self, mock_client_class, test_audio_samples):
        """Test audio identification when client fails"""
        mock_client = Mock()
        mock_client.identify.side_effect = Exception("Identification failed")
        mock_client_class.return_value = mock_client

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with open(audio_file, 'rb') as f:
                files = {'file': (audio_file.name, f, 'audio/wav')}
                response = await client.post('/api/v1/analysis/identify', files=files)

        assert response.status_code == 500


class TestAnalysisIntegration:
    """Integration tests for analysis routes"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.analysis.BPMKeyDetector')
    @patch('samplemind.interfaces.api.routes.analysis.LoopSegmenter')
    async def test_full_analysis_workflow(
        self,
        mock_segmenter_class,
        mock_detector_class,
        test_audio_samples
    ):
        """Test complete analysis workflow: BPM/key -> loops"""
        # Setup mocks
        mock_detector = Mock()
        mock_detector.detect_bpm.return_value = {
            'bpm': 120.0,
            'confidence': 0.9
        }
        mock_detector.detect_key.return_value = 'C major'
        mock_detector_class.return_value = mock_detector

        mock_segmenter = Mock()
        mock_segmenter.segment_8bars.return_value = [
            {
                'start_bar': 0,
                'end_bar': 8,
                'start_sample': 0,
                'end_sample': 44100 * 4,
                'duration': 4.0,
                'bpm': 120.0,
                'segment_index': 0,
                'audio': None,
                'sample_rate': 44100
            }
        ]
        mock_segmenter._score_segment.return_value = 0.85
        mock_segmenter_class.return_value = mock_segmenter

        audio_file = test_audio_samples['120_c_major']

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Detect BPM/key
            with open(audio_file, 'rb') as f:
                files = {'file': (audio_file.name, f, 'audio/wav')}
                bpm_response = await client.post('/api/v1/analysis/bpm-key', files=files)

            assert bpm_response.status_code == 200
            bpm_data = bpm_response.json()
            assert bpm_data['bpm'] == 120.0

            # 2. Extract loops
            with open(audio_file, 'rb') as f:
                files = {'file': (audio_file.name, f, 'audio/wav')}
                loops_response = await client.post('/api/v1/analysis/loops', files=files)

            assert loops_response.status_code == 200
            loops_data = loops_response.json()
            assert 'segments' in loops_data
