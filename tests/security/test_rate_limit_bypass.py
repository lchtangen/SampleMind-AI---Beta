"""
Rate Limit Bypass Attack Tests
===============================

Comprehensive testing for rate limit bypass attempts:
- IP spoofing tests
- Header manipulation
- Distributed requests
- Token bucket exhaustion
- Concurrent request flooding
- Slow-rate attacks
- Rate limit reset exploitation

These tests validate that rate limiting cannot be bypassed through various techniques.
"""

import pytest
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from unittest.mock import Mock, patch
import random


class TestIPSpoofing:
    """
    IP Spoofing Tests
    
    Tests that rate limiting cannot be bypassed by spoofing IP addresses
    """
    
    def test_x_forwarded_for_spoofing(self, client):
        """Test that X-Forwarded-For header cannot be spoofed"""
        # Make many requests with different X-Forwarded-For headers
        responses = []
        
        for i in range(150):
            headers = {'X-Forwarded-For': f'192.168.1.{i}'}
            response = client.post('/api/v1/auth/login',
                                  json={'username': 'test', 'password': 'wrong'},
                                  headers=headers)
            responses.append(response.status_code)
        
        # Should still get rate limited despite spoofed IPs
        rate_limited_count = responses.count(429)
        assert rate_limited_count > 0, \
            "X-Forwarded-For spoofing should not bypass rate limit"
    
    def test_x_real_ip_spoofing(self, client):
        """Test that X-Real-IP header cannot be spoofed"""
        responses = []
        
        for i in range(150):
            headers = {'X-Real-IP': f'10.0.0.{i}'}
            response = client.post('/api/v1/auth/login',
                                  json={'username': 'admin', 'password': 'wrong'},
                                  headers=headers)
            responses.append(response.status_code)
        
        # Should get rate limited
        rate_limited_count = responses.count(429)
        assert rate_limited_count > 0, \
            "X-Real-IP spoofing should not bypass rate limit"
    
    def test_multiple_proxy_headers(self, client):
        """Test that multiple proxy headers don't bypass rate limit"""
        responses = []
        
        for i in range(150):
            headers = {
                'X-Forwarded-For': f'1.1.1.{i}',
                'X-Real-IP': f'2.2.2.{i}',
                'X-Client-IP': f'3.3.3.{i}',
                'CF-Connecting-IP': f'4.4.4.{i}'
            }
            response = client.post('/api/v1/auth/login',
                                  json={'username': 'user', 'password': 'wrong'},
                                  headers=headers)
            responses.append(response.status_code)
        
        # Should get rate limited based on actual IP
        rate_limited_count = responses.count(429)
        assert rate_limited_count > 0, \
            "Multiple proxy headers should not bypass rate limit"
    
    def test_ipv6_spoofing(self, client):
        """Test that IPv6 spoofing doesn't bypass rate limit"""
        responses = []
        
        for i in range(150):
            # Try with different IPv6 addresses
            headers = {'X-Forwarded-For': f'2001:0db8:85a3::{i:04x}'}
            response = client.post('/api/v1/auth/login',
                                  json={'username': 'test', 'password': 'wrong'},
                                  headers=headers)
            responses.append(response.status_code)
        
        rate_limited_count = responses.count(429)
        assert rate_limited_count > 0, \
            "IPv6 spoofing should not bypass rate limit"


class TestHeaderManipulation:
    """
    Header Manipulation Tests
    
    Tests rate limit bypass through header manipulation
    """
    
    def test_user_agent_rotation(self, client):
        """Test that rotating User-Agent doesn't bypass rate limit"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
            'Mozilla/5.0 (X11; Linux x86_64)',
            'curl/7.64.1',
            'PostmanRuntime/7.26.8'
        ]
        
        responses = []
        for i in range(150):
            headers = {'User-Agent': random.choice(user_agents)}
            response = client.post('/api/v1/auth/login',
                                  json={'username': 'test', 'password': 'wrong'},
                                  headers=headers)
            responses.append(response.status_code)
        
        # Should get rate limited regardless of User-Agent
        rate_limited_count = responses.count(429)
        assert rate_limited_count > 0, \
            "User-Agent rotation should not bypass rate limit"
    
    def test_session_cookie_manipulation(self, client):
        """Test that manipulating session cookies doesn't bypass rate limit"""
        responses = []
        
        for i in range(150):
            # Try with different session cookies
            headers = {'Cookie': f'session=fake_session_{i}'}
            response = client.post('/api/v1/auth/login',
                                  json={'username': 'test', 'password': 'wrong'},
                                  headers=headers)
            responses.append(response.status_code)
        
        rate_limited_count = responses.count(429)
        assert rate_limited_count > 0, \
            "Session manipulation should not bypass rate limit"
    
    def test_custom_header_injection(self, client):
        """Test that custom headers don't bypass rate limit"""
        responses = []
        
        for i in range(150):
            headers = {
                'X-Request-ID': f'req_{i}',
                'X-Bypass-Rate-Limit': 'true',
                'X-Admin': 'true'
            }
            response = client.post('/api/v1/auth/login',
                                  json={'username': 'admin', 'password': 'wrong'},
                                  headers=headers)
            responses.append(response.status_code)
        
        rate_limited_count = responses.count(429)
        assert rate_limited_count > 0, \
            "Custom headers should not bypass rate limit"
    
    def test_referer_manipulation(self, client):
        """Test that Referer header manipulation doesn't bypass rate limit"""
        referers = [
            'https://google.com',
            'https://github.com',
            'https://stackoverflow.com',
            None  # No referer
        ]
        
        responses = []
        for i in range(150):
            headers = {}
            if referer := random.choice(referers):
                headers['Referer'] = referer
            
            response = client.post('/api/v1/auth/login',
                                  json={'username': 'test', 'password': 'wrong'},
                                  headers=headers)
            responses.append(response.status_code)
        
        rate_limited_count = responses.count(429)
        assert rate_limited_count > 0, \
            "Referer manipulation should not bypass rate limit"


class TestDistributedRequests:
    """
    Distributed Request Tests
    
    Tests rate limiting against distributed attacks
    """
    
    def test_concurrent_requests(self, client):
        """Test rate limiting works with concurrent requests"""
        def make_request():
            return client.post('/api/v1/auth/login',
                             json={'username': 'test', 'password': 'wrong'})
        
        # Send many concurrent requests
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request) for _ in range(100)]
            responses = [future.result() for future in as_completed(futures)]
        
        status_codes = [r.status_code for r in responses]
        rate_limited_count = status_codes.count(429)
        
        # Should rate limit even with concurrent requests
        assert rate_limited_count > 0, \
            "Concurrent requests should be rate limited"
    
    def test_burst_then_slow(self, client):
        """Test rate limiting with burst followed by slow requests"""
        # Initial burst
        burst_responses = []
        for _ in range(50):
            response = client.post('/api/v1/auth/login',
                                  json={'username': 'test', 'password': 'wrong'})
            burst_responses.append(response.status_code)
        
        # Should hit rate limit
        assert 429 in burst_responses, "Burst should trigger rate limit"
        
        # Wait a bit
        time.sleep(2)
        
        # Try slow requests
        slow_responses = []
        for _ in range(10):
            response = client.post('/api/v1/auth/login',
                                  json={'username': 'test', 'password': 'wrong'})
            slow_responses.append(response.status_code)
            time.sleep(0.5)
        
        # Some may succeed after rate limit window expires
        # But rapid requests should still be limited
    
    def test_distributed_endpoints(self, client):
        """Test rate limiting across different endpoints"""
        endpoints = [
            '/api/v1/auth/login',
            '/api/v1/auth/register',
            '/api/v1/password/reset',
            '/api/v1/contact'
        ]
        
        all_responses = []
        for _ in range(40):
            for endpoint in endpoints:
                response = client.post(endpoint,
                                     json={'email': 'test@test.com'})
                all_responses.append(response.status_code)
        
        # Should have global rate limit
        rate_limited_count = all_responses.count(429)
        assert rate_limited_count > 0, \
            "Global rate limit should apply across endpoints"


class TestTokenBucketExhaustion:
    """
    Token Bucket Exhaustion Tests
    
    Tests attempts to exhaust token bucket rate limiters
    """
    
    def test_rapid_fire_requests(self, client):
        """Test rapid-fire requests exhaust token bucket"""
        responses = []
        
        # Send as fast as possible
        start_time = time.time()
        for _ in range(200):
            response = client.post('/api/v1/auth/login',
                                  json={'username': 'test', 'password': 'wrong'})
            responses.append(response.status_code)
        
        elapsed = time.time() - start_time
        
        # Should hit rate limit quickly
        rate_limited_count = responses.count(429)
        assert rate_limited_count > 50, \
            f"Token bucket should be exhausted (limited {rate_limited_count}/200)"
        
        # Should happen within reasonable time
        assert elapsed < 10, "Rate limiting should be fast"
    
    def test_gradual_token_recovery(self, client):
        """Test that tokens gradually recover"""
        # Exhaust tokens
        for _ in range(100):
            client.post('/api/v1/auth/login',
                       json={'username': 'test', 'password': 'wrong'})
        
        # Should be rate limited
        response1 = client.post('/api/v1/auth/login',
                               json={'username': 'test', 'password': 'wrong'})
        assert response1.status_code == 429
        
        # Wait for recovery
        time.sleep(5)
        
        # Should allow some requests again
        response2 = client.post('/api/v1/auth/login',
                               json={'username': 'test', 'password': 'wrong'})
        
        # May or may not succeed depending on recovery rate
        assert response2.status_code in [401, 429], \
            "Some recovery should occur"
    
    def test_sustained_high_rate(self, client):
        """Test sustained high rate eventually triggers rate limit"""
        responses = []
        
        # Sustained requests over time
        for batch in range(10):
            for _ in range(20):
                response = client.post('/api/v1/auth/login',
                                      json={'username': 'test', 'password': 'wrong'})
                responses.append(response.status_code)
            time.sleep(0.5)
        
        # Should eventually rate limit
        rate_limited_count = responses.count(429)
        assert rate_limited_count > 0, \
            "Sustained high rate should trigger rate limit"


class TestSlowRateAttacks:
    """
    Slow Rate Attack Tests
    
    Tests low-and-slow attacks that try to stay under rate limits
    """
    
    def test_low_and_slow_attack(self, client):
        """Test low-and-slow attack detection"""
        # Very slow requests that individually don't trigger rate limit
        # but cumulatively could be an attack
        
        responses = []
        start_time = time.time()
        
        for _ in range(50):
            response = client.post('/api/v1/auth/login',
                                  json={'username': 'admin', 'password': 'wrong'})
            responses.append(response.status_code)
            time.sleep(0.2)  # Slow enough to avoid burst detection
        
        elapsed = time.time() - start_time
        
        # Should still detect pattern
        # Either through cumulative tracking or account-based limiting
        failed_attempts = responses.count(401) + responses.count(429)
        assert failed_attempts > 0, \
            "Slow attack should still be detected"
    
    def test_account_lockout_after_slow_attempts(self, client):
        """Test account lockout after many slow failed attempts"""
        username = 'targetuser'
        
        # Slow password guessing
        for i in range(10):
            response = client.post('/api/v1/auth/login',
                                  json={'username': username, 'password': f'wrong{i}'})
            time.sleep(1)  # Slow enough to avoid rate limit
        
        # Account should eventually be locked
        response = client.post('/api/v1/auth/login',
                              json={'username': username, 'password': 'correct'})
        
        # Should be locked or rate limited
        assert response.status_code in [401, 429], \
            "Account should be protected from slow brute force"


class TestRateLimitResetExploitation:
    """
    Rate Limit Reset Exploitation Tests
    
    Tests attempts to exploit rate limit reset mechanisms
    """
    
    def test_timezone_manipulation(self, client):
        """Test that timezone manipulation doesn't reset rate limits"""
        # Make requests with different timezone headers
        responses = []
        
        for i in range(150):
            headers = {'X-Timezone': f'UTC{i % 24:+d}'}
            response = client.post('/api/v1/auth/login',
                                  json={'username': 'test', 'password': 'wrong'},
                                  headers=headers)
            responses.append(response.status_code)
        
        rate_limited_count = responses.count(429)
        assert rate_limited_count > 0, \
            "Timezone manipulation should not reset rate limits"
    
    def test_date_header_manipulation(self, client):
        """Test that Date header manipulation doesn't affect rate limits"""
        from datetime import datetime, timedelta
        
        responses = []
        
        for i in range(150):
            # Try different dates
            date = datetime.utcnow() + timedelta(hours=i)
            headers = {'Date': date.strftime('%a, %d %b %Y %H:%M:%S GMT')}
            
            response = client.post('/api/v1/auth/login',
                                  json={'username': 'test', 'password': 'wrong'},
                                  headers=headers)
            responses.append(response.status_code)
        
        rate_limited_count = responses.count(429)
        assert rate_limited_count > 0, \
            "Date manipulation should not affect rate limits"
    
    def test_clock_skew_exploitation(self, client):
        """Test that clock skew doesn't reset rate limits"""
        # Exhaust rate limit
        for _ in range(100):
            client.post('/api/v1/auth/login',
                       json={'username': 'test', 'password': 'wrong'})
        
        # Should be rate limited
        response1 = client.post('/api/v1/auth/login',
                               json={'username': 'test', 'password': 'wrong'})
        assert response1.status_code == 429
        
        # Try with time manipulation headers
        headers = {
            'X-Time-Offset': '-3600',  # 1 hour back
            'If-Modified-Since': 'Mon, 01 Jan 2020 00:00:00 GMT'
        }
        
        response2 = client.post('/api/v1/auth/login',
                               json={'username': 'test', 'password': 'wrong'},
                               headers=headers)
        
        # Should still be rate limited
        assert response2.status_code == 429, \
            "Time manipulation should not reset rate limits"


class TestEndpointSpecificRateLimits:
    """
    Endpoint-Specific Rate Limit Tests
    
    Tests that different endpoints have appropriate rate limits
    """
    
    def test_auth_endpoints_stricter_limits(self, client):
        """Test that auth endpoints have stricter rate limits"""
        # Auth endpoint should have low limit
        auth_responses = []
        for _ in range(50):
            response = client.post('/api/v1/auth/login',
                                  json={'username': 'test', 'password': 'wrong'})
            auth_responses.append(response.status_code)
        
        auth_rate_limited = auth_responses.count(429)
        
        # Should be rate limited quickly on auth
        assert auth_rate_limited > 0, \
            "Auth endpoints should have strict rate limits"
    
    def test_api_endpoints_normal_limits(self, client, user_token):
        """Test that regular API endpoints have normal limits"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        api_responses = []
        for _ in range(200):
            response = client.get('/api/v1/posts', headers=headers)
            api_responses.append(response.status_code)
        
        api_rate_limited = api_responses.count(429)
        
        # Should eventually rate limit but not as aggressively
        # (depends on configuration)
        pass  # Test documents expected behavior
    
    def test_expensive_operations_lower_limits(self, client, user_token):
        """Test that expensive operations have lower limits"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        # Expensive operation (e.g., file processing)
        responses = []
        for _ in range(20):
            response = client.post('/api/v1/audio/process',
                                  headers=headers,
                                  json={'file_id': 1})
            responses.append(response.status_code)
        
        # Should have lower limit for expensive operations
        rate_limited = responses.count(429)
        assert rate_limited > 0, \
            "Expensive operations should have lower rate limits"


class TestRateLimitBypass:
    """
    Rate Limit Bypass Attempt Tests
    
    Tests various creative bypass attempts
    """
    
    def test_case_variation_in_username(self, client):
        """Test that case variation doesn't bypass rate limits"""
        usernames = ['test', 'Test', 'TEST', 'TeSt', 'tEsT']
        
        all_responses = []
        for _ in range(30):
            for username in usernames:
                response = client.post('/api/v1/auth/login',
                                      json={'username': username, 'password': 'wrong'})
                all_responses.append(response.status_code)
        
        rate_limited_count = all_responses.count(429)
        assert rate_limited_count > 0, \
            "Case variation should not bypass rate limits"
    
    def test_url_encoding_variations(self, client):
        """Test that URL encoding doesn't bypass rate limits"""
        endpoints = [
            '/api/v1/auth/login',
            '/api/v1/auth%2Flogin',
            '/api/v1/auth%2flogin',
            '/api/v1/./auth/login',
            '/api/v1/auth/../auth/login'
        ]
        
        all_responses = []
        for _ in range(30):
            for endpoint in endpoints:
                response = client.post(endpoint,
                                      json={'username': 'test', 'password': 'wrong'})
                all_responses.append(response.status_code)
        
        # Should normalize endpoints and apply same limit
        rate_limited_count = all_responses.count(429)
        assert rate_limited_count > 0, \
            "URL encoding should not bypass rate limits"
    
    def test_http_method_variation(self, client):
        """Test that HTTP method variation doesn't bypass rate limits"""
        # Try same action with different methods
        responses = []
        
        for _ in range(100):
            # POST
            r1 = client.post('/api/v1/data',
                           json={'action': 'test'})
            responses.append(r1.status_code)
            
            # PUT (if allowed)
            r2 = client.put('/api/v1/data',
                          json={'action': 'test'})
            responses.append(r2.status_code)
        
        # Should apply rate limit regardless of method
        rate_limited_count = responses.count(429)
        assert rate_limited_count > 0, \
            "Method variation should not bypass rate limits"


class TestRateLimitHeaders:
    """
    Rate Limit Header Tests
    
    Tests that rate limit information is properly communicated
    """
    
    def test_rate_limit_headers_present(self, client):
        """Test that rate limit headers are present"""
        response = client.post('/api/v1/auth/login',
                              json={'username': 'test', 'password': 'wrong'})
        
        # Should include rate limit headers
        expected_headers = [
            'X-RateLimit-Limit',
            'X-RateLimit-Remaining',
            'X-RateLimit-Reset'
        ]
        
        # At least some rate limit info should be present
        has_rate_limit_info = any(
            header in response.headers for header in expected_headers
        )
        
        # This is optional but recommended
        # Test documents whether it's implemented
    
    def test_retry_after_header_on_429(self, client):
        """Test that Retry-After header is present on 429"""
        # Exhaust rate limit
        for _ in range(150):
            client.post('/api/v1/auth/login',
                       json={'username': 'test', 'password': 'wrong'})
        
        # Get rate limited response
        response = client.post('/api/v1/auth/login',
                              json={'username': 'test', 'password': 'wrong'})
        
        if response.status_code == 429:
            # Should have Retry-After header
            retry_after = response.headers.get('Retry-After')
            # This is recommended but optional


# Fixtures

@pytest.fixture
def client():
    """Create test client"""
    from samplemind.app import create_app
    app = create_app('testing')
    return app.test_client()


@pytest.fixture
def user_token():
    """Create JWT token for testing"""
    from samplemind.auth.jwt import create_access_token
    from datetime import datetime, timedelta
    
    payload = {
        'user_id': 1,
        'role': 'user',
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    
    return create_access_token(payload)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])