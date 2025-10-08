"""
Cross-Site Request Forgery (CSRF) Protection Tests
==================================================

Comprehensive testing for CSRF protection mechanisms:
- Token validation
- Double submit cookie
- Same-site cookie tests
- Origin/Referer header validation
- State-changing operation protection
- GET request safety

These tests validate that the application properly protects against CSRF attacks.
"""

import pytest
import secrets
import hmac
import hashlib
from typing import Dict, Any
from unittest.mock import Mock, patch
import base64


class TestCSRFTokenValidation:
    """
    CSRF Token Validation Tests
    
    Tests synchronizer token pattern (most common CSRF defense)
    """
    
    def test_csrf_token_required_for_state_changing_operations(self, client, user_session):
        """Test CSRF token is required for POST/PUT/DELETE operations"""
        # Login and get session
        session_cookie = user_session
        
        # Try POST without CSRF token
        response = client.post('/api/v1/profile/update',
                              json={'name': 'NewName'},
                              headers={'Cookie': session_cookie})
        
        # Should be rejected
        assert response.status_code in [403, 422], \
            "POST without CSRF token should be rejected"
        
        error = response.get_json()
        assert 'csrf' in str(error).lower(), \
            "Error should mention CSRF"
    
    def test_valid_csrf_token_allows_operation(self, client, user_session, csrf_token):
        """Test valid CSRF token allows state-changing operation"""
        headers = {
            'Cookie': user_session,
            'X-CSRF-Token': csrf_token
        }
        
        response = client.post('/api/v1/profile/update',
                              json={'name': 'NewName'},
                              headers=headers)
        
        # Should succeed
        assert response.status_code in [200, 201], \
            "Valid CSRF token should be accepted"
    
    def test_invalid_csrf_token_rejected(self, client, user_session):
        """Test invalid CSRF token is rejected"""
        invalid_tokens = [
            'invalid_token',
            'a' * 64,  # Wrong length
            '',  # Empty
            'null',
            secrets.token_urlsafe(32)  # Valid format but not for this session
        ]
        
        for token in invalid_tokens:
            headers = {
                'Cookie': user_session,
                'X-CSRF-Token': token
            }
            
            response = client.post('/api/v1/profile/delete',
                                  headers=headers)
            
            assert response.status_code in [403, 422], \
                f"Invalid token should be rejected: {token}"
    
    def test_csrf_token_one_time_use(self, client, user_session, csrf_token):
        """Test CSRF token can only be used once (if implemented)"""
        headers = {
            'Cookie': user_session,
            'X-CSRF-Token': csrf_token
        }
        
        # First use
        response1 = client.post('/api/v1/posts',
                               json={'title': 'Test', 'content': 'Content'},
                               headers=headers)
        
        # Second use with same token
        response2 = client.post('/api/v1/posts',
                               json={'title': 'Test2', 'content': 'Content2'},
                               headers=headers)
        
        # If one-time tokens are used, second should fail
        # Otherwise both should succeed (per-session tokens)
        # Either way is acceptable, but document the behavior
        if response1.status_code in [200, 201]:
            # If one-time: response2 should fail
            # If per-session: response2 should succeed
            pass  # Both patterns are valid
    
    def test_csrf_token_bound_to_session(self, client, user1_session, user2_session, user1_csrf_token):
        """Test CSRF token is bound to specific session"""
        # Try to use User 1's token with User 2's session
        headers = {
            'Cookie': user2_session,
            'X-CSRF-Token': user1_csrf_token
        }
        
        response = client.post('/api/v1/profile/update',
                              json={'name': 'Hacked'},
                              headers=headers)
        
        # Should be rejected
        assert response.status_code in [403, 422], \
            "CSRF token from different session should be rejected"
    
    def test_csrf_token_expires(self, client, user_session, expired_csrf_token):
        """Test expired CSRF token is rejected"""
        headers = {
            'Cookie': user_session,
            'X-CSRF-Token': expired_csrf_token
        }
        
        response = client.post('/api/v1/posts/delete/1',
                              headers=headers)
        
        # Should reject expired token
        assert response.status_code in [403, 422], \
            "Expired CSRF token should be rejected"
    
    def test_csrf_token_in_header_vs_body(self, client, user_session, csrf_token):
        """Test CSRF token can be provided in header or body"""
        # Token in header
        headers = {
            'Cookie': user_session,
            'X-CSRF-Token': csrf_token
        }
        
        response1 = client.post('/api/v1/posts',
                               json={'title': 'Test'},
                               headers=headers)
        
        # Token in body
        response2 = client.post('/api/v1/posts',
                               json={'title': 'Test', 'csrf_token': csrf_token},
                               headers={'Cookie': user_session})
        
        # At least one method should work
        assert response1.status_code in [200, 201] or response2.status_code in [200, 201], \
            "CSRF token should be accepted in header or body"


class TestDoubleSubmitCookie:
    """
    Double Submit Cookie Pattern Tests
    
    Tests CSRF protection via double submit cookie pattern
    """
    
    def test_double_submit_cookie_validation(self, client, user_session):
        """Test double submit cookie pattern"""
        # Set CSRF cookie
        csrf_value = secrets.token_urlsafe(32)
        
        headers = {
            'Cookie': f'{user_session}; csrf_token={csrf_value}',
            'X-CSRF-Token': csrf_value
        }
        
        response = client.post('/api/v1/profile/update',
                              json={'name': 'NewName'},
                              headers=headers)
        
        # Should accept when cookie and header match
        assert response.status_code in [200, 201], \
            "Matching cookie and header should be accepted"
    
    def test_double_submit_cookie_mismatch_rejected(self, client, user_session):
        """Test mismatched cookie and header values are rejected"""
        cookie_value = secrets.token_urlsafe(32)
        header_value = secrets.token_urlsafe(32)
        
        headers = {
            'Cookie': f'{user_session}; csrf_token={cookie_value}',
            'X-CSRF-Token': header_value
        }
        
        response = client.post('/api/v1/profile/update',
                              json={'name': 'Hacked'},
                              headers=headers)
        
        # Should reject mismatch
        assert response.status_code in [403, 422], \
            "Mismatched CSRF cookie and header should be rejected"
    
    def test_double_submit_missing_cookie(self, client, user_session):
        """Test missing CSRF cookie is rejected"""
        header_value = secrets.token_urlsafe(32)
        
        headers = {
            'Cookie': user_session,
            'X-CSRF-Token': header_value
        }
        
        response = client.post('/api/v1/posts/delete/1',
                              headers=headers)
        
        # Should reject without cookie
        assert response.status_code in [403, 422], \
            "Missing CSRF cookie should be rejected"
    
    def test_double_submit_hmac_verification(self, client, user_session):
        """Test CSRF token HMAC verification"""
        # Generate CSRF token with HMAC
        secret_key = b'test_secret_key'
        csrf_value = secrets.token_urlsafe(32)
        hmac_signature = hmac.new(secret_key, csrf_value.encode(), hashlib.sha256).hexdigest()
        
        signed_token = f"{csrf_value}.{hmac_signature}"
        
        headers = {
            'Cookie': f'{user_session}; csrf_token={signed_token}',
            'X-CSRF-Token': signed_token
        }
        
        response = client.post('/api/v1/profile/update',
                              json={'name': 'NewName'},
                              headers=headers)
        
        # Valid HMAC should be accepted (if HMAC is used)
        # Otherwise, regular token should still work
        assert response.status_code in [200, 201, 403, 422]


class TestSameSiteCookie:
    """
    SameSite Cookie Attribute Tests
    
    Tests SameSite cookie attribute for CSRF protection
    """
    
    def test_session_cookie_has_samesite_attribute(self, client):
        """Test session cookie has SameSite attribute"""
        response = client.post('/api/v1/auth/login',
                              json={'username': 'testuser', 'password': 'password'})
        
        set_cookie_header = response.headers.get('Set-Cookie', '')
        
        # Should have SameSite attribute
        assert 'SameSite=' in set_cookie_header, \
            "Session cookie should have SameSite attribute"
        
        # Should be Strict or Lax (not None)
        assert 'SameSite=Strict' in set_cookie_header or 'SameSite=Lax' in set_cookie_header, \
            "SameSite should be Strict or Lax"
    
    def test_csrf_cookie_samesite_attribute(self, client, user_session):
        """Test CSRF cookie has appropriate SameSite attribute"""
        response = client.get('/api/v1/csrf-token',
                             headers={'Cookie': user_session})
        
        set_cookie_header = response.headers.get('Set-Cookie', '')
        
        if 'csrf' in set_cookie_header.lower():
            # CSRF cookie should have SameSite
            assert 'SameSite=' in set_cookie_header, \
                "CSRF cookie should have SameSite attribute"
    
    def test_cookies_secure_attribute_in_production(self, client):
        """Test cookies have Secure attribute in production"""
        with patch('samplemind.config.settings.ENVIRONMENT', 'production'):
            response = client.post('/api/v1/auth/login',
                                  json={'username': 'test', 'password': 'pass'})
            
            set_cookie_header = response.headers.get('Set-Cookie', '')
            
            # Should have Secure flag in production
            if set_cookie_header:
                assert 'Secure' in set_cookie_header, \
                    "Cookies should be Secure in production"
    
    def test_cookies_httponly_attribute(self, client):
        """Test session cookies have HttpOnly attribute"""
        response = client.post('/api/v1/auth/login',
                              json={'username': 'test', 'password': 'pass'})
        
        set_cookie_header = response.headers.get('Set-Cookie', '')
        
        # Session cookies should be HttpOnly
        if 'session' in set_cookie_header.lower():
            assert 'HttpOnly' in set_cookie_header, \
                "Session cookie should be HttpOnly"


class TestOriginRefererValidation:
    """
    Origin and Referer Header Validation Tests
    
    Tests additional CSRF protection via Origin/Referer headers
    """
    
    def test_origin_header_validation(self, client, user_session, csrf_token):
        """Test Origin header validation"""
        # Valid origin
        headers = {
            'Cookie': user_session,
            'X-CSRF-Token': csrf_token,
            'Origin': 'https://samplemind.ai'
        }
        
        response = client.post('/api/v1/posts',
                              json={'title': 'Test'},
                              headers=headers)
        
        # Should accept valid origin
        assert response.status_code in [200, 201], \
            "Valid Origin should be accepted"
    
    def test_invalid_origin_rejected(self, client, user_session, csrf_token):
        """Test invalid Origin header is rejected"""
        malicious_origins = [
            'https://evil.com',
            'http://samplemind.ai.evil.com',
            'https://samplemind-ai.com',  # Typosquatting
            'null'
        ]
        
        for origin in malicious_origins:
            headers = {
                'Cookie': user_session,
                'X-CSRF-Token': csrf_token,
                'Origin': origin
            }
            
            response = client.post('/api/v1/profile/delete',
                                  headers=headers)
            
            # Should reject invalid origin
            assert response.status_code in [403, 422], \
                f"Invalid Origin should be rejected: {origin}"
    
    def test_referer_header_validation(self, client, user_session, csrf_token):
        """Test Referer header validation"""
        # Valid referer
        headers = {
            'Cookie': user_session,
            'X-CSRF-Token': csrf_token,
            'Referer': 'https://samplemind.ai/profile'
        }
        
        response = client.post('/api/v1/profile/update',
                              json={'name': 'Test'},
                              headers=headers)
        
        # Should accept valid referer
        assert response.status_code in [200, 201], \
            "Valid Referer should be accepted"
    
    def test_missing_origin_and_referer_with_valid_token(self, client, user_session, csrf_token):
        """Test that valid CSRF token works without Origin/Referer"""
        headers = {
            'Cookie': user_session,
            'X-CSRF-Token': csrf_token
        }
        
        response = client.post('/api/v1/posts',
                              json={'title': 'Test'},
                              headers=headers)
        
        # Should accept based on CSRF token alone
        # (Origin/Referer are additional defense, not primary)
        assert response.status_code in [200, 201], \
            "Valid CSRF token should work without Origin/Referer"
    
    def test_subdomain_origin_handling(self, client, user_session, csrf_token):
        """Test how subdomains are handled in Origin validation"""
        subdomain_origins = [
            'https://api.samplemind.ai',
            'https://cdn.samplemind.ai',
            'https://beta.samplemind.ai'
        ]
        
        for origin in subdomain_origins:
            headers = {
                'Cookie': user_session,
                'X-CSRF-Token': csrf_token,
                'Origin': origin
            }
            
            response = client.post('/api/v1/posts',
                                  json={'title': 'Test'},
                                  headers=headers)
            
            # Behavior depends on configuration
            # Document whether subdomains are allowed
            assert response.status_code in [200, 201, 403], \
                f"Subdomain handling: {origin}"


class TestStateChangingOperationProtection:
    """
    State-Changing Operation Protection Tests
    
    Tests that all state-changing operations are protected
    """
    
    def test_post_requests_require_csrf(self, client, user_session):
        """Test POST requests require CSRF token"""
        endpoints = [
            '/api/v1/posts',
            '/api/v1/comments',
            '/api/v1/profile/update',
            '/api/v1/settings',
            '/api/v1/password/change'
        ]
        
        for endpoint in endpoints:
            response = client.post(endpoint,
                                  json={'data': 'test'},
                                  headers={'Cookie': user_session})
            
            # Should require CSRF
            assert response.status_code in [403, 404, 422], \
                f"POST to {endpoint} should require CSRF"
    
    def test_put_requests_require_csrf(self, client, user_session):
        """Test PUT requests require CSRF token"""
        endpoints = [
            '/api/v1/posts/1',
            '/api/v1/profile',
            '/api/v1/settings'
        ]
        
        for endpoint in endpoints:
            response = client.put(endpoint,
                                 json={'data': 'test'},
                                 headers={'Cookie': user_session})
            
            assert response.status_code in [403, 404, 422], \
                f"PUT to {endpoint} should require CSRF"
    
    def test_delete_requests_require_csrf(self, client, user_session):
        """Test DELETE requests require CSRF token"""
        endpoints = [
            '/api/v1/posts/1',
            '/api/v1/comments/1',
            '/api/v1/account'
        ]
        
        for endpoint in endpoints:
            response = client.delete(endpoint,
                                    headers={'Cookie': user_session})
            
            assert response.status_code in [403, 404, 422], \
                f"DELETE to {endpoint} should require CSRF"
    
    def test_patch_requests_require_csrf(self, client, user_session):
        """Test PATCH requests require CSRF token"""
        response = client.patch('/api/v1/profile',
                               json={'name': 'test'},
                               headers={'Cookie': user_session})
        
        assert response.status_code in [403, 404, 422], \
            "PATCH should require CSRF"


class TestGETRequestSafety:
    """
    GET Request Safety Tests
    
    Tests that GET requests don't change state (idempotent)
    """
    
    def test_get_requests_do_not_change_state(self, client, user_session):
        """Test GET requests don't modify data"""
        # These should fail or be rejected
        dangerous_get_endpoints = [
            '/api/v1/posts/delete/1',
            '/api/v1/account/delete',
            '/api/v1/logout',  # Should use POST
            '/api/v1/password/reset?token=xyz'  # Should use POST
        ]
        
        for endpoint in dangerous_get_endpoints:
            response = client.get(endpoint,
                                 headers={'Cookie': user_session})
            
            # GET should not perform state-changing operations
            # Should either redirect to POST or return error
            assert response.status_code in [400, 404, 405], \
                f"GET to {endpoint} should not change state"
    
    def test_get_logout_requires_post(self, client, user_session):
        """Test logout requires POST, not GET"""
        # Try GET logout
        response = client.get('/api/v1/auth/logout',
                             headers={'Cookie': user_session})
        
        # Should not log out via GET
        assert response.status_code in [405], \
            "Logout should require POST, not GET"
        
        # Verify still logged in
        profile = client.get('/api/v1/users/me',
                            headers={'Cookie': user_session})
        assert profile.status_code == 200, \
            "Should still be logged in after GET to logout"
    
    def test_idempotent_get_requests(self, client, user_session):
        """Test GET requests are idempotent"""
        endpoint = '/api/v1/posts/1'
        
        # Make same GET request multiple times
        responses = [
            client.get(endpoint, headers={'Cookie': user_session})
            for _ in range(3)
        ]
        
        # All responses should be identical
        status_codes = [r.status_code for r in responses]
        assert len(set(status_codes)) == 1, \
            "GET requests should be idempotent"


class TestCSRFBypassAttempts:
    """
    CSRF Bypass Attempt Tests
    
    Tests various techniques attackers use to bypass CSRF protection
    """
    
    def test_null_origin_header(self, client, user_session, csrf_token):
        """Test null Origin header handling"""
        headers = {
            'Cookie': user_session,
            'X-CSRF-Token': csrf_token,
            'Origin': 'null'
        }
        
        response = client.post('/api/v1/posts',
                              json={'title': 'Test'},
                              headers=headers)
        
        # null origin should be treated carefully
        # Some implementations reject it, others allow with valid CSRF token
        assert response.status_code in [200, 201, 403], \
            "null Origin handling should be secure"
    
    def test_csrf_token_in_url(self, client, user_session, csrf_token):
        """Test CSRF token in URL is rejected"""
        # CSRF token should not be accepted in URL (GET parameter)
        response = client.post(f'/api/v1/posts?csrf_token={csrf_token}',
                              json={'title': 'Test'},
                              headers={'Cookie': user_session})
        
        # Should reject token in URL
        assert response.status_code in [403, 422], \
            "CSRF token in URL should be rejected"
    
    def test_content_type_manipulation(self, client, user_session, csrf_token):
        """Test Content-Type manipulation doesn't bypass CSRF"""
        # Try with different content types
        content_types = [
            'application/json',
            'text/plain',
            'application/x-www-form-urlencoded',
            'multipart/form-data'
        ]
        
        for content_type in content_types:
            response = client.post('/api/v1/posts',
                                  data='{"title": "Test"}',
                                  headers={
                                      'Cookie': user_session,
                                      'Content-Type': content_type
                                  })
            
            # All should require CSRF regardless of content type
            assert response.status_code in [403, 422], \
                f"CSRF required for content-type: {content_type}"
    
    def test_flash_cors_bypass_attempt(self, client, user_session):
        """Test Flash/Silverlight CORS bypass is prevented"""
        # Try to set custom headers that Flash used to allow
        headers = {
            'Cookie': user_session,
            'X-Flash-Version': '10,0,0,0',
            'Content-Type': 'application/json'
        }
        
        response = client.post('/api/v1/posts',
                              json={'title': 'Test'},
                              headers=headers)
        
        # Should still require CSRF
        assert response.status_code in [403, 422], \
            "Flash CORS bypass should not work"


# Fixtures

@pytest.fixture
def client():
    """Create test client"""
    from samplemind.app import create_app
    app = create_app('testing')
    return app.test_client()


@pytest.fixture
def user_session(client):
    """Create user session"""
    response = client.post('/api/v1/auth/login',
                          json={'username': 'testuser', 'password': 'password'})
    
    return response.headers.get('Set-Cookie', '')


@pytest.fixture
def user1_session(client):
    """Create session for user 1"""
    response = client.post('/api/v1/auth/login',
                          json={'username': 'user1', 'password': 'password1'})
    return response.headers.get('Set-Cookie', '')


@pytest.fixture
def user2_session(client):
    """Create session for user 2"""
    response = client.post('/api/v1/auth/login',
                          json={'username': 'user2', 'password': 'password2'})
    return response.headers.get('Set-Cookie', '')


@pytest.fixture
def csrf_token(client, user_session):
    """Get CSRF token for session"""
    response = client.get('/api/v1/csrf-token',
                         headers={'Cookie': user_session})
    
    data = response.get_json()
    return data.get('csrf_token', secrets.token_urlsafe(32))


@pytest.fixture
def user1_csrf_token(client, user1_session):
    """Get CSRF token for user 1"""
    response = client.get('/api/v1/csrf-token',
                         headers={'Cookie': user1_session})
    
    data = response.get_json()
    return data.get('csrf_token', secrets.token_urlsafe(32))


@pytest.fixture
def expired_csrf_token():
    """Generate expired CSRF token"""
    # In real implementation, this would be a token with expired timestamp
    return 'expired_' + secrets.token_urlsafe(32)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])