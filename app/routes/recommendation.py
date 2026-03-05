"""
Food recommendation endpoint.
"""

import logging
from fastapi import APIRouter, HTTPException, status

from ..schemas.recommendation import (
    RecommendRequest,
    RecommendResponse,
    RecommendationData,
)
from ..services.recommendation_service import get_recommendation_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/recommend", tags=["Recommendation"])


@router.post(
    "",
    response_model=RecommendResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Food Recommendations",
    description="""
    Get food recommendations based on items already ordered.
    
    The recommendation engine uses conditional probability to suggest
    items that are frequently ordered together.
    
    **Required:**
    - `restaurant_id`: The restaurant to get recommendations for
    
    **Algorithm:**
    - Uses P(item_j | item_i) - probability of ordering item_j given item_i
    - For multiple items, uses average conditional probability
    - Returns items with highest probability scores
    """,
)
async def get_recommendations(request: RecommendRequest) -> RecommendResponse:
    """
    Get food recommendations based on order history.
    
    Args:
        request: RecommendRequest containing:
            - restaurant_id: Restaurant ID to get recommendations for
            - already_ordered: List of menuItemIds already ordered
            - num_recommendations: Number of recommendations to return (1-10)
    
    Returns:
        RecommendResponse with list of recommended menuItemIds
        
    Raises:
        HTTPException: If recommendation fails or restaurant not found
    """
    try:
        service = get_recommendation_service(request.restaurant_id)
        
        recommendations = service.recommend(
            n=request.num_recommendations,
            already_ordered=request.already_ordered
        )
        
        if not recommendations:
            logger.warning(f"No recommendations available for {request.restaurant_id}")
            return RecommendResponse(
                success=True,
                data=RecommendationData(
                    recommendations=[],
                    based_on=request.already_ordered,
                    restaurant_id=request.restaurant_id
                ),
                message="No recommendations available for the given items"
            )
        
        logger.info(
            f"Generated {len(recommendations)} recommendations for "
            f"restaurant {request.restaurant_id}"
        )
        
        return RecommendResponse(
            success=True,
            data=RecommendationData(
                recommendations=recommendations,
                based_on=request.already_ordered,
                restaurant_id=request.restaurant_id
            ),
            message=f"Successfully generated {len(recommendations)} recommendations"
        )
        
    except ValueError as e:
        logger.warning(f"Restaurant not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Recommendation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )
