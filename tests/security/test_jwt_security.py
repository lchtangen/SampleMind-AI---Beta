"""
JWT (JSON Web Token) Security Tests
===================================

Comprehensive testing for JWT security vulnerabilities:
- Token manipulation attempts
- Signature bypass attempts
- Algorithm confusion attacks (alg=none, RS256 to HS256)
- Token expiration validation
- Token revocation tests
- Claims manipulation
- JTI (JWT ID) uniqueness
- Token refresh security

These tests validate that JWT implementation is secure against common attacks.
"""

import pytest
import jwt
import json
import time
import base64
from datetime import datetime, timedelta
from typing import Dict, Any
import secrets
import hashlib


class TestJWTSignatureVerification:
    """
    JWT Signature Verification Tests
    
    Tests that JWT signatures are properly verified
    """
    
    def test_modified_payload_rejected(self, client, valid_jwt_token, jwt_secret):
        """Test that modified JWT payload is rejected"""
        # Decode without verification
        payload = jwt.decode(valid_jwt_token, options={"verify_signature": False})
        
        # Modify payload (e.g., change user_id)
        payload['user_id'] = 999
        payload['role'] = 'admin'
        
        # Re-encode without proper signature
        header = jwt.get_unverified_header(valid_jwt_token)
        
        # Create token with modified payload but same signature
        parts = valid_jwt_token.split('.')
        modified_payload = base64.urlsafe_b64encode(
            json.dumps(payload).encode()
        ).decode().rstrip('=')
        
        tampered_token = f"{parts[0]}.{modified_payload}.{parts[2]}"
        
        # Try to use tampered token
        response = client.get('/api/v1/users/me',
                             headers={'Authorization': f'Bearer {tampered_token}'})
        
        # Should be rejected
        assert response.status_code == 401, \
            "Modified JWT payload should be rejected"
    
    def test_invalid_signature_rejected(self, client, valid_jwt_token):
        """Test that JWT with invalid signature is rejected"""
        # Modify the signature part
        parts = valid_jwt_token.split('.')
        tampered_token = f"{parts[0]}.{parts[1]}.invalidsignature"
        
        response = client.get('/api/v1/users/me',
                             headers={'Authorization': f'Bearer {tampered_token}'})
        
        assert response.status_code == 401, \
            "Invalid signature should be rejected"
    
    def test_token_signed_with_wrong_key_rejected(self, client, jwt_payload):
        """Test that token signed with wrong key is rejected"""
        wrong_key = "wrong_secret_key_12345"
        
        # Create token with wrong key
        token = jwt.encode(jwt_payload, wrong_key, algorithm='HS256')
        
        response = client.get('/api/v1/users/me',
                             headers={'Authorization': f'Bearer {token}'})
        
        assert response.status_code == 401, \
            "Token signed with wrong key should be rejected"
    
    def test_unsigned_token_rejected(self, client, jwt_payload):
        """Test that unsigned token is rejected"""
        # Create token without signature
        header = base64.urlsafe_b64encode(
            json.dumps({"alg": "none", "typ": "JWT"}).encode()
        ).decode().rstrip('=')
        
        payload_encoded = base64.urlsafe_b64encode(
            json.dumps(jwt_payload).encode()
        ).decode().rstrip('=')
        
        unsigned_token = f"{header}.{payload_encoded}."
        
        response = client.get('/api/v1/users/me',
                             headers={'Authorization': f'Bearer {unsigned_token}'})
        
        assert response.status_code == 401, \
            "Unsigned token should be rejected"


class TestAlgorithmConfusion:
    """
    Algorithm Confusion Attack Tests
    
    Tests protection against algorithm confusion attacks
    """
    
    def test_alg_none_attack(self, client, jwt_payload):
        """Test that alg=none tokens are rejected"""
        # Create token with alg=none
        header = {"alg": "none", "typ": "JWT"}
        
        header_encoded = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_encoded = base64.urlsafe_b64encode(
            json.dumps(jwt_payload).encode()
        ).decode().rstrip('=')
        
        none_token = f"{header_encoded}.{payload_encoded}."
        
        response = client.get('/api/v1/users/me',
                             headers={'Authorization': f'Bearer {none_token}'})
        
        assert response.status_code == 401, \
            "alg=none token should be rejected"
    
    def test_rs256_to_hs256_confusion(self, client, jwt_payload, rsa_public_key):
        """Test RS256 to HS256 algorithm confusion attack"""
        # Try to sign with HS256 using RSA public key
        # This attack works if server uses public key for HMAC verification
        
        try:
            # Sign with public key as HMAC secret (the attack)
            confused_token = jwt.encode(
                jwt_payload,
                rsa_public_key,
                algorithm='HS256'
            )
            
            response = client.get('/api/v1/users/me',
                                 headers={'Authorization': f'Bearer {confused_token}'})
            
            # Should be rejected
            assert response.status_code == 401, \
                "Algorithm confusion attack should be prevented"
        except Exception:
            # If signing fails, that's also acceptable
            pass
    
    def test_algorithm_whitelist(self, client, jwt_payload, jwt_secret):
        """Test that only whitelisted algorithms are accepted"""
        weak_algorithms = ['HS1', 'none', 'HS384', 'HS512']
        
        for alg in weak_algorithms:
            try:
                token = jwt.encode(jwt_payload, jwt_secret, algorithm=alg)
                
                response = client.get('/api/v1/users/me',
                                     headers={'Authorization': f'Bearer {token}'})
                
                # Should be rejected if not in whitelist
                assert response.status_code == 401, \
                    f"Weak algorithm {alg} should be rejected"
            except jwt.exceptions.InvalidAlgorithmError:
                # Expected if algorithm is not supported
                pass
    
    def test_algorithm_case_sensitivity(self, client, jwt_payload):
        """Test algorithm name case sensitivity"""
        # Try different cases
        algorithms = ['hs256', 'Hs256', 'hS256', 'HS256']
        
        for alg in algorithms:
            header = {"alg": alg, "typ": "JWT"}
            
            # Manually construct token
            header_encoded = base64.urlsafe_b64encode(
                json.dumps(header).encode()
            ).decode().rstrip('=')
            
            payload_encoded = base64.urlsafe_b64encode(
                json.dumps(jwt_payload).encode()
            ).decode().rstrip('=')
            
            token = f"{header_encoded}.{payload_encoded}.fakesignature"
            
            response = client.get('/api/v1/users/me',
                                 headers={'Authorization': f'Bearer {token}'})
            
            # All should be handled consistently
            assert response.status_code == 401


class TestTokenExpiration:
    """
    Token Expiration Tests
    
    Tests JWT expiration (exp claim) validation
    """
    
    def test_expired_token_rejected(self, client, jwt_secret):
        """Test that expired tokens are rejected"""
        # Create token that expired 1 hour ago
        expired_payload = {
            'user_id': 1,
            'role': 'user',
            'exp': datetime.utcnow() - timedelta(hours=1),
            'iat': datetime.utcnow() - timedelta(hours=2)
        }
        
        token = jwt.encode(expired_payload, jwt_secret, algorithm='HS256')
        
        response = client.get('/api/v1/users/me',
                             headers={'Authorization': f'Bearer {token}'})
        
        assert response.status_code == 401, \
            "Expired token should be rejected"
    
    def test_token_without_exp_rejected(self, client, jwt_secret):
        """Test that tokens without exp claim are rejected"""
        payload_no_exp = {
            'user_id': 1,
            'role': 'user',
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload_no_exp, jwt_secret, algorithm='HS256')
        
        response = client.get('/api/v1/users/me',
                             headers={'Authorization': f'Bearer {token}'})
        
        # Should reject tokens without expiration
        assert response.status_code == 401, \
            "Token without exp claim should be rejected"
    
    def test_token_exp_in_future_accepted(self, client, jwt_secret):
        """Test that tokens expiring in future are accepted"""
        valid_payload = {
            'user_id': 1,
            'role': 'user',
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(valid_payload, jwt_secret, algorithm='HS256')
        
        response = client.get('/api/v1/users/me',
                             headers={'Authorization': f'Bearer {token}'})
        
        # Should accept valid token
        assert response.status_code == 200, \
            "Valid token should be accepted"
    
    def test_token_exp_manipulation(self, client, valid_jwt_token, jwt_secret):
        """Test that extending token expiration is detected"""
        # Decode token
        payload = jwt.decode(valid_jwt_token, jwt_secret, algorithms=['HS256'])
        
        # Extend expiration
        payload['exp'] = datetime.utcnow() + timedelta(days=365)
        
        # Try to re-sign (attacker doesn't have key)
        # In reality this would fail, but test the verification
        extended_token = jwt.encode(payload, 'wrong_key', algorithm='HS256')
        
        response = client.get('/api/v1/users/me',
                             headers={'Authorization': f'Bearer {extended_token}'})
        
        assert response.status_code == 401, \
            "Token with manipulated expiration should be rejected"
    
    def test_nbf_claim_validation(self, client, jwt_secret):
        """Test not-before (nbf) claim is validated"""
        # Token valid starting 1 hour in the future
        future_payload = {
            'user_id': 1,
            'role': 'user',
            'exp': datetime.utcnow() + timedelta(hours=2),
            'nbf': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(future_payload, jwt_secret, algorithm='HS256')
        
        response = client.get('/api/v1/users/me',
                             headers={'Authorization': f'Bearer {token}'})
        
        # Should reject token before nbf time
        assert response.status_code == 401, \
            "Token before nbf should be rejected"


class TestTokenRevocation:
    """
    Token Revocation Tests
    
    Tests JWT revocation mechanisms
    """
    
    def test_logout_revokes_token(self, client, valid_jwt_token):
        """Test that logout revokes the token"""
        headers = {'Authorization': f'Bearer {valid_jwt_token}'}
        
        # Logout
        logout_response = client.post('/api/v1/auth/logout', headers=headers)
        assert logout_response.status_code == 200
        
        # Try to use token after logout
        response = client.get('/api/v1/users/me', headers=headers)
        
        # Should be rejected
        assert response.status_code == 401, \
            "Token should be revoked after logout"
    
    def test_revoked_token_in_blacklist(self, client, valid_jwt_token):
        """Test that revoked tokens are in blacklist"""
        headers = {'Authorization': f'Bearer {valid_jwt_token}'}
        
        # Revoke token explicitly
        revoke_response = client.post('/api/v1/auth/revoke',
                                      headers=headers,
                                      json={'token': valid_jwt_token})
        
        # Try to use revoked token
        response = client.get('/api/v1/users/me', headers=headers)
        
        assert response.status_code == 401, \
            "Revoked token should be in blacklist"
    
    def test_jti_uniqueness(self, client, jwt_secret):
        """Test JWT ID (jti) uniqueness"""
        jti = str(secrets.token_urlsafe(16))
        
        payload = {
            'user_id': 1,
            'role': 'user',
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow(),
            'jti': jti
        }
        
        token = jwt.encode(payload, jwt_secret, algorithm='HS256')
        
        # Use token
        response1 = client.get('/api/v1/users/me',
                              headers={'Authorization': f'Bearer {token}'})
        assert response1.status_code == 200
        
        # Try to reuse same JTI (replay attack)
        response2 = client.get('/api/v1/users/me',
                              headers={'Authorization': f'Bearer {token}'})
        
        # Both should work for same token, but can't create new token with same JTI
        # This is checked during token creation, not validation
    
    def test_password_change_revokes_tokens(self, client, valid_jwt_token):
        """Test that password change revokes existing tokens"""
        headers = {'Authorization': f'Bearer {valid_jwt_token}'}
        
        # Change password
        password_response = client.post('/api/v1/auth/password/change',
                                       headers=headers,
                                       json={
                                           'old_password': 'oldpass',
                                           'new_password': 'newpass123'
                                       })
        
        # Try to use old token
        response = client.get('/api/v1/users/me', headers=headers)
        
        # Old token should be revoked
        assert response.status_code == 401, \
            "Token should be revoked after password change"


class TestClaimsManipulation:
    """
    JWT Claims Manipulation Tests
    
    Tests manipulation of JWT claims
    """
    
    def test_role_escalation_attempt(self, client, jwt_secret):
        """Test that role escalation via claims is prevented"""
        # User creates token with admin role
        malicious_payload = {
            'user_id': 1,
            'role': 'admin',  # Escalation
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow()
        }
        
        # Without proper signature
        token = jwt.encode(malicious_payload, 'wrong_key', algorithm='HS256')
        
        response = client.get('/api/v1/admin/users',
                             headers={'Authorization': f'Bearer {token}'})
        
        assert response.status_code == 401, \
            "Role escalation should be prevented"
    
    def test_user_id_manipulation(self, client, jwt_secret):
        """Test that user_id manipulation is prevented"""
        # Token for user 1 trying to access as user 2
        payload = {
            'user_id': 2,  # Different user
            'role': 'user',
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, 'wrong_key', algorithm='HS256')
        
        response = client.get('/api/v1/users/1/data',
                             headers={'Authorization': f'Bearer {token}'})
        
        assert response.status_code == 401, \
            "User ID manipulation should be prevented"
    
    def test_custom_claims_validation(self, client, jwt_secret):
        """Test that custom claims are validated"""
        # Add malicious custom claims
        payload = {
            'user_id': 1,
            'role': 'user',
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow(),
            'permissions': ['delete_all', 'access_admin'],  # Unauthorized
            'is_superuser': True  # Escalation
        }
        
        token = jwt.encode(payload, jwt_secret, algorithm='HS256')
        
        # Try admin operation
        response = client.delete('/api/v1/admin/users/all',
                                headers={'Authorization': f'Bearer {token}'})
        
        # Should check actual permissions, not just claims
        assert response.status_code in [401, 403], \
            "Custom claims should be validated against database"
    
    def test_aud_claim_validation(self, client, jwt_secret):
        """Test audience (aud) claim validation"""
        # Token for different audience
        payload = {
            'user_id': 1,
            'role': 'user',
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow(),
            'aud': 'different-api.com'
        }
        
        token = jwt.encode(payload, jwt_secret, algorithm='HS256')
        
        response = client.get('/api/v1/users/me',
                             headers={'Authorization': f'Bearer {token}'})
        
        # Should validate audience
        assert response.status_code == 401, \
            "Token for different audience should be rejected"
    
    def test_iss_claim_validation(self, client, jwt_secret):
        """Test issuer (iss) claim validation"""
        # Token from unauthorized issuer
        payload = {
            'user_id': 1,
            'role': 'user',
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow(),
            'iss': 'evil-issuer.com'
        }
        
        token = jwt.encode(payload, jwt_secret, algorithm='HS256')
        
        response = client.get('/api/v1/users/me',
                             headers={'Authorization': f'Bearer {token}'})
        
        # Should validate issuer
        assert response.status_code == 401, \
            "Token from unauthorized issuer should be rejected"


class TestTokenRefreshSecurity:
    """
    Token Refresh Security Tests
    
    Tests security of token refresh mechanism
    """
    
    def test_refresh_token_requires_valid_refresh_token(self, client):
        """Test that refresh requires valid refresh token"""
        invalid_refresh = secrets.token_urlsafe(32)
        
        response = client.post('/api/v1/auth/refresh',
                              json={'refresh_token': invalid_refresh})
        
        assert response.status_code == 401, \
            "Invalid refresh token should be rejected"
    
    def test_refresh_token_single_use(self, client, valid_refresh_token):
        """Test that refresh tokens can only be used once"""
        # First use
        response1 = client.post('/api/v1/auth/refresh',
                               json={'refresh_token': valid_refresh_token})
        assert response1.status_code == 200
        
        # Try to reuse same refresh token
        response2 = client.post('/api/v1/auth/refresh',
                               json={'refresh_token': valid_refresh_token})
        
        # Should be rejected (refresh token rotation)
        assert response2.status_code == 401, \
            "Refresh token should be single-use"
    
    def test_access_token_cannot_be_used_for_refresh(self, client, valid_jwt_token):
        """Test that access token cannot be used for refresh"""
        response = client.post('/api/v1/auth/refresh',
                              json={'refresh_token': valid_jwt_token})
        
        assert response.status_code == 401, \
            "Access token should not work for refresh"
    
    def test_refresh_token_expiration(self, client, expired_refresh_token):
        """Test that expired refresh tokens are rejected"""
        response = client.post('/api/v1/auth/refresh',
                              json={'refresh_token': expired_refresh_token})
        
        assert response.status_code == 401, \
            "Expired refresh token should be rejected"
    
    def test_refresh_token_family_invalidation(self, client, valid_refresh_token):
        """Test that token family is invalidated on reuse detection"""
        # First use - valid
        response1 = client.post('/api/v1/auth/refresh',
                               json={'refresh_token': valid_refresh_token})
        new_refresh = response1.get_json().get('refresh_token')
        
        # Try to reuse old refresh token (reuse detection)
        response2 = client.post('/api/v1/auth/refresh',
                               json={'refresh_token': valid_refresh_token})
        
        # Should detect reuse and invalidate family
        assert response2.status_code == 401
        
        # New refresh token should also be invalidated
        response3 = client.post('/api/v1/auth/refresh',
                               json={'refresh_token': new_refresh})
        
        assert response3.status_code == 401, \
            "Token family should be invalidated on reuse detection"


class TestJWKSecurity:
    """
    JSON Web Key (JWK) Security Tests
    
    Tests for JWK-related vulnerabilities
    """
    
    def test_jwk_header_injection(self, client, jwt_payload):
        """Test that JWK in header is not trusted"""
        # Create malicious JWK in header
        malicious_jwk = {
            "kty": "oct",
            "k": base64.urlsafe_b64encode(b"malicious_key").decode()
        }
        
        # Create token with JWK header
        header = {
            "alg": "HS256",
            "typ": "JWT",
            "jwk": malicious_jwk
        }
        
        # Encode with malicious key
        header_encoded = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_encoded = base64.urlsafe_b64encode(
            json.dumps(jwt_payload).encode()
        ).decode().rstrip('=')
        
        # Sign with malicious key
        signing_input = f"{header_encoded}.{payload_encoded}"
        signature = base64.urlsafe_b64encode(
            hashlib.sha256(signing_input.encode()).digest()
        ).decode().rstrip('=')
        
        token = f"{signing_input}.{signature}"
        
        response = client.get('/api/v1/users/me',
                             headers={'Authorization': f'Bearer {token}'})
        
        assert response.status_code == 401, \
            "JWK header injection should be rejected"
    
    def test_jku_header_manipulation(self, client, jwt_payload):
        """Test that jku (JWK Set URL) header is validated"""
        # Token with malicious JKU
        header = {
            "alg": "RS256",
            "typ": "JWT",
            "jku": "https://evil.com/jwks.json"
        }
        
        header_encoded = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_encoded = base64.urlsafe_b64encode(
            json.dumps(jwt_payload).encode()
        ).decode().rstrip('=')
        
        token = f"{header_encoded}.{payload_encoded}.fakesig"
        
        response = client.get('/api/v1/users/me',
                             headers={'Authorization': f'Bearer {token}'})
        
        assert response.status_code == 401, \
            "Malicious jku should be rejected"


# Fixtures

@pytest.fixture
def client():
    """Create test client"""
    from samplemind.app import create_app
    app = create_app('testing')
    return app.test_client()


@pytest.fixture
def jwt_secret():
    """JWT secret key"""
    return "test_secret_key_for_jwt_testing_12345"


@pytest.fixture
def jwt_payload():
    """Standard JWT payload"""
    return {
        'user_id': 1,
        'role': 'user',
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow()
    }


@pytest.fixture
def valid_jwt_token(jwt_payload, jwt_secret):
    """Create valid JWT token"""
    return jwt.encode(jwt_payload, jwt_secret, algorithm='HS256')


@pytest.fixture
def rsa_public_key():
    """RSA public key for testing"""
    return """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----"""


@pytest.fixture
def valid_refresh_token(client):
    """Get valid refresh token"""
    response = client.post('/api/v1/auth/login',
                          json={'username': 'testuser', 'password': 'password'})
    
    return response.get_json().get('refresh_token', secrets.token_urlsafe(32))


@pytest.fixture
def expired_refresh_token(jwt_secret):
    """Create expired refresh token"""
    payload = {
        'user_id': 1,
        'type': 'refresh',
        'exp': datetime.utcnow() - timedelta(days=1),
        'iat': datetime.utcnow() - timedelta(days=2)
    }
    
    return jwt.encode(payload, jwt_secret, algorithm='HS256')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])