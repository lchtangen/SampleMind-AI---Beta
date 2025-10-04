"""
Unit tests for authentication system
"""
import pytest
from datetime import datetime, timedelta
from jose import jwt

from samplemind.core.auth.jwt_handler import create_access_token, create_refresh_token, verify_token, decode_token
from samplemind.core.auth.password import hash_password, verify_password


class TestPasswordHashing:
    """Test password hashing and verification"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "SecurePassword123!"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "SecurePassword123!"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "SecurePassword123!"
        wrong_password = "WrongPassword456!"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_hash_different_for_same_password(self):
        """Test that hashing same password twice gives different hashes"""
        password = "SecurePassword123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2


class TestJWTTokens:
    """Test JWT token creation and verification"""
    
    def test_create_access_token(self):
        """Test access token creation"""
        data = {"sub": "testuser", "user_id": "123"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_refresh_token(self):
        """Test refresh token creation"""
        data = {"sub": "testuser", "user_id": "123"}
        token = create_refresh_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_decode_valid_token(self):
        """Test decoding valid token"""
        data = {"sub": "testuser", "user_id": "123"}
        token = create_access_token(data)
        
        decoded = decode_token(token)
        
        assert decoded is not None
        assert decoded["sub"] == "testuser"
        assert decoded["user_id"] == "123"
    
    def test_verify_valid_token(self):
        """Test verifying valid token"""
        data = {"sub": "testuser", "user_id": "123"}
        token = create_access_token(data)
        
        is_valid = verify_token(token, "access")
        
        assert is_valid is True
    
    def test_verify_invalid_token(self):
        """Test verifying invalid token"""
        invalid_token = "invalid.token.here"
        
        is_valid = verify_token(invalid_token, "access")
        
        assert is_valid is False
    
    def test_token_expiration(self):
        """Test token expiration"""
        data = {"sub": "testuser"}
        # Create token that expires immediately
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        is_valid = verify_token(token, "access")
        
        assert is_valid is False
    
    def test_different_token_types(self):
        """Test access and refresh tokens are different"""
        data = {"sub": "testuser"}
        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)
        
        access_decoded = decode_token(access_token)
        refresh_decoded = decode_token(refresh_token)
        
        assert access_decoded["type"] == "access"
        assert refresh_decoded["type"] == "refresh"
