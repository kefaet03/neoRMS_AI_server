"""
Food Recommendation Service.
Uses conditional probability to recommend food items based on order history.
Fetches order history from SQLite database per restaurant.
"""

import json
import logging
import sqlite3
from collections import defaultdict
from pathlib import Path
from typing import Set

logger = logging.getLogger(__name__)


# Path to SQLite database
DB_PATH = Path(__file__).parent.parent.parent / "orders.db"


def get_order_history_from_db(restaurant_id: str) -> dict[str, list[str]]:
    """
    Fetch order history for a specific restaurant from SQLite database.
    
    Args:
        restaurant_id: The restaurant ID to filter by
        
    Returns:
        Dictionary mapping order_id to list of menuItemIds
        Format: {"001": ["M101", "M104"], "002": ["M102", "M106"]}
    """
    if not DB_PATH.exists():
        logger.warning(f"Database not found at {DB_PATH}. Run db_preprocessing.py first.")
        return {}
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT order_id, items FROM orders WHERE restaurant_id = ?",
            (restaurant_id,)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        order_history = {}
        for order_id, items_json in rows:
            order_history[order_id] = json.loads(items_json)
        
        logger.info(f"Loaded {len(order_history)} orders for restaurant {restaurant_id}")
        return order_history
        
    except Exception as e:
        logger.error(f"Failed to fetch order history: {e}")
        return {}


class RecommendationService:
    """
    Probabilistic Food Recommendation Engine.
    
    Uses conditional probability P(item_j | item_i) to recommend
    food items based on what the customer has already ordered.
    """
    
    def __init__(self, order_history: dict[str, list[str]], restaurant_id: str):
        """
        Initialize the recommendation engine.
        
        Args:
            order_history: Dictionary mapping order IDs to list of menuItemIds.
            restaurant_id: The restaurant ID this service is for.
        """
        self.order_history = order_history
        self.restaurant_id = restaurant_id
        self.item_frequency: dict[str, int] = defaultdict(int)
        self.co_occurrence: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.total_orders = len(self.order_history)
        self._is_initialized = False
        
    def initialize(self) -> None:
        """Build the probability model from order history."""
        if self._is_initialized:
            return
            
        logger.info("Building recommendation probability model...")
        
        for order_id, items in self.order_history.items():
            # Count individual item frequencies
            for item in items:
                self.item_frequency[item] += 1
            
            # Count co-occurrences (bidirectional)
            for i, item_i in enumerate(items):
                for j, item_j in enumerate(items):
                    if i != j:
                        self.co_occurrence[item_i][item_j] += 1
        
        self._is_initialized = True
        logger.info(
            f"Recommendation model initialized: {len(self.item_frequency)} items, "
            f"{self.total_orders} orders"
        )
    
    def get_item_probability(self, item: str) -> float:
        """
        Calculate P(item) - probability of an item being ordered.
        
        Args:
            item: The food item
            
        Returns:
            Probability of the item appearing in an order
        """
        return self.item_frequency[item] / self.total_orders if self.total_orders > 0 else 0.0
    
    def get_conditional_probability(self, item_j: str, given_item_i: str) -> float:
        """
        Calculate P(item_j | item_i).
        
        Args:
            item_j: The item we want to predict
            given_item_i: The item that is already ordered
            
        Returns:
            Conditional probability
        """
        if self.item_frequency[given_item_i] == 0:
            return 0.0
        return self.co_occurrence[given_item_i][item_j] / self.item_frequency[given_item_i]
    
    def get_combined_conditional_probability(self, candidate: str, given_items: Set[str]) -> float:
        """
        Calculate combined conditional probability given multiple items.
        
        Args:
            candidate: The candidate item to recommend
            given_items: Set of items already selected
            
        Returns:
            Combined conditional probability (average)
        """
        if not given_items:
            return self.get_item_probability(candidate)
        
        total_prob = sum(
            self.get_conditional_probability(candidate, item)
            for item in given_items
        )
        return total_prob / len(given_items)
    
    def recommend(self, n: int = 3, already_ordered: list[str] = None) -> list[str]:
        """
        Recommend n food items based on conditional probability.
        
        Args:
            n: Number of items to recommend
            already_ordered: List of items already ordered by the customer
            
        Returns:
            List of recommended items
        """
        if not self._is_initialized:
            self.initialize()
            
        if already_ordered is None:
            already_ordered = []
        
        recommendations = []
        selected: Set[str] = set(already_ordered)
        all_items = set(self.item_frequency.keys())
        
        for _ in range(n):
            candidates = all_items - selected
            
            if not candidates:
                break
            
            best_item = None
            best_prob = -1.0
            
            for candidate in candidates:
                if selected:
                    prob = self.get_combined_conditional_probability(candidate, selected)
                else:
                    prob = self.get_item_probability(candidate)
                
                if prob > best_prob:
                    best_prob = prob
                    best_item = candidate
            
            if best_item:
                recommendations.append(best_item)
                selected.add(best_item)
        
        logger.debug(f"Generated {len(recommendations)} recommendations for {already_ordered}")
        return recommendations
    
    @property
    def is_ready(self) -> bool:
        """Check if the service is ready."""
        return self._is_initialized


# Cache for recommendation services per restaurant
_recommendation_services: dict[str, RecommendationService] = {}


def get_recommendation_service(restaurant_id: str) -> RecommendationService:
    """
    Get or create a recommendation service for a specific restaurant.
    
    Fetches order history from SQLite database and caches the service.
    
    Args:
        restaurant_id: The restaurant ID to get recommendations for
        
    Returns:
        RecommendationService instance for the restaurant
        
    Raises:
        ValueError: If no order history found for the restaurant
    """
    global _recommendation_services
    
    # Return cached service if available
    if restaurant_id in _recommendation_services:
        logger.debug(f"Using cached recommendation service for {restaurant_id}")
        return _recommendation_services[restaurant_id]
    
    # Fetch order history from database
    order_history = get_order_history_from_db(restaurant_id)
    
    if not order_history:
        raise ValueError(f"No order history found for restaurant: {restaurant_id}")
    
    # Create and cache the service
    service = RecommendationService(order_history, restaurant_id)
    service.initialize()
    _recommendation_services[restaurant_id] = service
    
    logger.info(f"Created new recommendation service for restaurant {restaurant_id}")
    return service


def clear_recommendation_cache(restaurant_id: str = None) -> None:
    """
    Clear the recommendation service cache.
    
    Args:
        restaurant_id: If provided, only clear cache for this restaurant.
                      If None, clear all cached services.
    """
    global _recommendation_services
    
    if restaurant_id:
        if restaurant_id in _recommendation_services:
            del _recommendation_services[restaurant_id]
            logger.info(f"Cleared recommendation cache for {restaurant_id}")
    else:
        _recommendation_services.clear()
        logger.info("Cleared all recommendation caches")
