"""
OWASP Top 10 Security Validation Tests
======================================

This module tests the application against the OWASP Top 10 security risks:
- A01: Broken Access Control
- A02: Cryptographic Failures  
- A03: Injection
- A04: Insecure Design
- A05: Security Misconfiguration
- A06: Vulnerable and Outdated Components
- A07: Identification and Authentication Failures
- A08: Software and Data Integrity Failures
- A09: Security Logging and Monitoring Failures
- A10: Server-Side Request Forgery (SSRF)

Reference: https://owasp.org/Top10/
"""

import pytest
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any
import os
import json


class TestA01BrokenAccessControl:
    """
    A01:2021 – Broken Access Control
    
    Tests for:
    - Unauthorized access to resources
    - Privilege escalation
    - Missing authorization checks
    - Insecure direct object references (IDOR)
    """
    
    def test_unauthorized_resource_access(self, client, test_user):
        """Test that unauthorized users cannot access protected resources"""
        # Attempt to access protected endpoint without authentication
        response = client.get('/api/v1/admin/users')
        assert response.status_code == 401, "Unauthenticated access should be denied"
        
    def test_privilege_escalation_prevention(self, client, user_token, admin_token):
        """Test that regular users cannot perform admin actions"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        # Attempt admin action with user token
        response = client.post('/api/v1/admin/users', 
                              headers=headers,
                              json={'username': 'newadmin', 'role': 'admin'})
        assert response.status_code == 403, "User should not be able to create admin"
        
    def test_idor_protection(self, client, user1_token, user2_id):
        """Test protection against Insecure Direct Object References"""
        headers = {'Authorization': f'Bearer {user1_token}'}
        
        # User 1 tries to access User 2's data
        response = client.get(f'/api/v1/users/{user2_id}/data', headers=headers)
        assert response.status_code == 403, "Should not access other user's data"
        
    def test_path_traversal_prevention(self, client, user_token):
        """Test prevention of path traversal attacks"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        # Attempt path traversal
        malicious_paths = [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32\\config\\sam',
            '%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd'
        ]
        
        for path in malicious_paths:
            response = client.get(f'/api/v1/files/{path}', headers=headers)
            assert response.status_code in [400, 403, 404], f"Path traversal blocked for {path}"
            
    def test_horizontal_privilege_escalation(self, client, user1_token, user2_id):
        """Test that users cannot modify other users' resources"""
        headers = {'Authorization': f'Bearer {user1_token}'}
        
        response = client.put(f'/api/v1/users/{user2_id}',
                             headers=headers,
                             json={'email': 'hacked@evil.com'})
        assert response.status_code == 403, "Should not modify other user's profile"


class TestA02CryptographicFailures:
    """
    A02:2021 – Cryptographic Failures
    
    Tests for:
    - Weak encryption algorithms
    - Hardcoded secrets
    - Insecure random number generation
    - Missing encryption for sensitive data
    """
    
    def test_password_hashing_strength(self):
        """Test that passwords are hashed with strong algorithms"""
        from samplemind.auth.utils import hash_password
        
        password = "SecureP@ssw0rd123"
        hashed = hash_password(password)
        
        # Should use bcrypt or argon2
        assert hashed.startswith(('$2b$', '$argon2')), "Should use strong hashing"
        assert len(hashed) > 50, "Hash should be sufficiently long"
        
    def test_no_hardcoded_secrets(self):
        """Test that no secrets are hardcoded in configuration"""
        from samplemind.config import settings
        
        sensitive_keys = ['secret_key', 'jwt_secret', 'api_key', 'password']
        
        for key in sensitive_keys:
            value = getattr(settings, key, None)
            if value:
                # Should not be default/example values
                assert value not in ['changeme', 'secret', 'password', 'admin'], \
                    f"{key} contains insecure default value"
                assert len(value) >= 32, f"{key} should be at least 32 chars"
                
    def test_secure_random_generation(self):
        """Test that cryptographically secure random is used"""
        import secrets
        
        # Generate tokens
        token1 = secrets.token_urlsafe(32)
        token2 = secrets.token_urlsafe(32)
        
        assert token1 != token2, "Random tokens should be unique"
        assert len(token1) > 40, "Token should be sufficiently long"
        
    def test_sensitive_data_not_in_logs(self, caplog):
        """Test that sensitive data is not logged"""
        from samplemind.auth.utils import authenticate_user
        
        username = "testuser"
        password = "SecretPassword123!"
        
        # This should not log the password
        with caplog.at_level('DEBUG'):
            authenticate_user(username, password)
            
        # Check logs don't contain password
        for record in caplog.records:
            assert password not in record.message, "Password leaked in logs"
            
    def test_tls_required_for_sensitive_operations(self, client):
        """Test that sensitive operations require HTTPS"""
        # This test would check middleware/decorator that enforces HTTPS
        from samplemind.middleware.security import require_https
        
        # Mock request without HTTPS
        mock_request = Mock()
        mock_request.is_secure = False
        mock_request.path = '/api/v1/auth/login'
        
        with pytest.raises(Exception) as exc_info:
            require_https(mock_request)
        assert 'HTTPS required' in str(exc_info.value)


class TestA03Injection:
    """
    A03:2021 – Injection
    
    Tests for:
    - SQL injection
    - NoSQL injection
    - Command injection
    - LDAP injection
    """
    
    def test_sql_injection_prevention(self, client, user_token):
        """Test prevention of SQL injection attacks"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "1' UNION SELECT * FROM users--",
            "admin'--",
            "' OR 1=1--"
        ]
        
        for payload in sql_payloads:
            response = client.get(f'/api/v1/users/search?q={payload}', 
                                headers=headers)
            # Should either sanitize or reject
            if response.status_code == 200:
                data = response.get_json()
                # Should not return all users or cause error
                assert len(data.get('results', [])) < 100, \
                    "SQL injection may have succeeded"
                    
    def test_nosql_injection_prevention(self, client, user_token):
        """Test prevention of NoSQL injection attacks"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        nosql_payloads = [
            {'$gt': ''},
            {'$ne': None},
            {'$where': 'this.password'},
            {'username': {'$regex': '.*'}}
        ]
        
        for payload in nosql_payloads:
            response = client.post('/api/v1/users/search',
                                  headers=headers,
                                  json={'filter': payload})
            assert response.status_code in [400, 422], \
                "NoSQL injection should be blocked"
                
    def test_command_injection_prevention(self, client, admin_token):
        """Test prevention of command injection"""
        headers = {'Authorization': f'Bearer {admin_token}'}
        
        command_payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "& whoami",
            "`rm -rf /`",
            "$(curl evil.com)"
        ]
        
        for payload in command_payloads:
            response = client.post('/api/v1/system/exec',
                                  headers=headers,
                                  json={'command': f'ping {payload}'})
            # Should reject or sanitize
            assert response.status_code in [400, 403], \
                "Command injection should be blocked"
                
    def test_ldap_injection_prevention(self, client, user_token):
        """Test prevention of LDAP injection"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        ldap_payloads = [
            "*)(uid=*))(|(uid=*",
            "admin)(&(password=*))",
            "*)(objectClass=*"
        ]
        
        for payload in ldap_payloads:
            response = client.get(f'/api/v1/ldap/search?user={payload}',
                                headers=headers)
            assert response.status_code in [400, 404], \
                "LDAP injection should be blocked"


class TestA04InsecureDesign:
    """
    A04:2021 – Insecure Design
    
    Tests for:
    - Missing rate limiting
    - Insufficient business logic validation
    - Missing security requirements
    """
    
    def test_rate_limiting_exists(self, client):
        """Test that rate limiting is implemented"""
        # Rapid-fire requests
        responses = []
        for _ in range(100):
            response = client.post('/api/v1/auth/login',
                                  json={'username': 'test', 'password': 'test'})
            responses.append(response.status_code)
            
        # Should eventually get rate limited (429)
        assert 429 in responses, "Rate limiting should trigger"
        
    def test_business_logic_validation(self, client, user_token):
        """Test business logic validation"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        # Try to create order with negative quantity
        response = client.post('/api/v1/orders',
                              headers=headers,
                              json={'quantity': -10, 'item_id': 1})
        assert response.status_code == 400, "Negative quantity should be rejected"
        
        # Try to withdraw more than balance
        response = client.post('/api/v1/wallet/withdraw',
                              headers=headers,
                              json={'amount': 999999999})
        assert response.status_code == 400, "Insufficient funds check failed"
        
    def test_workflow_sequence_validation(self, client, user_token):
        """Test that workflow steps must be followed in order"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        # Try to complete order before payment
        order_response = client.post('/api/v1/orders',
                                    headers=headers,
                                    json={'item_id': 1, 'quantity': 1})
        order_id = order_response.get_json()['id']
        
        # Skip payment, try to ship directly
        ship_response = client.post(f'/api/v1/orders/{order_id}/ship',
                                   headers=headers)
        assert ship_response.status_code == 400, \
            "Should not ship unpaid order"


class TestA05SecurityMisconfiguration:
    """
    A05:2021 – Security Misconfiguration
    
    Tests for:
    - Default credentials
    - Unnecessary features enabled
    - Verbose error messages
    - Missing security headers
    """
    
    def test_no_default_credentials(self, client):
        """Test that default credentials don't work"""
        default_creds = [
            ('admin', 'admin'),
            ('admin', 'password'),
            ('root', 'root'),
            ('user', 'user')
        ]
        
        for username, password in default_creds:
            response = client.post('/api/v1/auth/login',
                                  json={'username': username, 'password': password})
            assert response.status_code == 401, \
                f"Default creds {username}:{password} should not work"
                
    def test_debug_mode_disabled(self):
        """Test that debug mode is disabled in production"""
        from samplemind.config import settings
        
        if os.getenv('ENVIRONMENT') == 'production':
            assert not settings.DEBUG, "Debug should be disabled in production"
            
    def test_error_messages_not_verbose(self, client):
        """Test that error messages don't leak sensitive info"""
        response = client.get('/api/v1/nonexistent')
        
        assert response.status_code == 404
        error_msg = response.get_json().get('message', '')
        
        # Should not contain stack traces or file paths
        assert '/home/' not in error_msg, "Error reveals file paths"
        assert 'Traceback' not in error_msg, "Error contains stack trace"
        
    def test_security_headers_present(self, client):
        """Test that security headers are set"""
        response = client.get('/api/v1/health')
        
        required_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000',
            'Content-Security-Policy': lambda v: v is not None
        }
        
        for header, expected in required_headers.items():
            value = response.headers.get(header)
            if callable(expected):
                assert expected(value), f"Header {header} validation failed"
            else:
                assert value == expected, f"Missing/incorrect header: {header}"
                
    def test_directory_listing_disabled(self, client):
        """Test that directory listing is disabled"""
        response = client.get('/static/')
        
        assert response.status_code in [403, 404], \
            "Directory listing should be disabled"


class TestA06VulnerableComponents:
    """
    A06:2021 – Vulnerable and Outdated Components
    
    Tests for:
    - Outdated dependencies
    - Known vulnerabilities
    - Unsupported versions
    """
    
    def test_no_known_vulnerable_dependencies(self):
        """Test that dependencies don't have known vulnerabilities"""
        import pkg_resources
        import json
        
        # This would typically integrate with safety or snyk
        # For demo, we check basic version requirements
        
        critical_packages = {
            'django': '3.2.0',  # Min secure version
            'flask': '2.0.0',
            'requests': '2.25.0',
            'cryptography': '3.3.0'
        }
        
        for package, min_version in critical_packages.items():
            try:
                installed = pkg_resources.get_distribution(package)
                installed_version = installed.version
                # Basic version check (proper check would use packaging.version)
                assert installed_version >= min_version, \
                    f"{package} {installed_version} is below minimum {min_version}"
            except pkg_resources.DistributionNotFound:
                pass  # Package not used
                
    def test_python_version_supported(self):
        """Test that Python version is supported"""
        import sys
        
        major, minor = sys.version_info[:2]
        
        # Python 3.8+ required
        assert major == 3 and minor >= 8, \
            f"Python {major}.{minor} is not supported"
            
    def test_no_deprecated_crypto_used(self):
        """Test that deprecated cryptographic functions aren't used"""
        # Check that we're not using old/insecure algorithms
        from samplemind.auth.utils import hash_password
        import inspect
        
        source = inspect.getsource(hash_password)
        
        # Should not use MD5, SHA1, or weak algorithms
        forbidden = ['md5', 'sha1', 'des']
        for algo in forbidden:
            assert algo not in source.lower(), \
                f"Deprecated algorithm {algo} found"


class TestA07AuthenticationFailures:
    """
    A07:2021 – Identification and Authentication Failures
    
    Tests for:
    - Weak password policies
    - Missing MFA
    - Session fixation
    - Credential stuffing
    """
    
    def test_password_complexity_requirements(self, client):
        """Test password complexity is enforced"""
        weak_passwords = [
            'password',
            '12345678',
            'qwerty',
            'admin123',
            'Pass123'  # Too short
        ]
        
        for password in weak_passwords:
            response = client.post('/api/v1/auth/register',
                                  json={
                                      'username': 'newuser',
                                      'email': 'test@test.com',
                                      'password': password
                                  })
            assert response.status_code == 400, \
                f"Weak password '{password}' should be rejected"
                
    def test_account_lockout_after_failed_attempts(self, client):
        """Test account lockout after multiple failed login attempts"""
        username = 'testuser'
        
        # Try multiple failed logins
        for i in range(6):
            response = client.post('/api/v1/auth/login',
                                  json={'username': username, 'password': 'wrong'})
                                  
        # Account should be locked
        response = client.post('/api/v1/auth/login',
                              json={'username': username, 'password': 'correct'})
        assert response.status_code == 429, "Account should be locked"
        
    def test_session_fixation_prevention(self, client):
        """Test that session ID changes after login"""
        # Get initial session
        response1 = client.get('/api/v1/health')
        session1 = response1.headers.get('Set-Cookie')
        
        # Login
        client.post('/api/v1/auth/login',
                   json={'username': 'test', 'password': 'test'})
        
        # Get new session
        response2 = client.get('/api/v1/users/me')
        session2 = response2.headers.get('Set-Cookie')
        
        # Sessions should be different
        assert session1 != session2, "Session should regenerate after login"
        
    def test_jwt_token_expiration(self):
        """Test that JWT tokens have expiration"""
        from samplemind.auth.jwt import create_access_token
        
        token = create_access_token({'user_id': 1})
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        assert 'exp' in decoded, "Token should have expiration"
        
        exp_time = datetime.fromtimestamp(decoded['exp'])
        now = datetime.utcnow()
        
        # Should expire within reasonable time (e.g., 24 hours)
        assert exp_time - now < timedelta(days=1), \
            "Token expiration too long"


class TestA08SoftwareDataIntegrity:
    """
    A08:2021 – Software and Data Integrity Failures
    
    Tests for:
    - Unsigned updates
    - Insecure deserialization
    - Missing integrity checks
    """
    
    def test_no_insecure_deserialization(self, client, user_token):
        """Test that insecure deserialization is prevented"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        # Try to send serialized Python object (pickle)
        import pickle
        malicious_data = pickle.dumps({'__reduce__': lambda: os.system('whoami')})
        
        response = client.post('/api/v1/data/import',
                              headers=headers,
                              data=malicious_data,
                              content_type='application/octet-stream')
                              
        assert response.status_code in [400, 415], \
            "Insecure deserialization should be blocked"
            
    def test_file_upload_integrity(self, client, user_token):
        """Test file upload includes integrity checks"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        # Upload file with checksum
        file_content = b"test file content"
        checksum = hashlib.sha256(file_content).hexdigest()
        
        response = client.post('/api/v1/files/upload',
                              headers=headers,
                              data={'file': (file_content, 'test.txt'),
                                   'checksum': checksum})
                                   
        assert response.status_code == 200, "Valid file should upload"
        
        # Try with wrong checksum
        response = client.post('/api/v1/files/upload',
                              headers=headers,
                              data={'file': (file_content, 'test.txt'),
                                   'checksum': 'wrongchecksum'})
                                   
        assert response.status_code == 400, "Invalid checksum should be rejected"
        
    def test_ci_cd_signature_verification(self):
        """Test that CI/CD artifacts are verified"""
        # This would check signature verification in deployment
        # For demo purposes, we check configuration
        from samplemind.config import settings
        
        if hasattr(settings, 'VERIFY_DEPLOYMENT_SIGNATURES'):
            assert settings.VERIFY_DEPLOYMENT_SIGNATURES, \
                "Deployment signature verification should be enabled"


class TestA09LoggingMonitoringFailures:
    """
    A09:2021 – Security Logging and Monitoring Failures
    
    Tests for:
    - Missing security event logging
    - Insufficient log retention
    - No alerting on security events
    """
    
    def test_security_events_logged(self, client, caplog):
        """Test that security events are logged"""
        import logging
        
        with caplog.at_level(logging.WARNING):
            # Failed login attempt
            client.post('/api/v1/auth/login',
                       json={'username': 'admin', 'password': 'wrong'})
                       
        # Should log the failed attempt
        assert any('failed login' in record.message.lower() 
                  for record in caplog.records), \
            "Failed login should be logged"
            
    def test_audit_trail_for_sensitive_operations(self, client, admin_token, caplog):
        """Test that sensitive operations are audited"""
        headers = {'Authorization': f'Bearer {admin_token}'}
        
        with caplog.at_level('INFO'):
            # Perform sensitive operation
            client.delete('/api/v1/users/123', headers=headers)
            
        # Should be in audit log
        assert any('user' in record.message.lower() and 'delete' in record.message.lower()
                  for record in caplog.records), \
            "User deletion should be audited"
            
    def test_no_sensitive_data_in_logs(self, caplog):
        """Test that logs don't contain sensitive data"""
        from samplemind.auth.utils import process_payment
        
        with caplog.at_level('DEBUG'):
            process_payment(card_number='4111111111111111', cvv='123')
            
        for record in caplog.records:
            # Should not log full card number or CVV
            assert '4111111111111111' not in record.message, \
                "Card number leaked in logs"
            assert '123' not in record.message or 'cvv' not in record.message.lower(), \
                "CVV leaked in logs"


class TestA10ServerSideRequestForgery:
    """
    A10:2021 – Server-Side Request Forgery (SSRF)
    
    Tests for:
    - Internal resource access
    - Cloud metadata access
    - Port scanning
    """
    
    def test_ssrf_prevention_internal_urls(self, client, user_token):
        """Test that SSRF to internal URLs is prevented"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        internal_urls = [
            'http://localhost/admin',
            'http://127.0.0.1:8080',
            'http://169.254.169.254/latest/meta-data/',  # AWS metadata
            'http://metadata.google.internal/',  # GCP metadata
            'http://192.168.1.1',
            'http://10.0.0.1',
            'file:///etc/passwd'
        ]
        
        for url in internal_urls:
            response = client.post('/api/v1/fetch',
                                  headers=headers,
                                  json={'url': url})
            assert response.status_code in [400, 403], \
                f"SSRF to {url} should be blocked"
                
    def test_ssrf_prevention_url_redirect(self, client, user_token):
        """Test that redirects to internal URLs are prevented"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        # URL that redirects to internal resource
        response = client.post('/api/v1/fetch',
                              headers=headers,
                              json={'url': 'http://evil.com/redirect-to-internal'})
                              
        # Should either block or follow securely
        assert response.status_code in [400, 403], \
            "Redirect to internal resource should be blocked"
            
    def test_url_schema_validation(self, client, user_token):
        """Test that only safe URL schemas are allowed"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        unsafe_schemas = [
            'file:///etc/passwd',
            'ftp://internal.server/data',
            'gopher://internal:70',
            'dict://localhost:11211/stats'
        ]
        
        for url in unsafe_schemas:
            response = client.post('/api/v1/fetch',
                                  headers=headers,
                                  json={'url': url})
            assert response.status_code in [400, 403], \
                f"Unsafe schema in {url} should be blocked"


# Fixtures

@pytest.fixture
def client():
    """Create test client"""
    from samplemind.app import create_app
    app = create_app('testing')
    return app.test_client()


@pytest.fixture
def test_user():
    """Create test user"""
    from samplemind.models import User
    user = User(username='testuser', email='test@example.com')
    user.set_password('SecureP@ssw0rd123')
    return user


@pytest.fixture
def user_token(test_user):
    """Create JWT token for regular user"""
    from samplemind.auth.jwt import create_access_token
    return create_access_token({'user_id': test_user.id, 'role': 'user'})


@pytest.fixture
def admin_token():
    """Create JWT token for admin user"""
    from samplemind.auth.jwt import create_access_token
    return create_access_token({'user_id': 1, 'role': 'admin'})


@pytest.fixture
def user1_token():
    """Create JWT token for user 1"""
    from samplemind.auth.jwt import create_access_token
    return create_access_token({'user_id': 1, 'role': 'user'})


@pytest.fixture
def user2_id():
    """User 2 ID for IDOR tests"""
    return 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])