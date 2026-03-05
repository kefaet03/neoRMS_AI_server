"""
Review analysis endpoint.
"""

import logging
from fastapi import APIRouter, HTTPException, status

from ..schemas.review import (
    AnalyzeReviewRequest,
    AnalyzeReviewResponse,
    ReviewAnalysisData,
    Complaint,
)
from ..services.review_service import get_review_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analyze-review", tags=["Review Analysis"])


@router.post(
    "",
    response_model=AnalyzeReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Reviews for Complaints",
    description="""
    Analyze restaurant reviews to extract complaints.
    
    Supports English, Bengali, and Banglish reviews.
    
    **Features:**
    - Pre-filters short/invalid reviews
    - Extracts food items and issues mentioned
    - Categorizes complaints (temperature, taste, quality, etc.)
    - Groups complaints by item and issue
    
    **Complaint Categories:**
    - temperature: cold, frozen, lukewarm, etc.
    - taste: tasteless, bland, bitter, etc.
    - quality: rotten, spoiled, stale, etc.
    - cooking: undercooked, overcooked, burnt, etc.
    - service: slow, rude, delayed, etc.
    - hygiene: dirty, contaminated, etc.
    - other: miscellaneous issues
    """,
)
async def analyze_reviews(request: AnalyzeReviewRequest) -> AnalyzeReviewResponse:
    """
    Analyze reviews and extract complaints.
    
    Args:
        request: AnalyzeReviewRequest containing list of review texts
    
    Returns:
        AnalyzeReviewResponse with extracted complaints
        
    Raises:
        HTTPException: If analysis fails
    """
    try:
        service = get_review_service()
        
        result = await service.analyze(request.reviews)
        
        # Convert complaint dicts to Complaint objects
        complaints = [Complaint(**c) for c in result["complaints"]]
        
        analysis_data = ReviewAnalysisData(
            total_reviews=result["total_reviews"],
            kept_reviews=result["kept_reviews"],
            ignored_reviews=result["ignored_reviews"],
            total_complaints=result["total_complaints"],
            complaints=complaints,
            complaints_grouped=result["complaints_grouped"],
        )
        
        logger.info(
            f"Analyzed {result['total_reviews']} reviews, "
            f"found {result['total_complaints']} complaints"
        )
        
        message = (
            f"Analyzed {result['kept_reviews']} reviews, "
            f"extracted {result['total_complaints']} complaints"
        )
        if result["ignored_reviews"] > 0:
            message += f" ({result['ignored_reviews']} reviews filtered out)"
        
        return AnalyzeReviewResponse(
            success=True,
            data=analysis_data,
            message=message
        )
        
    except Exception as e:
        logger.error(f"Review analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze reviews: {str(e)}"
        )
