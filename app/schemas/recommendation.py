"""
Schemas for recommendation endpoint.
"""

from pydantic import BaseModel, Field


class RecommendRequest(BaseModel):
    """
    Request schema for food recommendation.
    
    The recommendation engine uses conditional probability
    to suggest items based on what the customer has already ordered.
    """
    restaurant_id: str = Field(
        ...,
        description="The restaurant ID to get recommendations for",
        examples=["R1"]
    )
    already_ordered: list[str] = Field(
        default_factory=list,
        description="List of menuItemIds already ordered by the customer",
        examples=[["M101", "M104"]]
    )
    num_recommendations: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of recommendations to return (1-10)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "restaurant_id": "R1",
                "already_ordered": ["M101", "M104"],
                "num_recommendations": 3
            }
        }


class RecommendationData(BaseModel):
    """Response data containing recommendations."""
    recommendations: list[str] = Field(
        ...,
        description="List of recommended menuItemIds"
    )
    based_on: list[str] = Field(
        ...,
        description="MenuItemIds the recommendations are based on"
    )
    restaurant_id: str = Field(
        ...,
        description="The restaurant ID the recommendations are for"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "recommendations": ["M103", "M107", "M105"],
                "based_on": ["M101", "M104"],
                "restaurant_id": "R1"
            }
        }


class RecommendResponse(BaseModel):
    """Full response for recommendation endpoint."""
    success: bool
    data: RecommendationData | None = None
    message: str | None = None
