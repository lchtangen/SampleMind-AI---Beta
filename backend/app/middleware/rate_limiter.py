"""
Rate limiting middleware for API endpoints
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple
import asyncio


class RateLimiter(BaseHTTPMiddleware):
    """
    Rate limiting middleware with per-IP and per-user limits
    
    Features:
    - Per-minute and per-hour rate limits
    - IP-based limiting for unauthenticated requests
    - User-based limiting for authenticated requests
    - Configurable limits per endpoint
    - Rate limit headers in responses
    """
    
    def __init__(self, app, per_minute: int = 60, per_hour: int = 1000, start_cleanup: bool = True):
        super().__init__(app)
        self.per_minute = per_minute
        self.per_hour = per_hour
        
        # Storage: {identifier: [(timestamp, count)]}
        self.requests: Dict[str, list] = defaultdict(list)
        
        # Cleanup old entries every 5 minutes (skip in tests)
        if start_cleanup and app is not None:
            try:
                asyncio.create_task(self.cleanup_loop())
            except RuntimeError:
                # No event loop running (e.g., in tests)
                pass
    
    def get_identifier(self, request: Request) -> str:
        """Get unique identifier for rate limiting"""
        # Try to get user ID from token
        user_id = request.state.get('user_id')
        if user_id:
            return f"user:{user_id}"
        
        # Fall back to IP address
        forwarded = request.headers.get('X-Forwarded-For')
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"
        
        client_host = request.client.host if request.client else 'unknown'
        return f"ip:{client_host}"
    
    def check_rate_limit(self, identifier: str) -> Tuple[bool, Dict]:
        """
        Check if request is within rate limits
        
        Returns:
            (allowed, headers) tuple
        """
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        # Get request history
        requests = self.requests[identifier]
        
        # Count requests in last minute and hour
        minute_count = sum(1 for ts, _ in requests if ts > minute_ago)
        hour_count = sum(1 for ts, _ in requests if ts > hour_ago)
        
        # Check limits
        minute_remaining = max(0, self.per_minute - minute_count)
        hour_remaining = max(0, self.per_hour - hour_count)
        
        allowed = minute_count < self.per_minute and hour_count < self.per_hour
        
        # Prepare headers
        headers = {
            'X-RateLimit-Limit-Minute': str(self.per_minute),
            'X-RateLimit-Limit-Hour': str(self.per_hour),
            'X-RateLimit-Remaining-Minute': str(minute_remaining),
            'X-RateLimit-Remaining-Hour': str(hour_remaining),
            'X-RateLimit-Reset': str(int((now + timedelta(minutes=1)).timestamp())),
        }
        
        return allowed, headers
    
    def record_request(self, identifier: str):
        """Record a request for rate limiting"""
        now = datetime.now()
        self.requests[identifier].append((now, 1))
        
        # Keep only last hour of data
        hour_ago = now - timedelta(hours=1)
        self.requests[identifier] = [
            (ts, count) for ts, count in self.requests[identifier]
            if ts > hour_ago
        ]
    
    async def cleanup_loop(self):
        """Periodically clean up old rate limit data"""
        while True:
            await asyncio.sleep(300)  # 5 minutes
            
            now = datetime.now()
            hour_ago = now - timedelta(hours=1)
            
            # Clean up old entries
            for identifier in list(self.requests.keys()):
                self.requests[identifier] = [
                    (ts, count) for ts, count in self.requests[identifier]
                    if ts > hour_ago
                ]
                
                # Remove empty entries
                if not self.requests[identifier]:
                    del self.requests[identifier]
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        # Skip rate limiting for health checks
        if request.url.path in ['/health', '/']:
            return await call_next(request)
        
        # Get identifier
        identifier = self.get_identifier(request)
        
        # Check rate limit
        allowed, headers = self.check_rate_limit(identifier)
        
        if not allowed:
            # Rate limit exceeded
            return JSONResponse(
                status_code=429,
                content={
                    'detail': 'Rate limit exceeded. Please try again later.',
                    'retry_after': 60
                },
                headers=headers
            )
        
        # Record request
        self.record_request(identifier)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        for key, value in headers.items():
            response.headers[key] = value
        
        return response


class EndpointRateLimiter:
    """
    Decorator for per-endpoint rate limiting
    
    Usage:
        @app.get("/heavy-operation")
        @rate_limit(per_minute=10)
        async def heavy_operation():
            ...
    """
    
    def __init__(self, per_minute: int = 60):
        self.per_minute = per_minute
        self.requests = defaultdict(list)
    
    async def __call__(self, request: Request):
        identifier = self._get_identifier(request)
        
        if not await self._check_limit(identifier):
            raise HTTPException(
                status_code=429,
                detail=f'Rate limit exceeded: {self.per_minute} requests per minute'
            )
    
    def _get_identifier(self, request: Request) -> str:
        """Get unique identifier"""
        user_id = getattr(request.state, 'user_id', None)
        if user_id:
            return f"user:{user_id}"
        
        client_host = request.client.host if request.client else 'unknown'
        return f"ip:{client_host}"
    
    async def _check_limit(self, identifier: str) -> bool:
        """Check if request is within limit"""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old requests
        self.requests[identifier] = [
            ts for ts in self.requests[identifier]
            if ts > minute_ago
        ]
        
        # Check limit
        if len(self.requests[identifier]) >= self.per_minute:
            return False
        
        # Record request
        self.requests[identifier].append(now)
        return True


def rate_limit(per_minute: int = 60):
    """
    Decorator factory for rate limiting
    
    Usage:
        @app.get("/api/data")
        @rate_limit(per_minute=30)
        async def get_data():
            return {"data": "..."}
    """
    limiter = EndpointRateLimiter(per_minute=per_minute)
    
    async def dependency(request: Request):
        await limiter(request)
    
    return dependency
