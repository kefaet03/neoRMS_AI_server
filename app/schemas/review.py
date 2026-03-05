"""
Schemas for review analysis endpoint.
"""

from typing import Literal
from pydantic import BaseModel, Field


class AnalyzeReviewRequest(BaseModel):
    """
    Request schema for review analysis.
    
    Analyzes restaurant reviews to extract complaints.
    Supports English, Bengali, and Banglish reviews.
    """
    reviews: list[str] = Field(
        ...,
        min_length=1,
        description="List of review text strings to analyze",
        examples=[["The burger was cold and the service was slow", "Biryani ta oshadharon chilo!"]]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "reviews": [
                    "The burger was cold and tasteless",
                    "Delivery took 2 hours, food was stale",
                    "Great biryani, loved it!"
                ]
            }
        }


class Complaint(BaseModel):
    """Individual complaint extracted from a review."""
    item: str = Field(..., description="The food item or service mentioned")
    issue: str = Field(..., description="The specific issue or complaint")
    category: Literal["temperature", "taste", "quality", "cooking", "service", "hygiene", "other"] = Field(
        ...,
        description="Category of the complaint"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "item": "burger",
                "issue": "cold",
                "category": "temperature"
            }
        }


class ComplaintSummary(BaseModel):
    """Summary of grouped complaints."""
    count: int = Field(..., description="Number of occurrences")
    category: str = Field(..., description="Complaint category")


class ReviewAnalysisData(BaseModel):
    """Response data containing analysis results."""
    total_reviews: int = Field(..., description="Total number of reviews submitted")
    kept_reviews: int = Field(..., description="Number of reviews that were analyzed")
    ignored_reviews: int = Field(..., description="Number of reviews filtered out (too short, etc.)")
    total_complaints: int = Field(..., description="Total number of complaints extracted")
    complaints: list[Complaint] = Field(
        default_factory=list,
        description="List of extracted complaints"
    )
    complaints_grouped: dict = Field(
        default_factory=dict,
        description="Complaints grouped by item and issue"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_reviews": 5,
                "kept_reviews": 4,
                "ignored_reviews": 1,
                "total_complaints": 3,
                "complaints": [
                    {"item": "burger", "issue": "cold", "category": "temperature"},
                    {"item": "service", "issue": "slow", "category": "service"}
                ],
                "complaints_grouped": {
                    "burger": {"cold": {"count": 1, "category": "temperature"}}
                }
            }
        }


class AnalyzeReviewResponse(BaseModel):
    """Full response for review analysis endpoint."""
    success: bool
    data: ReviewAnalysisData | None = None
    message: str | None = None
