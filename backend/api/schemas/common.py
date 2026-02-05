from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel

T = TypeVar("T")

class PaginationMetadata(BaseModel):
    """Pagination metadata"""
    total: int
    offset: int
    limit: int
    has_more: bool

class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response"""
    data: List[T]
    pagination: PaginationMetadata

class SingleResponse(BaseModel, Generic[T]):
    """Standard single item response"""
    data: T
    message: Optional[str] = None

class MessageResponse(BaseModel):
    """Standard message-only response"""
    message: str
    details: Optional[dict] = None

class BulkOperationResponse(BaseModel):
    """Standard bulk operation response"""
    success_count: int
    error_count: int
    errors: Optional[List[dict]] = None
