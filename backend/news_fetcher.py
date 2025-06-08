import os
import requests
import hashlib
from typing import List, Dict, Optional
from datetime import datetime
from database import DatabaseManager

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
    
    def fetch_by_keyword(self, keyword: str, limit: int = 10) -> List[Dict]:
        """Fetch articles by keyword search."""
        params = {
            "search": keyword,
            "limit": limit,
            "language": "en"
        }
        
        data = self._make_request("all", params)
        if not data or "data" not in data:
            return []
        
        return self._process_articles(data["data"])
    
    def fetch_by_category(self, category: str, limit: int = 10) -> List[Dict]:
        """Fetch articles by category."""
        params = {
            "categories": category,
            "limit": limit,
            "language": "en"
        }
        
        data = self._make_request("all", params)
        if not data or "data" not in data:
            return []
        
        return self._process_articles(data["data"])
    
    def fetch_general(self, limit: int = 10) -> List[Dict]:
        """Fetch general trending news."""
        params = {
            "limit": limit,
            "language": "en"
        }
        
        data = self._make_request("top", params)
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
                "keywords": ", ".join(keywords)
            }
            
            processed.append(processed_article)
        
        return processed
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Simple keyword extraction from text."""
        if not text:
            return []
        
        # Simple stopwords to filter out
        stopwords = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
            "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", 
            "has", "had", "do", "does", "did", "will", "would", "could", "should"
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
    
    def fetch_personalized_articles(self, user_keywords: List[str], limit: int = 10) -> List[Dict]:
        """Fetch articles based on user preferences."""
        all_articles = []
        
        for keyword in user_keywords:
            articles = self.api.fetch_by_keyword(keyword, limit=3)
            all_articles.extend(articles)
        
        # Store articles in database
        for article in all_articles:
            self.db.insert_article(
                article["id"],
                article["title"],
                article["content"],
                article["url"],
                article["source"],
                article["keywords"]
            )
        
        return all_articles[:limit]
    
    def fetch_exploration_articles(self, categories: List[str], limit: int = 5) -> List[Dict]:
        """Fetch articles from exploration categories."""
        all_articles = []
        
        for category in categories:
            articles = self.api.fetch_by_category(category, limit=2)
            all_articles.extend(articles)
        
        # Store articles in database
        for article in all_articles:
            self.db.insert_article(
                article["id"],
                article["title"],
                article["content"],
                article["url"],
                article["source"],
                article["keywords"]
            )
        
        return all_articles[:limit]
    
    def fetch_general_articles(self, limit: int = 3) -> List[Dict]:
        """Fetch general trending articles."""
        articles = self.api.fetch_general(limit)
        
        # Store articles in database
        for article in articles:
            self.db.insert_article(
                article["id"],
                article["title"],
                article["content"],
                article["url"],
                article["source"],
                article["keywords"]
            )
        
        return articles
    
    def get_recommended_articles(self, limit: int = 20) -> List[Dict]:
        """Get recommended articles using 70/20/10 strategy."""
        # Get user's top keywords
        top_keywords = self.db.get_top_keywords(limit=5)
        
        articles = []
        
        # 70% personalized content
        if top_keywords:
            personalized = self.fetch_personalized_articles(top_keywords[:3], limit=14)
            articles.extend(personalized)
        
        # 20% exploration content
        exploration_categories = ["technology", "business", "science", "health", "sports"]
        exploration = self.fetch_exploration_articles(exploration_categories[:2], limit=4)
        articles.extend(exploration)
        
        # 10% general content
        general = self.fetch_general_articles(limit=2)
        articles.extend(general)
        
        # Remove duplicates and limit results
        seen_ids = set()
        unique_articles = []
        for article in articles:
            if article["id"] not in seen_ids:
                seen_ids.add(article["id"])
                unique_articles.append(article)
                if len(unique_articles) >= limit:
                    break
        
        return unique_articles


# For testing
if __name__ == "__main__":
    fetcher = NewsFetcher()
    articles = fetcher.get_recommended_articles(limit=10)
    for article in articles:
        print(f"- {article['title']}")