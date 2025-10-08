"""
Authentication Module
Comprehensive authentication and authorization utilities

This module provides:
- JWT token management (access & refresh tokens)
- API key generation and validation
- Secure key hashing with bcrypt
- Usage tracking and metrics
- Permission scoping
- Token/key revocation
"""

from .jwt_manager import JWTManager
from .api_key_manager import (
    APIKeyManager,
    APIKeyScope,
    get_api_key_manager,
)

__all__ = [
    # JWT Management
    'JWTManager',
    
    # API Key Management
    'APIKeyManager',
    'APIKeyScope',
    'get_api_key_manager',
]