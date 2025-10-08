"""
API Key Management System
Secure API key generation, validation, and lifecycle management

This module provides production-grade API key management with:
- Cryptographically secure key generation (32+ bytes)
- bcrypt hashing for secure storage
- Key validation and lookup
- Usage tracking per key (request counts, last used timestamp)
- Permission scoping (read, write, admin)
- Key rotation support
- Automatic expiration handling
- Key listing and revocation
- MongoDB integration for persistent storage
- Prometheus metrics integration
"""

import logging
import secrets
import hashlib
from typing import Optional, List, Dict, Any, Set
from datetime import datetime, timedelta
from enum import Enum

try:
    from passlib.hash import bcrypt as bcrypt_hasher
    BCRYPT_AVAILABLE = True
except ImportError:
    bcrypt_hasher = None  # type: ignore
    BCRYPT_AVAILABLE = False
    logging.warning("passlib[bcrypt] not available, API key features disabled")

from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import PyMongoError, DuplicateKeyError
from bson import ObjectId

from prometheus_client import Counter, Histogram
from ..monitoring.metrics import registry

logger = logging.getLogger(__name__)


# ====================
# Prometheus Metrics
# ====================

api_key_operations_total = Counter(
    "samplemind_api_key_operations_total",
    "Total API key operations",
    ["operation", "status"],
    registry=registry,
)

api_key_validations_total = Counter(
    "samplemind_api_key_validations_total",
    "Total API key validation attempts",
    ["result"],
    registry=registry,
)

api_key_validation_duration_seconds = Histogram(
    "samplemind_api_key_validation_duration_seconds",
    "API key validation duration in seconds",
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1),
    registry=registry,
)

api_key_usage_by_key = Counter(
    "samplemind_api_key_usage_by_key_total",
    "Total API key usage by key prefix",
    ["key_prefix"],
    registry=registry,
)


# ====================
# Enums
# ====================

class APIKeyScope(str, Enum):
    """API key permission scopes"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


# ====================
# API Key Manager
# ====================

class APIKeyManager:
    """
    Manages API keys for programmatic access to the SampleMind API
    
    Features:
    - Secure key generation (32+ bytes)
    - bcrypt hashing for storage
    - Usage tracking
    - Permission scoping
    - Automatic expiration
    - Key rotation support
    """

    # Constants
    KEY_LENGTH = 32  # 32 bytes = 256 bits
    PREFIX_LENGTH = 8  # First 8 characters for identification
    COLLECTION_NAME = "api_keys"
    
    # Bcrypt configuration
    BCRYPT_ROUNDS = 12  # Recommended for good security/performance balance

    def __init__(
        self,
        database: Database,
        default_expiry_days: int = 90,
        max_keys_per_user: int = 10
    ):
        """
        Initialize API key manager

        Args:
            database: MongoDB database instance
            default_expiry_days: Default key expiration (90 days)
            max_keys_per_user: Maximum keys per user (default: 10)
        """
        if not BCRYPT_AVAILABLE:
            raise RuntimeError("passlib[bcrypt] is required for API key support")

        self.db = database
        self.collection: Collection = database[self.COLLECTION_NAME]
        self.default_expiry = timedelta(days=default_expiry_days)
        self.max_keys_per_user = max_keys_per_user

        # Initialize indexes
        self._ensure_indexes()
        
        logger.info(
            f"APIKeyManager initialized "
            f"(expiry: {default_expiry_days}d, max_keys: {max_keys_per_user})"
        )

    def _ensure_indexes(self) -> None:
        """Create necessary database indexes"""
        try:
            # Index on key_hash for fast validation lookups
            self.collection.create_index("key_hash", unique=True)
            
            # Index on key_prefix for identification
            self.collection.create_index("key_prefix")
            
            # Index on user_id for listing user keys
            self.collection.create_index("user_id")
            
            # Compound index for user queries
            self.collection.create_index([("user_id", 1), ("is_active", 1)])
            
            # Index on expiration for automatic cleanup
            self.collection.create_index("expires_at")
            
            logger.debug("API key indexes created successfully")
        except PyMongoError as e:
            logger.error(f"Failed to create indexes: {e}")

    def generate_api_key(
        self,
        user_id: str,
        name: str,
        scopes: List[str],
        description: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Generate a new API key
        
        Args:
            user_id: User ID who owns the key
            name: Friendly name for the key
            scopes: Permission scopes (e.g., ['read', 'write'])
            description: Optional description
            expires_at: Optional custom expiration date
            
        Returns:
            Dictionary containing:
                - api_key: The plaintext key (show only once!)
                - key_prefix: First 8 characters for identification
                - key_id: Database ID
                - created_at: Creation timestamp
                - expires_at: Expiration timestamp
                
        Raises:
            ValueError: If user has too many keys or invalid scopes
            PyMongoError: If database operation fails
        """
        import time
        start_time = time.time()
        
        try:
            # Validate scopes
            valid_scopes = {s.value for s in APIKeyScope}
            invalid_scopes = set(scopes) - valid_scopes
            if invalid_scopes:
                raise ValueError(f"Invalid scopes: {invalid_scopes}")

            # Check if user has too many keys
            active_keys = self.collection.count_documents({
                "user_id": user_id,
                "is_active": True
            })
            
            if active_keys >= self.max_keys_per_user:
                api_key_operations_total.labels(
                    operation="generate", status="error"
                ).inc()
                raise ValueError(
                    f"User has reached maximum of {self.max_keys_per_user} active keys"
                )

            # Generate cryptographically secure random key
            raw_key = secrets.token_urlsafe(self.KEY_LENGTH)
            key_prefix = raw_key[:self.PREFIX_LENGTH]
            
            # Hash the key for storage
            if bcrypt_hasher is None:
                raise RuntimeError("bcrypt not available")
            key_hash = bcrypt_hasher.hash(raw_key, rounds=self.BCRYPT_ROUNDS)
            
            # Calculate expiration
            if expires_at is None:
                expires_at = datetime.utcnow() + self.default_expiry
            
            # Create key document
            now = datetime.utcnow()
            key_doc = {
                "key_hash": key_hash,
                "key_prefix": key_prefix,
                "user_id": user_id,
                "name": name,
                "description": description,
                "scopes": scopes,
                "usage_count": 0,
                "last_used_at": None,
                "expires_at": expires_at,
                "created_at": now,
                "updated_at": now,
                "is_active": True
            }
            
            # Insert into database
            result = self.collection.insert_one(key_doc)
            key_id = str(result.inserted_id)
            
            # Record metrics
            api_key_operations_total.labels(
                operation="generate", status="success"
            ).inc()
            
            duration = time.time() - start_time
            logger.info(
                f"API key generated for user {user_id}: "
                f"{key_prefix}... (duration: {duration:.3f}s)"
            )
            
            # Return plaintext key (only time it's visible!)
            return {
                "api_key": raw_key,
                "key_prefix": key_prefix,
                "key_id": key_id,
                "name": name,
                "scopes": scopes,
                "created_at": now,
                "expires_at": expires_at
            }
            
        except (ValueError, PyMongoError) as e:
            api_key_operations_total.labels(
                operation="generate", status="error"
            ).inc()
            logger.error(f"Failed to generate API key: {e}")
            raise

    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Validate an API key and return its metadata
        
        Args:
            api_key: The plaintext API key to validate
            
        Returns:
            Dictionary with key metadata if valid, None otherwise
            Contains: user_id, scopes, usage_count, expires_at, etc.
            
        Note:
            This method also updates usage statistics
        """
        import time
        start_time = time.time()
        
        try:
            key_prefix = api_key[:self.PREFIX_LENGTH]
            
            # Find potential matching keys by prefix
            candidates = self.collection.find({
                "key_prefix": key_prefix,
                "is_active": True
            })
            
            for candidate in candidates:
                # Verify hash
                if bcrypt_hasher is None:
                    raise RuntimeError("bcrypt not available")
                if bcrypt_hasher.verify(api_key, candidate["key_hash"]):
                    # Check expiration
                    expires_at = candidate.get("expires_at")
                    if expires_at and datetime.utcnow() > expires_at:
                        api_key_validations_total.labels(result="expired").inc()
                        logger.warning(f"API key expired: {key_prefix}...")
                        return None
                    
                    # Update usage statistics
                    self.collection.update_one(
                        {"_id": candidate["_id"]},
                        {
                            "$inc": {"usage_count": 1},
                            "$set": {
                                "last_used_at": datetime.utcnow(),
                                "updated_at": datetime.utcnow()
                            }
                        }
                    )
                    
                    # Record metrics
                    api_key_validations_total.labels(result="valid").inc()
                    api_key_usage_by_key.labels(key_prefix=key_prefix).inc()
                    
                    duration = time.time() - start_time
                    api_key_validation_duration_seconds.observe(duration)
                    
                    logger.debug(f"API key validated: {key_prefix}... (duration: {duration:.3f}s)")
                    
                    # Return metadata (without sensitive info)
                    return {
                        "key_id": str(candidate["_id"]),
                        "key_prefix": key_prefix,
                        "user_id": candidate["user_id"],
                        "name": candidate["name"],
                        "scopes": candidate["scopes"],
                        "usage_count": candidate["usage_count"] + 1,
                        "last_used_at": datetime.utcnow(),
                        "expires_at": candidate.get("expires_at"),
                        "created_at": candidate["created_at"]
                    }
            
            # No valid key found
            api_key_validations_total.labels(result="invalid").inc()
            duration = time.time() - start_time
            api_key_validation_duration_seconds.observe(duration)
            
            logger.warning(f"Invalid API key attempt: {key_prefix}...")
            return None
            
        except PyMongoError as e:
            api_key_validations_total.labels(result="error").inc()
            logger.error(f"Database error during key validation: {e}")
            return None

    def revoke_api_key(self, key_id: str, user_id: str) -> bool:
        """
        Revoke an API key
        
        Args:
            key_id: Database ID of the key
            user_id: User ID (for authorization)
            
        Returns:
            True if revoked, False otherwise
        """
        try:
            result = self.collection.update_one(
                {
                    "_id": ObjectId(key_id),
                    "user_id": user_id  # Ensure user owns the key
                },
                {
                    "$set": {
                        "is_active": False,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                api_key_operations_total.labels(
                    operation="revoke", status="success"
                ).inc()
                logger.info(f"API key revoked: {key_id}")
                return True
            else:
                api_key_operations_total.labels(
                    operation="revoke", status="not_found"
                ).inc()
                logger.warning(f"API key not found or already revoked: {key_id}")
                return False
                
        except PyMongoError as e:
            api_key_operations_total.labels(
                operation="revoke", status="error"
            ).inc()
            logger.error(f"Failed to revoke API key: {e}")
            return False

    def list_user_keys(
        self,
        user_id: str,
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List all API keys for a user
        
        Args:
            user_id: User ID
            include_inactive: Include revoked keys (default: False)
            
        Returns:
            List of key metadata dictionaries
        """
        try:
            query: Dict[str, Any] = {"user_id": user_id}
            if not include_inactive:
                query["is_active"] = True
            
            keys = self.collection.find(query).sort("created_at", -1)
            
            result = []
            for key in keys:
                result.append({
                    "key_id": str(key["_id"]),
                    "key_prefix": key["key_prefix"],
                    "name": key["name"],
                    "description": key.get("description"),
                    "scopes": key["scopes"],
                    "usage_count": key["usage_count"],
                    "last_used_at": key.get("last_used_at"),
                    "expires_at": key.get("expires_at"),
                    "created_at": key["created_at"],
                    "is_active": key["is_active"]
                })
            
            api_key_operations_total.labels(
                operation="list", status="success"
            ).inc()
            
            logger.debug(f"Listed {len(result)} keys for user {user_id}")
            return result
            
        except PyMongoError as e:
            api_key_operations_total.labels(
                operation="list", status="error"
            ).inc()
            logger.error(f"Failed to list API keys: {e}")
            return []

    def rotate_api_key(
        self,
        key_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Rotate an API key (revoke old, generate new with same settings)
        
        Args:
            key_id: Database ID of the key to rotate
            user_id: User ID (for authorization)
            
        Returns:
            New key information if successful, None otherwise
        """
        try:
            # Get existing key
            old_key = self.collection.find_one({
                "_id": ObjectId(key_id),
                "user_id": user_id
            })
            
            if not old_key:
                logger.warning(f"Key not found for rotation: {key_id}")
                return None
            
            # Revoke old key
            self.revoke_api_key(key_id, user_id)
            
            # Generate new key with same settings
            new_key = self.generate_api_key(
                user_id=user_id,
                name=old_key["name"],
                scopes=old_key["scopes"],
                description=old_key.get("description"),
                expires_at=old_key.get("expires_at")
            )
            
            api_key_operations_total.labels(
                operation="rotate", status="success"
            ).inc()
            
            logger.info(f"API key rotated: {key_id} -> {new_key['key_id']}")
            return new_key
            
        except (ValueError, PyMongoError) as e:
            api_key_operations_total.labels(
                operation="rotate", status="error"
            ).inc()
            logger.error(f"Failed to rotate API key: {e}")
            return None

    def update_key_scopes(
        self,
        key_id: str,
        user_id: str,
        scopes: List[str]
    ) -> bool:
        """
        Update permission scopes for an API key
        
        Args:
            key_id: Database ID of the key
            user_id: User ID (for authorization)
            scopes: New list of scopes
            
        Returns:
            True if updated, False otherwise
        """
        try:
            # Validate scopes
            valid_scopes = {s.value for s in APIKeyScope}
            invalid_scopes = set(scopes) - valid_scopes
            if invalid_scopes:
                raise ValueError(f"Invalid scopes: {invalid_scopes}")
            
            result = self.collection.update_one(
                {
                    "_id": ObjectId(key_id),
                    "user_id": user_id
                },
                {
                    "$set": {
                        "scopes": scopes,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                api_key_operations_total.labels(
                    operation="update_scopes", status="success"
                ).inc()
                logger.info(f"Updated scopes for key {key_id}: {scopes}")
                return True
            else:
                api_key_operations_total.labels(
                    operation="update_scopes", status="not_found"
                ).inc()
                return False
                
        except (ValueError, PyMongoError) as e:
            api_key_operations_total.labels(
                operation="update_scopes", status="error"
            ).inc()
            logger.error(f"Failed to update key scopes: {e}")
            return False

    def cleanup_expired_keys(self) -> int:
        """
        Deactivate expired API keys
        
        Returns:
            Number of keys deactivated
        """
        try:
            result = self.collection.update_many(
                {
                    "expires_at": {"$lt": datetime.utcnow()},
                    "is_active": True
                },
                {
                    "$set": {
                        "is_active": False,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            count = result.modified_count
            if count > 0:
                api_key_operations_total.labels(
                    operation="cleanup", status="success"
                ).inc()
                logger.info(f"Deactivated {count} expired API keys")
            
            return count
            
        except PyMongoError as e:
            api_key_operations_total.labels(
                operation="cleanup", status="error"
            ).inc()
            logger.error(f"Failed to cleanup expired keys: {e}")
            return 0

    def get_key_info(self, key_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific API key
        
        Args:
            key_id: Database ID of the key
            user_id: User ID (for authorization)
            
        Returns:
            Key metadata if found, None otherwise
        """
        try:
            key = self.collection.find_one({
                "_id": ObjectId(key_id),
                "user_id": user_id
            })
            
            if not key:
                return None
            
            return {
                "key_id": str(key["_id"]),
                "key_prefix": key["key_prefix"],
                "name": key["name"],
                "description": key.get("description"),
                "scopes": key["scopes"],
                "usage_count": key["usage_count"],
                "last_used_at": key.get("last_used_at"),
                "expires_at": key.get("expires_at"),
                "created_at": key["created_at"],
                "updated_at": key["updated_at"],
                "is_active": key["is_active"]
            }
            
        except PyMongoError as e:
            logger.error(f"Failed to get key info: {e}")
            return None

    def has_scope(self, key_metadata: Dict[str, Any], required_scope: str) -> bool:
        """
        Check if an API key has a required scope
        
        Args:
            key_metadata: Key metadata from validate_api_key()
            required_scope: Required scope (e.g., 'write')
            
        Returns:
            True if key has the scope, False otherwise
        """
        scopes = key_metadata.get("scopes", [])
        
        # Admin scope grants all permissions
        if APIKeyScope.ADMIN.value in scopes:
            return True
        
        return required_scope in scopes


# ====================
# Singleton Instance
# ====================

_api_key_manager: Optional[APIKeyManager] = None


def get_api_key_manager(database: Database) -> APIKeyManager:
    """
    Get or create singleton API key manager instance
    
    Args:
        database: MongoDB database instance
        
    Returns:
        APIKeyManager instance
    """
    global _api_key_manager
    
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager(database)
    
    return _api_key_manager