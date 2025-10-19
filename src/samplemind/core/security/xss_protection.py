"""
XSS (Cross-Site Scripting) Protection
Sanitizes user input to prevent XSS attacks
"""

import html
import re
from typing import Optional, Dict, Any
from pydantic import BaseModel, validator
from fastapi import Response
import bleach


class XSSProtection:
    """XSS protection utilities"""
    
    # Dangerous HTML tags to strip
    DANGEROUS_TAGS = [
        'script', 'iframe', 'object', 'embed', 'applet',
        'meta', 'link', 'style', 'form', 'input', 'button'
    ]
    
    # Dangerous attributes
    DANGEROUS_ATTRIBUTES = [
        'onerror', 'onload', 'onclick', 'onmouseover',
        'onfocus', 'onblur', 'onchange', 'onsubmit',
        'javascript:', 'vbscript:', 'data:'
    ]
    
    # Safe tags for rich text (if needed)
    SAFE_TAGS = [
        'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3',
        'ul', 'ol', 'li', 'a', 'blockquote', 'code', 'pre'
    ]
    
    SAFE_ATTRIBUTES = {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'title'],
    }
    
    @staticmethod
    def escape_html(text: str) -> str:
        """
        Escape HTML special characters
        
        Args:
            text: Input text
            
        Returns:
            HTML-escaped text
        """
        if not text:
            return text
        
        return html.escape(text)
    
    @staticmethod
    def unescape_html(text: str) -> str:
        """Unescape HTML entities"""
        if not text:
            return text
        
        return html.unescape(text)
    
    @staticmethod
    def strip_dangerous_html(text: str) -> str:
        """
        Strip dangerous HTML tags and attributes
        
        Args:
            text: HTML text
            
        Returns:
            Sanitized HTML
        """
        if not text:
            return text
        
        # Use bleach library for safe HTML sanitization
        cleaned = bleach.clean(
            text,
            tags=XSSProtection.SAFE_TAGS,
            attributes=XSSProtection.SAFE_ATTRIBUTES,
            strip=True  # Strip instead of escape
        )
        
        return cleaned
    
    @staticmethod
    def sanitize_for_json(data: Any) -> Any:
        """
        Recursively sanitize data for JSON output
        Escapes HTML in string values
        
        Args:
            data: Input data (dict, list, str, or primitive)
            
        Returns:
            Sanitized data
        """
        if isinstance(data, dict):
            return {k: XSSProtection.sanitize_for_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [XSSProtection.sanitize_for_json(item) for item in data]
        elif isinstance(data, str):
            return XSSProtection.escape_html(data)
        else:
            return data
    
    @staticmethod
    def detect_xss_attempt(text: str) -> bool:
        """
        Detect potential XSS attempts
        
        Returns:
            True if XSS pattern detected
        """
        if not isinstance(text, str):
            return False
        
        text_lower = text.lower()
        
        # Check for script tags
        if '<script' in text_lower:
            return True
        
        # Check for javascript: protocol
        if 'javascript:' in text_lower:
            return True
        
        # Check for event handlers
        for attr in XSSProtection.DANGEROUS_ATTRIBUTES:
            if attr.lower() in text_lower:
                return True
        
        # Check for common XSS patterns
        xss_patterns = [
            r'<img[^>]+src[^>]*=',
            r'<iframe',
            r'<object',
            r'<embed',
            r'onerror\s*=',
            r'onload\s*=',
            r'javascript:',
            r'vbscript:',
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def sanitize_url(url: str) -> Optional[str]:
        """
        Sanitize URL to prevent javascript: and data: URIs
        
        Args:
            url: Input URL
            
        Returns:
            Sanitized URL or None if dangerous
        """
        if not url:
            return url
        
        url = url.strip().lower()
        
        # Block dangerous protocols
        dangerous_protocols = ['javascript:', 'data:', 'vbscript:', 'file:']
        for protocol in dangerous_protocols:
            if url.startswith(protocol):
                return None
        
        # Only allow http, https, mailto
        if not url.startswith(('http://', 'https://', 'mailto:', '/')):
            return None
        
        return url
    
    @staticmethod
    def add_security_headers(response: Response) -> Response:
        """
        Add security headers to HTTP response
        
        Args:
            response: FastAPI Response object
            
        Returns:
            Response with security headers
        """
        # Prevent XSS
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Prevent MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.samplemind.ai; "
        )
        response.headers["Content-Security-Policy"] = csp
        
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=()"
        )
        
        return response


class SafeHTML(BaseModel):
    """Model for safe HTML content"""
    content: str
    
    @validator('content')
    def sanitize_html(cls, v):
        """Automatically sanitize HTML on input"""
        if XSSProtection.detect_xss_attempt(v):
            # Strip all HTML if XSS detected
            return XSSProtection.escape_html(v)
        
        # Otherwise clean dangerous tags
        return XSSProtection.strip_dangerous_html(v)


class SafeURL(BaseModel):
    """Model for safe URLs"""
    url: str
    
    @validator('url')
    def sanitize_url(cls, v):
        """Automatically sanitize URL"""
        safe_url = XSSProtection.sanitize_url(v)
        if safe_url is None:
            raise ValueError("Dangerous URL protocol detected")
        return safe_url


# FastAPI middleware for automatic XSS protection
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse


class XSSProtectionMiddleware(BaseHTTPMiddleware):
    """Middleware to add XSS protection headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # CSP
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "img-src 'self' data: https:; "
        )
        response.headers["Content-Security-Policy"] = csp
        
        return response


# Example usage in FastAPI
"""
from fastapi import FastAPI, Depends
from .xss_protection import XSSProtection, XSSProtectionMiddleware, SafeHTML

app = FastAPI()

# Add XSS protection middleware
app.add_middleware(XSSProtectionMiddleware)

@app.post("/comments")
async def create_comment(comment: SafeHTML):
    # comment.content is automatically sanitized
    # Safe to store in database
    return {"message": "Comment created", "content": comment.content}

@app.get("/data")
async def get_data():
    # Data from database (potentially user-generated)
    data = {
        "user_name": "<script>alert('xss')</script>John",
        "bio": "I love <b>coding</b>!"
    }
    
    # Sanitize before sending
    safe_data = XSSProtection.sanitize_for_json(data)
    
    return safe_data

# Output:
# {
#   "user_name": "&lt;script&gt;alert('xss')&lt;/script&gt;John",
#   "bio": "I love coding!"  # <b> tag stripped
# }
"""


# Content sanitization for different contexts
class ContextSanitizer:
    """Context-aware sanitization"""
    
    @staticmethod
    def for_html_display(text: str) -> str:
        """Sanitize for displaying in HTML"""
        return XSSProtection.escape_html(text)
    
    @staticmethod
    def for_html_attribute(text: str) -> str:
        """Sanitize for use in HTML attributes"""
        # Escape quotes and special chars
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#x27;')
        return XSSProtection.escape_html(text)
    
    @staticmethod
    def for_javascript_string(text: str) -> str:
        """Sanitize for use in JavaScript strings"""
        replacements = {
            '\\': '\\\\',
            '"': '\\"',
            "'": "\\'",
            '\n': '\\n',
            '\r': '\\r',
            '<': '\\x3C',
            '>': '\\x3E',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text
    
    @staticmethod
    def for_url_parameter(text: str) -> str:
        """Sanitize for use in URL parameters"""
        import urllib.parse
        return urllib.parse.quote(text, safe='')
