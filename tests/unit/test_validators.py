"""
Unit tests for input validation layer
Tests all validators for security and functionality
"""

import pytest
import io
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from pydantic import ValidationError as PydanticValidationError

from samplemind.validation.validators import (
    ValidationError,
    FileUploadValidator,
    StringValidator,
    EmailValidator,
    URLValidator,
    AudioAnalysisRequest,
    UserRegistrationRequest,
    APIKeyCreateRequest,
    BatchProcessRequest,
    validate_audio_upload,
    sanitize_user_input,
    validate_email_address,
    validate_url_string,
    MAX_FILE_SIZE,
    ALLOWED_AUDIO_EXTENSIONS,
)


class TestFileUploadValidator:
    """Test file upload validation"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.validator = FileUploadValidator()
    
    def create_mock_file(self, filename, content, content_type="audio/mpeg"):
        """Helper to create mock UploadFile"""
        mock_file = Mock()
        mock_file.filename = filename
        mock_file.content_type = content_type
        mock_file.file = io.BytesIO(content)
        return mock_file
    
    def test_valid_mp3_file(self):
        """Test validation of valid MP3 file"""
        content = b"ID3\x03\x00\x00\x00" + b"\x00" * 100  # MP3 with ID3 header
        mock_file = self.create_mock_file("test.mp3", content)
        
        result = self.validator.validate_audio_file(mock_file)
        
        assert result["valid"] is True
        assert result["filename"] == "test.mp3"
        assert result["extension"] == ".mp3"
        assert result["size"] == len(content)
    
    def test_valid_wav_file(self):
        """Test validation of valid WAV file"""
        content = b"RIFF\x00\x00\x00\x00WAVEfmt " + b"\x00" * 100
        mock_file = self.create_mock_file("test.wav", content, "audio/wav")
        
        result = self.validator.validate_audio_file(mock_file)
        
        assert result["valid"] is True
        assert result["extension"] == ".wav"
    
    def test_valid_flac_file(self):
        """Test validation of valid FLAC file"""
        content = b"fLaC" + b"\x00" * 100
        mock_file = self.create_mock_file("test.flac", content, "audio/flac")
        
        result = self.validator.validate_audio_file(mock_file)
        
        assert result["valid"] is True
        assert result["extension"] == ".flac"
    
    def test_valid_ogg_file(self):
        """Test validation of valid OGG file"""
        content = b"OggS" + b"\x00" * 100
        mock_file = self.create_mock_file("test.ogg", content, "audio/ogg")
        
        result = self.validator.validate_audio_file(mock_file)
        
        assert result["valid"] is True
        assert result["extension"] == ".ogg"
    
    def test_valid_m4a_file(self):
        """Test validation of valid M4A file"""
        content = b"\x00\x00\x00\x20ftypM4A " + b"\x00" * 100
        mock_file = self.create_mock_file("test.m4a", content, "audio/mp4")
        
        result = self.validator.validate_audio_file(mock_file)
        
        assert result["valid"] is True
        assert result["extension"] == ".m4a"
    
    def test_invalid_extension(self):
        """Test rejection of invalid file extension"""
        content = b"\x00" * 100
        mock_file = self.create_mock_file("test.exe", content)
        
        with pytest.raises(ValidationError, match="Invalid file extension"):
            self.validator.validate_audio_file(mock_file)
    
    def test_empty_file(self):
        """Test rejection of empty file"""
        mock_file = self.create_mock_file("test.mp3", b"")
        
        with pytest.raises(ValidationError, match="File is empty"):
            self.validator.validate_audio_file(mock_file)
    
    def test_file_too_large(self):
        """Test rejection of oversized file"""
        # Create file larger than MAX_FILE_SIZE
        content = b"\x00" * (MAX_FILE_SIZE + 1)
        mock_file = self.create_mock_file("test.mp3", content)
        
        with pytest.raises(ValidationError, match="exceeds maximum"):
            self.validator.validate_audio_file(mock_file)
    
    def test_magic_number_mismatch(self):
        """Test rejection when magic number doesn't match extension"""
        # MP3 extension but wrong magic number
        content = b"WRONG" + b"\x00" * 100
        mock_file = self.create_mock_file("test.mp3", content)
        
        with pytest.raises(ValidationError, match="magic number does not match"):
            self.validator.validate_audio_file(mock_file)
    
    def test_malicious_content_script(self):
        """Test detection of embedded script"""
        content = b"ID3" + b"<script>alert('xss')</script>" + b"\x00" * 100
        mock_file = self.create_mock_file("test.mp3", content)
        
        with pytest.raises(ValidationError, match="malicious content"):
            self.validator.validate_audio_file(mock_file)
    
    def test_malicious_content_php(self):
        """Test detection of embedded PHP"""
        content = b"ID3" + b"<?php system('ls'); ?>" + b"\x00" * 100
        mock_file = self.create_mock_file("test.mp3", content)
        
        with pytest.raises(ValidationError, match="malicious content"):
            self.validator.validate_audio_file(mock_file)
    
    def test_malicious_content_executable(self):
        """Test detection of embedded executable"""
        content = b"ID3" + b"MZ\x90\x00" + b"\x00" * 100  # PE header
        mock_file = self.create_mock_file("test.mp3", content)
        
        with pytest.raises(ValidationError, match="malicious content"):
            self.validator.validate_audio_file(mock_file)
    
    def test_filename_sanitization(self):
        """Test filename sanitization"""
        # Filename with path traversal attempt
        content = b"ID3\x03\x00\x00\x00" + b"\x00" * 100
        mock_file = self.create_mock_file("../../etc/passwd.mp3", content)
        
        result = self.validator.validate_audio_file(mock_file)
        
        # Should strip path components
        assert ".." not in result["filename"]
        assert "/" not in result["filename"]
        assert result["filename"] == "etcpasswd.mp3"
    
    def test_filename_dangerous_chars(self):
        """Test removal of dangerous characters from filename"""
        content = b"ID3\x03\x00\x00\x00" + b"\x00" * 100
        mock_file = self.create_mock_file("test<>|:.mp3", content)
        
        result = self.validator.validate_audio_file(mock_file)
        
        # Should remove dangerous characters
        assert "<" not in result["filename"]
        assert ">" not in result["filename"]
        assert "|" not in result["filename"]
    
    def test_filename_length_limit(self):
        """Test filename length limiting"""
        long_name = "a" * 300 + ".mp3"
        content = b"ID3\x03\x00\x00\x00" + b"\x00" * 100
        mock_file = self.create_mock_file(long_name, content)
        
        result = self.validator.validate_audio_file(mock_file)
        
        # Should be truncated
        assert len(result["filename"]) <= 255


class TestStringValidator:
    """Test string validation and sanitization"""
    
    def test_sanitize_basic_string(self):
        """Test basic string sanitization"""
        result = StringValidator.sanitize_string("Hello World")
        assert result == "Hello World"
    
    def test_sanitize_removes_html(self):
        """Test HTML tag removal"""
        result = StringValidator.sanitize_string("<script>alert('xss')</script>Hello")
        assert "<script>" not in result
        assert "</script>" not in result
        assert "Hello" in result
    
    def test_sanitize_removes_null_bytes(self):
        """Test null byte removal"""
        result = StringValidator.sanitize_string("Hello\x00World")
        assert "\x00" not in result
        assert result == "Hello World"
    
    def test_sanitize_normalizes_whitespace(self):
        """Test whitespace normalization"""
        result = StringValidator.sanitize_string("Hello    \n\n   World")
        assert result == "Hello World"
    
    def test_sanitize_length_validation(self):
        """Test string length validation"""
        with pytest.raises(ValidationError, match="exceeds maximum"):
            StringValidator.sanitize_string("a" * 10001, max_length=10000)
    
    def test_sanitize_non_string_input(self):
        """Test rejection of non-string input"""
        with pytest.raises(ValidationError, match="must be a string"):
            StringValidator.sanitize_string(12345)
    
    def test_sql_injection_union_select(self):
        """Test SQL injection detection - UNION SELECT"""
        with pytest.raises(ValidationError, match="SQL patterns"):
            StringValidator.validate_sql_safe("1 UNION SELECT * FROM users")
    
    def test_sql_injection_drop_table(self):
        """Test SQL injection detection - DROP TABLE"""
        with pytest.raises(ValidationError, match="SQL patterns"):
            StringValidator.validate_sql_safe("'; DROP TABLE users; --")
    
    def test_sql_injection_comments(self):
        """Test SQL injection detection - SQL comments"""
        with pytest.raises(ValidationError, match="SQL patterns"):
            StringValidator.validate_sql_safe("test' -- comment")
    
    def test_sql_injection_or_equals(self):
        """Test SQL injection detection - OR = OR"""
        with pytest.raises(ValidationError, match="SQL patterns"):
            StringValidator.validate_sql_safe("1' OR '1'='1")
    
    def test_sql_safe_valid_string(self):
        """Test valid string passes SQL safety check"""
        result = StringValidator.validate_sql_safe("Hello World 123")
        assert result == "Hello World 123"
    
    def test_xss_prevention_script_tag(self):
        """Test XSS prevention - script tag"""
        result = StringValidator.validate_xss_safe("<script>alert('xss')</script>")
        assert "<script>" not in result.lower()
    
    def test_xss_prevention_javascript_protocol(self):
        """Test XSS prevention - javascript: protocol"""
        with pytest.raises(ValidationError, match="XSS patterns"):
            StringValidator.validate_xss_safe("javascript:alert('xss')")
    
    def test_xss_prevention_event_handler(self):
        """Test XSS prevention - event handlers"""
        with pytest.raises(ValidationError, match="XSS patterns"):
            StringValidator.validate_xss_safe("<img onerror='alert(1)'>")
    
    def test_xss_prevention_eval(self):
        """Test XSS prevention - eval function"""
        with pytest.raises(ValidationError, match="XSS patterns"):
            StringValidator.validate_xss_safe("eval(malicious_code)")
    
    def test_xss_safe_valid_string(self):
        """Test valid string passes XSS safety check"""
        result = StringValidator.validate_xss_safe("Hello World <b>test</b>")
        # Tags should be stripped but text preserved
        assert "Hello World" in result


class TestEmailValidator:
    """Test email validation"""
    
    def test_valid_email(self):
        """Test validation of valid email"""
        result = EmailValidator.validate_email("user@example.com")
        assert result == "user@example.com"
    
    def test_valid_email_with_subdomain(self):
        """Test validation of email with subdomain"""
        result = EmailValidator.validate_email("user@mail.example.com")
        assert result == "user@mail.example.com"
    
    def test_valid_email_with_plus(self):
        """Test validation of email with + sign"""
        result = EmailValidator.validate_email("user+tag@example.com")
        assert result == "user+tag@example.com"
    
    def test_email_case_insensitive(self):
        """Test email is converted to lowercase"""
        result = EmailValidator.validate_email("User@Example.COM")
        assert result == "user@example.com"
    
    def test_invalid_email_no_at(self):
        """Test rejection of email without @ symbol"""
        with pytest.raises(ValidationError, match="Invalid email format"):
            EmailValidator.validate_email("userexample.com")
    
    def test_invalid_email_multiple_at(self):
        """Test rejection of email with multiple @ symbols"""
        with pytest.raises(ValidationError, match="multiple @ symbols"):
            EmailValidator.validate_email("user@@example.com")
    
    def test_invalid_email_no_domain(self):
        """Test rejection of email without domain"""
        with pytest.raises(ValidationError, match="Invalid email format"):
            EmailValidator.validate_email("user@")
    
    def test_invalid_email_no_local(self):
        """Test rejection of email without local part"""
        with pytest.raises(ValidationError, match="Invalid email format"):
            EmailValidator.validate_email("@example.com")
    
    def test_invalid_email_domain_starts_with_dot(self):
        """Test rejection of domain starting with dot"""
        with pytest.raises(ValidationError, match="cannot start or end"):
            EmailValidator.validate_email("user@.example.com")
    
    def test_invalid_email_domain_ends_with_dot(self):
        """Test rejection of domain ending with dot"""
        with pytest.raises(ValidationError, match="cannot start or end"):
            EmailValidator.validate_email("user@example.com.")
    
    def test_email_too_long(self):
        """Test rejection of overly long email"""
        long_email = "a" * 300 + "@example.com"
        with pytest.raises(ValidationError, match="exceeds maximum length"):
            EmailValidator.validate_email(long_email)
    
    def test_empty_email(self):
        """Test rejection of empty email"""
        with pytest.raises(ValidationError, match="Email is required"):
            EmailValidator.validate_email("")


class TestURLValidator:
    """Test URL validation"""
    
    def test_valid_http_url(self):
        """Test validation of valid HTTP URL"""
        result = URLValidator.validate_url("http://example.com")
        assert result == "http://example.com"
    
    def test_valid_https_url(self):
        """Test validation of valid HTTPS URL"""
        result = URLValidator.validate_url("https://example.com")
        assert result == "https://example.com"
    
    def test_valid_url_with_path(self):
        """Test validation of URL with path"""
        result = URLValidator.validate_url("https://example.com/path/to/resource")
        assert result == "https://example.com/path/to/resource"
    
    def test_valid_url_with_subdomain(self):
        """Test validation of URL with subdomain"""
        result = URLValidator.validate_url("https://api.example.com")
        assert result == "https://api.example.com"
    
    def test_require_https(self):
        """Test HTTPS requirement"""
        with pytest.raises(ValidationError, match="must use HTTPS"):
            URLValidator.validate_url("http://example.com", require_https=True)
    
    def test_require_https_passes(self):
        """Test HTTPS requirement passes for HTTPS URL"""
        result = URLValidator.validate_url("https://example.com", require_https=True)
        assert result == "https://example.com"
    
    def test_invalid_url_no_protocol(self):
        """Test rejection of URL without protocol"""
        with pytest.raises(ValidationError, match="Invalid URL format"):
            URLValidator.validate_url("example.com")
    
    def test_dangerous_protocol_javascript(self):
        """Test rejection of javascript: protocol"""
        with pytest.raises(ValidationError, match="Dangerous URL protocol"):
            URLValidator.validate_url("javascript:alert('xss')")
    
    def test_dangerous_protocol_data(self):
        """Test rejection of data: protocol"""
        with pytest.raises(ValidationError, match="Dangerous URL protocol"):
            URLValidator.validate_url("data:text/html,<script>alert(1)</script>")
    
    def test_dangerous_protocol_file(self):
        """Test rejection of file: protocol"""
        with pytest.raises(ValidationError, match="Dangerous URL protocol"):
            URLValidator.validate_url("file:///etc/passwd")
    
    def test_url_too_long(self):
        """Test rejection of overly long URL"""
        long_url = "https://example.com/" + "a" * 3000
        with pytest.raises(ValidationError, match="exceeds maximum length"):
            URLValidator.validate_url(long_url)
    
    def test_empty_url(self):
        """Test rejection of empty URL"""
        with pytest.raises(ValidationError, match="URL is required"):
            URLValidator.validate_url("")


class TestPydanticModels:
    """Test Pydantic model validation"""
    
    def test_audio_analysis_request_valid(self):
        """Test valid audio analysis request"""
        request = AudioAnalysisRequest(
            file_id="test123",
            analysis_type="tempo",
            options={"detailed": True}
        )
        assert request.file_id == "test123"
        assert request.analysis_type == "tempo"
    
    def test_audio_analysis_request_invalid_file_id(self):
        """Test rejection of invalid file ID characters"""
        with pytest.raises(PydanticValidationError):
            AudioAnalysisRequest(
                file_id="test<>123",
                analysis_type="tempo"
            )
    
    def test_audio_analysis_request_invalid_type(self):
        """Test rejection of invalid analysis type"""
        with pytest.raises(PydanticValidationError):
            AudioAnalysisRequest(
                file_id="test123",
                analysis_type="invalid_type"
            )
    
    def test_user_registration_valid(self):
        """Test valid user registration"""
        user = UserRegistrationRequest(
            email="user@example.com",
            username="testuser",
            password="Password123"
        )
        assert user.email == "user@example.com"
        assert user.username == "testuser"
    
    def test_user_registration_invalid_username(self):
        """Test rejection of invalid username characters"""
        with pytest.raises(PydanticValidationError):
            UserRegistrationRequest(
                email="user@example.com",
                username="test<>user",
                password="Password123"
            )
    
    def test_user_registration_weak_password(self):
        """Test rejection of weak password"""
        with pytest.raises(PydanticValidationError):
            UserRegistrationRequest(
                email="user@example.com",
                username="testuser",
                password="weak"
            )
    
    def test_user_registration_no_uppercase(self):
        """Test rejection of password without uppercase"""
        with pytest.raises(PydanticValidationError):
            UserRegistrationRequest(
                email="user@example.com",
                username="testuser",
                password="password123"
            )
    
    def test_user_registration_no_lowercase(self):
        """Test rejection of password without lowercase"""
        with pytest.raises(PydanticValidationError):
            UserRegistrationRequest(
                email="user@example.com",
                username="testuser",
                password="PASSWORD123"
            )
    
    def test_user_registration_no_digit(self):
        """Test rejection of password without digit"""
        with pytest.raises(PydanticValidationError):
            UserRegistrationRequest(
                email="user@example.com",
                username="testuser",
                password="Password"
            )
    
    def test_api_key_create_valid(self):
        """Test valid API key creation request"""
        request = APIKeyCreateRequest(
            name="My API Key",
            description="For testing",
            scopes=["read", "write"]
        )
        assert request.name == "My API Key"
        assert "read" in request.scopes
    
    def test_api_key_create_invalid_scope(self):
        """Test rejection of invalid scope"""
        with pytest.raises(PydanticValidationError):
            APIKeyCreateRequest(
                name="My API Key",
                scopes=["read", "invalid_scope"]
            )
    
    def test_batch_process_valid(self):
        """Test valid batch process request"""
        request = BatchProcessRequest(
            file_ids=["file1", "file2", "file3"],
            analysis_type="tempo"
        )
        assert len(request.file_ids) == 3
    
    def test_batch_process_invalid_file_id(self):
        """Test rejection of invalid file ID in batch"""
        with pytest.raises(PydanticValidationError):
            BatchProcessRequest(
                file_ids=["file1", "file<>2"],
                analysis_type="tempo"
            )


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    def test_sanitize_user_input(self):
        """Test sanitize_user_input convenience function"""
        result = sanitize_user_input("<script>alert('xss')</script>Hello")
        assert "<script>" not in result
        assert "Hello" in result
    
    def test_validate_email_address(self):
        """Test validate_email_address convenience function"""
        result = validate_email_address("User@Example.COM")
        assert result == "user@example.com"
    
    def test_validate_url_string(self):
        """Test validate_url_string convenience function"""
        result = validate_url_string("https://example.com")
        assert result == "https://example.com"
    
    def test_validate_url_string_https_required(self):
        """Test validate_url_string with HTTPS requirement"""
        with pytest.raises(ValidationError):
            validate_url_string("http://example.com", require_https=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])