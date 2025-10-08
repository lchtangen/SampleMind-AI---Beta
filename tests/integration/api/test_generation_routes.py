"""
Tests for Music Generation API Routes

Tests AI music generation endpoints using Google Gemini Lyria.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from httpx import AsyncClient, ASGITransport
from pathlib import Path

from samplemind.interfaces.api.main import app


class TestMusicGenerationEndpoint:
    """Test /api/v1/generate/music endpoint"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.generation.LyriaRealTimeEngine')
    async def test_generate_music_basic(self, mock_engine_class):
        """Test basic music generation"""
        # Setup mock
        mock_engine = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.audio_path = Path('/tmp/generated.wav')
        mock_result.generation_time = 5.2
        mock_result.metadata = {'duration': 30, 'format': 'wav'}
        mock_engine.generate_music = AsyncMock(return_value=mock_result)
        mock_engine_class.return_value = mock_engine

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                '/api/v1/generate/music',
                json={
                    'prompt': 'Upbeat electronic music for coding',
                    'duration': 30
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'generation_id' in data
        assert data['audio_url'] is not None
        assert data['generation_time'] == 5.2

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.generation.LyriaRealTimeEngine')
    async def test_generate_music_with_style_and_mood(self, mock_engine_class):
        """Test music generation with style and mood parameters"""
        mock_engine = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.audio_path = Path('/tmp/generated.wav')
        mock_result.generation_time = 6.0
        mock_result.metadata = {}
        mock_engine.generate_music = AsyncMock(return_value=mock_result)
        mock_engine_class.return_value = mock_engine

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                '/api/v1/generate/music',
                json={
                    'prompt': 'Epic soundtrack',
                    'style': 'orchestral',
                    'mood': 'uplifting',
                    'tempo': 90,
                    'duration': 60
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.generation.LyriaRealTimeEngine')
    async def test_generate_music_with_key(self, mock_engine_class):
        """Test music generation with musical key specification"""
        mock_engine = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.audio_path = Path('/tmp/generated.wav')
        mock_result.generation_time = 5.5
        mock_result.metadata = {}
        mock_engine.generate_music = AsyncMock(return_value=mock_result)
        mock_engine_class.return_value = mock_engine

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                '/api/v1/generate/music',
                json={
                    'prompt': 'Calm piano piece',
                    'style': 'classical',
                    'key': 'C minor',
                    'tempo': 70,
                    'duration': 30
                }
            )

        assert response.status_code == 200

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.generation.LyriaRealTimeEngine')
    async def test_generate_music_with_variations(self, mock_engine_class):
        """Test generating multiple variations"""
        mock_engine = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.audio_path = Path('/tmp/generated.wav')
        mock_result.generation_time = 7.0
        mock_result.metadata = {}
        mock_engine.generate_music = AsyncMock(return_value=mock_result)
        mock_engine_class.return_value = mock_engine

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                '/api/v1/generate/music',
                json={
                    'prompt': 'Electronic beat',
                    'style': 'electronic',
                    'variations': 3
                }
            )

        assert response.status_code == 200

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.generation.LyriaRealTimeEngine')
    async def test_generate_music_failure(self, mock_engine_class):
        """Test music generation failure"""
        mock_engine = Mock()
        mock_result = Mock()
        mock_result.success = False
        mock_result.metadata = {'error': 'Generation failed'}
        mock_engine.generate_music = AsyncMock(return_value=mock_result)
        mock_engine_class.return_value = mock_engine

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                '/api/v1/generate/music',
                json={'prompt': 'Test music'}
            )

        assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_generate_music_invalid_style(self):
        """Test music generation with invalid style"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                '/api/v1/generate/music',
                json={
                    'prompt': 'Test music',
                    'style': 'invalid_style'
                }
            )

        # Should handle validation error
        assert response.status_code in [400, 422, 500]

    @pytest.mark.asyncio
    async def test_generate_music_missing_prompt(self):
        """Test music generation without prompt"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                '/api/v1/generate/music',
                json={'duration': 30}
            )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.generation.LyriaRealTimeEngine')
    async def test_generate_music_engine_exception(self, mock_engine_class):
        """Test music generation when engine throws exception"""
        mock_engine = Mock()
        mock_engine.generate_music = AsyncMock(side_effect=Exception("Engine error"))
        mock_engine_class.return_value = mock_engine

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                '/api/v1/generate/music',
                json={'prompt': 'Test music'}
            )

        assert response.status_code == 500


class TestVariationsEndpoint:
    """Test /api/v1/generate/variations endpoint"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.generation.LyriaRealTimeEngine')
    async def test_generate_variations_success(self, mock_engine_class):
        """Test generating multiple variations"""
        mock_engine = Mock()

        # Create successful results
        mock_results = []
        for i in range(3):
            mock_result = Mock()
            mock_result.success = True
            mock_result.audio_path = Path(f'/tmp/variation_{i}.wav')
            mock_result.generation_time = 5.0 + i
            mock_result.metadata = {'variation_index': i}
            mock_results.append(mock_result)

        mock_engine.generate_variations = AsyncMock(return_value=mock_results)
        mock_engine_class.return_value = mock_engine

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                '/api/v1/generate/variations',
                json={
                    'prompt': 'Electronic beat',
                    'count': 3,
                    'style': 'electronic'
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['total_variations'] == 3
        assert data['completed'] == 3
        assert data['failed'] == 0
        assert len(data['results']) == 3

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.generation.LyriaRealTimeEngine')
    async def test_generate_variations_partial_success(self, mock_engine_class):
        """Test generating variations with some failures"""
        mock_engine = Mock()

        # Mix of success and failure
        mock_results = [
            Mock(success=True, audio_path=Path('/tmp/v1.wav'), generation_time=5.0, metadata={}),
            Mock(success=False, audio_path=None, generation_time=0, metadata={'error': 'Failed'}),
            Mock(success=True, audio_path=Path('/tmp/v2.wav'), generation_time=5.5, metadata={})
        ]

        mock_engine.generate_variations = AsyncMock(return_value=mock_results)
        mock_engine_class.return_value = mock_engine

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                '/api/v1/generate/variations',
                json={
                    'prompt': 'Test music',
                    'count': 3
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert data['completed'] == 2
        assert data['failed'] == 1

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.generation.LyriaRealTimeEngine')
    async def test_generate_variations_with_parameters(self, mock_engine_class):
        """Test variations with style, mood, and tempo"""
        mock_engine = Mock()
        mock_engine.generate_variations = AsyncMock(return_value=[])
        mock_engine_class.return_value = mock_engine

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                '/api/v1/generate/variations',
                json={
                    'prompt': 'Jazz improvisation',
                    'count': 5,
                    'style': 'jazz',
                    'mood': 'relaxed',
                    'tempo': 110
                }
            )

        assert response.status_code == 200


class TestStylesEndpoint:
    """Test /api/v1/generate/styles endpoint"""

    @pytest.mark.asyncio
    async def test_list_music_styles(self):
        """Test listing available music styles"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/generate/styles')

        assert response.status_code == 200
        data = response.json()
        assert 'styles' in data
        assert 'total' in data
        assert data['total'] > 0

        # Check structure of styles
        if len(data['styles']) > 0:
            style = data['styles'][0]
            assert 'name' in style
            assert 'display_name' in style
            assert 'description' in style
            assert 'typical_tempo' in style

    @pytest.mark.asyncio
    async def test_styles_include_common_genres(self):
        """Test that common music styles are included"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/generate/styles')

        data = response.json()
        style_names = [s['name'] for s in data['styles']]

        # Check for common styles
        assert 'electronic' in style_names
        assert 'orchestral' in style_names
        assert 'jazz' in style_names


class TestMoodsEndpoint:
    """Test /api/v1/generate/moods endpoint"""

    @pytest.mark.asyncio
    async def test_list_music_moods(self):
        """Test listing available music moods"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/generate/moods')

        assert response.status_code == 200
        data = response.json()
        assert 'moods' in data
        assert 'total' in data
        assert data['total'] > 0

        # Check structure
        if len(data['moods']) > 0:
            mood = data['moods'][0]
            assert 'name' in mood
            assert 'display_name' in mood
            assert 'description' in mood
            assert 'emotion' in mood

    @pytest.mark.asyncio
    async def test_moods_include_common_emotions(self):
        """Test that common moods are included"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/generate/moods')

        data = response.json()
        mood_names = [m['name'] for m in data['moods']]

        # Check for common moods
        assert 'energetic' in mood_names
        assert 'calm' in mood_names
        assert 'dark' in mood_names


class TestExamplesEndpoint:
    """Test /api/v1/generate/examples endpoint"""

    @pytest.mark.asyncio
    async def test_get_generation_examples(self):
        """Test getting example prompts"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/generate/examples')

        assert response.status_code == 200
        data = response.json()
        assert 'examples' in data
        assert 'total' in data
        assert data['total'] > 0

        # Check example structure
        if len(data['examples']) > 0:
            example = data['examples'][0]
            assert 'prompt' in example
            assert 'style' in example
            assert 'mood' in example
            assert 'tempo' in example
            assert 'use_case' in example

    @pytest.mark.asyncio
    async def test_examples_include_various_use_cases(self):
        """Test that examples cover different use cases"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/generate/examples')

        data = response.json()
        use_cases = [e['use_case'] for e in data['examples']]

        # Should have diverse use cases
        assert len(set(use_cases)) > 1


class TestGenerationHealthEndpoint:
    """Test /api/v1/generate/health endpoint"""

    @pytest.mark.asyncio
    async def test_generation_health_check(self):
        """Test generation service health check"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/generate/health')

        assert response.status_code == 200
        data = response.json()
        assert 'status' in data
        assert 'api_configured' in data
        assert 'model' in data
        assert data['model'] == 'lyria-realtime'

    @pytest.mark.asyncio
    @patch.dict('os.environ', {'GOOGLE_AI_API_KEY': 'test-key'})
    async def test_generation_health_with_api_key(self):
        """Test health check with API key configured"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/generate/health')

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert data['api_configured'] is True

    @pytest.mark.asyncio
    @patch.dict('os.environ', {}, clear=True)
    async def test_generation_health_without_api_key(self):
        """Test health check without API key"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/generate/health')

        assert response.status_code == 200
        data = response.json()
        # Status might be degraded without API key
        assert 'status' in data


class TestGenerationIntegration:
    """Integration tests for generation routes"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.generation.LyriaRealTimeEngine')
    async def test_full_generation_workflow(self, mock_engine_class):
        """Test complete workflow: check styles -> generate music"""
        mock_engine = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.audio_path = Path('/tmp/generated.wav')
        mock_result.generation_time = 5.0
        mock_result.metadata = {}
        mock_engine.generate_music = AsyncMock(return_value=mock_result)
        mock_engine_class.return_value = mock_engine

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Get available styles
            styles_response = await client.get('/api/v1/generate/styles')
            assert styles_response.status_code == 200
            styles = styles_response.json()['styles']

            # 2. Get available moods
            moods_response = await client.get('/api/v1/generate/moods')
            assert moods_response.status_code == 200
            moods = moods_response.json()['moods']

            # 3. Get examples for inspiration
            examples_response = await client.get('/api/v1/generate/examples')
            assert examples_response.status_code == 200

            # 4. Generate music using first style and mood
            if len(styles) > 0 and len(moods) > 0:
                gen_response = await client.post(
                    '/api/v1/generate/music',
                    json={
                        'prompt': 'Test music generation',
                        'style': styles[0]['name'],
                        'mood': moods[0]['name'],
                        'duration': 30
                    }
                )

                assert gen_response.status_code == 200
                assert gen_response.json()['success'] is True

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.generation.LyriaRealTimeEngine')
    async def test_variations_workflow(self, mock_engine_class):
        """Test workflow of generating variations"""
        mock_engine = Mock()
        mock_results = [
            Mock(success=True, audio_path=Path(f'/tmp/v{i}.wav'), generation_time=5.0, metadata={})
            for i in range(3)
        ]
        mock_engine.generate_variations = AsyncMock(return_value=mock_results)
        mock_engine_class.return_value = mock_engine

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Generate variations
            response = await client.post(
                '/api/v1/generate/variations',
                json={
                    'prompt': 'Electronic beat for dancing',
                    'count': 3,
                    'style': 'electronic'
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data['total_variations'] == 3
            assert data['completed'] == 3
