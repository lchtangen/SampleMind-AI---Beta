"""
Enhanced JWT Authentication Manager
Secure token generation, validation, and revocation

This module provides production-grade JWT authentication with:
- Access tokens (short-lived, 1 hour)
- Refresh tokens (long-lived, 30 days)
- Token revocation (Redis-backed blacklist)
- Rotating signing keys
- Comprehensive validation
"""

import logging
import secrets
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json

try:
    from jose import jwt, JWTError
    from jose.exceptions import ExpiredSignatureError, JWTClaimsError
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    logging.warning("python-jose not available, JWT features disabled")

import redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


class JWTManager:
    """
    Enhanced JWT token manager with revocation support
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 60,
        refresh_token_expire_days: int = 30,
        issuer: str = "samplemind.ai",
        audience: str = "samplemind-api",
        redis_client: Optional[redis.Redis] = None
    ):
        """
        Initialize JWT manager

        Args:
            secret_key: Secret key for signing tokens
            algorithm: JWT algorithm (default: HS256)
            access_token_expire_minutes: Access token TTL (default: 60 minutes)
            refresh_token_expire_days: Refresh token TTL (default: 30 days)
            issuer: Token issuer claim
            audience: Token audience claim
            redis_client: Redis client for token revocation
        """
        if not JWT_AVAILABLE:
            raise RuntimeError("python-jose is required for JWT support")

        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire = timedelta(minutes=access_token_expire_minutes)
        self.refresh_token_expire = timedelta(days=refresh_token_expire_days)
        self.issuer = issuer
        self.audience = audience
        self.redis = redis_client

        # Token counters
        self._tokens_created = 0
        self._tokens_validated = 0
        self._tokens_revoked = 0
        self._validation_failures = 0

        logger.info(
            f"JWTManager initialized "
            f"(access: {access_token_expire_minutes}m, refresh: {refresh_token_expire_days}d)"
        )

    def create_access_token(
        self,
        subject: str,
        additional_claims: Optional[Dict[str, Any]] = None,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create access token

        Args:
            subject: User ID or identifier
            additional_claims: Additional claims to include
            expires_delta: Custom expiration delta

        Returns:
            Encoded JWT access token
        """
        expire = datetime.utcnow() + (expires_delta or self.access_token_expire)

        claims = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": self.issuer,
            "aud": self.audience,
            "type": "access",
            "jti": secrets.token_urlsafe(16)  # Unique token ID
        }

        # Add additional claims
        if additional_claims:
            claims.update(additional_claims)

        token = jwt.encode(claims, self.secret_key, algorithm=self.algorithm)
        self._tokens_created += 1

        logger.debug(f"Access token created for subject: {subject}")
        return token

    def create_refresh_token(
        self,
        subject: str,
        additional_claims: Optional[Dict[str, Any]] = None,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create refresh token

        Args:
            subject: User ID or identifier
            additional_claims: Additional claims to include
            expires_delta: Custom expiration delta

        Returns:
            Encoded JWT refresh token
        """
        expire = datetime.utcnow() + (expires_delta or self.refresh_token_expire)

        claims = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": self.issuer,
            "aud": self.audience,
            "type": "refresh",
            "jti": secrets.token_urlsafe(16)
        }

        if additional_claims:
            claims.update(additional_claims)

        token = jwt.encode(claims, self.secret_key, algorithm=self.algorithm)
        self._tokens_created += 1

        logger.debug(f"Refresh token created for subject: {subject}")
        return token

    def verify_token(
        self,
        token: str,
        expected_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify and decode JWT token

        Args:
            token: JWT token to verify
            expected_type: Expected token type ('access' or 'refresh')

        Returns:
            Decoded token claims

        Raises:
            JWTError: If token is invalid
        """
        try:
            # Check if token is revoked
            if self._is_token_revoked(token):
                self._validation_failures += 1
                raise JWTError("Token has been revoked")

            # Decode and validate
            claims = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                issuer=self.issuer,
                audience=self.audience
            )

            # Verify token type if specified
            if expected_type and claims.get("type") != expected_type:
