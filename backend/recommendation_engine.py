from typing import List, Dict
from news_fetcher import NewsFetcher
from preference_engine import PreferenceEngine


class RecommendationEngine:
    """Main recommendation engine implementing the 70/20/10 strategy."""

    def __init__(self):
        self.news_fetcher = NewsFetcher()
        self.preference_engine = PreferenceEngine()

    def get_recommendations(self, limit: int = 20) -> List[Dict]:
        """Get personalized article recommendations using 70/20/10 strategy."""

        # Bootstrap preferences if none exist (cold start)
        if not self.preference_engine.get_user_preferences():
            self.preference_engine.bootstrap_preferences()

        # Get user's top keywords for personalized content
        top_keywords = self.preference_engine.get_positive_keywords(limit=5)

        articles = []

        # 70% personalized content (14 out of 20 articles)
        personalized_limit = int(limit * 0.7)
        if top_keywords:
            personalized_articles = self.news_fetcher.fetch_personalized_articles(
                top_keywords[:3], limit=personalized_limit
            )
            articles.extend(personalized_articles)

        # 20% exploration content (4 out of 20 articles)
        exploration_limit = int(limit * 0.2)
        exploration_categories = self.preference_engine.get_exploration_categories()[:2]
        exploration_articles = self.news_fetcher.fetch_exploration_articles(
            exploration_categories, limit=exploration_limit
        )
        articles.extend(exploration_articles)

        # 10% general trending content (2 out of 20 articles)
        general_limit = limit - len(articles)
        general_articles = self.news_fetcher.fetch_general_articles(limit=general_limit)
        articles.extend(general_articles)

        # Remove duplicates while preserving order
        seen_ids = set()
        unique_articles = []
        for article in articles:
            if article["id"] not in seen_ids:
                seen_ids.add(article["id"])
                unique_articles.append(article)
                if len(unique_articles) >= limit:
                    break

        return unique_articles

    def process_user_feedback(self, article_id: str, reaction: str):
        """Process user feedback and update preferences."""
        if reaction not in ["like", "dislike"]:
            raise ValueError("Reaction must be 'like' or 'dislike'")

        self.preference_engine.process_reaction(article_id, reaction)

    def get_user_profile(self) -> Dict:
        """Get user preference profile for debugging/display."""
        return self.preference_engine.get_preference_summary()

    def reset_user_data(self):
        """Reset all user preferences and reactions."""
        self.preference_engine.reset_preferences()


# For testing
if __name__ == "__main__":
    engine = RecommendationEngine()

    print("Getting recommendations...")
    recommendations = engine.get_recommendations(limit=10)

    print(f"\nFound {len(recommendations)} articles:")
    for i, article in enumerate(recommendations, 1):
        print(f"{i}. {article['title'][:80]}...")
        print(f"   Source: {article['source']}")
        print(f"   Keywords: {article['keywords']}")
        print()

    print("\nUser profile:")
    profile = engine.get_user_profile()
    print(profile)
