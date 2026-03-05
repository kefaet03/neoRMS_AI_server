"""
Health check endpoint.
"""

import logging
from fastapi import APIRouter, status

from ..schemas.base import HealthCheckResponse, APIResponse
from ..services.recommendation_service import get_recommendation_service
from ..services.review_service import get_review_service
from ..services.sentiment_service import get_sentiment_service
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=APIResponse[HealthCheckResponse],
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check the health status of the API and its services.",
)
async def health_check() -> APIResponse[HealthCheckResponse]:
    """
    Health check endpoint.
    
    Returns the overall health status of the API and 
    the status of individual services/models.
    
    Returns:
        APIResponse containing health status information
    """
    # Check individual services
    services_status = {
        "recommendation_engine": "ready" if get_recommendation_service().is_ready else "loading",
        "review_analyzer": "ready" if get_review_service().is_ready else "loading",
        "sentiment_analyzer": "ready" if get_sentiment_service().is_ready else "loading",
    }
    
    # Overall status
    all_ready = all(s == "ready" for s in services_status.values())
    overall_status = "healthy" if all_ready else "degraded"
    
    health_data = HealthCheckResponse(
        status=overall_status,
        version=settings.APP_VERSION,
        services=services_status
    )
    
    logger.info(f"Health check: {overall_status}")
    
    return APIResponse(
        success=True,
        data=health_data,
        message="Service is operational"
    )
