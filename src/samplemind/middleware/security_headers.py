"""
Security Headers & CORS Middleware for SampleMind AI
Implements comprehensive security headers and CORS policies for production-grade security

Features:
- Configurable security headers (X-Content-Type-Options, X-Frame-Options, etc.)
- Content Security Policy (CSP) with nonce generation
- Environment-based CORS configuration (dev vs prod)
- Header validation and sanitization
- Prometheus metrics integration
- Security headers testing utility
"""

import logging
import secrets
import re
from typing import Optional, Dict, List, Callable, Pattern, Any
from enum import Enum
from dataclasses import dataclass, field

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp
from prometheus_client import Counter, Histogram

logger = logging.getLogger(__name__)


# ====================
# Prometheus Metrics
# ====================

security_headers_applied_total = Counter(
    "samplemind_security_headers_applied_total",
    "Total security headers applied",
    ["header_name"]
)

csp_violations_total = Counter(
    "samplemind_csp_violations_total",
    "Total CSP violations reported",
    ["directive"]
)

cors_requests_total = Counter(
    "samplemind_cors_requests_total",
    "Total CORS requests",
    ["origin", "status"]
)

security_header_processing_seconds = Histogram(
    "samplemind_security_header_processing_seconds",
    "Security header processing duration",
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05)
)


# ====================
# Configuration Models
# ====================

class Environment(str, Enum):
    """Application environment"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class SecurityHeadersConfig:
    """
    Configuration for security headers
    
    Attributes:
        x_content_type_options: Prevent MIME type sniffing
        x_frame_options: Clickjacking protection
        x_xss_protection: XSS protection
        strict_transport_security: HTTPS enforcement
        content_security_policy: CSP directives
        referrer_policy: Referrer information control
        permissions_policy: Browser feature permissions
    """
    x_content_type_options: str = "nosniff"
    x_frame_options: str = "DENY"
    x_xss_protection: str = "1; mode=block"
    strict_transport_security: str = "max-age=31536000; includeSubDomains"
    content_security_policy: str = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    referrer_policy: str = "strict-origin-when-cross-origin"
    permissions_policy: str = "geolocation=(), microphone=(), camera=()"
    
    # CSP nonce support
    use_csp_nonce: bool = True
    csp_report_uri: Optional[str] = None
    
    def to_dict(self) -> Dict[str, str]:
        """Convert config to header dictionary"""
        return {
            "X-Content-Type-Options": self.x_content_type_options,
            "X-Frame-Options": self.x_frame_options,
            "X-XSS-Protection": self.x_xss_protection,
            "Strict-Transport-Security": self.strict_transport_security,
            "Content-Security-Policy": self.content_security_policy,
            "Referrer-Policy": self.referrer_policy,
            "Permissions-Policy": self.permissions_policy,
        }


@dataclass
class CORSConfig:
    """
    Configuration for CORS policy
    
    Attributes:
        allow_origins: List of allowed origins
        allow_origin_regex: Regex pattern for allowed origins
        allow_credentials: Allow cookies/auth headers
        allow_methods: Allowed HTTP methods
        allow_headers: Allowed request headers
        expose_headers: Headers exposed to client
        max_age: Preflight cache duration
    """
    allow_origins: List[str] = field(default_factory=lambda: ["https://samplemind.ai", "https://app.samplemind.ai"])
    allow_origin_regex: Optional[str] = r"https://.*\.samplemind\.ai"
    allow_credentials: bool = True
    allow_methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
    allow_headers: List[str] = field(default_factory=lambda: ["*"])
    expose_headers: List[str] = field(default_factory=lambda: ["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"])
    max_age: int = 3600
    
    @staticmethod
    def for_development() -> 'CORSConfig':
        """Development CORS configuration (more permissive)"""
        return CORSConfig(
            allow_origins=["*"],
            allow_origin_regex=None,
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["*"],
            max_age=86400,
        )
    
    @staticmethod
    def for_production() -> 'CORSConfig':
        """Production CORS configuration (restrictive)"""
        return CORSConfig(
            allow_origins=["https://samplemind.ai", "https://app.samplemind.ai"],
            allow_origin_regex=r"https://.*\.samplemind\.ai",
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["*"],
            expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
            max_age=3600,
        )


# ====================
# CSP Nonce Generator
# ====================

class CSPNonceGenerator:
    """
    Generates cryptographically secure nonces for Content Security Policy
    
    Nonces are used to allow specific inline scripts/styles while blocking others.
    """
    
    @staticmethod
    def generate_nonce() -> str:
        """
        Generate a cryptographically secure nonce
        
        Returns:
            Base64-encoded random bytes (32 bytes = 44 chars base64)
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def add_nonce_to_csp(csp: str, nonce: str) -> str:
        """
        Add nonce to CSP directives
        
        Args:
            csp: Original CSP string
            nonce: Generated nonce
        
        Returns:
            CSP with nonce added to script-src and style-src
        """
        # Add nonce to script-src
        if "script-src" in csp:
            csp = re.sub(
                r"script-src ([^;]+)",
                f"script-src \\1 'nonce-{nonce}'",
                csp
            )
        else:
            csp += f"; script-src 'nonce-{nonce}'"
        
        # Add nonce to style-src
        if "style-src" in csp:
            csp = re.sub(
                r"style-src ([^;]+)",
                f"style-src \\1 'nonce-{nonce}'",
                csp
            )
        else:
            csp += f"; style-src 'nonce-{nonce}'"
        
        return csp.strip()


# ====================
# Header Validator
# ====================

class HeaderValidator:
    """
    Validates and sanitizes security headers
    """
    
    # Valid header name pattern (RFC 7230)
    HEADER_NAME_PATTERN: Pattern = re.compile(r"^[!#$%&'*+\-.0-9A-Z^_`a-z|~]+$")
    
    # Valid header value pattern (printable ASCII except control chars)
    HEADER_VALUE_PATTERN: Pattern = re.compile(r"^[\x20-\x7E]*$")
    
    @classmethod
    def validate_header_name(cls, name: str) -> bool:
        """
        Validate header name according to RFC 7230
        
        Args:
            name: Header name
        
        Returns:
            True if valid, False otherwise
        """
        return bool(cls.HEADER_NAME_PATTERN.match(name))
    
    @classmethod
    def validate_header_value(cls, value: str) -> bool:
        """
        Validate header value (printable ASCII only)
        
        Args:
            value: Header value
        
        Returns:
            True if valid, False otherwise
        """
        return bool(cls.HEADER_VALUE_PATTERN.match(value))
    
    @classmethod
    def sanitize_header_value(cls, value: str) -> str:
        """
        Sanitize header value by removing invalid characters
        
        Args:
            value: Header value
        
        Returns:
            Sanitized value
        """
        # Remove control characters and non-printable ASCII
        return ''.join(char for char in value if 0x20 <= ord(char) <= 0x7E)
    
    @classmethod
    def validate_headers(cls, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Validate and sanitize all headers
        
        Args:
            headers: Dictionary of headers
        
        Returns:
            Validated and sanitized headers
        """
        validated = {}
        
        for name, value in headers.items():
            if not cls.validate_header_name(name):
                logger.warning(f"Invalid header name skipped: {name}")
                continue
            
            if not cls.validate_header_value(value):
                logger.warning(f"Invalid header value for {name}, sanitizing")
                value = cls.sanitize_header_value(value)
            
            validated[name] = value
        
        return validated


# ====================
# Security Headers Middleware
# ====================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for applying security headers
    
    Applies comprehensive security headers to all responses,
    with CSP nonce generation and header validation.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        config: Optional[SecurityHeadersConfig] = None,
        enabled: bool = True,
    ):
        """
        Initialize security headers middleware
        
        Args:
            app: FastAPI application
            config: Security headers configuration
            enabled: Enable/disable middleware
        """
        super().__init__(app)
        self.enabled = enabled
        self.config = config or SecurityHeadersConfig()
        
        logger.info(f"SecurityHeadersMiddleware initialized (enabled={enabled})")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and add security headers to response"""
        
        # Skip if disabled
        if not self.enabled:
            return await call_next(request)
        
        import time
        start_time = time.time()
        
        # Generate CSP nonce if enabled
        nonce: Optional[str] = None
        if self.config.use_csp_nonce:
            nonce = CSPNonceGenerator.generate_nonce()
            # Store nonce in request state for use in templates
            request.state.csp_nonce = nonce
        
        # Process request
        response = await call_next(request)
        
        # Get security headers
        headers = self.config.to_dict()
        
        # Add nonce to CSP if generated
        if nonce and "Content-Security-Policy" in headers:
            headers["Content-Security-Policy"] = CSPNonceGenerator.add_nonce_to_csp(
                headers["Content-Security-Policy"],
                nonce
            )
        
        # Add CSP report URI if configured
        if self.config.csp_report_uri and "Content-Security-Policy" in headers:
            headers["Content-Security-Policy"] += f"; report-uri {self.config.csp_report_uri}"
        
        # Validate headers
        headers = HeaderValidator.validate_headers(headers)
        
        # Apply headers to response
        for name, value in headers.items():
            response.headers[name] = value
            security_headers_applied_total.labels(header_name=name).inc()
        
        # Record processing time
        duration = time.time() - start_time
        security_header_processing_seconds.observe(duration)
        
        return response


# ====================
# CORS Configuration Helper
# ====================

def configure_cors(
    app: ASGIApp,
    environment: Environment = Environment.PRODUCTION,
    custom_config: Optional[CORSConfig] = None
) -> CORSMiddleware:
    """
    Configure CORS middleware based on environment
    
    Args:
        app: FastAPI application
        environment: Application environment
        custom_config: Custom CORS configuration (overrides environment default)
    
    Returns:
        Configured CORS middleware
    
    Example:
        app = FastAPI()
        configure_cors(app, Environment.DEVELOPMENT)
    """
    # Get config based on environment
    if custom_config:
        config = custom_config
    elif environment == Environment.DEVELOPMENT:
        config = CORSConfig.for_development()
        logger.info("Using permissive CORS configuration for development")
    else:
        config = CORSConfig.for_production()
        logger.info("Using restrictive CORS configuration for production")
    
    # Create and return CORS middleware
    middleware = CORSMiddleware(
        app=app,
        allow_origins=config.allow_origins,
        allow_origin_regex=config.allow_origin_regex,
        allow_credentials=config.allow_credentials,
        allow_methods=config.allow_methods,
        allow_headers=config.allow_headers,
        expose_headers=config.expose_headers,
        max_age=config.max_age,
    )
    
    logger.info(f"CORS middleware configured: {len(config.allow_origins)} origins allowed")
    
    return middleware


# ====================
# Security Headers Testing Utility
# ====================

class SecurityHeadersTester:
    """
    Utility for testing security headers configuration
    
    Provides methods to validate that all required security headers
    are present and properly configured.
    """
    
    REQUIRED_HEADERS = [
        "X-Content-Type-Options",
        "X-Frame-Options",
        "X-XSS-Protection",
        "Strict-Transport-Security",
        "Content-Security-Policy",
        "Referrer-Policy",
        "Permissions-Policy",
    ]
    
    @classmethod
    def test_headers(cls, headers: Dict[str, str]) -> Dict[str, bool]:
        """
        Test if all required security headers are present
        
        Args:
            headers: Response headers dictionary
        
        Returns:
            Dictionary mapping header names to presence status
        """
        results = {}
        
        for header in cls.REQUIRED_HEADERS:
            results[header] = header in headers
        
        return results
    
    @classmethod
    def validate_csp(cls, csp: str) -> Dict[str, bool]:
        """
        Validate Content Security Policy directives
        
        Args:
            csp: CSP header value
        
        Returns:
            Dictionary mapping directives to presence status
        """
        recommended_directives = [
            "default-src",
            "script-src",
            "style-src",
            "img-src",
            "font-src",
            "connect-src",
        ]
        
        results = {}
        for directive in recommended_directives:
            results[directive] = directive in csp
        
        return results
    
    @classmethod
    def check_hsts(cls, hsts: str) -> Dict[str, bool]:
        """
        Check HSTS header configuration
        
        Args:
            hsts: HSTS header value
        
        Returns:
            Dictionary with HSTS features
        """
        return {
            "has_max_age": "max-age=" in hsts,
            "includes_subdomains": "includeSubDomains" in hsts,
            "preload": "preload" in hsts,
        }
    
    @classmethod
    def generate_report(cls, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Generate comprehensive security headers report
        
        Args:
            headers: Response headers dictionary
        
        Returns:
            Comprehensive report dictionary
        """
        report = {
            "headers_present": cls.test_headers(headers),
            "all_required_present": all(cls.test_headers(headers).values()),
        }
        
        # Check CSP if present
        if "Content-Security-Policy" in headers:
            report["csp_directives"] = cls.validate_csp(headers["Content-Security-Policy"])
        
        # Check HSTS if present
        if "Strict-Transport-Security" in headers:
            report["hsts_config"] = cls.check_hsts(headers["Strict-Transport-Security"])
        
        return report


# ====================
# CSP Violation Reporter
# ====================

async def handle_csp_violation(request: Request) -> Response:
    """
    Handle CSP violation reports
    
    CSP violation reports are sent as POST requests to the report-uri
    
    Args:
        request: FastAPI request with CSP violation report
    
    Returns:
        Response acknowledging receipt
    """
    try:
        violation_data = await request.json()
        
        # Extract violation details
        csp_report = violation_data.get("csp-report", {})
        directive = csp_report.get("violated-directive", "unknown")
        blocked_uri = csp_report.get("blocked-uri", "unknown")
        
        # Log violation
        logger.warning(
            f"CSP Violation: {directive} blocked {blocked_uri}",
            extra={"csp_report": csp_report}
        )
        
        # Record metric
        csp_violations_total.labels(directive=directive).inc()
        
    except Exception as e:
        logger.error(f"Error processing CSP violation report: {e}")
    
    # Return 204 No Content
    return Response(status_code=204)


# ====================
# Convenience Functions
# ====================

def create_security_middleware(
    environment: Environment = Environment.PRODUCTION,
    custom_config: Optional[SecurityHeadersConfig] = None,
    enabled: bool = True
) -> Callable[[ASGIApp], SecurityHeadersMiddleware]:
    """
    Create security headers middleware factory
    
    Args:
        environment: Application environment
        custom_config: Custom security headers config
        enabled: Enable/disable middleware
    
    Returns:
        Middleware factory function
    
    Example:
        app = FastAPI()
        app.add_middleware(create_security_middleware(Environment.PRODUCTION))
    """
    # Use default config based on environment if not provided
    if not custom_config:
        if environment == Environment.DEVELOPMENT:
            custom_config = SecurityHeadersConfig(
                strict_transport_security="max-age=0",  # No HSTS in dev
                use_csp_nonce=False,  # Simpler CSP in dev
            )
    
    def middleware_factory(app: ASGIApp) -> SecurityHeadersMiddleware:
        return SecurityHeadersMiddleware(
            app=app,
            config=custom_config,
            enabled=enabled
        )
    
    return middleware_factory


def get_csp_nonce(request: Request) -> Optional[str]:
    """
    Get CSP nonce from request state
    
    Use this in templates to add nonce to inline scripts/styles
    
    Args:
        request: FastAPI request
    
    Returns:
        CSP nonce if available, None otherwise
    
    Example (in Jinja2 template):
        <script nonce="{{ csp_nonce }}">
            // Inline script
        </script>
    """
    return getattr(request.state, "csp_nonce", None)