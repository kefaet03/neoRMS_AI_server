"""
Application configuration settings.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Settings
    APP_NAME: str = "RMS AI Modules API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8888
    
    # CORS Settings
    CORS_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]
    
    # Model Paths (relative to api_server directory)
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    SENTIMENT_MODEL_PATH: Path = BASE_DIR.parent / "AM42" / "saved_models" / "logistic_regression.pkl"
    TFIDF_VECTORIZER_PATH: Path = BASE_DIR.parent / "AM42" / "saved_models" / "tfidf_vectorizer.pkl"
    
    # Gemini API (for review analyzer)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
