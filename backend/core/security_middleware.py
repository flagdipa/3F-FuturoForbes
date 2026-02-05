"""
Security middleware and utilities for API protection.
Includes rate limiting, CSRF protection, XSS prevention, and security headers.
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import secrets
import time
import bleach
import re
from typing import Dict, Any

# Rate Limiter Configuration
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    storage_uri="memory://"
)

# CSRF Protection
class CSRFProtection:
    """CSRF token generation and validation"""
    
    _tokens: Dict[str, Dict[str, Any]] = {}  # In-memory storage
    TOKEN_EXPIRY = 3600  # 1 hour
    
    @staticmethod
    def generate_token(session_id: str) -> str:
        """Generate CSRF token for session"""
        token = secrets.token_urlsafe(32)
        timestamp = time.time()
        
        CSRFProtection._tokens[session_id] = {
            'token': token,
            'created_at': timestamp
        }
        
        return token
    
    @staticmethod
    def validate_token(token: str, session_id: str) -> bool:
        """Validate CSRF token"""
        stored = CSRFProtection._tokens.get(session_id)
        
        if not stored:
            return False
        
        # Check expiry
        if time.time() - stored['created_at'] > CSRFProtection.TOKEN_EXPIRY:
            del CSRFProtection._tokens[session_id]
            return False
        
        return secrets.compare_digest(stored['token'], token)
    
    @staticmethod
    def cleanup_expired():
        """Remove expired tokens"""
        current_time = time.time()
        expired = [
            sid for sid, data in CSRFProtection._tokens.items()
            if current_time - data['created_at'] > CSRFProtection.TOKEN_EXPIRY
        ]
        for sid in expired:
            del CSRFProtection._tokens[sid]

csrf_protection = CSRFProtection()


# Input Sanitization
class InputSanitizer:
    """XSS and injection prevention"""
    
    ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li']
    ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """Sanitize HTML to prevent XSS"""
        if not text:
            return text
        
        return bleach.clean(
            text,
            tags=InputSanitizer.ALLOWED_TAGS,
            attributes=InputSanitizer.ALLOWED_ATTRIBUTES,
            strip=True
        )
    
    @staticmethod
    def sanitize_string(text: str) -> str:
        """Remove dangerous characters"""
        if not text:
            return text
        
        text = text.replace('\x00', '')
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        return text

input_sanitizer = InputSanitizer()


# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        if 'Server' in response.headers:
            del response.headers['Server']
        
        return response
