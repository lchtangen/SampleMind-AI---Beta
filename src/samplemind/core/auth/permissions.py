"""
Permission checking middleware and decorators
"""

from functools import wraps
from typing import List, Optional, Callable
from fastapi import HTTPException, status, Depends
from .rbac import Permission, UserRole, RBACService
from .dependencies import get_current_user


class PermissionDenied(HTTPException):
    """Exception raised when user lacks required permission"""
    def __init__(self, permission: Permission):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied. Required permission: {permission.value}"
        )


class InsufficientRole(HTTPException):
    """Exception raised when user role is insufficient"""
    def __init__(self, required_role: UserRole):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient role. Required: {required_role.value}"
        )


def require_permission(permission: Permission):
    """
    Dependency that checks if current user has required permission
    
    Usage:
        @app.get("/protected")
        async def protected_route(user = Depends(require_permission(Permission.AUDIO_UPLOAD))):
            return {"message": "Access granted"}
    """
    async def permission_checker(current_user = Depends(get_current_user)):
        user_role = UserRole(current_user.get("role", "free"))
        
        if not RBACService.has_permission(user_role, permission):
            raise PermissionDenied(permission)
        
        return current_user
    
    return permission_checker


def require_any_permission(*permissions: Permission):
    """
    Dependency that checks if user has ANY of the required permissions
    
    Usage:
        @app.get("/flexible")
        async def route(user = Depends(require_any_permission(
            Permission.AUDIO_UPLOAD, 
            Permission.AUDIO_BATCH_PROCESS
        ))):
            return {"message": "Access granted"}
    """
    async def permission_checker(current_user = Depends(get_current_user)):
        user_role = UserRole(current_user.get("role", "free"))
        
        if not RBACService.has_any_permission(user_role, list(permissions)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required one of: {[p.value for p in permissions]}"
            )
        
        return current_user
    
    return permission_checker


def require_all_permissions(*permissions: Permission):
    """
    Dependency that checks if user has ALL required permissions
    """
    async def permission_checker(current_user = Depends(get_current_user)):
        user_role = UserRole(current_user.get("role", "free"))
        
        if not RBACService.has_all_permissions(user_role, list(permissions)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required all of: {[p.value for p in permissions]}"
            )
        
        return current_user
    
    return permission_checker


def require_role(minimum_role: UserRole):
    """
    Dependency that checks if user has minimum required role
    
    Usage:
        @app.get("/pro-only")
        async def pro_route(user = Depends(require_role(UserRole.PRO))):
            return {"message": "Pro user access"}
    """
    async def role_checker(current_user = Depends(get_current_user)):
        user_role = UserRole(current_user.get("role", "free"))
        
        role_hierarchy = {
            UserRole.FREE: 0,
            UserRole.PRO: 1,
            UserRole.STUDIO: 2,
            UserRole.ENTERPRISE: 3,
            UserRole.ADMIN: 4,
        }
        
        if role_hierarchy.get(user_role, 0) < role_hierarchy.get(minimum_role, 0):
            raise InsufficientRole(minimum_role)
        
        return current_user
    
    return role_checker


def admin_only():
    """Shortcut for admin-only routes"""
    return require_role(UserRole.ADMIN)


# Rate limiting helpers
def check_rate_limit(user_role: UserRole, resource: str, current_usage: int) -> bool:
    """Check if user has exceeded rate limits"""
    from .rbac import get_role_limits
    
    limits = get_role_limits(user_role)
    
    limit_key = f"max_{resource}"
    if limit_key not in limits:
        return True  # No limit defined
    
    max_limit = limits[limit_key]
    
    if max_limit == -1:  # Unlimited
        return True
    
    return current_usage < max_limit


class RateLimitExceeded(HTTPException):
    """Exception for rate limit violations"""
    def __init__(self, resource: str, limit: int):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded for {resource}. Limit: {limit}"
        )


async def check_upload_limit(current_user = Depends(get_current_user)):
    """Check if user can upload more files today"""
    user_role = UserRole(current_user.get("role", "free"))
    
    # TODO: Get actual usage from database
    current_uploads_today = 0  # Placeholder
    
    if not check_rate_limit(user_role, "uploads_per_day", current_uploads_today):
        from .rbac import get_role_limits
        limit = get_role_limits(user_role)["max_uploads_per_day"]
        raise RateLimitExceeded("uploads per day", limit)
    
    return current_user


async def check_storage_limit(current_user = Depends(get_current_user)):
    """Check if user has storage space available"""
    user_role = UserRole(current_user.get("role", "free"))
    
    # TODO: Get actual storage usage from database
    current_storage_mb = 0  # Placeholder
    
    if not check_rate_limit(user_role, "storage_mb", current_storage_mb):
        from .rbac import get_role_limits
        limit = get_role_limits(user_role)["max_storage_mb"]
        raise RateLimitExceeded("storage (MB)", limit)
    
    return current_user
