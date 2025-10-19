"""
API Key Generation and Management
For external developer access to SampleMind AI API
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel
from enum import Enum


class APIKeyPrefix(str, Enum):
    """API key prefixes for identification"""
    PRODUCTION = "sm_live_"
    DEVELOPMENT = "sm_test_"
    INTERNAL = "sm_internal_"


class APIKeyPermission(str, Enum):
    """Permissions that can be granted to API keys"""
    READ_AUDIO = "audio:read"
    WRITE_AUDIO = "audio:write"
    DELETE_AUDIO = "audio:delete"
    ANALYZE_AUDIO = "audio:analyze"
    SEARCH = "search:all"
    COLLECTIONS_READ = "collections:read"
    COLLECTIONS_WRITE = "collections:write"
    ADMIN = "admin:all"


class APIKey(BaseModel):
    """API Key model"""
    key_id: str
    user_id: str
    name: str
    key_hash: str  # Never store plain key
    prefix: str  # First 8 chars for identification
    permissions: List[APIKeyPermission]
    
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    
    is_active: bool = True
    usage_count: int = 0
    rate_limit_per_minute: int = 60
    
    # Metadata
    description: Optional[str] = None
    environment: str = "production"  # production, development, testing
    ip_whitelist: List[str] = []


class APIKeyCreate(BaseModel):
    """API Key creation request"""
    name: str
    permissions: List[APIKeyPermission]
    expires_in_days: Optional[int] = None  # None = no expiration
    rate_limit_per_minute: int = 60
    description: Optional[str] = None
    environment: str = "production"
    ip_whitelist: List[str] = []


class APIKeyResponse(BaseModel):
    """API Key creation response"""
    key_id: str
    key: str  # Only shown once!
    prefix: str
    name: str
    permissions: List[APIKeyPermission]
    created_at: datetime
    expires_at: Optional[datetime]
    
    warning: str = "Store this key securely. It will not be shown again."


class APIKeyPublic(BaseModel):
    """Public API key info (no sensitive data)"""
    key_id: str
    name: str
    prefix: str
    permissions: List[APIKeyPermission]
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    is_active: bool
    usage_count: int


class APIKeyService:
    """Service for managing API keys"""
    
    @staticmethod
    def generate_key(prefix: APIKeyPrefix = APIKeyPrefix.PRODUCTION) -> tuple[str, str]:
        """
        Generate a secure API key
        
        Returns:
            tuple: (full_key, key_hash)
        """
        # Generate 32 bytes of random data
        random_bytes = secrets.token_bytes(32)
        
        # Create base64-like key (URL safe)
        key_secret = secrets.token_urlsafe(32)
        
        # Combine prefix with secret
        full_key = f"{prefix.value}{key_secret}"
        
        # Hash the key for storage
        key_hash = hashlib.sha256(full_key.encode()).hexdigest()
        
        return full_key, key_hash
    
    @staticmethod
    def hash_key(key: str) -> str:
        """Hash an API key for comparison"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    @staticmethod
    def verify_key(provided_key: str, stored_hash: str) -> bool:
        """Verify an API key against stored hash"""
        provided_hash = APIKeyService.hash_key(provided_key)
        return secrets.compare_digest(provided_hash, stored_hash)
    
    @staticmethod
    def create_api_key(
        user_id: str,
        key_create: APIKeyCreate,
        environment: str = "production"
    ) -> APIKeyResponse:
        """
        Create a new API key for a user
        
        Args:
            user_id: User creating the key
            key_create: Key creation parameters
            environment: production, development, or testing
            
        Returns:
            APIKeyResponse with the generated key (shown only once!)
        """
        # Choose prefix based on environment
        prefix_map = {
            "production": APIKeyPrefix.PRODUCTION,
            "development": APIKeyPrefix.DEVELOPMENT,
            "testing": APIKeyPrefix.DEVELOPMENT,
        }
        prefix = prefix_map.get(environment, APIKeyPrefix.PRODUCTION)
        
        # Generate key
        full_key, key_hash = APIKeyService.generate_key(prefix)
        
        # Generate unique key ID
        key_id = f"key_{secrets.token_urlsafe(16)}"
        
        # Calculate expiration
        expires_at = None
        if key_create.expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=key_create.expires_in_days)
        
        # Create response (key shown only here!)
        return APIKeyResponse(
            key_id=key_id,
            key=full_key,  # Only shown once!
            prefix=full_key[:16],  # First 16 chars for identification
            name=key_create.name,
            permissions=key_create.permissions,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
        )
    
    @staticmethod
    def is_key_valid(api_key: APIKey) -> tuple[bool, Optional[str]]:
        """
        Check if an API key is valid
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if not api_key.is_active:
            return False, "API key has been revoked"
        
        if api_key.expires_at and datetime.utcnow() > api_key.expires_at:
            return False, "API key has expired"
        
        return True, None
    
    @staticmethod
    def check_permission(api_key: APIKey, required_permission: APIKeyPermission) -> bool:
        """Check if API key has required permission"""
        if APIKeyPermission.ADMIN in api_key.permissions:
            return True  # Admin has all permissions
        
        return required_permission in api_key.permissions
    
    @staticmethod
    def check_ip_whitelist(api_key: APIKey, client_ip: str) -> bool:
        """Check if client IP is whitelisted (if whitelist is configured)"""
        if not api_key.ip_whitelist:
            return True  # No whitelist = all IPs allowed
        
        return client_ip in api_key.ip_whitelist


# Example usage
"""
# Create an API key
key_service = APIKeyService()
key_create = APIKeyCreate(
    name="Production API Key",
    permissions=[
        APIKeyPermission.READ_AUDIO,
        APIKeyPermission.ANALYZE_AUDIO,
        APIKeyPermission.SEARCH
    ],
    expires_in_days=365,
    rate_limit_per_minute=100,
    description="Main production key for web app"
)

response = key_service.create_api_key(
    user_id="user_123",
    key_create=key_create,
    environment="production"
)

print(f"Your API key: {response.key}")
print("Store this securely - it will not be shown again!")

# Verify a key later
is_valid = key_service.verify_key(
    provided_key="sm_live_abc123...",
    stored_hash=stored_hash_from_db
)
"""
