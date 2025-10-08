"""
Unit tests for Security Headers & CORS Middleware

Tests cover:
- Security headers application
- CSP nonce generation
- Header validation
- CORS configuration
- Environment-specific configs
- Security headers testing utility
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import FastAPI, Request, Response
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from src.samplemind.middleware.security_headers import (
    SecurityHeadersMiddleware,
    SecurityHeadersConfig,
    CORSConfig,
    Environment,
    CSPNonceGenerator,
    HeaderValidator,
    SecurityHeadersTester,
    configure_cors,
    create_security_middleware,
    get_csp_nonce,
    handle_csp_violation,
)


# ====================
# Fixtures
# ====================

@pytest.fixture
def app():
    """Create FastAPI test application"""
    app = FastAPI()
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "test"}
    
    @app.get("/test-nonce")
    async def test_nonce_endpoint(request: Request):
        nonce = get_csp_nonce(request)
        return {"nonce": nonce}
    
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def security_config():
    """Default security headers configuration"""
    return SecurityHeadersConfig()


@pytest.fixture
def custom_security_config():
    """Custom security headers configuration"""
    return SecurityHeadersConfig(
        x_frame_options="SAMEORIGIN",
        content_security_policy="default-src 'self'",
        use_csp_nonce=False,
    )


# ====================
# SecurityHeadersConfig Tests
# ====================

class TestSecurityHeadersConfig:
    """Test SecurityHeadersConfig dataclass"""
    
    def test_default_config(self, security_config):
        """Test default configuration values"""
        assert security_config.x_content_type_options == "nosniff"
        assert security_config.x_frame_options == "DENY"
        assert security_config.x_xss_protection == "1; mode=block"
        assert "max-age=31536000" in security_config.strict_transport_security
        assert security_config.use_csp_nonce is True
    
    def test_to_dict(self, security_config):
        """Test conversion to dictionary"""
        headers = security_config.to_dict()
        
        assert isinstance(headers, dict)
        assert "X-Content-Type-Options" in headers
        assert "X-Frame-Options" in headers
        assert "X-XSS-Protection" in headers
        assert "Strict-Transport-Security" in headers
        assert "Content-Security-Policy" in headers
        assert "Referrer-Policy" in headers
        assert "Permissions-Policy" in headers
    
    def test_custom_config(self, custom_security_config):
        """Test custom configuration"""
        assert custom_security_config.x_frame_options == "SAMEORIGIN"
        assert custom_security_config.content_security_policy == "default-src 'self'"
        assert custom_security_config.use_csp_nonce is False


# ====================
# CORSConfig Tests
# ====================

class TestCORSConfig:
    """Test CORSConfig dataclass"""
    
    def test_default_production_config(self):
        """Test default production CORS configuration"""
        config = CORSConfig.for_production()
        
        assert "https://samplemind.ai" in config.allow_origins
        assert config.allow_credentials is True
        assert "GET" in config.allow_methods
        assert "POST" in config.allow_methods
        assert config.max_age == 3600
    
    def test_development_config(self):
        """Test development CORS configuration"""
        config = CORSConfig.for_development()
        
        assert "*" in config.allow_origins
        assert config.allow_credentials is False
        assert "*" in config.allow_methods
        assert config.max_age == 86400
    
    def test_custom_cors_config(self):
        """Test custom CORS configuration"""
        config = CORSConfig(
            allow_origins=["https://example.com"],
            allow_credentials=True,
            allow_methods=["GET", "POST"],
            max_age=7200,
        )
        
        assert "https://example.com" in config.allow_origins
        assert config.allow_credentials is True
        assert "GET" in config.allow_methods
        assert config.max_age == 7200


# ====================
# CSPNonceGenerator Tests
# ====================

class TestCSPNonceGenerator:
    """Test CSP nonce generation"""
    
    def test_generate_nonce(self):
        """Test nonce generation"""
        nonce = CSPNonceGenerator.generate_nonce()
        
        assert isinstance(nonce, str)
        assert len(nonce) > 20  # Base64 encoded, should be fairly long
        
        # Generate multiple nonces, they should be unique
        nonces = [CSPNonceGenerator.generate_nonce() for _ in range(10)]
        assert len(set(nonces)) == 10  # All unique
    
    def test_add_nonce_to_csp_script_src(self):
        """Test adding nonce to CSP script-src"""
        csp = "default-src 'self'; script-src 'self'"
        nonce = "test-nonce-123"
        
        result = CSPNonceGenerator.add_nonce_to_csp(csp, nonce)
        
        assert f"'nonce-{nonce}'" in result
        assert "script-src" in result
    
    def test_add_nonce_to_csp_style_src(self):
        """Test adding nonce to CSP style-src"""
        csp = "default-src 'self'; style-src 'self'"
        nonce = "test-nonce-456"
        
        result = CSPNonceGenerator.add_nonce_to_csp(csp, nonce)
        
        assert f"'nonce-{nonce}'" in result
        assert "style-src" in result
    
    def test_add_nonce_to_csp_both(self):
        """Test adding nonce to both script-src and style-src"""
        csp = "default-src 'self'; script-src 'self'; style-src 'self'"
        nonce = "test-nonce-789"
        
        result = CSPNonceGenerator.add_nonce_to_csp(csp, nonce)
        
        assert result.count(f"'nonce-{nonce}'") == 2  # Once for script, once for style
    
    def test_add_nonce_creates_directives_if_missing(self):
        """Test adding nonce creates directives if they don't exist"""
        csp = "default-src 'self'"
        nonce = "test-nonce-abc"
        
        result = CSPNonceGenerator.add_nonce_to_csp(csp, nonce)
        
        assert "script-src" in result
        assert "style-src" in result
        assert f"'nonce-{nonce}'" in result


# ====================
# HeaderValidator Tests
# ====================

class TestHeaderValidator:
    """Test header validation and sanitization"""
    
    def test_validate_valid_header_name(self):
        """Test validation of valid header names"""
        assert HeaderValidator.validate_header_name("X-Custom-Header") is True
        assert HeaderValidator.validate_header_name("Content-Type") is True
        assert HeaderValidator.validate_header_name("Authorization") is True
    
    def test_validate_invalid_header_name(self):
        """Test validation of invalid header names"""
        assert HeaderValidator.validate_header_name("Invalid Header") is False  # Space
        assert HeaderValidator.validate_header_name("Invalid\nHeader") is False  # Newline
        assert HeaderValidator.validate_header_name("") is False  # Empty
    
    def test_validate_valid_header_value(self):
        """Test validation of valid header values"""
        assert HeaderValidator.validate_header_value("simple value") is True
        assert HeaderValidator.validate_header_value("value123") is True
        assert HeaderValidator.validate_header_value("") is True  # Empty is valid
    
    def test_validate_invalid_header_value(self):
        """Test validation of invalid header values"""
        assert HeaderValidator.validate_header_value("value\x00null") is False  # Null byte
        assert HeaderValidator.validate_header_value("value\nwith\nnewlines") is False
    
    def test_sanitize_header_value(self):
        """Test header value sanitization"""
        # Remove control characters
        result = HeaderValidator.sanitize_header_value("value\x00\x01\x02")
        assert result == "value"
        
        # Keep printable ASCII
        result = HeaderValidator.sanitize_header_value("normal value 123")
        assert result == "normal value 123"
    
    def test_validate_headers_dict(self):
        """Test validation of headers dictionary"""
        headers = {
            "Valid-Header": "valid value",
            "Invalid Header": "should be removed",
            "Another-Valid": "value\x00with\x01control",  # Will be sanitized
        }
        
        validated = HeaderValidator.validate_headers(headers)
        
        assert "Valid-Header" in validated
        assert "Invalid Header" not in validated
        assert "Another-Valid" in validated
        assert validated["Another-Valid"] == "valuewithcontrol"


# ====================
# SecurityHeadersMiddleware Tests
# ====================

class TestSecurityHeadersMiddleware:
    """Test SecurityHeadersMiddleware"""
    
    def test_middleware_applies_headers(self, app, security_config):
        """Test that middleware applies all security headers"""
        app.add_middleware(
            SecurityHeadersMiddleware,
            config=security_config,
            enabled=True
        )
        
        client = TestClient(app)
        response = client.get("/test")
        
        assert response.status_code == 200
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        assert "Strict-Transport-Security" in response.headers
        assert "Content-Security-Policy" in response.headers
        assert "Referrer-Policy" in response.headers
        assert "Permissions-Policy" in response.headers
    
    def test_middleware_disabled(self, app, security_config):
        """Test that middleware can be disabled"""
        app.add_middleware(
            SecurityHeadersMiddleware,
            config=security_config,
            enabled=False
        )
        
        client = TestClient(app)
        response = client.get("/test")
        
        # Headers should not be present when disabled
        assert "X-Content-Type-Options" not in response.headers
        assert "X-Frame-Options" not in response.headers
    
    def test_middleware_csp_nonce_generation(self, app):
        """Test CSP nonce generation and injection"""
        config = SecurityHeadersConfig(use_csp_nonce=True)
        app.add_middleware(SecurityHeadersMiddleware, config=config, enabled=True)
        
        client = TestClient(app)
        response = client.get("/test-nonce")
        
        # Check nonce in response
        data = response.json()
        assert data["nonce"] is not None
        assert len(data["nonce"]) > 20
        
        # Check nonce in CSP header
        csp = response.headers.get("Content-Security-Policy", "")
        assert "'nonce-" in csp
    
    def test_middleware_no_nonce_when_disabled(self, app):
        """Test no nonce when disabled"""
        config = SecurityHeadersConfig(use_csp_nonce=False)
        app.add_middleware(SecurityHeadersMiddleware, config=config, enabled=True)
        
        client = TestClient(app)
        response = client.get("/test-nonce")
        
        data = response.json()
        assert data["nonce"] is None
    
    def test_middleware_csp_report_uri(self, app):
        """Test CSP report URI addition"""
        config = SecurityHeadersConfig(csp_report_uri="/csp-violation-report")
        app.add_middleware(SecurityHeadersMiddleware, config=config, enabled=True)
        
        client = TestClient(app)
        response = client.get("/test")
        
        csp = response.headers.get("Content-Security-Policy", "")
        assert "report-uri /csp-violation-report" in csp


# ====================
# SecurityHeadersTester Tests
# ====================

class TestSecurityHeadersTester:
    """Test SecurityHeadersTester utility"""
    
    def test_test_headers_all_present(self):
        """Test when all required headers are present"""
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=()",
        }
        
        results = SecurityHeadersTester.test_headers(headers)
        
        assert all(results.values())  # All should be True
    
    def test_test_headers_missing(self):
        """Test when some headers are missing"""
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
        }
        
        results = SecurityHeadersTester.test_headers(headers)
        
        assert results["X-Content-Type-Options"] is True
        assert results["X-Frame-Options"] is True
        assert results["X-XSS-Protection"] is False
        assert results["Strict-Transport-Security"] is False
    
    def test_validate_csp(self):
        """Test CSP directive validation"""
        csp = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'"
        
        results = SecurityHeadersTester.validate_csp(csp)
        
        assert results["default-src"] is True
        assert results["script-src"] is True
        assert results["style-src"] is True
        assert results["img-src"] is True
    
    def test_check_hsts(self):
        """Test HSTS header validation"""
        hsts = "max-age=31536000; includeSubDomains; preload"
        
        results = SecurityHeadersTester.check_hsts(hsts)
        
        assert results["has_max_age"] is True
        assert results["includes_subdomains"] is True
        assert results["preload"] is True
    
    def test_check_hsts_minimal(self):
        """Test HSTS with minimal configuration"""
        hsts = "max-age=31536000"
        
        results = SecurityHeadersTester.check_hsts(hsts)
        
        assert results["has_max_age"] is True
        assert results["includes_subdomains"] is False
        assert results["preload"] is False
    
    def test_generate_report(self):
        """Test comprehensive report generation"""
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=()",
        }
        
        report = SecurityHeadersTester.generate_report(headers)
        
        assert "headers_present" in report
        assert "all_required_present" in report
        assert "csp_directives" in report
        assert "hsts_config" in report
        assert report["all_required_present"] is True


# ====================
# Helper Functions Tests
# ====================

class TestHelperFunctions:
    """Test helper functions"""
    
    def test_get_csp_nonce_present(self):
        """Test getting CSP nonce when present"""
        request = Mock(spec=Request)
        request.state = Mock()
        request.state.csp_nonce = "test-nonce-xyz"
        
        nonce = get_csp_nonce(request)
        assert nonce == "test-nonce-xyz"
    
    def test_get_csp_nonce_absent(self):
        """Test getting CSP nonce when absent"""
        request = Mock(spec=Request)
        request.state = Mock()
        
        nonce = get_csp_nonce(request)
        assert nonce is None
    
    def test_create_security_middleware_production(self):
        """Test creating security middleware for production"""
        middleware_factory = create_security_middleware(
            environment=Environment.PRODUCTION,
            enabled=True
        )
        
        assert callable(middleware_factory)
        
        # Create middleware instance
        app = Mock()
        middleware = middleware_factory(app)
        assert isinstance(middleware, SecurityHeadersMiddleware)
        assert middleware.enabled is True
    
    def test_create_security_middleware_development(self):
        """Test creating security middleware for development"""
        middleware_factory = create_security_middleware(
            environment=Environment.DEVELOPMENT,
            enabled=True
        )
        
        app = Mock()
        middleware = middleware_factory(app)
        assert isinstance(middleware, SecurityHeadersMiddleware)
        # Development config should have relaxed HSTS
        assert "max-age=0" in middleware.config.strict_transport_security
    
    def test_create_security_middleware_disabled(self):
        """Test creating disabled security middleware"""
        middleware_factory = create_security_middleware(enabled=False)
        
        app = Mock()
        middleware = middleware_factory(app)
        assert middleware.enabled is False
    
    @pytest.mark.asyncio
    async def test_handle_csp_violation(self):
        """Test CSP violation handler"""
        request = Mock(spec=Request)
        request.json = AsyncMock(return_value={
            "csp-report": {
                "violated-directive": "script-src",
                "blocked-uri": "https://evil.com/script.js",
            }
        })
        
        response = await handle_csp_violation(request)
        
        assert response.status_code == 204
    
    @pytest.mark.asyncio
    async def test_handle_csp_violation_invalid_data(self):
        """Test CSP violation handler with invalid data"""
        request = Mock(spec=Request)
        request.json = AsyncMock(side_effect=Exception("Invalid JSON"))
        
        # Should not raise exception
        response = await handle_csp_violation(request)
        assert response.status_code == 204


# ====================
# Integration Tests
# ====================

class TestSecurityHeadersIntegration:
    """Integration tests for security headers middleware"""
    
    def test_full_security_stack(self, app):
        """Test complete security headers stack"""
        # Add security middleware
        config = SecurityHeadersConfig(
            use_csp_nonce=True,
            csp_report_uri="/csp-report"
        )
        app.add_middleware(SecurityHeadersMiddleware, config=config, enabled=True)
        
        client = TestClient(app)
        response = client.get("/test")
        
        # Verify all security headers
        assert response.status_code == 200
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert "max-age=" in response.headers.get("Strict-Transport-Security", "")
        
        # Verify CSP with nonce
        csp = response.headers.get("Content-Security-Policy", "")
        assert "'nonce-" in csp
        assert "report-uri /csp-report" in csp
        
        # Test header validation
        tester_results = SecurityHeadersTester.test_headers(dict(response.headers))
        assert all(tester_results.values())
    
    def test_environment_based_configuration(self, app):
        """Test environment-based security configuration"""
        # Production environment
        middleware_factory = create_security_middleware(
            environment=Environment.PRODUCTION,
            enabled=True
        )
        
        # Apply to app
        prod_middleware = middleware_factory(app)
        
        # Verify production settings
        assert "max-age=31536000" in prod_middleware.config.strict_transport_security
        assert prod_middleware.config.use_csp_nonce is True


# ====================
# Edge Cases and Error Handling
# ====================

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_headers_config(self):
        """Test with empty/minimal config"""
        config = SecurityHeadersConfig(
            x_content_type_options="",
            x_frame_options="",
        )
        
        headers = config.to_dict()
        assert "X-Content-Type-Options" in headers
        assert headers["X-Content-Type-Options"] == ""
    
    def test_very_long_csp(self):
        """Test with very long CSP"""
        long_csp = "; ".join([f"directive{i}-src 'self'" for i in range(100)])
        config = SecurityHeadersConfig(content_security_policy=long_csp)
        
        assert len(config.content_security_policy) > 1000
    
    def test_special_characters_in_headers(self):
        """Test special characters in header values"""
        # Test with various special characters
        test_values = [
            "value with spaces",
            "value-with-dashes",
            "value_with_underscores",
            "value123",
        ]
        
        for value in test_values:
            assert HeaderValidator.validate_header_value(value)
    
    def test_nonce_uniqueness(self):
        """Test that nonces are unique across requests"""
        nonces = set()
        for _ in range(100):
            nonce = CSPNonceGenerator.generate_nonce()
            assert nonce not in nonces
            nonces.add(nonce)
        
        assert len(nonces) == 100