"""
Review Analyzer Service.
Extracts complaints from restaurant reviews.

Note: The original AM4 module uses Google Gemini API for analysis.
This service provides a mock implementation for local testing
and can be configured to use the actual Gemini API.
"""

import logging
import re
from typing import Literal
from collections import defaultdict

from ..schemas.review import Complaint

logger = logging.getLogger(__name__)


# Complaint categories
CATEGORIES = ["temperature", "taste", "quality", "cooking", "service", "hygiene", "other"]

# Keywords for mock complaint extraction
COMPLAINT_KEYWORDS = {
    "temperature": ["cold", "frozen", "lukewarm", "hot", "warm", "thanda", "garam", "heated"],
    "taste": ["tasteless", "bland", "bitter", "sour", "salty", "sweet", "spicy", "stale", "bad taste"],
    "quality": ["rotten", "spoiled", "expired", "old", "fresh", "bad quality", "poor", "substandard"],
    "cooking": ["undercooked", "overcooked", "raw", "burnt", "oily", "greasy", "dry"],
    "service": ["slow", "rude", "late", "delayed", "wrong order", "missing", "staff", "waiter"],
    "hygiene": ["dirty", "unclean", "hair", "insect", "bug", "unhygienic", "contaminated"],
}

# Common food items
FOOD_ITEMS = [
    "burger", "pizza", "biryani", "chicken", "rice", "naan", "roti", "curry",
    "fries", "noodles", "pasta", "sandwich", "wrap", "steak", "fish", "prawn",
    "kebab", "tikka", "dal", "soup", "salad", "drink", "coke", "coffee", "tea",
    "food", "meal", "order", "delivery"
]


class ReviewAnalyzerService:
    """
    Service for analyzing restaurant reviews and extracting complaints.
    
    This implementation uses keyword-based extraction for local testing.
    For production, configure GEMINI_API_KEY to use the actual LLM.
    """
    
    def __init__(self, use_llm: bool = False, api_key: str = None):
        """
        Initialize the review analyzer.
        
        Args:
            use_llm: Whether to use Gemini LLM (requires API key)
            api_key: Gemini API key (optional)
        """
        self.use_llm = use_llm and api_key
        self.api_key = api_key
        self._is_initialized = False
        
    def initialize(self) -> None:
        """Initialize the service."""
        if self._is_initialized:
            return
            
        logger.info(f"Review analyzer initialized (LLM mode: {self.use_llm})")
        self._is_initialized = True
    
    def _prefilter(self, text: str) -> tuple[bool, str | None]:
        """
        Pre-filter reviews to skip invalid ones.
        
        Args:
            text: Review text
            
        Returns:
            Tuple of (keep, reason)
        """
        if not text or len(text.strip()) < 10:
            return False, "too_short"
        if len(text) > 5000:
            return False, "too_long"
        return True, None
    
    def _extract_complaints_mock(self, reviews: list[str]) -> list[Complaint]:
        """
        Extract complaints using keyword matching (mock implementation).
        
        Args:
            reviews: List of review texts
            
        Returns:
            List of extracted complaints
        """
        complaints = []
        
        for review in reviews:
            review_lower = review.lower()
            
            # Find food items mentioned
            items_found = []
            for item in FOOD_ITEMS:
                if item in review_lower:
                    items_found.append(item)
            
            if not items_found:
                items_found = ["food"]  # Default
            
            # Find complaint keywords
            for category, keywords in COMPLAINT_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in review_lower:
                        # Check for negation
                        negation_pattern = rf"(not|no|never|n't)\s+(\w+\s+){{0,3}}{re.escape(keyword)}"
                        if re.search(negation_pattern, review_lower):
                            continue
                        
                        # Create complaint
                        for item in items_found[:1]:  # Use first item found
                            complaint = Complaint(
                                item=item,
                                issue=keyword,
                                category=category
                            )
                            if complaint not in complaints:
                                complaints.append(complaint)
                        break
        
        return complaints
    
    def _group_complaints(self, complaints: list[Complaint]) -> list[dict]:
        """
        Group complaints by item and issue.
        
        Args:
            complaints: List of complaints
            
        Returns:
            List of food complaints with issues array:
            [{"foodName": str, "issues": [{"issue": str, "count": int, "category": str}]}]
        """
        grouped: dict = defaultdict(lambda: defaultdict(lambda: {"count": 0, "category": ""}))
        
        for complaint in complaints:
            grouped[complaint.item][complaint.issue]["count"] += 1
            grouped[complaint.item][complaint.issue]["category"] = complaint.category
        
        # Convert to new array format
        result = []
        for food_name, issues_dict in grouped.items():
            issues_list = [
                {
                    "issue": issue,
                    "count": data["count"],
                    "category": data["category"]
                }
                for issue, data in issues_dict.items()
            ]
            result.append({
                "foodName": food_name,
                "issues": issues_list
            })
        
        return result
    
    async def analyze(self, reviews: list[str]) -> dict:
        """
        Analyze reviews and extract complaints.
        
        Args:
            reviews: List of review texts
            
        Returns:
            Analysis results dict
        """
        if not self._is_initialized:
            self.initialize()
        
        total = len(reviews)
        kept_texts: list[str] = []
        ignored = 0
        
        # Pre-filter reviews
        for text in reviews:
            keep, reason = self._prefilter(text)
            if not keep:
                ignored += 1
                continue
            kept_texts.append(text.strip())
        
        # Extract complaints
        if self.use_llm:
            # TODO: Implement actual Gemini API call
            complaints = self._extract_complaints_mock(kept_texts)
            logger.info("Using mock extraction (LLM not fully implemented)")
        else:
            complaints = self._extract_complaints_mock(kept_texts)
        
        # Group complaints
        grouped = self._group_complaints(complaints)
        
        logger.debug(f"Analyzed {len(kept_texts)} reviews, found {len(complaints)} complaints")
        
        return {
            "total_reviews": total,
            "kept_reviews": len(kept_texts),
            "ignored_reviews": ignored,
            "total_complaints": len(complaints),
            "complaints_grouped": grouped,
        }
    
    @property
    def is_ready(self) -> bool:
        """Check if the service is ready."""
        return self._is_initialized


# Singleton instance
_review_service: ReviewAnalyzerService | None = None


def get_review_service() -> ReviewAnalyzerService:
    """Get the singleton review analyzer service instance."""
    global _review_service
    if _review_service is None:
        from ..config import settings
        _review_service = ReviewAnalyzerService(
            use_llm=bool(settings.GEMINI_API_KEY),
            api_key=settings.GEMINI_API_KEY
        )
    return _review_service
