"""
Feature flags system for controlled feature rollout
"""

from enum import Enum
from typing import Dict, Optional, Set
from pydantic import BaseModel


class FeatureFlag(str, Enum):
    """Available feature flags"""
    
    # Audio Features
    AUDIO_UPLOAD = "audio_upload"
    AUDIO_ANALYSIS = "audio_analysis"
    AUDIO_DOWNLOAD = "audio_download"
    AUDIO_STREAMING = "audio_streaming"
    
    # AI Features
    AI_GENRE_DETECTION = "ai_genre_detection"
    AI_MOOD_DETECTION = "ai_mood_detection"
    AI_INSTRUMENT_DETECTION = "ai_instrument_detection"
    AI_MASTERING = "ai_mastering"
    AI_VOCAL_SEPARATION = "ai_vocal_separation"
    
    # Real-time Features
    WEBSOCKET_UPDATES = "websocket_updates"
    LIVE_COLLABORATION = "live_collaboration"
    
    # Advanced Features
    THREE_D_VISUALIZATION = "3d_visualization"
    VR_MODE = "vr_mode"
    BLOCKCHAIN_NFT = "blockchain_nft"
    
    # Social Features
    USER_PROFILES = "user_profiles"
    SOCIAL_SHARING = "social_sharing"
    COMMENTS = "comments"
    
    # Premium Features
    PREMIUM_TIER = "premium_tier"
    ADVANCED_ANALYSIS = "advanced_analysis"
    BATCH_PROCESSING = "batch_processing"


class FeatureStatus(BaseModel):
    """Feature flag status"""
    enabled: bool
    description: str
    beta: bool = False
    premium: bool = False
    rollout_percentage: int = 100  # 0-100


class FeatureFlagManager:
    """
    Manage feature flags for controlled rollout
    
    Features can be:
    - Enabled globally
    - Enabled for specific users
    - Enabled for percentage of users (gradual rollout)
    - Marked as beta or premium
    """
    
    def __init__(self):
        self.flags: Dict[FeatureFlag, FeatureStatus] = {
            # Audio Features - ENABLED
            FeatureFlag.AUDIO_UPLOAD: FeatureStatus(
                enabled=True,
                description="Upload audio files"
            ),
            FeatureFlag.AUDIO_ANALYSIS: FeatureStatus(
                enabled=True,
                description="Analyze audio features"
            ),
            FeatureFlag.AUDIO_DOWNLOAD: FeatureStatus(
                enabled=True,
                description="Download processed audio"
            ),
            FeatureFlag.AUDIO_STREAMING: FeatureStatus(
                enabled=False,
                description="Stream audio in browser",
                beta=True
            ),
            
            # AI Features - PARTIAL
            FeatureFlag.AI_GENRE_DETECTION: FeatureStatus(
                enabled=True,
                description="AI-powered genre detection"
            ),
            FeatureFlag.AI_MOOD_DETECTION: FeatureStatus(
                enabled=True,
                description="AI-powered mood detection"
            ),
            FeatureFlag.AI_INSTRUMENT_DETECTION: FeatureStatus(
                enabled=True,
                description="AI-powered instrument detection"
            ),
            FeatureFlag.AI_MASTERING: FeatureStatus(
                enabled=False,
                description="AI-powered mastering",
                beta=True,
                premium=True
            ),
            FeatureFlag.AI_VOCAL_SEPARATION: FeatureStatus(
                enabled=False,
                description="AI vocal separation",
                beta=True,
                premium=True
            ),
            
            # Real-time Features
            FeatureFlag.WEBSOCKET_UPDATES: FeatureStatus(
                enabled=True,
                description="Real-time WebSocket updates"
            ),
            FeatureFlag.LIVE_COLLABORATION: FeatureStatus(
                enabled=False,
                description="Real-time collaboration",
                beta=True
            ),
            
            # Advanced Features
            FeatureFlag.THREE_D_VISUALIZATION: FeatureStatus(
                enabled=False,
                description="3D audio visualization",
                beta=True,
                rollout_percentage=50
            ),
            FeatureFlag.VR_MODE: FeatureStatus(
                enabled=False,
                description="VR/XR mode",
                beta=True
            ),
            FeatureFlag.BLOCKCHAIN_NFT: FeatureStatus(
                enabled=False,
                description="Blockchain & NFT integration",
                beta=True
            ),
            
            # Social Features
            FeatureFlag.USER_PROFILES: FeatureStatus(
                enabled=False,
                description="Public user profiles",
                beta=True
            ),
            FeatureFlag.SOCIAL_SHARING: FeatureStatus(
                enabled=False,
                description="Share to social media"
            ),
            FeatureFlag.COMMENTS: FeatureStatus(
                enabled=False,
                description="Comments on tracks"
            ),
            
            # Premium Features
            FeatureFlag.PREMIUM_TIER: FeatureStatus(
                enabled=False,
                description="Premium subscription tier",
                premium=True
            ),
            FeatureFlag.ADVANCED_ANALYSIS: FeatureStatus(
                enabled=False,
                description="Advanced audio analysis",
                premium=True
            ),
            FeatureFlag.BATCH_PROCESSING: FeatureStatus(
                enabled=False,
                description="Batch process multiple files",
                premium=True
            ),
        }
        
        # Users with beta access
        self.beta_users: Set[int] = set()
        
        # Users with premium access
        self.premium_users: Set[int] = set()
        
        # Feature overrides per user
        self.user_overrides: Dict[int, Set[FeatureFlag]] = {}
    
    def is_enabled(
        self,
        flag: FeatureFlag,
        user_id: Optional[int] = None,
        is_premium: bool = False
    ) -> bool:
        """
        Check if feature is enabled
        
        Args:
            flag: Feature flag to check
            user_id: Optional user ID for user-specific flags
            is_premium: Whether user has premium subscription
        
        Returns:
            True if feature is enabled for this user
        """
        status = self.flags.get(flag)
        if not status:
            return False
        
        # Check user-specific override
        if user_id and user_id in self.user_overrides:
            if flag in self.user_overrides[user_id]:
                return True
        
        # Check if globally disabled
        if not status.enabled:
            return False
        
        # Check premium requirement
        if status.premium and not is_premium:
            return False
        
        # Check beta requirement
        if status.beta and user_id and user_id not in self.beta_users:
            return False
        
        # Check rollout percentage
        if status.rollout_percentage < 100 and user_id:
            # Simple hash-based distribution
            user_hash = hash(f"{flag.value}:{user_id}") % 100
            if user_hash >= status.rollout_percentage:
                return False
        
        return True
    
    def enable_flag(self, flag: FeatureFlag):
        """Enable feature flag globally"""
        if flag in self.flags:
            self.flags[flag].enabled = True
    
    def disable_flag(self, flag: FeatureFlag):
        """Disable feature flag globally"""
        if flag in self.flags:
            self.flags[flag].enabled = False
    
    def add_beta_user(self, user_id: int):
        """Grant beta access to user"""
        self.beta_users.add(user_id)
    
    def remove_beta_user(self, user_id: int):
        """Remove beta access from user"""
        self.beta_users.discard(user_id)
    
    def add_premium_user(self, user_id: int):
        """Grant premium access to user"""
        self.premium_users.add(user_id)
    
    def remove_premium_user(self, user_id: int):
        """Remove premium access from user"""
        self.premium_users.discard(user_id)
    
    def enable_for_user(self, flag: FeatureFlag, user_id: int):
        """Enable specific feature for specific user"""
        if user_id not in self.user_overrides:
            self.user_overrides[user_id] = set()
        self.user_overrides[user_id].add(flag)
    
    def disable_for_user(self, flag: FeatureFlag, user_id: int):
        """Disable specific feature for specific user"""
        if user_id in self.user_overrides:
            self.user_overrides[user_id].discard(flag)
    
    def get_enabled_features(
        self,
        user_id: Optional[int] = None,
        is_premium: bool = False
    ) -> Dict[str, FeatureStatus]:
        """
        Get all enabled features for user
        
        Returns:
            Dict of enabled feature flags and their status
        """
        enabled = {}
        for flag, status in self.flags.items():
            if self.is_enabled(flag, user_id, is_premium):
                enabled[flag.value] = status
        return enabled
    
    def set_rollout_percentage(self, flag: FeatureFlag, percentage: int):
        """Set rollout percentage for gradual feature rollout"""
        if flag in self.flags:
            self.flags[flag].rollout_percentage = max(0, min(100, percentage))


# Global feature flag manager
feature_flags = FeatureFlagManager()


# Convenience functions
def is_feature_enabled(
    flag: FeatureFlag,
    user_id: Optional[int] = None,
    is_premium: bool = False
) -> bool:
    """Check if feature is enabled"""
    return feature_flags.is_enabled(flag, user_id, is_premium)


def get_user_features(
    user_id: Optional[int] = None,
    is_premium: bool = False
) -> Dict[str, FeatureStatus]:
    """Get all enabled features for user"""
    return feature_flags.get_enabled_features(user_id, is_premium)
