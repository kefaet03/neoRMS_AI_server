"""
Sentiment Analysis Service.
Uses Logistic Regression with TF-IDF for 3-class sentiment classification.
"""

import logging
from pathlib import Path
from typing import Literal

import joblib
import numpy as np

logger = logging.getLogger(__name__)


# Sentiment label mapping
SENTIMENT_LABELS = {
    0: "Negative",
    1: "Neutral",
    2: "Positive"
}


class SentimentService:
    """
    Sentiment Analysis Service using Logistic Regression.
    
    Classifies food reviews into:
    - 0: Negative (original rating 1-2)
    - 1: Neutral (original rating 3)
    - 2: Positive (original rating 4-5)
    """
    
    def __init__(self, model_path: Path = None, vectorizer_path: Path = None):
        """
        Initialize the sentiment service.
        
        Args:
            model_path: Path to the Logistic Regression model (.pkl)
            vectorizer_path: Path to the TF-IDF vectorizer (.pkl)
        """
        self.model_path = model_path
        self.vectorizer_path = vectorizer_path
        self.model = None
        self.vectorizer = None
        self._is_initialized = False
        self._use_mock = False
        
    def initialize(self) -> None:
        """Load the model and vectorizer."""
        if self._is_initialized:
            return
        
        try:
            if self.model_path and self.model_path.exists():
                logger.info(f"Loading sentiment model from {self.model_path}")
                self.model = joblib.load(self.model_path)
            else:
                logger.warning(f"Model not found at {self.model_path}, using mock predictions")
                self._use_mock = True
                
            if self.vectorizer_path and self.vectorizer_path.exists():
                logger.info(f"Loading TF-IDF vectorizer from {self.vectorizer_path}")
                self.vectorizer = joblib.load(self.vectorizer_path)
            else:
                logger.warning(f"Vectorizer not found at {self.vectorizer_path}, using mock predictions")
                self._use_mock = True
                
        except Exception as e:
            logger.error(f"Failed to load sentiment model: {e}")
            self._use_mock = True
        
        self._is_initialized = True
        logger.info(f"Sentiment service initialized (mock mode: {self._use_mock})")
    
    def _predict_mock(self, text: str) -> tuple[int, np.ndarray]:
        """
        Mock prediction based on simple keyword analysis.
        
        Args:
            text: Review text
            
        Returns:
            Tuple of (predicted_label, probability_scores)
        """
        text_lower = text.lower()
        
        # Positive keywords
        positive_words = ["great", "excellent", "amazing", "love", "best", "delicious", 
                         "tasty", "good", "nice", "wonderful", "awesome", "fantastic",
                         "oshadharon", "bhalo", "darun"]
        
        # Negative keywords  
        negative_words = ["bad", "terrible", "awful", "horrible", "worst", "disgusting",
                          "tasteless", "cold", "stale", "rude", "slow", "poor",
                          "kharap", "baje", "ganda"]
        
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)
        
        if pos_count > neg_count:
            label = 2  # Positive
            scores = np.array([0.1, 0.15, 0.75])
        elif neg_count > pos_count:
            label = 0  # Negative
            scores = np.array([0.75, 0.15, 0.1])
        else:
            label = 1  # Neutral
            scores = np.array([0.25, 0.5, 0.25])
        
        return label, scores
    
    def predict(self, text: str) -> dict:
        """
        Predict sentiment for a review text.
        
        Args:
            text: Review text to analyze
            
        Returns:
            Dictionary with prediction results
        """
        if not self._is_initialized:
            self.initialize()
        
        if self._use_mock:
            label, scores = self._predict_mock(text)
        else:
            # Vectorize the text
            text_vectorized = self.vectorizer.transform([text])
            
            # Get prediction
            label = int(self.model.predict(text_vectorized)[0])
            
            # Get probability scores
            if hasattr(self.model, 'predict_proba'):
                scores = self.model.predict_proba(text_vectorized)[0]
            else:
                # Fallback for models without predict_proba
                scores = np.zeros(3)
                scores[label] = 1.0
        
        confidence = float(scores[label])
        
        result = {
            "text": text,
            "sentiment_label": label,
            "sentiment_name": SENTIMENT_LABELS[label],
            "confidence": round(confidence, 4),
            "scores": {
                "negative": round(float(scores[0]), 4),
                "neutral": round(float(scores[1]), 4),
                "positive": round(float(scores[2]), 4),
            }
        }
        
        logger.debug(f"Sentiment prediction: {result['sentiment_name']} ({confidence:.2%})")
        return result
    
    @property
    def is_ready(self) -> bool:
        """Check if the service is ready."""
        return self._is_initialized


# Singleton instance
_sentiment_service: SentimentService | None = None


def get_sentiment_service() -> SentimentService:
    """Get the singleton sentiment service instance."""
    global _sentiment_service
    if _sentiment_service is None:
        from ..config import settings
        _sentiment_service = SentimentService(
            model_path=settings.SENTIMENT_MODEL_PATH,
            vectorizer_path=settings.TFIDF_VECTORIZER_PATH
        )
    return _sentiment_service
