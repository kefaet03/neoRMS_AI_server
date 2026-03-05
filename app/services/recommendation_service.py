"""
Food Recommendation Service.
Uses conditional probability to recommend food items based on order history.
"""

import logging
from collections import defaultdict
from typing import Set

logger = logging.getLogger(__name__)


# Sample order history for the recommendation engine
# In production, this would be loaded from a database
# DEFAULT_ORDER_HISTORY = {
#     "ORD1001": ["Kacchi Biryani", "Borhani", "Chicken Roast"],
#     "ORD1002": ["Beef Tehari", "Chicken Reshmi Kebab", "Firni"],
#     "ORD1003": ["Butter Chicken", "Garlic Naan", "Chicken Tikka Masala", "Mango Lassi"],
#     "ORD1004": ["Morog Polao", "Beef Bhuna", "Plain Rice", "Salad"],
#     "ORD1005": ["Shorshe Ilish", "Steamed Rice", "Dal", "Begun Bharta"],
#     "ORD1006": ["Chicken Burger", "French Fries", "Coke"],
#     "ORD1007": ["BBQ Chicken Pizza", "Chicken Wings", "Cold Coffee"],
#     "ORD1008": ["Beef Steak", "Mashed Potato", "Sauteed Vegetables", "Lemonade"],
#     "ORD1009": ["Chicken Alfredo Pasta", "Garlic Bread", "Chocolate Milkshake"],
#     "ORD1010": ["Falooda", "Fuchka", "Chotpoti"],
#     "ORD1011": ["Mixed Fried Rice", "Thai Soup", "Chicken Fry"],
#     "ORD1012": ["Grilled Chicken Sandwich", "Onion Rings", "Iced Tea"],
#     "ORD1013": ["Beef Kala Bhuna", "Tandoori Roti", "Borhani"],
#     "ORD1014": ["Prawn Malai Curry", "Polao Rice", "Green Salad"],
#     "ORD1015": ["Cheese Pasta", "BBQ Chicken Wrap", "Mocha Coffee"],
# }

DEFAULT_ORDER_HISTORY = {
    "ORD1001": ["001", "002", "014"],  # Kacchi Biryani, Borhani, Salad
    "ORD1002": ["008", "007", "021"],  # Garlic Naan, Butter Chicken, Coke
    "ORD1003": ["025", "042", "045", "006"],  # Beef Steak, Tandoori Roti, Green Salad, Firni
    "ORD1004": ["019", "020", "021"],  # Chicken Burger, French Fries, Coke
    "ORD1005": ["011", "002", "014"],  # Morog Polao, Borhani, Salad
    "ORD1006": ["009", "008", "030"],  # Chicken Tikka Masala, Garlic Naan, Garlic Bread
    "ORD1007": ["004", "016", "017"],  # Beef Tehari, Steamed Rice, Dal
    "ORD1008": ["022", "039", "040"],  # BBQ Chicken Pizza, Onion Rings, Iced Tea
    "ORD1009": ["033", "034", "028"],  # Fuchka, Chotpoti, Lemonade
    "ORD1010": ["037", "020", "021"],  # Chicken Fry, French Fries, Coke
    "ORD1011": ["043", "044", "014"],  # Prawn Malai Curry, Polao Rice, Salad
    "ORD1012": ["029", "030", "031"],  # Chicken Alfredo Pasta, Garlic Bread, Chocolate Milkshake
    "ORD1013": ["041", "016", "017"],  # Beef Kala Bhuna, Steamed Rice, Dal
    "ORD1014": ["005", "001", "002"],  # Chicken Reshmi Kebab, Kacchi Biryani, Borhani
    "ORD1015": ["023", "020", "028"],  # Chicken Wings, French Fries, Lemonade
    "ORD1016": ["035", "036", "014"],  # Mixed Fried Rice, Thai Soup, Salad
    "ORD1017": ["047", "039", "048"],  # BBQ Chicken Wrap, Onion Rings, Mocha Coffee
    "ORD1018": ["015", "016", "017"],  # Shorshe Ilish, Steamed Rice, Dal
    "ORD1019": ["038", "020", "040"],  # Grilled Chicken Sandwich, French Fries, Iced Tea
    "ORD1020": ["032", "010"],  # Falooda, Mango Lassi
    "ORD1021": ["025", "026", "027"],  # Beef Steak, Mashed Potato, Sauteed Vegetables
    "ORD1022": ["007", "008", "014"],  # Butter Chicken, Garlic Naan, Salad
    "ORD1023": ["001", "002"],  # Kacchi Biryani, Borhani
    "ORD1024": ["019", "021"],  # Chicken Burger, Coke
    "ORD1025": ["011", "014"],  # Morog Polao, Salad
    "ORD1026": ["009", "030"],  # Chicken Tikka Masala, Garlic Bread
    "ORD1027": ["004", "017"],  # Beef Tehari, Dal
    "ORD1028": ["022", "040"],  # BBQ Chicken Pizza, Iced Tea
    "ORD1029": ["033", "028"],  # Fuchka, Lemonade
    "ORD1030": ["037", "021"],  # Chicken Fry, Coke
    "ORD1031": ["043", "044"],  # Prawn Malai Curry, Polao Rice
    "ORD1032": ["029", "031"],  # Chicken Alfredo Pasta, Chocolate Milkshake
    "ORD1033": ["041", "016"],  # Beef Kala Bhuna, Steamed Rice
    "ORD1034": ["005", "002"],  # Chicken Reshmi Kebab, Borhani
    "ORD1035": ["023", "028"],  # Chicken Wings, Lemonade
    "ORD1036": ["035", "014"],  # Mixed Fried Rice, Salad
    "ORD1037": ["047", "048"],  # BBQ Chicken Wrap, Mocha Coffee
    "ORD1038": ["015", "017"],  # Shorshe Ilish, Dal
    "ORD1039": ["038", "040"],  # Grilled Chicken Sandwich, Iced Tea
    "ORD1040": ["032", "006"],  # Falooda, Firni
    "ORD1041": ["025", "027"],  # Beef Steak, Sauteed Vegetables
    "ORD1042": ["007", "014"],  # Butter Chicken, Salad
    "ORD1043": ["001", "014"],  # Kacchi Biryani, Salad
    "ORD1044": ["019", "020"],  # Chicken Burger, French Fries
    "ORD1045": ["011", "002"],  # Morog Polao, Borhani
    "ORD1046": ["009", "008"],  # Chicken Tikka Masala, Garlic Naan
    "ORD1047": ["004", "016"],  # Beef Tehari, Steamed Rice
    "ORD1048": ["022", "039"],  # BBQ Chicken Pizza, Onion Rings
    "ORD1049": ["033", "034"],  # Fuchka, Chotpoti
    "ORD1050": ["037", "020", "021"]  # Chicken Fry, French Fries, Coke
}


class RecommendationService:
    """
    Probabilistic Food Recommendation Engine.
    
    Uses conditional probability P(item_j | item_i) to recommend
    food items based on what the customer has already ordered.
    """
    
    def __init__(self, order_history: dict = None):
        """
        Initialize the recommendation engine.
        
        Args:
            order_history: Dictionary mapping order IDs to list of items.
                          If None, uses default sample data.
        """
        self.order_history = order_history or DEFAULT_ORDER_HISTORY
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


# Singleton instance
_recommendation_service: RecommendationService | None = None


def get_recommendation_service() -> RecommendationService:
    """Get the singleton recommendation service instance."""
    global _recommendation_service
    if _recommendation_service is None:
        _recommendation_service = RecommendationService()
    return _recommendation_service
