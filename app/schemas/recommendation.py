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
    already_ordered: list[str] = Field(
        default_factory=list,
        description="List of items already ordered by the customer",
        examples=[["Kacchi Biryani", "Borhani"]]
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
                "already_ordered": ["Kacchi Biryani", "Borhani"],
                "num_recommendations": 3
            }
        }


class RecommendationData(BaseModel):
    """Response data containing recommendations."""
    recommendations: list[str] = Field(
        ...,
        description="List of recommended food items"
    )
    based_on: list[str] = Field(
        ...,
        description="Items the recommendations are based on"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "recommendations": ["Chicken Roast", "Morog Polao", "Beef Bhuna"],
                "based_on": ["Kacchi Biryani", "Borhani"]
            }
        }


class RecommendResponse(BaseModel):
    """Full response for recommendation endpoint."""
    success: bool
    data: RecommendationData | None = None
    message: str | None = None
