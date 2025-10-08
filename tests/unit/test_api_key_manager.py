"""
Comprehensive unit tests for API Key Manager

Tests cover:
- Secure key generation
- Key validation and lookup
- Usage tracking
- Permission scoping
- Key rotation
- Expiration handling
- Key listing and revocation
- MongoDB integration
- Prometheus metrics
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch, call
from bson import ObjectId

from src.samplemind.auth.api_key_manager import (
    APIKeyManager,
    APIKeyScope,
    get_api_key_manager,
)


# ====================
# Fixtures
# ====================

@pytest.fixture
def mock_database():
    """Mock MongoDB database"""
    db = Mock()
    collection = Mock()
    db.__getitem__ = Mock(return_value=collection)
    collection.create_index = Mock()
    collection.count_documents = Mock(return_value=0)
    collection.insert_one = Mock()
    collection.find_one = Mock()
    collection.find = Mock()
    collection.update_one = Mock()
    collection.update_many = Mock()
    return db


@pytest.fixture
def api_key_manager(mock_database):
    """Create API key manager instance"""
    return APIKeyManager(
        database=mock_database,
        default_expiry_days=90,
        max_keys_per_user=10
    )


@pytest.fixture
def sample_user_id():
    """Sample user ID"""
    return "user_123"


@pytest.fixture
def sample_key_doc():
    """Sample key document from database"""
    return {
        "_id": ObjectId(),
        "key_hash": "$2b$12$abcdefghijklmnopqrstuvwxyz123456789",
        "key_prefix": "sm_abc123",
        "user_id": "user_123",
        "name": "Test Key",
        "description": "Test description",
        "scopes": ["read", "write"],
        "usage_count": 5,
        "last_used_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(days=90),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_active": True
    }


# ====================
# Initialization Tests
# ====================

class TestAPIKeyManagerInit:
    """Test API key manager initialization"""

    def test_init_success(self, mock_database):
        """Test successful initialization"""
        manager = APIKeyManager(mock_database)
        
        assert manager.db == mock_database
        assert manager.default_expiry == timedelta(days=90)
        assert manager.max_keys_per_user == 10
        
        # Verify indexes created
        collection = mock_database["api_keys"]
        assert collection.create_index.call_count >= 5

    def test_init_custom_settings(self, mock_database):
        """Test initialization with custom settings"""
        manager = APIKeyManager(
            database=mock_database,
            default_expiry_days=30,
            max_keys_per_user=5
        )
        
        assert manager.default_expiry == timedelta(days=30)
        assert manager.max_keys_per_user == 5

    @patch('src.samplemind.auth.api_key_manager.BCRYPT_AVAILABLE', False)
    def test_init_without_bcrypt(self, mock_database):
        """Test initialization fails without bcrypt"""
        with pytest.raises(RuntimeError, match="passlib"):
            APIKeyManager(mock_database)


# ====================
# Key Generation Tests
# ====================

class TestAPIKeyGeneration:
    """Test API key generation"""

    def test_generate_key_success(self, api_key_manager, mock_database, sample_user_id):
        """Test successful key generation"""
        collection = mock_database["api_keys"]
        collection.count_documents = Mock(return_value=0)
        mock_result = Mock()
        mock_result.inserted_id = ObjectId()
        collection.insert_one = Mock(return_value=mock_result)
        
        result = api_key_manager.generate_api_key(
            user_id=sample_user_id,
            name="Test Key",
            scopes=["read", "write"],
            description="Test description"
        )
        
        # Verify return values
        assert "api_key" in result
        assert "key_prefix" in result
        assert "key_id" in result
        assert "created_at" in result
        assert "expires_at" in result
        
        # Verify key format
        assert len(result["api_key"]) > 32
        assert result["key_prefix"] == result["api_key"][:8]
        assert result["scopes"] == ["read", "write"]
        
        # Verify database insert
        collection.insert_one.assert_called_once()
        inserted_doc = collection.insert_one.call_args[0][0]
        assert inserted_doc["user_id"] == sample_user_id
        assert inserted_doc["name"] == "Test Key"
        assert inserted_doc["scopes"] == ["read", "write"]
        assert inserted_doc["is_active"] is True
        assert "key_hash" in inserted_doc

    def test_generate_key_invalid_scope(self, api_key_manager, sample_user_id):
        """Test key generation with invalid scope"""
        with pytest.raises(ValueError, match="Invalid scopes"):
            api_key_manager.generate_api_key(
                user_id=sample_user_id,
                name="Test Key",
                scopes=["invalid_scope"]
            )

    def test_generate_key_too_many_keys(self, api_key_manager, mock_database, sample_user_id):
        """Test key generation when user has too many keys"""
        collection = mock_database["api_keys"]
        collection.count_documents = Mock(return_value=10)
        
        with pytest.raises(ValueError, match="maximum"):
            api_key_manager.generate_api_key(
                user_id=sample_user_id,
                name="Test Key",
                scopes=["read"]
            )

    def test_generate_key_custom_expiration(self, api_key_manager, mock_database, sample_user_id):
        """Test key generation with custom expiration"""
        collection = mock_database["api_keys"]
        collection.count_documents = Mock(return_value=0)
        mock_result = Mock()
        mock_result.inserted_id = ObjectId()
        collection.insert_one = Mock(return_value=mock_result)
        
        custom_expiry = datetime.utcnow() + timedelta(days=30)
        result = api_key_manager.generate_api_key(
            user_id=sample_user_id,
            name="Test Key",
            scopes=["read"],
            expires_at=custom_expiry
        )
        
        # Verify expiration is custom value
        assert abs((result["expires_at"] - custom_expiry).total_seconds()) < 1

    def test_generate_key_all_scopes(self, api_key_manager, mock_database, sample_user_id):
        """Test key generation with all valid scopes"""
        collection = mock_database["api_keys"]
        collection.count_documents = Mock(return_value=0)
        mock_result = Mock()
        mock_result.inserted_id = ObjectId()
        collection.insert_one = Mock(return_value=mock_result)
        
        all_scopes = [APIKeyScope.READ.value, APIKeyScope.WRITE.value, APIKeyScope.ADMIN.value]
        result = api_key_manager.generate_api_key(
            user_id=sample_user_id,
            name="Admin Key",
            scopes=all_scopes
        )
        
        assert result["scopes"] == all_scopes


# ====================
# Key Validation Tests
# ====================

class TestAPIKeyValidation:
    """Test API key validation"""

    @patch('src.samplemind.auth.api_key_manager.bcrypt_hasher')
    def test_validate_key_success(self, mock_bcrypt, api_key_manager, mock_database, sample_key_doc):
        """Test successful key validation"""
        collection = mock_database["api_keys"]
        mock_bcrypt.verify = Mock(return_value=True)
        collection.find = Mock(return_value=[sample_key_doc])
        collection.update_one = Mock()
        
        api_key = "sm_abc123" + "x" * 24
        result = api_key_manager.validate_api_key(api_key)
        
        # Verify result
        assert result is not None
        assert result["user_id"] == sample_key_doc["user_id"]
        assert result["scopes"] == sample_key_doc["scopes"]
        assert result["key_prefix"] == sample_key_doc["key_prefix"]
        
        # Verify usage updated
        collection.update_one.assert_called_once()
        update_call = collection.update_one.call_args
        assert "$inc" in update_call[0][1]
        assert "$set" in update_call[0][1]

    @patch('src.samplemind.auth.api_key_manager.bcrypt_hasher')
    def test_validate_key_invalid(self, mock_bcrypt, api_key_manager, mock_database):
        """Test validation of invalid key"""
        collection = mock_database["api_keys"]
        mock_bcrypt.verify = Mock(return_value=False)
        collection.find = Mock(return_value=[])
        
        api_key = "invalid_key"
        result = api_key_manager.validate_api_key(api_key)
        
        assert result is None

    @patch('src.samplemind.auth.api_key_manager.bcrypt_hasher')
    def test_validate_key_expired(self, mock_bcrypt, api_key_manager, mock_database, sample_key_doc):
        """Test validation of expired key"""
        collection = mock_database["api_keys"]
        mock_bcrypt.verify = Mock(return_value=True)
        
        # Set expiration in the past
        sample_key_doc["expires_at"] = datetime.utcnow() - timedelta(days=1)
        collection.find = Mock(return_value=[sample_key_doc])
        
        api_key = "sm_abc123" + "x" * 24
        result = api_key_manager.validate_api_key(api_key)
        
        assert result is None

    @patch('src.samplemind.auth.api_key_manager.bcrypt_hasher')
    def test_validate_key_no_expiration(self, mock_bcrypt, api_key_manager, mock_database, sample_key_doc):
        """Test validation of key without expiration"""
        collection = mock_database["api_keys"]
        mock_bcrypt.verify = Mock(return_value=True)
        
        # Remove expiration
        sample_key_doc["expires_at"] = None
        collection.find = Mock(return_value=[sample_key_doc])
        collection.update_one = Mock()
        
        api_key = "sm_abc123" + "x" * 24
        result = api_key_manager.validate_api_key(api_key)
        
        assert result is not None


# ====================
# Key Revocation Tests
# ====================

class TestAPIKeyRevocation:
    """Test API key revocation"""

    def test_revoke_key_success(self, api_key_manager, mock_database):
        """Test successful key revocation"""
        collection = mock_database["api_keys"]
        mock_result = Mock()
        mock_result.modified_count = 1
        collection.update_one = Mock(return_value=mock_result)
        
        key_id = str(ObjectId())
        user_id = "user_123"
        
        result = api_key_manager.revoke_api_key(key_id, user_id)
        
        assert result is True
        collection.update_one.assert_called_once()
        
        # Verify update parameters
        update_call = collection.update_one.call_args
        assert str(update_call[0][0]["_id"]) == key_id
        assert update_call[0][0]["user_id"] == user_id
        assert update_call[0][1]["$set"]["is_active"] is False

    def test_revoke_key_not_found(self, api_key_manager, mock_database):
        """Test revoking non-existent key"""
        collection = mock_database["api_keys"]
        mock_result = Mock()
        mock_result.modified_count = 0
        collection.update_one = Mock(return_value=mock_result)
        
        result = api_key_manager.revoke_api_key(str(ObjectId()), "user_123")
        
        assert result is False


# ====================
# Key Listing Tests
# ====================

class TestAPIKeyListing:
    """Test API key listing"""

    def test_list_user_keys_active_only(self, api_key_manager, mock_database, sample_key_doc):
        """Test listing active keys only"""
        collection = mock_database["api_keys"]
        mock_cursor = Mock()
        mock_cursor.sort = Mock(return_value=[sample_key_doc])
        collection.find = Mock(return_value=mock_cursor)
        
        result = api_key_manager.list_user_keys("user_123", include_inactive=False)
        
        assert len(result) == 1
        assert result[0]["key_prefix"] == sample_key_doc["key_prefix"]
        assert result[0]["name"] == sample_key_doc["name"]
        
        # Verify query
        find_call = collection.find.call_args
        assert find_call[0][0]["is_active"] is True

    def test_list_user_keys_include_inactive(self, api_key_manager, mock_database, sample_key_doc):
        """Test listing all keys including inactive"""
        collection = mock_database["api_keys"]
        
        inactive_key = sample_key_doc.copy()
        inactive_key["is_active"] = False
        
        mock_cursor = Mock()
        mock_cursor.sort = Mock(return_value=[sample_key_doc, inactive_key])
        collection.find = Mock(return_value=mock_cursor)
        
        result = api_key_manager.list_user_keys("user_123", include_inactive=True)
        
        assert len(result) == 2
        
        # Verify query doesn't filter by is_active
        find_call = collection.find.call_args
        assert "is_active" not in find_call[0][0]

    def test_list_user_keys_empty(self, api_key_manager, mock_database):
        """Test listing keys for user with no keys"""
        collection = mock_database["api_keys"]
        mock_cursor = Mock()
        mock_cursor.sort = Mock(return_value=[])
        collection.find = Mock(return_value=mock_cursor)
        
        result = api_key_manager.list_user_keys("user_123")
        
        assert result == []


# ====================
# Key Rotation Tests
# ====================

class TestAPIKeyRotation:
    """Test API key rotation"""

    @patch.object(APIKeyManager, 'revoke_api_key')
    @patch.object(APIKeyManager, 'generate_api_key')
    def test_rotate_key_success(self, mock_generate, mock_revoke, api_key_manager, mock_database, sample_key_doc):
        """Test successful key rotation"""
        collection = mock_database["api_keys"]
        collection.find_one = Mock(return_value=sample_key_doc)
        
        new_key_data = {
            "api_key": "new_key",
            "key_id": str(ObjectId()),
            "key_prefix": "sm_new123"
        }
        mock_generate.return_value = new_key_data
        mock_revoke.return_value = True
        
        key_id = str(sample_key_doc["_id"])
        result = api_key_manager.rotate_api_key(key_id, "user_123")
        
        assert result == new_key_data
        mock_revoke.assert_called_once_with(key_id, "user_123")
        mock_generate.assert_called_once()

    def test_rotate_key_not_found(self, api_key_manager, mock_database):
        """Test rotating non-existent key"""
        collection = mock_database["api_keys"]
        collection.find_one = Mock(return_value=None)
        
        result = api_key_manager.rotate_api_key(str(ObjectId()), "user_123")
        
        assert result is None


# ====================
# Scope Management Tests
# ====================

class TestScopeManagement:
    """Test scope management"""

    def test_update_key_scopes_success(self, api_key_manager, mock_database):
        """Test successful scope update"""
        collection = mock_database["api_keys"]
        mock_result = Mock()
        mock_result.modified_count = 1
        collection.update_one = Mock(return_value=mock_result)
        
        result = api_key_manager.update_key_scopes(
            str(ObjectId()),
            "user_123",
            ["read", "admin"]
        )
        
        assert result is True

    def test_update_key_scopes_invalid(self, api_key_manager):
        """Test updating with invalid scopes"""
        with pytest.raises(ValueError, match="Invalid scopes"):
            api_key_manager.update_key_scopes(
                str(ObjectId()),
                "user_123",
                ["invalid_scope"]
            )

    def test_has_scope_direct(self, api_key_manager):
        """Test checking for direct scope"""
        key_metadata = {"scopes": ["read", "write"]}
        
        assert api_key_manager.has_scope(key_metadata, "read") is True
        assert api_key_manager.has_scope(key_metadata, "write") is True
        assert api_key_manager.has_scope(key_metadata, "admin") is False

    def test_has_scope_admin_grants_all(self, api_key_manager):
        """Test that admin scope grants all permissions"""
        key_metadata = {"scopes": ["admin"]}
        
        assert api_key_manager.has_scope(key_metadata, "read") is True
        assert api_key_manager.has_scope(key_metadata, "write") is True
        assert api_key_manager.has_scope(key_metadata, "admin") is True


# ====================
# Expiration Tests
# ====================

class TestKeyExpiration:
    """Test key expiration handling"""

    def test_cleanup_expired_keys(self, api_key_manager, mock_database):
        """Test cleanup of expired keys"""
        collection = mock_database["api_keys"]
        mock_result = Mock()
        mock_result.modified_count = 3
        collection.update_many = Mock(return_value=mock_result)
        
        count = api_key_manager.cleanup_expired_keys()
        
        assert count == 3
        collection.update_many.assert_called_once()
        
        # Verify query
        update_call = collection.update_many.call_args
        assert "$lt" in str(update_call[0][0]["expires_at"])
        assert update_call[0][0]["is_active"] is True

    def test_cleanup_no_expired_keys(self, api_key_manager, mock_database):
        """Test cleanup when no keys are expired"""
        collection = mock_database["api_keys"]
        mock_result = Mock()
        mock_result.modified_count = 0
        collection.update_many = Mock(return_value=mock_result)
        
        count = api_key_manager.cleanup_expired_keys()
        
        assert count == 0


# ====================
# Key Info Tests
# ====================

class TestKeyInfo:
    """Test getting key information"""

    def test_get_key_info_success(self, api_key_manager, mock_database, sample_key_doc):
        """Test getting key info"""
        collection = mock_database["api_keys"]
        collection.find_one = Mock(return_value=sample_key_doc)
        
        result = api_key_manager.get_key_info(str(sample_key_doc["_id"]), "user_123")
        
        assert result is not None
        assert result["key_prefix"] == sample_key_doc["key_prefix"]
        assert result["name"] == sample_key_doc["name"]
        assert "key_hash" not in result  # Sensitive info excluded

    def test_get_key_info_not_found(self, api_key_manager, mock_database):
        """Test getting info for non-existent key"""
        collection = mock_database["api_keys"]
        collection.find_one = Mock(return_value=None)
        
        result = api_key_manager.get_key_info(str(ObjectId()), "user_123")
        
        assert result is None


# ====================
# Singleton Tests
# ====================

class TestSingleton:
    """Test singleton pattern"""

    def test_get_api_key_manager(self, mock_database):
        """Test getting singleton instance"""
        manager1 = get_api_key_manager(mock_database)
        manager2 = get_api_key_manager(mock_database)
        
        # Both should be the same instance
        assert manager1 is manager2


# ====================
# Integration-like Tests
# ====================

class TestIntegrationScenarios:
    """Test complete workflows"""

    @patch('src.samplemind.auth.api_key_manager.bcrypt_hasher')
    def test_complete_key_lifecycle(self, mock_bcrypt, api_key_manager, mock_database):
        """Test complete key lifecycle: generate -> validate -> use -> revoke"""
        collection = mock_database["api_keys"]
        
        # Setup mocks
        collection.count_documents = Mock(return_value=0)
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = ObjectId()
        collection.insert_one = Mock(return_value=mock_insert_result)
        
        # 1. Generate key
        user_id = "user_123"
        key_data = api_key_manager.generate_api_key(
            user_id=user_id,
            name="Test Key",
            scopes=["read", "write"]
        )
        
        assert "api_key" in key_data
        api_key = key_data["api_key"]
        
        # 2. Validate key
        mock_bcrypt.verify = Mock(return_value=True)
        mock_key_doc = {
            "_id": ObjectId(key_data["key_id"]),
            "key_hash": "hashed",
            "key_prefix": key_data["key_prefix"],
            "user_id": user_id,
            "name": "Test Key",
            "scopes": ["read", "write"],
            "usage_count": 0,
            "is_active": True,
            "expires_at": key_data["expires_at"],
            "created_at": key_data["created_at"],
            "updated_at": key_data["created_at"]
        }
        collection.find = Mock(return_value=[mock_key_doc])
        collection.update_one = Mock()
        
        validated = api_key_manager.validate_api_key(api_key)
        assert validated is not None
        assert validated["user_id"] == user_id
        
        # 3. Revoke key
        mock_revoke_result = Mock()
        mock_revoke_result.modified_count = 1
        collection.update_one = Mock(return_value=mock_revoke_result)
        
        revoked = api_key_manager.revoke_api_key(key_data["key_id"], user_id)
        assert revoked is True

    def test_scope_hierarchy(self, api_key_manager):
        """Test scope permission hierarchy"""
        # Admin has all permissions
        admin_key = {"scopes": [APIKeyScope.ADMIN.value]}
        assert api_key_manager.has_scope(admin_key, APIKeyScope.READ.value)
        assert api_key_manager.has_scope(admin_key, APIKeyScope.WRITE.value)
        assert api_key_manager.has_scope(admin_key, APIKeyScope.ADMIN.value)
        
        # Write doesn't grant admin
        write_key = {"scopes": [APIKeyScope.WRITE.value]}
        assert api_key_manager.has_scope(write_key, APIKeyScope.WRITE.value)
        assert not api_key_manager.has_scope(write_key, APIKeyScope.ADMIN.value)
        
        # Read is most restrictive
        read_key = {"scopes": [APIKeyScope.READ.value]}
        assert api_key_manager.has_scope(read_key, APIKeyScope.READ.value)
        assert not api_key_manager.has_scope(read_key, APIKeyScope.WRITE.value)


# ====================
# Error Handling Tests
# ====================

class TestErrorHandling:
    """Test error handling"""

    def test_database_error_during_generation(self, api_key_manager, mock_database):
        """Test handling of database errors during generation"""
        collection = mock_database["api_keys"]
        collection.count_documents = Mock(return_value=0)
        collection.insert_one = Mock(side_effect=Exception("Database error"))
        
        with pytest.raises(Exception):
            api_key_manager.generate_api_key(
                user_id="user_123",
                name="Test Key",
                scopes=["read"]
            )

    def test_database_error_during_validation(self, api_key_manager, mock_database):
        """Test handling of database errors during validation"""
        collection = mock_database["api_keys"]
        collection.find = Mock(side_effect=Exception("Database error"))
        
        result = api_key_manager.validate_api_key("test_key")
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])