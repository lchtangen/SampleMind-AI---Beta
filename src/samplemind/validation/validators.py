"""
Input Validation Layer
Comprehensive validation for all inputs to prevent security vulnerabilities

This module provides:
- File upload validation (size, type, content verification)
- Audio format validation with magic number checking
- String sanitization and length limits
- Email and URL validation
- SQL injection and XSS prevention
- Pydantic integration for API schemas
"""

import re
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False
    magic = None

import bleach
from pathlib import Path
from typing import Optional, Dict, Any, List, Set
from pydantic import BaseModel, EmailStr, HttpUrl, Field, field_validator
from fastapi import UploadFile, HTTPException
import logging

logger = logging.getLogger(__name__)


# Constants
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".ogg", ".m4a"}
MAX_STRING_LENGTH = 10000
MAX_FILENAME_LENGTH = 255
MAX_EMAIL_LENGTH = 320
MAX_URL_LENGTH = 2048

# Magic number signatures for audio formats
AUDIO_MAGIC_NUMBERS = {
    "mp3": [b"ID3", b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"],
    "wav": [b"RIFF"],
    "flac": [b"fLaC"],
    "ogg": [b"OggS"],
    "m4a": [b"ftypM4A", b"ftypisom", b"ftypmp42"],
}


class ValidationError(Exception):
    """Custom validation error"""
    pass


class FileUploadValidator:
    """
    Validates file uploads for security and format compliance
    
    Features:
    - File size validation
    - Extension validation
    - Magic number verification
    - Content type validation
    - Malicious content detection
    """
    
    def __init__(self):
        if HAS_MAGIC:
            self.magic = magic.Magic(mime=True)
        else:
            self.magic = None
        self.allowed_extensions = ALLOWED_AUDIO_EXTENSIONS
        self.max_file_size = MAX_FILE_SIZE
    
    def validate_audio_file(self, file: UploadFile) -> Dict[str, Any]:
        """
        Comprehensive audio file validation
        
        Args:
            file: Uploaded file object
            
        Returns:
            Dict with validation results
            
        Raises:
            ValidationError: If validation fails
        """
        logger.info(f"Validating audio file: {file.filename}")
        
        # Validate filename
        if not file.filename:
            raise ValidationError("Filename is required")
        
        filename = self._sanitize_filename(file.filename)
        
        # Validate extension
        extension = Path(filename).suffix.lower()
        if extension not in self.allowed_extensions:
            raise ValidationError(
                f"Invalid file extension: {extension}. "
                f"Allowed: {', '.join(self.allowed_extensions)}"
            )
        
        # Read file content
        file_content = file.file.read()
        file.file.seek(0)  # Reset file pointer
        
        # Validate file size
        file_size = len(file_content)
        if file_size == 0:
            raise ValidationError("File is empty")
        
        if file_size > self.max_file_size:
            raise ValidationError(
                f"File size ({file_size} bytes) exceeds maximum "
                f"allowed size ({self.max_file_size} bytes)"
            )
        
        # Validate magic numbers
        self._validate_magic_numbers(file_content, extension)
        
        # Validate MIME type (if magic library is available)
        if self.magic is not None:
            mime_type = self.magic.from_buffer(file_content)
            self._validate_mime_type(mime_type, extension)
        else:
            mime_type = "application/octet-stream"
            logger.warning("python-magic not installed, skipping MIME type validation")
        
        # Check for malicious content
        self._check_malicious_content(file_content)
        
        logger.info(f"File validation successful: {filename}")
        
        return {
            "filename": filename,
            "extension": extension,
            "size": file_size,
            "mime_type": mime_type,
            "valid": True
        }
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent path traversal attacks"""
        # Remove path components
        filename = Path(filename).name
        
        # Remove dangerous characters
        filename = re.sub(r'[^\w\s\-\.]', '', filename)
        
        # Limit length
        if len(filename) > MAX_FILENAME_LENGTH:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:MAX_FILENAME_LENGTH - len(ext) - 1] + '.' + ext
        
        return filename
    
    def _validate_magic_numbers(self, content: bytes, extension: str) -> None:
        """Validate file magic numbers match the extension"""
        format_key = extension.lstrip('.')
        
        if format_key not in AUDIO_MAGIC_NUMBERS:
            raise ValidationError(f"Unsupported audio format: {extension}")
        
        magic_numbers = AUDIO_MAGIC_NUMBERS[format_key]
        
        # Check if content starts with any of the valid magic numbers
        for magic_num in magic_numbers:
            if content.startswith(magic_num):
                return
        
        # Special handling for WAV files (check for WAVE format)
        if format_key == "wav" and b"WAVE" in content[:16]:
            return
        
        raise ValidationError(
            f"File magic number does not match expected format for {extension}"
        )
    
    def _validate_mime_type(self, mime_type: str, extension: str) -> None:
        """Validate MIME type matches the file extension"""
        valid_mime_types = {
            ".mp3": ["audio/mpeg", "audio/mp3"],
            ".wav": ["audio/wav", "audio/x-wav", "audio/wave"],
            ".flac": ["audio/flac", "audio/x-flac"],
            ".ogg": ["audio/ogg", "application/ogg"],
            ".m4a": ["audio/mp4", "audio/x-m4a", "audio/m4a"],
        }
        
        expected_types = valid_mime_types.get(extension, [])
        
        if mime_type not in expected_types:
            logger.warning(
                f"MIME type mismatch: got {mime_type}, "
                f"expected one of {expected_types}"
            )
            # Don't raise error, just log warning (some systems report different MIME types)
    
    def _check_malicious_content(self, content: bytes) -> None:
        """Check for potentially malicious content in audio files"""
        # Check for embedded scripts or executables
        dangerous_patterns = [
            b"<script",
            b"<?php",
            b"#!/bin/",
            b"MZ\x90\x00",  # PE executable header
            b"\x7fELF",  # ELF executable header
        ]
        
        content_lower = content.lower()
        
        for pattern in dangerous_patterns:
            if pattern.lower() in content_lower:
                raise ValidationError("File contains potentially malicious content")


class StringValidator:
    """
    Validates and sanitizes string inputs
    
    Features:
    - Length validation
    - XSS prevention through sanitization
    - SQL injection prevention
    - HTML tag stripping
    """
    
    @staticmethod
    def sanitize_string(
        value: str,
        max_length: int = MAX_STRING_LENGTH,
        strip_html: bool = True,
        allow_unicode: bool = True
    ) -> str:
        """
        Sanitize string input
        
        Args:
            value: Input string
            max_length: Maximum allowed length
            strip_html: Whether to strip HTML tags
            allow_unicode: Whether to allow unicode characters
            
        Returns:
            Sanitized string
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(value, str):
            raise ValidationError("Input must be a string")
        
        # Check length
        if len(value) > max_length:
            raise ValidationError(
                f"String length ({len(value)}) exceeds maximum ({max_length})"
            )
        
        # Strip HTML tags if requested
        if strip_html:
            value = bleach.clean(value, tags=[], strip=True)
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Normalize whitespace
        value = ' '.join(value.split())
        
        return value
    
    @staticmethod
    def validate_sql_safe(value: str) -> str:
        """
        Validate string is safe from SQL injection
        
        Note: This is a defense-in-depth measure. Always use parameterized queries.
        
        Args:
            value: Input string
            
        Returns:
            Validated string
            
        Raises:
            ValidationError: If potentially malicious SQL detected
        """
        # Check for common SQL injection patterns
        sql_patterns = [
            r"(\bunion\b.*\bselect\b)",
            r"(\bdrop\b.*\btable\b)",
            r"(\bexec\b|\bexecute\b).*\(",
            r"(--|#|\/\*|\*\/)",  # SQL comments
            r"(\bor\b.*=.*\bor\b)",
            r"(\';|\";)",  # Quote escaping
        ]
        
        value_lower = value.lower()
        
        for pattern in sql_patterns:
            if re.search(pattern, value_lower, re.IGNORECASE):
                raise ValidationError("Input contains potentially malicious SQL patterns")
        
        return value
    
    @staticmethod
    def validate_xss_safe(value: str) -> str:
        """
        Validate and sanitize against XSS attacks
        
        Args:
            value: Input string
            
        Returns:
            Sanitized string
        """
        # Use bleach to clean the input
        # Allow no tags by default for maximum security
        clean_value = bleach.clean(
            value,
            tags=[],
            attributes={},
            strip=True
        )
        
        # Additional checks for obfuscated XSS
        xss_patterns = [
            r"javascript:",
            r"on\w+\s*=",  # Event handlers
            r"<\s*script",
            r"eval\s*\(",
        ]
        
        clean_lower = clean_value.lower()
        
        for pattern in xss_patterns:
            if re.search(pattern, clean_lower, re.IGNORECASE):
                raise ValidationError("Input contains potentially malicious XSS patterns")
        
        return clean_value


class EmailValidator:
    """Validates email addresses"""
    
    @staticmethod
    def validate_email(email: str) -> str:
        """
        Validate email format
        
        Args:
            email: Email address
            
        Returns:
            Validated email
            
        Raises:
            ValidationError: If email is invalid
        """
        if not email:
            raise ValidationError("Email is required")
        
        if len(email) > MAX_EMAIL_LENGTH:
            raise ValidationError(f"Email exceeds maximum length ({MAX_EMAIL_LENGTH})")
        
        # Basic email regex (RFC 5322 simplified)
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            raise ValidationError("Invalid email format")
        
        # Additional checks
        if email.count('@') != 1:
            raise ValidationError("Invalid email format: multiple @ symbols")
        
        local, domain = email.split('@')
        
        if not local or not domain:
            raise ValidationError("Invalid email format: missing local or domain part")
        
        if domain.startswith('.') or domain.endswith('.'):
            raise ValidationError("Invalid email format: domain cannot start or end with .")
        
        return email.lower()


class URLValidator:
    """Validates URLs"""
    
    @staticmethod
    def validate_url(url: str, require_https: bool = False) -> str:
        """
        Validate URL format and security
        
        Args:
            url: URL string
            require_https: Whether to require HTTPS
            
        Returns:
            Validated URL
            
        Raises:
            ValidationError: If URL is invalid
        """
        if not url:
            raise ValidationError("URL is required")
        
        if len(url) > MAX_URL_LENGTH:
            raise ValidationError(f"URL exceeds maximum length ({MAX_URL_LENGTH})")
        
        # Basic URL pattern
        url_pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
        
        if not re.match(url_pattern, url):
            raise ValidationError("Invalid URL format")
        
        # Check for HTTPS if required
        if require_https and not url.startswith('https://'):
            raise ValidationError("URL must use HTTPS")
        
        # Check for dangerous protocols
        dangerous_protocols = ['javascript:', 'data:', 'file:', 'vbscript:']
        url_lower = url.lower()
        
        for protocol in dangerous_protocols:
            if url_lower.startswith(protocol):
                raise ValidationError(f"Dangerous URL protocol: {protocol}")
        
        return url


# Pydantic Models for API Validation

class AudioAnalysisRequest(BaseModel):
    """Request model for audio analysis"""
    file_id: str = Field(..., min_length=1, max_length=100)
    analysis_type: str = Field(..., min_length=1, max_length=50)
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @field_validator('file_id')
    @classmethod
    def validate_file_id(cls, v):
        """Validate file ID format"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("File ID contains invalid characters")
        return v
    
    @field_validator('analysis_type')
    @classmethod
    def validate_analysis_type(cls, v):
        """Validate analysis type"""
        allowed_types = {'tempo', 'key', 'genre', 'mood', 'full'}
        if v not in allowed_types:
            raise ValueError(f"Invalid analysis type. Allowed: {allowed_types}")
        return v


class UserRegistrationRequest(BaseModel):
    """Request model for user registration"""
    email: EmailStr = Field(..., max_length=MAX_EMAIL_LENGTH)
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """Validate username format"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Username can only contain letters, numbers, hyphens, and underscores")
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        
        # Check for at least one uppercase, one lowercase, and one digit
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r'\d', v):
            raise ValueError("Password must contain at least one digit")
        
        return v


class APIKeyCreateRequest(BaseModel):
    """Request model for API key creation"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default="", max_length=500)
    scopes: List[str] = Field(default_factory=list)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate API key name"""
        # Sanitize the name
        v = StringValidator.sanitize_string(v, max_length=100)
        if not v:
            raise ValueError("Name cannot be empty after sanitization")
        return v
    
    @field_validator('scopes')
    @classmethod
    def validate_scopes(cls, v):
        """Validate API key scopes"""
        allowed_scopes = {'read', 'write', 'delete', 'admin'}
        for scope in v:
            if scope not in allowed_scopes:
                raise ValueError(f"Invalid scope: {scope}")
        return v


class BatchProcessRequest(BaseModel):
    """Request model for batch processing"""
    file_ids: List[str] = Field(..., min_length=1, max_length=100)
    analysis_type: str = Field(..., min_length=1, max_length=50)
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @field_validator('file_ids')
    @classmethod
    def validate_file_ids(cls, v):
        """Validate list of file IDs"""
        for file_id in v:
            if not re.match(r'^[a-zA-Z0-9_-]+$', file_id):
                raise ValueError(f"File ID contains invalid characters: {file_id}")
        return v


# Convenience Functions

def validate_audio_upload(file: UploadFile) -> Dict[str, Any]:
    """
    Convenience function for audio file validation
    
    Args:
        file: Uploaded file
        
    Returns:
        Validation result dictionary
    """
    validator = FileUploadValidator()
    return validator.validate_audio_file(file)


def sanitize_user_input(text: str, max_length: int = MAX_STRING_LENGTH) -> str:
    """
    Convenience function for sanitizing user input
    
    Args:
        text: Input text
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    return StringValidator.sanitize_string(text, max_length=max_length)


def validate_email_address(email: str) -> str:
    """
    Convenience function for email validation
    
    Args:
        email: Email address
        
    Returns:
        Validated email
    """
    return EmailValidator.validate_email(email)


def validate_url_string(url: str, require_https: bool = False) -> str:
    """
    Convenience function for URL validation
    
    Args:
        url: URL string
        require_https: Whether to require HTTPS
        
    Returns:
        Validated URL
    """
    return URLValidator.validate_url(url, require_https=require_https)