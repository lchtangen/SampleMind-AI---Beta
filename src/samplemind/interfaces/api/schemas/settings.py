"""
Settings and User Preferences Schemas
"""

from datetime import datetime
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field, EmailStr


class APIKeyBase(BaseModel):
    """Base API key information"""
    name: str = Field(..., min_length=1, max_length=100, description="API key name")
    provider: str = Field(..., description="API provider (e.g., 'custom', 'plugin')")


class APIKeyCreate(APIKeyBase):
    """Create API key request"""
    permissions: List[str] = Field(default=["read"], description="API key permissions")


class APIKeyResponse(APIKeyBase):
    """API key response (without secret)"""
    key_id: str = Field(..., description="Unique API key ID")
    provider: str
    created_at: datetime
    last_used: Optional[datetime] = None
    is_active: bool = True
    permissions: List[str]

    class Config:
        """Pydantic configuration for ORM mode compatibility."""
        from_attributes = True


class APIKeyWithSecret(APIKeyResponse):
    """API key with secret (only shown once on creation)"""
    secret: str = Field(..., description="API key secret (shown only once)")


class AnalysisPreferences(BaseModel):
    """Audio analysis preferences"""
    default_analysis_level: str = Field(
        default="standard",
        description="Default analysis level: basic, standard, detailed, professional"
    )
    auto_analyze_on_upload: bool = Field(default=False, description="Automatically analyze files after upload")
    include_ai_analysis: bool = Field(default=True, description="Include AI-powered analysis")
    preferred_ai_provider: Optional[str] = Field(default=None, description="Preferred AI provider")
    extract_all_features: bool = Field(default=True, description="Extract all audio features")
    cache_analysis_results: bool = Field(default=True, description="Cache analysis results for reuse")


class UIPreferences(BaseModel):
    """User interface preferences"""
    theme: str = Field(default="system", description="Theme: light, dark, system")
    accent_color: str = Field(default="blue", description="Accent color for UI")
    language: str = Field(default="en", description="UI language")
    compact_mode: bool = Field(default=False, description="Use compact UI layout")
    show_tooltips: bool = Field(default=True, description="Show helpful tooltips")
    animations_enabled: bool = Field(default=True, description="Enable UI animations")


class NotificationPreferences(BaseModel):
    """Notification settings"""
    email_on_analysis_complete: bool = Field(default=True, description="Email when analysis completes")
    email_on_upload_error: bool = Field(default=True, description="Email on upload errors")
    in_app_notifications: bool = Field(default=True, description="Show in-app notifications")
    notification_sound: bool = Field(default=True, description="Play notification sounds")
    digest_frequency: str = Field(default="daily", description="Email digest frequency: never, daily, weekly")


class CloudSyncSettings(BaseModel):
    """Cloud synchronization settings"""
    enabled: bool = Field(default=False, description="Enable cloud sync")
    sync_frequency: int = Field(default=60, ge=30, le=3600, description="Sync frequency in seconds")
    sync_library: bool = Field(default=True, description="Sync library metadata")
    sync_analysis_results: bool = Field(default=True, description="Sync analysis results")
    sync_settings: bool = Field(default=True, description="Sync user settings")
    auto_backup: bool = Field(default=True, description="Automatically backup data")
    backup_frequency: str = Field(default="daily", description="Backup frequency: never, daily, weekly")


class UserPreferences(BaseModel):
    """Complete user preferences"""
    analysis: AnalysisPreferences = Field(default_factory=AnalysisPreferences)
    ui: UIPreferences = Field(default_factory=UIPreferences)
    notifications: NotificationPreferences = Field(default_factory=NotificationPreferences)
    cloud_sync: CloudSyncSettings = Field(default_factory=CloudSyncSettings)
    custom: Dict[str, Any] = Field(default_factory=dict, description="Custom preferences")


class UserSettingsResponse(BaseModel):
    """User settings response"""
    user_id: str
    username: str
    email: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    api_keys_count: int = 0
    storage_used_mb: float = 0
    total_uploads: int = 0
    total_analyses: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration for ORM mode compatibility."""
        from_attributes = True


class UserSettingsUpdate(BaseModel):
    """Update user settings"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)
    preferences: Optional[UserPreferences] = None


class UserProfileUpdate(BaseModel):
    """Update user profile"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)


class PrivacySettings(BaseModel):
    """Privacy and data settings"""
    data_retention_days: int = Field(default=365, ge=0, description="Days to retain analysis data (0=forever)")
    analytics_enabled: bool = Field(default=True, description="Allow usage analytics")
    crash_reports_enabled: bool = Field(default=True, description="Send crash reports")
    share_feedback: bool = Field(default=False, description="Share usage feedback with developers")
    profile_visibility: str = Field(default="private", description="Profile visibility: private, public")


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str


class PreferencesResponse(BaseModel):
    """Preferences response"""
    preferences: UserPreferences
    updated_at: datetime


class StorageStatsResponse(BaseModel):
    """Storage and usage statistics"""
    storage_used_mb: float
    storage_quota_mb: float
    storage_percent_used: float
    total_files: int
    total_analyses: int
    last_cleanup: Optional[datetime] = None


class ApiKeysListResponse(BaseModel):
    """List of API keys"""
    keys: List[APIKeyResponse]
    total: int
