"""
Input Validation and SQL Injection Prevention
"""

import re
from typing import Optional, Any, List
from pydantic import BaseModel, validator, Field
from fastapi import HTTPException, status


class ValidationError(HTTPException):
    """Custom validation error exception"""
    def __init__(self, field: str, message: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error for {field}: {message}"
        )


class InputSanitizer:
    """Utility class for input sanitization"""
    
    # Dangerous SQL patterns to detect
    SQL_INJECTION_PATTERNS = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bSELECT\b.*\bFROM\b)",
        r"(\bINSERT\b.*\bINTO\b)",
        r"(\bDELETE\b.*\bFROM\b)",
        r"(\bDROP\b.*\b(TABLE|DATABASE)\b)",
        r"(\bEXEC\b|\bEXECUTE\b)",
        r"(--|\#|\/\*)",  # SQL comments
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)",
        r"(;.*\b(SELECT|INSERT|UPDATE|DELETE)\b)",
    ]
    
    # Command injection patterns
    COMMAND_INJECTION_PATTERNS = [
        r"(;|\||&|`|\$\(|\$\{)",  # Shell metacharacters
        r"(\.\./|\.\.\\)",  # Path traversal
        r"(<script|javascript:|onerror=|onload=)",  # XSS attempts
    ]
    
    @staticmethod
    def detect_sql_injection(value: str) -> bool:
        """
        Detect potential SQL injection attempts
        
        Returns:
            True if suspicious pattern detected
        """
        if not isinstance(value, str):
            return False
        
        value_upper = value.upper()
        
        for pattern in InputSanitizer.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_upper, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def detect_command_injection(value: str) -> bool:
        """
        Detect potential command injection attempts
        
        Returns:
            True if suspicious pattern detected
        """
        if not isinstance(value, str):
            return False
        
        for pattern in InputSanitizer.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 500) -> str:
        """
        Sanitize string input
        
        Args:
            value: Input string
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
            
        Raises:
            ValidationError if suspicious pattern detected
        """
        if not value:
            return value
        
        # Check for SQL injection
        if InputSanitizer.detect_sql_injection(value):
            raise ValidationError("input", "Potential SQL injection detected")
        
        # Check for command injection
        if InputSanitizer.detect_command_injection(value):
            raise ValidationError("input", "Potential command injection detected")
        
        # Trim to max length
        if len(value) > max_length:
            value = value[:max_length]
        
        # Strip dangerous characters for text fields
        value = value.strip()
        
        return value
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal
        
        Args:
            filename: Original filename
            
        Returns:
            Safe filename
        """
        # Remove path components
        filename = filename.split("/")[-1].split("\\")[-1]
        
        # Remove dangerous characters
        filename = re.sub(r'[<>:"|?*]', '', filename)
        
        # Prevent hidden files
        if filename.startswith('.'):
            filename = filename[1:]
        
        # Ensure we have a filename
        if not filename:
            filename = "unnamed_file"
        
        return filename
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """
        Validate username format
        - 3-30 characters
        - Alphanumeric, underscore, hyphen only
        """
        if not username or len(username) < 3 or len(username) > 30:
            return False
        
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, username))


# Validated input models
class SafeSearchQuery(BaseModel):
    """Validated search query"""
    query: str = Field(..., min_length=1, max_length=500)
    
    @validator('query')
    def sanitize_query(cls, v):
        """Sanitize search query"""
        return InputSanitizer.sanitize_string(v, max_length=500)


class SafeFilename(BaseModel):
    """Validated filename"""
    filename: str = Field(..., min_length=1, max_length=255)
    
    @validator('filename')
    def sanitize_filename(cls, v):
        """Sanitize filename"""
        return InputSanitizer.sanitize_filename(v)


class SafeUsername(BaseModel):
    """Validated username"""
    username: str = Field(..., min_length=3, max_length=30)
    
    @validator('username')
    def validate_username(cls, v):
        """Validate username format"""
        if not InputSanitizer.validate_username(v):
            raise ValueError("Invalid username format. Use 3-30 alphanumeric characters, underscore, or hyphen.")
        return v


class SafeMetadata(BaseModel):
    """Validated metadata dictionary"""
    key: str = Field(..., min_length=1, max_length=100)
    value: str = Field(..., max_length=1000)
    
    @validator('key', 'value')
    def sanitize_field(cls, v):
        """Sanitize metadata field"""
        return InputSanitizer.sanitize_string(v, max_length=1000)


# Parameterized query helpers (for SQL/NoSQL)
class QueryBuilder:
    """Safe query builder using parameterization"""
    
    @staticmethod
    def build_where_clause(filters: dict) -> tuple[str, list]:
        """
        Build safe WHERE clause with parameters
        
        Returns:
            tuple: (where_clause, parameters)
        """
        conditions = []
        parameters = []
        
        for key, value in filters.items():
            # Validate key is safe column name
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', key):
                raise ValidationError("filter", f"Invalid filter key: {key}")
            
            conditions.append(f"{key} = ?")
            parameters.append(value)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        return where_clause, parameters
    
    @staticmethod
    def build_safe_search(search_term: str, fields: List[str]) -> tuple[str, list]:
        """
        Build safe search query
        
        Returns:
            tuple: (search_clause, parameters)
        """
        # Sanitize search term
        safe_term = InputSanitizer.sanitize_string(search_term)
        
        # Validate field names
        safe_fields = []
        for field in fields:
            if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', field):
                safe_fields.append(field)
        
        if not safe_fields:
            return "1=1", []
        
        # Build OR conditions for each field
        conditions = [f"{field} LIKE ?" for field in safe_fields]
        search_clause = "(" + " OR ".join(conditions) + ")"
        
        # Parameters with wildcards
        parameters = [f"%{safe_term}%" for _ in safe_fields]
        
        return search_clause, parameters


# Example usage
"""
# Validate and sanitize user input
sanitizer = InputSanitizer()

# Check for SQL injection
user_input = request.query_params.get("search")
if sanitizer.detect_sql_injection(user_input):
    raise HTTPException(400, "Invalid input detected")

# Sanitize string
safe_input = sanitizer.sanitize_string(user_input)

# Use parameterized queries (MongoDB example)
from motor.motor_asyncio import AsyncIOMotorClient

async def safe_search(search_term: str):
    # This is safe - MongoDB parameterizes automatically
    result = await db.audio_files.find({
        "title": {"$regex": sanitizer.sanitize_string(search_term)}
    }).to_list(100)
    return result

# For SQL (if using PostgreSQL via SQLAlchemy)
from sqlalchemy import text

async def safe_sql_query(user_id: str):
    # Parameterized query - safe from injection
    query = text("SELECT * FROM users WHERE user_id = :user_id")
    result = await db.execute(query, {"user_id": user_id})
    return result
"""
