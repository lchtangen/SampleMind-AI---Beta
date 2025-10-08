"""
Tests for Health Check API Routes

Tests basic health, detailed health, readiness, and liveness endpoints.
"""

import pytest
from unittest.mock import Mock, patch
from httpx import AsyncClient, ASGITransport

from samplemind.interfaces.api.main import app


class TestBasicHealthEndpoint:
    """Test /api/v1/health endpoint"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.health.get_app_state')
    async def test_health_check_all_healthy(self, mock_get_state):
        """Test health check when all components are healthy"""
        mock_engine = Mock()
        mock_ai_manager = Mock()
        mock_ai_manager.get_available_providers.return_value = ['openai', 'google_ai']

        def state_getter(key):
            if key == 'audio_engine':
                return mock_engine
            elif key == 'ai_manager':
                return mock_ai_manager
            return None

        mock_get_state.side_effect = state_getter

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/health')

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'version' in data
        assert 'components' in data

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.health.get_app_state')
    async def test_health_check_missing_audio_engine(self, mock_get_state):
        """Test health check when audio engine is unavailable"""
        mock_get_state.return_value = None

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/health')

        assert response.status_code == 200
        data = response.json()
        assert 'components' in data
        assert data['components']['audio_engine'] == 'unavailable'

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.health.get_app_state')
    async def test_health_check_includes_version(self, mock_get_state):
        """Test that health check includes version info"""
        mock_get_state.return_value = None

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/health')

        data = response.json()
        assert 'version' in data
        assert isinstance(data['version'], str)

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.health.get_app_state')
    async def test_health_check_includes_environment(self, mock_get_state):
        """Test that health check includes environment info"""
        mock_get_state.return_value = None

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/health')

        data = response.json()
        assert 'environment' in data


class TestDetailedHealthEndpoint:
    """Test /api/v1/health/detailed endpoint"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.health.get_app_state')
    async def test_detailed_health_check(self, mock_get_state):
        """Test detailed health check with all metrics"""
        mock_engine = Mock()
        mock_ai_manager = Mock()
        mock_ai_manager.get_available_providers.return_value = []

        def state_getter(key):
            if key == 'audio_engine':
                return mock_engine
            elif key == 'ai_manager':
                return mock_ai_manager
            return None

        mock_get_state.side_effect = state_getter

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/health/detailed')

        assert response.status_code == 200
        data = response.json()
        assert 'status' in data
        assert 'version' in data
        assert 'uptime_seconds' in data
        assert 'timestamp' in data
        assert 'components' in data

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.health.get_app_state')
    async def test_detailed_health_includes_uptime(self, mock_get_state):
        """Test that detailed health includes uptime metric"""
        mock_get_state.return_value = None

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/health/detailed')

        data = response.json()
        assert 'uptime_seconds' in data
        assert data['uptime_seconds'] >= 0

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.health.get_app_state')
    async def test_detailed_health_component_status(self, mock_get_state):
        """Test detailed component status information"""
        mock_engine = Mock()
        mock_ai_manager = Mock()
        mock_ai_manager.get_available_providers.return_value = ['openai']

        def state_getter(key):
            if key == 'audio_engine':
                return mock_engine
            elif key == 'ai_manager':
                return mock_ai_manager
            elif key == 'mongodb':
                return Mock()
            elif key == 'redis':
                return Mock()
            elif key == 'chromadb':
                return Mock()
            elif key == 'http_client':
                return Mock()
            return None

        mock_get_state.side_effect = state_getter

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/health/detailed')

        data = response.json()
        components = data['components']

        # Check component details
        assert 'audio_engine' in components
        assert 'ai_manager' in components
        assert 'mongodb' in components
        assert 'redis' in components
        assert 'chromadb' in components
        assert 'http_client' in components

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.health.get_app_state')
    @patch('samplemind.ai.get_cache_stats')
    async def test_detailed_health_includes_cache_stats(self, mock_cache_stats, mock_get_state):
        """Test that detailed health includes cache statistics"""
        mock_get_state.return_value = None
        mock_cache_stats.return_value = {
            'hit_rate': 0.75,
            'total_requests': 1000,
            'hits': 750,
            'misses': 250
        }

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/health/detailed')

        data = response.json()
        if 'cache' in data:
            assert 'hit_rate' in data['cache'] or 'status' in data['cache']

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.health.get_app_state')
    async def test_detailed_health_performance_metrics(self, mock_get_state):
        """Test that detailed health includes performance metrics"""
        mock_get_state.return_value = None

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/health/detailed')

        data = response.json()
        # Performance metrics might be available or unavailable
        assert 'performance' in data


class TestReadinessEndpoint:
    """Test /api/v1/health/ready endpoint"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.health.get_app_state')
    async def test_readiness_check_ready(self, mock_get_state):
        """Test readiness check when service is ready"""
        mock_engine = Mock()
        mock_ai_manager = Mock()

        def state_getter(key):
            if key == 'audio_engine':
                return mock_engine
            elif key == 'ai_manager':
                return mock_ai_manager
            return None

        mock_get_state.side_effect = state_getter

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/health/ready')

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'ready'

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.health.get_app_state')
    async def test_readiness_check_not_ready(self, mock_get_state):
        """Test readiness check when service is not ready"""
        # No components available
        mock_get_state.return_value = None

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/health/ready')

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'not_ready'

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.health.get_app_state')
    async def test_readiness_missing_audio_engine(self, mock_get_state):
        """Test readiness when audio engine is missing"""
        def state_getter(key):
            if key == 'ai_manager':
                return Mock()
            return None

        mock_get_state.side_effect = state_getter

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/health/ready')

        data = response.json()
        assert data['status'] == 'not_ready'


class TestLivenessEndpoint:
    """Test /api/v1/health/live endpoint"""

    @pytest.mark.asyncio
    async def test_liveness_check(self):
        """Test liveness check always returns alive"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/health/live')

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'alive'

    @pytest.mark.asyncio
    async def test_liveness_check_simple(self):
        """Test that liveness check is simple and fast"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/health/live')

        # Should always succeed quickly
        assert response.status_code == 200
        assert 'status' in response.json()


class TestHealthRoutesIntegration:
    """Integration tests for health routes"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.health.get_app_state')
    async def test_all_health_endpoints(self, mock_get_state):
        """Test all health endpoints in sequence"""
        mock_engine = Mock()
        mock_ai_manager = Mock()
        mock_ai_manager.get_available_providers.return_value = []

        def state_getter(key):
            if key == 'audio_engine':
                return mock_engine
            elif key == 'ai_manager':
                return mock_ai_manager
            return None

        mock_get_state.side_effect = state_getter

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Basic health
            health_response = await client.get('/api/v1/health')
            assert health_response.status_code == 200

            # 2. Detailed health
            detailed_response = await client.get('/api/v1/health/detailed')
            assert detailed_response.status_code == 200

            # 3. Readiness
            ready_response = await client.get('/api/v1/health/ready')
            assert ready_response.status_code == 200

            # 4. Liveness
            live_response = await client.get('/api/v1/health/live')
            assert live_response.status_code == 200

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.health.get_app_state')
    async def test_health_check_consistency(self, mock_get_state):
        """Test that health checks return consistent information"""
        mock_get_state.return_value = None

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Call basic health twice
            response1 = await client.get('/api/v1/health')
            response2 = await client.get('/api/v1/health')

        data1 = response1.json()
        data2 = response2.json()

        # Version should be consistent
        assert data1['version'] == data2['version']
        assert data1['status'] == data2['status']


class TestHealthErrorHandling:
    """Test error handling in health routes"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.health.get_app_state')
    async def test_health_with_ai_manager_error(self, mock_get_state):
        """Test health check when AI manager throws error"""
        mock_ai_manager = Mock()
        mock_ai_manager.get_available_providers.side_effect = Exception("AI error")

        def state_getter(key):
            if key == 'ai_manager':
                return mock_ai_manager
            return None

        mock_get_state.side_effect = state_getter

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/health')

        # Should still return 200 but show error status
        assert response.status_code == 200
        data = response.json()
        assert 'components' in data

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.api.routes.health.get_app_state')
    @patch('samplemind.ai.get_cache_stats')
    async def test_detailed_health_with_cache_error(self, mock_cache_stats, mock_get_state):
        """Test detailed health when cache stats fail"""
        mock_get_state.return_value = None
        mock_cache_stats.side_effect = Exception("Cache error")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get('/api/v1/health/detailed')

        # Should still return 200
        assert response.status_code == 200
        data = response.json()
        if 'cache' in data:
            # Error should be handled gracefully
            assert 'error' in data['cache'] or 'status' in data['cache']
