from typing import List, Dict
from datetime import datetime
from database import DatabaseManager


class PreferenceEngine:
    """Manages user preferences and learning from reactions."""

    def __init__(self):
        self.db = DatabaseManager()
        self.weight_adjustment = 0.1  # Amount to adjust weights by
        self.max_weight = 1.0
        self.min_weight = -1.0

    def process_reaction(self, article_id: str, reaction: str):
        """Process user reaction and update preferences."""
        # Record the reaction
        self.db.insert_reaction(article_id, reaction)

        # Get article to extract keywords
        article = self.db.get_article(article_id)
        if not article or not article.get("keywords"):
            return

        # Extract keywords from article
        keywords = [kw.strip() for kw in article["keywords"].split(",") if kw.strip()]

        # Update preference weights
        adjustment = (
            self.weight_adjustment if reaction == "like" else -self.weight_adjustment
        )

        for keyword in keywords:
            current_weight = self.db.get_preference_weight(keyword)
            new_weight = max(
                self.min_weight, min(self.max_weight, current_weight + adjustment)
            )
            self.db.update_preference_weight(keyword, new_weight)

    def get_user_preferences(self) -> List[Dict]:
        """Get all user preferences ordered by weight."""
        return self.db.get_all_preferences()

    def get_positive_keywords(self, limit: int = 5) -> List[str]:
        """Get keywords with positive weights."""
        return self.db.get_top_keywords(limit)

    def get_preference_summary(self) -> Dict:
        """Get summary of user preferences for debugging."""
        all_prefs = self.get_user_preferences()

        positive_prefs = [p for p in all_prefs if p["weight"] > 0]
        negative_prefs = [p for p in all_prefs if p["weight"] < 0]

        return {
            "total_preferences": len(all_prefs),
            "positive_count": len(positive_prefs),
            "negative_count": len(negative_prefs),
            "top_positive": positive_prefs[:5],
            "top_negative": negative_prefs[:5],
        }

    def reset_preferences(self):
        """Clear all user preferences."""
        self.db.clear_all_preferences()

    def get_exploration_categories(self) -> List[str]:
        """Get categories for exploration (simple rotation)."""
        all_categories = ["technology", "business", "science", "health", "sports"]

        # For now, return all categories.
        # Could be enhanced to track which categories were recently used
        return all_categories

    def bootstrap_preferences(self):
        """Bootstrap with some default preferences for cold start."""
        default_keywords = [
            ("science", 0.2),
            ("business", 0.2),
            ("current_events", 0.1),
            ("technology", 0.1),
            ("health", 0.1),
        ]

        # Only add if no preferences exist
        if not self.get_user_preferences():
            for keyword, weight in default_keywords:
                self.db.update_preference_weight(keyword, weight)


# For testing
if __name__ == "__main__":
    engine = PreferenceEngine()

    # Test bootstrap
    engine.bootstrap_preferences()

    # Show current preferences
    prefs = engine.get_preference_summary()
    print(f"Current preferences: {prefs}")

    # Show top keywords
    top_keywords = engine.get_positive_keywords()
    print(f"Top keywords: {top_keywords}")
