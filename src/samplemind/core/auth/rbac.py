"""
Role-Based Access Control (RBAC) System
Defines user roles and permissions for SampleMind AI
"""

from enum import Enum
from typing import List, Set, Optional
from pydantic import BaseModel


class UserRole(str, Enum):
    """User role definitions"""
    FREE = "free"
    PRO = "pro"
    STUDIO = "studio"
    ENTERPRISE = "enterprise"
    ADMIN = "admin"


class Permission(str, Enum):
    """System permissions"""
    # Audio permissions
    AUDIO_UPLOAD = "audio:upload"
    AUDIO_ANALYZE = "audio:analyze"
    AUDIO_DELETE = "audio:delete"
    AUDIO_DOWNLOAD = "audio:download"
    AUDIO_SHARE = "audio:share"
    
    # Advanced audio permissions
    AUDIO_BATCH_PROCESS = "audio:batch_process"
    AUDIO_SOURCE_SEPARATION = "audio:source_separation"
    AUDIO_AI_GENERATION = "audio:ai_generation"
    
    # Search permissions
    SEARCH_BASIC = "search:basic"
    SEARCH_SEMANTIC = "search:semantic"
    SEARCH_ADVANCED = "search:advanced"
    
    # Collection permissions
    COLLECTION_CREATE = "collection:create"
    COLLECTION_EDIT = "collection:edit"
    COLLECTION_DELETE = "collection:delete"
    COLLECTION_SHARE = "collection:share"
    
    # API permissions
    API_KEY_CREATE = "api:key_create"
    API_KEY_REVOKE = "api:key_revoke"
    
    # Admin permissions
    ADMIN_USER_MANAGE = "admin:user_manage"
    ADMIN_ANALYTICS_VIEW = "admin:analytics_view"
    ADMIN_SYSTEM_CONFIG = "admin:system_config"


# Role to permissions mapping
ROLE_PERMISSIONS: dict[UserRole, Set[Permission]] = {
    UserRole.FREE: {
        Permission.AUDIO_UPLOAD,
        Permission.AUDIO_ANALYZE,
        Permission.AUDIO_DELETE,
        Permission.AUDIO_DOWNLOAD,
        Permission.SEARCH_BASIC,
        Permission.COLLECTION_CREATE,
        Permission.COLLECTION_EDIT,
        Permission.COLLECTION_DELETE,
    },
    
    UserRole.PRO: {
        # All FREE permissions plus:
        Permission.AUDIO_UPLOAD,
        Permission.AUDIO_ANALYZE,
        Permission.AUDIO_DELETE,
        Permission.AUDIO_DOWNLOAD,
        Permission.AUDIO_SHARE,
        Permission.AUDIO_BATCH_PROCESS,
        Permission.SEARCH_BASIC,
        Permission.SEARCH_SEMANTIC,
        Permission.COLLECTION_CREATE,
        Permission.COLLECTION_EDIT,
        Permission.COLLECTION_DELETE,
        Permission.COLLECTION_SHARE,
        Permission.API_KEY_CREATE,
    },
    
    UserRole.STUDIO: {
        # All PRO permissions plus:
        Permission.AUDIO_UPLOAD,
        Permission.AUDIO_ANALYZE,
        Permission.AUDIO_DELETE,
        Permission.AUDIO_DOWNLOAD,
        Permission.AUDIO_SHARE,
        Permission.AUDIO_BATCH_PROCESS,
        Permission.AUDIO_SOURCE_SEPARATION,
        Permission.AUDIO_AI_GENERATION,
        Permission.SEARCH_BASIC,
        Permission.SEARCH_SEMANTIC,
        Permission.SEARCH_ADVANCED,
        Permission.COLLECTION_CREATE,
        Permission.COLLECTION_EDIT,
        Permission.COLLECTION_DELETE,
        Permission.COLLECTION_SHARE,
        Permission.API_KEY_CREATE,
        Permission.API_KEY_REVOKE,
    },
    
    UserRole.ENTERPRISE: {
        # All STUDIO permissions (same set for now)
        Permission.AUDIO_UPLOAD,
        Permission.AUDIO_ANALYZE,
        Permission.AUDIO_DELETE,
        Permission.AUDIO_DOWNLOAD,
        Permission.AUDIO_SHARE,
        Permission.AUDIO_BATCH_PROCESS,
        Permission.AUDIO_SOURCE_SEPARATION,
        Permission.AUDIO_AI_GENERATION,
        Permission.SEARCH_BASIC,
        Permission.SEARCH_SEMANTIC,
        Permission.SEARCH_ADVANCED,
        Permission.COLLECTION_CREATE,
        Permission.COLLECTION_EDIT,
        Permission.COLLECTION_DELETE,
        Permission.COLLECTION_SHARE,
        Permission.API_KEY_CREATE,
        Permission.API_KEY_REVOKE,
    },
    
    UserRole.ADMIN: {
        # All permissions
        *[p for p in Permission],
    }
}


class RBACService:
    """Service for role-based access control"""
    
    @staticmethod
    def get_permissions_for_role(role: UserRole) -> Set[Permission]:
        """Get all permissions for a given role"""
        return ROLE_PERMISSIONS.get(role, set())
    
    @staticmethod
    def has_permission(role: UserRole, permission: Permission) -> bool:
        """Check if a role has a specific permission"""
        role_perms = ROLE_PERMISSIONS.get(role, set())
        return permission in role_perms
    
    @staticmethod
    def has_any_permission(role: UserRole, permissions: List[Permission]) -> bool:
        """Check if a role has any of the specified permissions"""
        role_perms = ROLE_PERMISSIONS.get(role, set())
        return any(perm in role_perms for perm in permissions)
    
    @staticmethod
    def has_all_permissions(role: UserRole, permissions: List[Permission]) -> bool:
        """Check if a role has all of the specified permissions"""
        role_perms = ROLE_PERMISSIONS.get(role, set())
        return all(perm in role_perms for perm in permissions)
    
    @staticmethod
    def can_upgrade_to(current_role: UserRole, target_role: UserRole) -> bool:
        """Check if a user can upgrade from current role to target role"""
        role_hierarchy = [
            UserRole.FREE,
            UserRole.PRO,
            UserRole.STUDIO,
            UserRole.ENTERPRISE,
            UserRole.ADMIN,
        ]
        
        try:
            current_idx = role_hierarchy.index(current_role)
            target_idx = role_hierarchy.index(target_role)
            return target_idx > current_idx
        except ValueError:
            return False


# Usage limits per role
ROLE_LIMITS = {
    UserRole.FREE: {
        "max_uploads_per_day": 10,
        "max_storage_mb": 100,
        "max_api_calls_per_minute": 10,
        "max_collections": 3,
        "max_batch_size": 5,
    },
    UserRole.PRO: {
        "max_uploads_per_day": 100,
        "max_storage_mb": 5000,  # 5GB
        "max_api_calls_per_minute": 100,
        "max_collections": 50,
        "max_batch_size": 50,
    },
    UserRole.STUDIO: {
        "max_uploads_per_day": 1000,
        "max_storage_mb": 50000,  # 50GB
        "max_api_calls_per_minute": 500,
        "max_collections": 500,
        "max_batch_size": 200,
    },
    UserRole.ENTERPRISE: {
        "max_uploads_per_day": -1,  # Unlimited
        "max_storage_mb": -1,  # Unlimited
        "max_api_calls_per_minute": 2000,
        "max_collections": -1,  # Unlimited
        "max_batch_size": 1000,
    },
    UserRole.ADMIN: {
        "max_uploads_per_day": -1,
        "max_storage_mb": -1,
        "max_api_calls_per_minute": -1,
        "max_collections": -1,
        "max_batch_size": -1,
    },
}


def get_role_limits(role: UserRole) -> dict:
    """Get usage limits for a role"""
    return ROLE_LIMITS.get(role, ROLE_LIMITS[UserRole.FREE])
