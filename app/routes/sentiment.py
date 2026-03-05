"""
Sentiment analysis endpoint.
"""

import logging
from fastapi import APIRouter, HTTPException, status

from ..schemas.sentiment import (
    SentimentRequest,
    SentimentResponse,
    SentimentData,
    SentimentScores,
)
from ..services.sentiment_service import get_sentiment_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sentiment", tags=["Sentiment Analysis"])


@router.post(
    "",
    response_model=SentimentResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Sentiment",
    description="""
    Analyze the sentiment of a food review.
    
    Uses Logistic Regression with TF-IDF vectorization.
    
    **Sentiment Classes:**
    - 0 (Negative): Reviews with original rating 1-2
    - 1 (Neutral): Reviews with original rating 3
    - 2 (Positive): Reviews with original rating 4-5
    
    **Output:**
    - sentiment_label: Numeric label (0, 1, or 2)
    - sentiment_name: Human-readable name
    - confidence: Model confidence for the prediction
    - scores: Probability distribution across all classes
    """,
)
async def analyze_sentiment(request: SentimentRequest) -> SentimentResponse:
    """
    Analyze sentiment of a review text.
    
    Args:
        request: SentimentRequest containing the review text
    
    Returns:
        SentimentResponse with sentiment prediction
        
    Raises:
        HTTPException: If sentiment analysis fails
    """
    try:
        service = get_sentiment_service()
        
        result = service.predict(request.text)
        
        sentiment_data = SentimentData(
            text=result["text"],
            sentiment_label=result["sentiment_label"],
            sentiment_name=result["sentiment_name"],
            confidence=result["confidence"],
            scores=SentimentScores(**result["scores"]),
        )
        
        logger.info(
            f"Sentiment: {result['sentiment_name']} "
            f"(confidence: {result['confidence']:.2%})"
        )
        
        return SentimentResponse(
            success=True,
            data=sentiment_data,
            message=f"Sentiment: {result['sentiment_name']}"
        )
        
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze sentiment: {str(e)}"
        )
