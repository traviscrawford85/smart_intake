"""
Base schemas for API responses.
"""
from typing import Any, Dict, Optional, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """Base response schema."""
    success: bool = Field(True, description="Request success status")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[T] = Field(None, description="Response data")


class ErrorResponse(BaseModel):
    """Error response schema."""
    success: bool = Field(False, description="Request success status")
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")


class SuccessResponse(BaseModel):
    """Success response schema."""
    success: bool = Field(True, description="Request success status")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response schema."""
    success: bool = Field(True, description="Request success status")
    data: list[T] = Field(..., description="Response data items")
    pagination: Dict[str, Any] = Field(..., description="Pagination information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": [],
                "pagination": {
                    "current_page": 1,
                    "per_page": 50,
                    "total_count": 100,
                    "total_pages": 2,
                    "has_next": True,
                    "has_prev": False
                }
            }
        }
