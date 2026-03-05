"""
Base response schema for consistent API responses.
"""

from typing import Any, Generic, TypeVar, Optional
from pydantic import BaseModel, Field


T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """
    Standard API response wrapper.
    
    All API responses follow this structure:
    {
        "success": true/false,
        "data": { ... },
        "message": "optional message"
    }
    """
    success: bool = Field(
        ...,
        description="Indicates whether the request was successful"
    )
    data: Optional[T] = Field(
        default=None,
        description="Response payload data"
    )
    message: Optional[str] = Field(
        default=None,
        description="Optional message providing additional context"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"key": "value"},
                "message": "Request processed successfully"
            }
        }


class HealthCheckResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(..., description="Service health status")
    version: str = Field(..., description="API version")
    services: dict[str, str] = Field(
        default_factory=dict,
        description="Status of individual services/models"
    )
