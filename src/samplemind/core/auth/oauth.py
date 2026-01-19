"""
OAuth2 Integration for Google and GitHub
Enables social login for SampleMind AI
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, HttpUrl
from enum import Enum
import httpx
from datetime import datetime


class OAuthProvider(str, Enum):
    """Supported OAuth providers"""
    GOOGLE = "google"
    GITHUB = "github"
    SPOTIFY = "spotify"  # Future


class OAuthConfig(BaseModel):
    """OAuth provider configuration"""
    client_id: str
    client_secret: str
    redirect_uri: str
    authorization_url: str
    token_url: str
    user_info_url: str
    scopes: list[str]


# OAuth Provider Configurations
OAUTH_PROVIDERS: Dict[OAuthProvider, Dict[str, Any]] = {
    OAuthProvider.GOOGLE: {
        "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "user_info_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        "scopes": ["openid", "email", "profile"],
    },
    OAuthProvider.GITHUB: {
        "authorization_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "user_info_url": "https://api.github.com/user",
        "scopes": ["read:user", "user:email"],
    },
    OAuthProvider.SPOTIFY: {
        "authorization_url": "https://accounts.spotify.com/authorize",
        "token_url": "https://accounts.spotify.com/api/token",
        "user_info_url": "https://api.spotify.com/v1/me",
        "scopes": ["user-read-email", "user-read-private"],
    },
}


class OAuthUser(BaseModel):
    """Standardized user info from OAuth providers"""
    provider: OAuthProvider
    provider_user_id: str
    email: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    raw_data: Dict[str, Any] = {}


class OAuthService:
    """Service for OAuth authentication"""
    
    def __init__(self, provider: OAuthProvider, config: OAuthConfig):
        self.provider = provider
        self.config = config
        self.provider_config = OAUTH_PROVIDERS[provider]
    
    def get_authorization_url(self, state: str) -> str:
        """
        Generate OAuth authorization URL
        
        Args:
            state: CSRF protection state parameter
            
        Returns:
            Authorization URL to redirect user to
        """
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.provider_config["scopes"]),
            "state": state,
        }
        
        # GitHub requires different parameter name
        if self.provider == OAuthProvider.GITHUB:
            params["allow_signup"] = "true"
        
        # Build URL
        base_url = self.provider_config["authorization_url"]
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        
        return f"{base_url}?{query_string}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from OAuth callback
            
        Returns:
            Token response with access_token, refresh_token, etc.
        """
        data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code,
            "redirect_uri": self.config.redirect_uri,
            "grant_type": "authorization_code",
        }
        
        headers = {}
        if self.provider == OAuthProvider.GITHUB:
            headers["Accept"] = "application/json"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.provider_config["token_url"],
                data=data,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
    
    async def get_user_info(self, access_token: str) -> OAuthUser:
        """
        Fetch user information from OAuth provider
        
        Args:
            access_token: Access token from token exchange
            
        Returns:
            Standardized OAuthUser object
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.provider_config["user_info_url"],
                headers=headers,
            )
            response.raise_for_status()
            user_data = response.json()
        
        # Parse user data based on provider
        return self._parse_user_data(user_data)
    
    def _parse_user_data(self, data: Dict[str, Any]) -> OAuthUser:
        """Parse provider-specific user data into standard format"""
        
        if self.provider == OAuthProvider.GOOGLE:
            return OAuthUser(
                provider=self.provider,
                provider_user_id=data["id"],
                email=data["email"],
                name=data.get("name"),
                avatar_url=data.get("picture"),
                raw_data=data,
            )
        
        elif self.provider == OAuthProvider.GITHUB:
            return OAuthUser(
                provider=self.provider,
                provider_user_id=str(data["id"]),
                email=data.get("email") or f"{data['login']}@github.local",  # Fallback
                name=data.get("name") or data["login"],
                avatar_url=data.get("avatar_url"),
                raw_data=data,
            )
        
        elif self.provider == OAuthProvider.SPOTIFY:
            return OAuthUser(
                provider=self.provider,
                provider_user_id=data["id"],
                email=data["email"],
                name=data.get("display_name"),
                avatar_url=data.get("images", [{}])[0].get("url") if data.get("images") else None,
                raw_data=data,
            )
        
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")


class OAuthLinkService:
    """Service for linking OAuth accounts to existing users"""
    
    @staticmethod
    async def link_oauth_account(
        user_id: str,
        oauth_user: OAuthUser
    ) -> bool:
        """
        Link an OAuth account to an existing user

        Args:
            user_id: Existing user ID
            oauth_user: OAuth user information

        Returns:
            True if successful
        """
        from datetime import datetime
        from samplemind.core.database import get_db
        import logging

        try:
            db = await get_db()

            # Store in database
            oauth_link = {
                "user_id": user_id,
                "provider": oauth_user.provider.value,
                "provider_user_id": oauth_user.provider_user_id,
                "email": oauth_user.email,
                "linked_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }

            # Upsert the OAuth link
            result = await db.oauth_links.update_one(
                {
                    "provider": oauth_user.provider.value,
                    "provider_user_id": oauth_user.provider_user_id
                },
                {
                    "$set": oauth_link
                },
                upsert=True
            )

            return result.acknowledged

        except Exception as e:
            logging.error(f"Error linking OAuth account: {e}")
            return False
    
    @staticmethod
    async def get_user_by_oauth(
        provider: OAuthProvider,
        provider_user_id: str
    ) -> Optional[str]:
        """
        Find user ID by OAuth provider account

        Returns:
            User ID if found, None otherwise
        """
        from samplemind.core.database import get_db
        import logging

        try:
            db = await get_db()

            # Query database for linked account
            oauth_link = await db.oauth_links.find_one({
                "provider": provider.value,
                "provider_user_id": provider_user_id
            })

            if oauth_link:
                return oauth_link["user_id"]
            return None

        except Exception as e:
            logging.error(f"Error getting user by OAuth: {e}")
            return None
    
    @staticmethod
    async def unlink_oauth_account(
        user_id: str,
        provider: OAuthProvider
    ) -> bool:
        """Unlink an OAuth provider from user account"""
        from samplemind.core.database import get_db
        import logging

        try:
            db = await get_db()

            # Remove from database
            result = await db.oauth_links.delete_one({
                "user_id": user_id,
                "provider": provider.value
            })

            return result.deleted_count > 0

        except Exception as e:
            logging.error(f"Error unlinking OAuth account: {e}")
            return False


# Example usage
"""
# Initialize OAuth service
oauth_config = OAuthConfig(
    client_id="your-google-client-id",
    client_secret="your-google-client-secret",
    redirect_uri="https://samplemind.ai/auth/google/callback",
    authorization_url=OAUTH_PROVIDERS[OAuthProvider.GOOGLE]["authorization_url"],
    token_url=OAUTH_PROVIDERS[OAuthProvider.GOOGLE]["token_url"],
    user_info_url=OAUTH_PROVIDERS[OAuthProvider.GOOGLE]["user_info_url"],
    scopes=OAUTH_PROVIDERS[OAuthProvider.GOOGLE]["scopes"],
)

oauth_service = OAuthService(OAuthProvider.GOOGLE, oauth_config)

# 1. Get authorization URL
state = "random_csrf_token"
auth_url = oauth_service.get_authorization_url(state)
# Redirect user to auth_url

# 2. Handle callback (after user authorizes)
async def handle_callback(code: str):
    # Exchange code for token
    token_data = await oauth_service.exchange_code_for_token(code)
    access_token = token_data["access_token"]
    
    # Get user info
    oauth_user = await oauth_service.get_user_info(access_token)
    
    # Check if user exists
    user_id = await OAuthLinkService.get_user_by_oauth(
        oauth_user.provider,
        oauth_user.provider_user_id
    )
    
    if user_id:
        # Existing user - log them in
        return create_session(user_id)
    else:
        # New user - create account
        new_user_id = await create_user_from_oauth(oauth_user)
        await OAuthLinkService.link_oauth_account(new_user_id, oauth_user)
        return create_session(new_user_id)
"""
