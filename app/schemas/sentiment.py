"""
Schemas for sentiment analysis endpoint.
"""

from typing import Literal
from pydantic import BaseModel, Field


class SentimentRequest(BaseModel):
    """
    Request schema for sentiment analysis.
    
    Analyzes the sentiment of a food review text.
    Uses Logistic Regression with TF-IDF vectorization.
    """
    text: str = Field(
        ...,
        min_length=1,
        description="Review text to analyze for sentiment",
        examples=["Biryani ta oshadharon chilo!"]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "The food was amazing and the service was excellent!"
            }
        }


class SentimentScores(BaseModel):
    """Probability scores for each sentiment class."""
    negative: float = Field(..., ge=0, le=1, description="Probability of negative sentiment")
    neutral: float = Field(..., ge=0, le=1, description="Probability of neutral sentiment")
    positive: float = Field(..., ge=0, le=1, description="Probability of positive sentiment")


class SentimentData(BaseModel):
    """Response data containing sentiment analysis results."""
    text: str = Field(..., description="The analyzed text")
    sentiment_label: int = Field(
        ...,
        ge=0,
        le=2,
        description="Sentiment label: 0=Negative, 1=Neutral, 2=Positive"
    )
    sentiment_name: Literal["Negative", "Neutral", "Positive"] = Field(
        ...,
        description="Human-readable sentiment name"
    )
    confidence: float = Field(
        ...,
        ge=0,
        le=1,
        description="Confidence score for the prediction"
    )
    scores: SentimentScores = Field(
        ...,
        description="Probability scores for each sentiment class"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "The food was amazing!",
                "sentiment_label": 2,
                "sentiment_name": "Positive",
                "confidence": 0.92,
                "scores": {
                    "negative": 0.03,
                    "neutral": 0.05,
                    "positive": 0.92
                }
            }
        }


class SentimentResponse(BaseModel):
    """Full response for sentiment analysis endpoint."""
    success: bool
    data: SentimentData | None = None
    message: str | None = None
