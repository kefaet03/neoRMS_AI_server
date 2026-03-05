"""
Review Analyzer Service.
Extracts complaints from restaurant reviews using Google Gemini API.

Uses the same implementation as AM4 module with Gemini 2.5 Flash (FREE tier).
Supports Banglish, Bengali, and English reviews.
"""

import json
import logging
import re
import time
from collections import defaultdict
from typing import Literal

from ..schemas.review import Complaint

logger = logging.getLogger(__name__)


# Complaint categories
CATEGORIES = ["temperature", "taste", "quality", "cooking", "service", "hygiene", "other"]

# Generic praise words to filter out
GENERIC_PRAISE = {"ok", "good", "nice", "awesome"}

# Negative keywords for prefilter signal detection
NEGATIVE_KEYWORDS = {
    "cold", "lukewarm", "too salty", "salty", "bland", "burnt", "raw",
    "undercooked", "overcooked", "stale", "soggy", "greasy", "oily",
    "dry", "hard", "rubbery", "smelly", "dirty", "hair", "late", "rude",
    "thanda", "garam", "kharap", "baje"
}

# System prompt for Gemini (from AM4)
GEMINI_SYSTEM_PROMPT = """You are a restaurant review analyzer that understands Banglish (Bengali + English), Bengali, and English.

Extract ONLY complaints about food items or service.
Ignore positive feedback completely.

Output a JSON list where each object has:
- "item": the food item name in English (e.g., "burger", "fries", "pizza", "biriyani")
- "issue": the problem in English (e.g., "cold", "too salty", "burnt")
- "category": one of ["temperature", "taste", "quality", "cooking", "service", "hygiene", "other"]

Examples of Banglish complaints to understand:
- "Pizza er edge jhule gase" → burnt edges
- "Burger thanda chilo" → cold
- "Beshi lobon diye" → too salty
- "Chicken kachcha chilo" → undercooked/raw
- "Service slow chilo" → slow service
- "Waiter rude chilo" → rude service

Rules:
- Only extract complaints/negative feedback
- If there are no complaints, return an empty list: []
- Be concise with the issue description (use English)
- One food item can have multiple issues
- Understand Banglish, Bengali, and English reviews"""

# Keywords for fallback mock extraction
COMPLAINT_KEYWORDS = {
    "temperature": ["cold", "frozen", "lukewarm", "hot", "warm", "thanda", "garam", "heated"],
    "taste": ["tasteless", "bland", "bitter", "sour", "salty", "sweet", "spicy", "stale", "bad taste"],
    "quality": ["rotten", "spoiled", "expired", "old", "fresh", "bad quality", "poor", "substandard"],
    "cooking": ["undercooked", "overcooked", "raw", "burnt", "oily", "greasy", "dry"],
    "service": ["slow", "rude", "late", "delayed", "wrong order", "missing", "staff", "waiter"],
    "hygiene": ["dirty", "unclean", "hair", "insect", "bug", "unhygienic", "contaminated"],
}

# Common food items for fallback
FOOD_ITEMS = [
    "burger", "pizza", "biryani", "chicken", "rice", "naan", "roti", "curry",
    "fries", "noodles", "pasta", "sandwich", "wrap", "steak", "fish", "prawn",
    "kebab", "tikka", "dal", "soup", "salad", "drink", "coke", "coffee", "tea",
    "food", "meal", "order", "delivery"
]


class ReviewAnalyzerService:
    """
    Service for analyzing restaurant reviews and extracting complaints.
    
    Uses Google Gemini 2.5 Flash (FREE tier) for intelligent complaint extraction.
    Supports Banglish, Bengali, and English reviews.
    Falls back to keyword-based extraction if Gemini API is unavailable.
    """
    
    def __init__(self, use_llm: bool = False, api_key: str = None):
        """
        Initialize the review analyzer.
        
        Args:
            use_llm: Whether to use Gemini LLM (requires API key)
            api_key: Gemini API key
        """
        self.use_llm = use_llm and bool(api_key)
        self.api_key = api_key
        self.model_name = "gemini-2.5-flash"
        self._is_initialized = False
        self._genai_client = None
        
    def initialize(self) -> None:
        """Initialize the service and configure Gemini if API key is available."""
        if self._is_initialized:
            return
        
        if self.use_llm and self.api_key:
            try:
                from google import genai
                self._genai_client = genai.Client(api_key=self.api_key)
                logger.info(f"Review analyzer initialized with Gemini ({self.model_name})")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}. Falling back to mock extraction.")
                self.use_llm = False
                self._genai_client = None
        else:
            logger.info("Review analyzer initialized (keyword-based fallback mode)")
        
        self._is_initialized = True
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for prefiltering."""
        return re.sub(r"\s+", " ", text.strip().lower())
    
    def _has_negative_signal(self, text: str) -> bool:
        """Check if text contains any negative keywords."""
        normalized = self._normalize_text(text)
        return any(keyword in normalized for keyword in NEGATIVE_KEYWORDS)
    
    def _prefilter(self, text: str) -> tuple[bool, str | None]:
        """
        Pre-filter reviews to skip invalid ones.
        
        Args:
            text: Review text
            
        Returns:
            Tuple of (keep, reason)
        """
        normalized = self._normalize_text(text)
        
        # if len(normalized) < 10:
        #     return False, "too_short"
        
        # if normalized in GENERIC_PRAISE:
        #     return False, "generic_praise"
        
        if len(text) > 5000:
            return False, "too_long"
        
        return True, None
    
    def _extract_complaints_gemini(self, reviews: list[str]) -> list[Complaint]:
        """
        Extract complaints using Google Gemini API.
        
        Args:
            reviews: List of review texts
            
        Returns:
            List of extracted complaints
        """
        if not self._genai_client:
            logger.warning("Gemini client not initialized, falling back to mock")
            return self._extract_complaints_mock(reviews)
        
        # Format reviews as numbered list
        reviews_text = "\n".join(f"{i+1}. {r}" for i, r in enumerate(reviews))
        
        prompt = f"""{GEMINI_SYSTEM_PROMPT}

Analyze these {len(reviews)} restaurant reviews and extract complaints:

{reviews_text}

Return ONLY a valid JSON array, no other text. Example format:
[{{"item": "burger", "issue": "cold", "category": "temperature"}}]
"""
        
        # Retry with exponential backoff for rate limits
        max_retries = 3
        content = ""
        
        for attempt in range(max_retries):
            try:
                response = self._genai_client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                content = response.text.strip()
                break
            except Exception as e:
                error_str = str(e)
                error_type = type(e).__name__
                
                if "ResourceExhausted" in error_type or "429" in error_str:
                    wait_time = (attempt + 1) * 2
                    logger.warning(f"Gemini rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    if attempt == max_retries - 1:
                        logger.error(f"Gemini API rate limit exceeded after {max_retries} retries")
                        return self._extract_complaints_mock(reviews)
                else:
                    logger.error(f"Gemini API error: {e}")
                    return self._extract_complaints_mock(reviews)
        
        # Extract JSON from response (handle markdown code blocks)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        # Parse JSON response
        try:
            data = json.loads(content)
            if isinstance(data, dict):
                data = data.get("complaints", data.get("results", []))
            if not isinstance(data, list):
                data = []
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse Gemini response as JSON: {e}")
            data = []
        
        # Convert to Complaint objects
        complaints: list[Complaint] = []
        for item in data:
            if isinstance(item, dict) and "item" in item and "issue" in item:
                category = item.get("category", "other")
                if category not in CATEGORIES:
                    category = "other"
                complaints.append(Complaint(
                    item=item["item"],
                    issue=item["issue"],
                    category=category,
                ))
        
        logger.info(f"Gemini extracted {len(complaints)} complaints from {len(reviews)} reviews")
        return complaints
    
    def _extract_complaints_mock(self, reviews: list[str]) -> list[Complaint]:
        """
        Extract complaints using keyword matching (fallback implementation).
        
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
        
        logger.info(f"Fallback extraction found {len(complaints)} complaints from {len(reviews)} reviews")
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
        
        Uses Gemini API if configured, otherwise falls back to keyword-based extraction.
        
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
        
        # Extract complaints using Gemini or fallback
        if self.use_llm and kept_texts:
            complaints = self._extract_complaints_gemini(kept_texts)
        else:
            complaints = self._extract_complaints_mock(kept_texts) if kept_texts else []
        
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
