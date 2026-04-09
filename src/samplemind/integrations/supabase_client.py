"""
Supabase Client — SampleMind Phase 13

Provides Supabase auth and database integration as the canonical cloud backend.
Sits alongside existing MongoDB layer — new features use Supabase, legacy code
uses MongoDB until migration is complete.

Configuration (env vars):
    SUPABASE_URL          — Supabase project URL (https://xxx.supabase.co)
    SUPABASE_ANON_KEY     — Supabase anon/public key
    SUPABASE_SERVICE_KEY  — Supabase service role key (server-side only)

Auth flow:
    1. User calls sign_in_with_email() → returns Session with JWT access token
    2. FastAPI middleware validates the JWT with verify_token()
    3. User record is synced to TortoiseUser on first login

Usage::

    from samplemind.integrations.supabase_client import get_supabase, SupabaseAuth

    # Sign in
    auth = SupabaseAuth()
    session = await auth.sign_in_with_email("user@example.com", "password")

    # Verify JWT from Authorization header
    user_id = await auth.verify_token(token)
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SupabaseSession:
    """Auth session returned after successful sign-in."""

    access_token: str
    refresh_token: str
    user_id: str
    email: str
    expires_in: int


@dataclass
class SupabaseUser:
    """Minimal Supabase user record."""

    id: str
    email: str
    email_confirmed_at: str | None
    created_at: str


# ── Client singleton ──────────────────────────────────────────────────────────

_client: object | None = None


def get_supabase() -> object | None:
    """
    Return the Supabase client singleton.

    Returns None if SUPABASE_URL or SUPABASE_ANON_KEY are not configured.
    """
    global _client

    if _client is not None:
        return _client

    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_ANON_KEY", "")

    if not url or not key:
        logger.warning(
            "SUPABASE_URL / SUPABASE_ANON_KEY not set — Supabase features disabled"
        )
        return None

    try:
        from supabase import create_client

        _client = create_client(url, key)
        logger.info(
            "✓ Supabase client initialized (project: %s)",
            url.split("//")[-1].split(".")[0],
        )
        return _client
    except ImportError:
        logger.warning("supabase SDK not installed — run: uv add supabase")
        return None
    except Exception as exc:
        logger.error("Supabase client init failed: %s", exc)
        return None


# ── Auth operations ───────────────────────────────────────────────────────────


class SupabaseAuth:
    """
    High-level Supabase authentication wrapper.

    Supports email/password, magic link, and JWT verification.
    """

    def __init__(self) -> None:
        self._client = get_supabase()

    @property
    def available(self) -> bool:
        return self._client is not None

    async def sign_up(self, email: str, password: str) -> SupabaseSession | None:
        """Register a new user and return a session."""
        if not self._client:
            return None
        try:
            response = self._client.auth.sign_up({"email": email, "password": password})
            return self._parse_session(response)
        except Exception as exc:
            logger.error("Supabase sign_up failed: %s", exc)
            return None

    async def sign_in_with_email(
        self, email: str, password: str
    ) -> SupabaseSession | None:
        """Sign in with email + password."""
        if not self._client:
            return None
        try:
            response = self._client.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            return self._parse_session(response)
        except Exception as exc:
            logger.error("Supabase sign_in failed: %s", exc)
            return None

    async def sign_in_magic_link(self, email: str) -> bool:
        """Send a magic link email. Returns True if email was sent."""
        if not self._client:
            return False
        try:
            self._client.auth.sign_in_with_otp({"email": email})
            return True
        except Exception as exc:
            logger.error("Supabase magic link failed: %s", exc)
            return False

    async def sign_out(self, access_token: str) -> bool:
        """Sign out and invalidate the session token."""
        if not self._client:
            return False
        try:
            self._client.auth.sign_out()
            return True
        except Exception as exc:
            logger.debug("Supabase sign_out: %s", exc)
            return False

    async def verify_token(self, access_token: str) -> str | None:
        """
        Verify a JWT access token and return the Supabase user ID.

        Returns:
            user_id (UUID string) if valid, None if invalid/expired.
        """
        if not self._client:
            return None
        try:
            user = self._client.auth.get_user(access_token)
            if user and user.user:
                return user.user.id
            return None
        except Exception as exc:
            logger.debug("Token verification failed: %s", exc)
            return None

    async def refresh_session(self, refresh_token: str) -> SupabaseSession | None:
        """Refresh an expired access token using the refresh token."""
        if not self._client:
            return None
        try:
            response = self._client.auth.refresh_session(refresh_token)
            return self._parse_session(response)
        except Exception as exc:
            logger.error("Supabase refresh failed: %s", exc)
            return None

    async def get_user(self, access_token: str) -> SupabaseUser | None:
        """Return the Supabase user record for a valid token."""
        if not self._client:
            return None
        try:
            response = self._client.auth.get_user(access_token)
            if response and response.user:
                u = response.user
                return SupabaseUser(
                    id=u.id,
                    email=u.email or "",
                    email_confirmed_at=getattr(u, "email_confirmed_at", None),
                    created_at=str(getattr(u, "created_at", "")),
                )
            return None
        except Exception as exc:
            logger.debug("get_user failed: %s", exc)
            return None

    @staticmethod
    def _parse_session(response: object) -> SupabaseSession | None:
        """Parse a Supabase AuthResponse into SupabaseSession."""
        try:
            session = getattr(response, "session", None)
            user = getattr(response, "user", None)
            if not session or not user:
                return None
            return SupabaseSession(
                access_token=session.access_token,
                refresh_token=session.refresh_token,
                user_id=user.id,
                email=user.email or "",
                expires_in=getattr(session, "expires_in", 3600),
            )
        except Exception as exc:
            logger.debug("Session parse failed: %s", exc)
            return None


# ── Tortoise sync helper ──────────────────────────────────────────────────────


async def sync_supabase_user(supabase_user_id: str, email: str) -> str:
    """
    Ensure a TortoiseUser exists for the given Supabase user.

    Creates the user if they don't exist yet.

    Returns:
        The internal user ID (TortoiseUser.id).
    """
    try:
        import hashlib

        from samplemind.core.database.tortoise_models import TortoiseUser

        # Derive a stable internal ID from Supabase UUID
        internal_id = hashlib.sha256(supabase_user_id.encode()).hexdigest()[:20]

        user = await TortoiseUser.get_or_none(supabase_user_id=supabase_user_id)
        if user:
            return user.id

        # Create new user record
        user = await TortoiseUser.create(
            id=internal_id,
            email=email,
            username=email.split("@")[0],
            hashed_password="",  # Supabase manages auth
            supabase_user_id=supabase_user_id,
            is_verified=True,
        )
        logger.info("Created TortoiseUser for Supabase user: %s", email)
        return user.id

    except Exception as exc:
        logger.error("Failed to sync Supabase user to Tortoise: %s", exc)
        return supabase_user_id  # fallback: use Supabase ID directly
