"""
API Routes.
"""

from .health import router as health_router
from .recommendation import router as recommendation_router
from .review import router as review_router
from .sentiment import router as sentiment_router


__all__ = [
    "health_router",
    "recommendation_router",
    "review_router",
    "sentiment_router",
]
