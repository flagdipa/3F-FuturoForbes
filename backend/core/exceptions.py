"""
Standardized exception classes for consistent error handling across the API.
"""
from fastapi import HTTPException
from typing import Optional, Dict, Any
from datetime import datetime


class APIException(HTTPException):
    """Base exception for API errors with structured response"""
    
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()
        
        super().__init__(
            status_code=status_code,
            detail={
                "error_code": error_code,
                "message": message,
                "details": self.details,
                "timestamp": self.timestamp
            }
        )


# 400 Class Errors - Client Errors
class ValidationError(APIException):
    """400 - Invalid request data"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(400, "VALIDATION_ERROR", message, details)


class BusinessRuleError(APIException):
    """400 - Business rule violation"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(400, "BUSINESS_RULE_ERROR", message, details)


# 401 Class Errors - Authentication
class AuthenticationError(APIException):
    """401 - Authentication failed"""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(401, "AUTH_ERROR", message)


class InvalidTokenError(APIException):
    """401 - Invalid or expired token"""
    
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(401, "INVALID_TOKEN", message)


# 403 Class Errors - Authorization
class AuthorizationError(APIException):
    """403 - Insufficient permissions"""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(403, "AUTHORIZATION_ERROR", message)


class CSRFError(APIException):
    """403 - CSRF token validation failed"""
    
    def __init__(self, message: str = "CSRF token validation failed"):
        super().__init__(403, "CSRF_ERROR", message)


# 404 Class Errors - Not Found
class ResourceNotFoundError(APIException):
    """404 - Resource not found"""
    
    def __init__(self, resource_type: str, resource_id: Any):
        message = f"{resource_type} with ID {resource_id} not found"
        super().__init__(404, "NOT_FOUND", message, {"resource_type": resource_type, "resource_id": str(resource_id)})


# 409 Class Errors - Conflict
class ConflictError(APIException):
    """409 - Resource conflict"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(409, "CONFLICT", message, details)


class DuplicateResourceError(APIException):
    """409 - Duplicate resource"""
    
    def __init__(self, resource_type: str, field: str, value: Any):
        message = f"{resource_type} with {field}='{value}' already exists"
        super().__init__(409, "DUPLICATE_RESOURCE", message, {
            "resource_type": resource_type,
            "field": field,
            "value": str(value)
        })


# 429 Class Errors - Rate Limiting
class RateLimitError(APIException):
    """429 - Too many requests"""
    
    def __init__(self, message: str = "Too many requests, please try again later"):
        super().__init__(429, "RATE_LIMIT_EXCEEDED", message)


# 500 Class Errors - Server Errors
class ServerError(APIException):
    """500 - Internal server error"""
    
    def __init__(self, message: str = "An internal error occurred", details: Optional[Dict[str, Any]] = None):
        super().__init__(500, "SERVER_ERROR", message, details)


class DatabaseError(APIException):
    """500 - Database operation failed"""
    
    def __init__(self, message: str = "Database operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(500, "DATABASE_ERROR", message, details)


class ExternalServiceError(APIException):
    """503 - External service unavailable"""
    
    def __init__(self, service_name: str, message: Optional[str] = None):
        msg = message or f"External service '{service_name}' is unavailable"
        super().__init__(503, "EXTERNAL_SERVICE_ERROR", msg, {"service": service_name})
