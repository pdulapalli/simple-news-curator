import os
import json
import requests
import hashlib
from typing import List, Dict, Optional
from database import DatabaseManager

NEWS_KIND = "top"
EXCLUDED_CATEGORIES = ["entertainment", "travel", "politics", "general", "sports"]


def load_trusted_domains():
    """Load trusted domains from news_sources.json file."""
    try:
        with open("news_sources.json", "r") as f:
            data = json.load(f)
            # Extract unique domains from the sources
            domains = set()
            for source in data.get("sources", []):
                domain = source.get("domain")
                if domain:
                    domains.add(domain)
            return list(domains)
    except FileNotFoundError:
        print("Warning: news_sources.json not found, using empty domain list")
        return []
    except Exception as e:
        print(f"Error loading trusted domains: {e}")
        return []


TRUSTED_DOMAINS = load_trusted_domains()


class NewsAPI:
    """Interface to TheNewsAPI.com for fetching articles."""

    def __init__(self):
        self.api_key = os.getenv("THENEWSAPI_KEY")
        self.base_url = "https://api.thenewsapi.com/v1/news"

        if not self.api_key:
            raise ValueError("THENEWSAPI_KEY environment variable is required")

    def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Make API request with error handling."""
        params["api_token"] = self.api_key

        try:
            response = requests.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None

    def fetch_by_keyword(self, keywords: List[str], limit: int = 10) -> List[Dict]:
        """Fetch articles by keyword search using OR logic."""
        search_query = " | ".join(keywords)
        params = {
            "search": search_query,
            "search_fields": "keywords,title,description",
            "limit": limit,
            "language": "en",
            "exclude_categories": ",".join(EXCLUDED_CATEGORIES),
            "sort": "relevance_score",
        }

        # Add trusted domains filter if available
        if TRUSTED_DOMAINS:
            params["domains"] = ",".join(TRUSTED_DOMAINS)

        data = self._make_request(NEWS_KIND, params)
        if not data or "data" not in data:
            return []

        return self._process_articles(data["data"])

    def fetch_by_category(self, category: str, limit: int = 10) -> List[Dict]:
        """Fetch articles by category."""
        params = {
            "categories": category,
            "limit": limit,
            "language": "en",
            "exclude_categories": ",".join(EXCLUDED_CATEGORIES),
        }

        # Add trusted domains filter if available
        if TRUSTED_DOMAINS:
            params["domains"] = ",".join(TRUSTED_DOMAINS)

        data = self._make_request(NEWS_KIND, params)
        if not data or "data" not in data:
            return []

        return self._process_articles(data["data"])

    def fetch_general(self, limit: int = 10) -> List[Dict]:
        """Fetch general trending news."""
        params = {
            "limit": limit,
            "language": "en",
            "exclude_categories": ",".join(EXCLUDED_CATEGORIES),
        }

        # Add trusted domains filter if available
        if TRUSTED_DOMAINS:
            params["domains"] = ",".join(TRUSTED_DOMAINS)

        data = self._make_request(NEWS_KIND, params)
        if not data or "data" not in data:
            return []

        return self._process_articles(data["data"])

    def _process_articles(self, articles: List[Dict]) -> List[Dict]:
        """Process and normalize article data."""
        processed = []

        for article in articles:
            # Generate unique ID from URL
            article_id = hashlib.md5(article.get("url", "").encode()).hexdigest()

            # Extract keywords from title (simple approach)
            title = article.get("title", "")
            keywords = self._extract_keywords(title)

            processed_article = {
                "id": article_id,
                "title": title,
                "content": article.get("description", ""),
                "url": article.get("url", ""),
                "source": article.get("source", ""),
                "categories": article.get("categories", ""),
                "keywords": ", ".join(keywords),
                "relevance_score": article.get("relevance_score"),
                "published_at": article.get("published_at"),
            }

            processed.append(processed_article)

        return processed

    def _extract_keywords(self, text: str) -> List[str]:
        """Simple keyword extraction from text."""
        if not text:
            return []

        # Simple stopwords to filter out
        stopwords = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
        }

        # Basic tokenization and filtering
        words = text.lower().replace(",", "").replace(".", "").replace("'", "").split()
        keywords = [word for word in words if len(word) > 2 and word not in stopwords]

        # Return first 5 keywords
        return keywords[:5]


class NewsFetcher:
    """Main service for fetching and storing news articles."""

    def __init__(self):
        self.api = NewsAPI()
        self.db = DatabaseManager()

    def _save_articles(self, articles: List[Dict]):
        """Helper method to save articles to database."""
        for article in articles:
            self.db.insert_article(
                article["id"],
                article["title"],
                article["content"],
                article["url"],
                article["source"],
                article["published_at"],
                article["keywords"],
            )

    def fetch_personalized_articles(
        self, user_keywords: List[str], limit: int = 10
    ) -> List[Dict]:
        """Fetch articles based on user preferences."""
        articles = self.api.fetch_by_keyword(user_keywords, limit=limit)
        self._save_articles(articles)
        return articles

    def fetch_general_articles(self, limit: int = 3) -> List[Dict]:
        """Fetch general trending articles."""
        articles = self.api.fetch_general(limit)
        self._save_articles(articles)
        return articles
