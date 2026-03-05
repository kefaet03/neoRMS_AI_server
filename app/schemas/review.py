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


class IssueDetail(BaseModel):
    """Individual issue within a food item."""
    issue: str = Field(..., description="The specific issue or complaint")
    count: int = Field(..., ge=1, description="Number of occurrences")
    category: str = Field(..., description="Complaint category")


class FoodComplaint(BaseModel):
    """Complaints grouped by food item."""
    foodName: str = Field(..., description="The food item name")
    issues: list[IssueDetail] = Field(..., description="List of issues for this food item")


class ReviewAnalysisData(BaseModel):
    """Response data containing analysis results."""
    total_reviews: int = Field(..., description="Total number of reviews submitted")
    kept_reviews: int = Field(..., description="Number of reviews that were analyzed")
    ignored_reviews: int = Field(..., description="Number of reviews filtered out (too short, etc.)")
    total_complaints: int = Field(..., description="Total number of complaints extracted")
    complaints_grouped: list[FoodComplaint] = Field(
        default_factory=list,
        description="Complaints grouped by food item with issues array"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_reviews": 5,
                "kept_reviews": 4,
                "ignored_reviews": 1,
                "total_complaints": 3,
                "complaints_grouped": [
                    {
                        "foodName": "burger",
                        "issues": [
                            {"issue": "cold", "count": 1, "category": "temperature"},
                            {"issue": "tasteless", "count": 1, "category": "taste"}
                        ]
                    },
                    {
                        "foodName": "food",
                        "issues": [
                            {"issue": "stale", "count": 1, "category": "taste"}
                        ]
                    }
                ]
            }
        }


class AnalyzeReviewResponse(BaseModel):
    """Full response for review analysis endpoint."""
    success: bool
    data: ReviewAnalysisData | None = None
    message: str | None = None
