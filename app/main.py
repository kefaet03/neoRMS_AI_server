"""
RMS AI Modules API Server
Production-ready FastAPI application.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .routes import (
    health_router,
    recommendation_router,
    review_router,
    sentiment_router,
)
from .services.recommendation_service import get_recommendation_service
from .services.review_service import get_review_service
from .services.sentiment_service import get_sentiment_service


# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    
    Initializes services on startup and cleans up on shutdown.
    """
    # Startup
    logger.info("=" * 60)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 60)
    
    # Initialize services
    logger.info("Initializing AI services...")
    
    try:
        # Initialize recommendation engine
        rec_service = get_recommendation_service()
        rec_service.initialize()
        logger.info("✓ Recommendation engine ready")
    except Exception as e:
        logger.error(f"✗ Failed to initialize recommendation engine: {e}")
    
    try:
        # Initialize review analyzer
        review_service = get_review_service()
        review_service.initialize()
        logger.info("✓ Review analyzer ready")
    except Exception as e:
        logger.error(f"✗ Failed to initialize review analyzer: {e}")
    
    try:
        # Initialize sentiment analyzer
        sentiment_service = get_sentiment_service()
        sentiment_service.initialize()
        logger.info("✓ Sentiment analyzer ready")
    except Exception as e:
        logger.error(f"✗ Failed to initialize sentiment analyzer: {e}")
    
    logger.info("-" * 60)
    logger.info(f"Server running at http://{settings.HOST}:{settings.PORT}")
    logger.info(f"API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("Shutting down server...")
    logger.info("Goodbye!")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## RMS AI Modules API

Production-ready API server for the Restaurant Management System AI modules.

### Available Modules:

1. **Recommendation Engine (AM1)**
   - Uses conditional probability for food recommendations
   - Based on order history patterns

2. **Review Analyzer (AM4)**
   - Extracts complaints from customer reviews
   - Supports English, Bengali, and Banglish

3. **Sentiment Analyzer (AM42)**
   - 3-class sentiment classification
   - Uses Logistic Regression with TF-IDF

### Response Format:

All endpoints return responses in this format:
```json
{
    "success": true,
    "data": {...},
    "message": "optional message"
}
```
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions globally."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "data": None,
            "message": f"Internal server error: {str(exc)}"
        }
    )


# Include routers
app.include_router(health_router)
app.include_router(recommendation_router)
app.include_router(review_router)
app.include_router(sentiment_router)


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Redirect to API documentation."""
    return {
        "success": True,
        "data": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "health": "/health"
        },
        "message": "Welcome to RMS AI Modules API"
    }
