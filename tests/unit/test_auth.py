"""
Unit tests for authentication system
"""
import pytest
from datetime import datetime, timedelta

from samplemind.core.auth.jwt_handler import (
    configure_jwt,
    create_access_token,
    create_refresh_token,
    verify_token,
    decode_token,
    get_token_expiration,
)
from samplemind.core.auth.password import hash_password, verify_password


@pytest.fixture(autouse=True)
def configure_test_jwt():
    """Configure deterministic JWT settings for tests."""
    configure_jwt(
        secret_key="test-secret-key",
        algorithm="HS256",
        access_expire=30,
        refresh_expire=7,
    )


class TestPasswordHashing:
    """Test password hashing and verification"""
    
    def test_hash_password(self):
        """Password hashing should return a bcrypt hash"""
        password = "SecurePassword123!"
        hashed = hash_password(password)
        
        assert hashed != password
        assert hashed.startswith("$2b$")
        assert verify_password(password, hashed)
    
    def test_verify_password_correct(self):
        """Correct password validates successfully"""
        password = "SecurePassword123!"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Incorrect password returns False"""
        password = "SecurePassword123!"
        wrong_password = "WrongPassword456!"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_hash_different_for_same_password(self):
        """Hashing the same password twice yields different salts"""
        password = "SecurePassword123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2


class TestJWTTokens:
    """Test JWT token creation and verification"""
    
    def test_create_access_token(self):
        """Access token contains user id and email claims"""
        token = create_access_token(
            user_id="user-123",
            email="test@example.com",
            additional_claims={"role": "producer"},
        )
        decoded = decode_token(token)
        
        assert decoded is not None
        assert decoded["sub"] == "user-123"
        assert decoded["email"] == "test@example.com"
        assert decoded["role"] == "producer"
        assert decoded["type"] == "access"
    
    def test_create_refresh_token(self):
        """Refresh token encodes type=refresh"""
        token = create_refresh_token("user-123")
        decoded = decode_token(token)
        
        assert decoded is not None
        assert decoded["sub"] == "user-123"
        assert decoded["type"] == "refresh"
    
    def test_verify_valid_token_returns_user_id(self):
        """verify_token returns user id when token valid"""
        token = create_access_token("user-123", "test@example.com")
        user_id = verify_token(token, "access")
        
        assert user_id == "user-123"
    
    def test_verify_invalid_token(self):
        """Invalid token returns None"""
        assert verify_token("invalid.token.here", "access") is None
    
    def test_token_expiration(self):
        """Expired tokens should fail verification"""
        token = create_access_token(
            "user-123",
            "test@example.com",
            expires_delta=timedelta(seconds=-5),
        )
        assert verify_token(token, "access") is None
    
    def test_refresh_vs_access_type(self):
        """Access and refresh tokens carry different type claims"""
        access_token = create_access_token("user-123", "test@example.com")
        refresh_token = create_refresh_token("user-123")
        
        assert decode_token(access_token)["type"] == "access"
        assert decode_token(refresh_token)["type"] == "refresh"
    
    def test_get_token_expiration(self):
        """get_token_expiration returns datetime in future"""
        token = create_access_token("user-123", "test@example.com")
        exp = get_token_expiration(token)
        
        assert isinstance(exp, datetime)
        assert exp > datetime.utcnow()
