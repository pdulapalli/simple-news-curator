import sqlite3
from typing import List, Dict, Optional

DATABASE_PATH = "news_curator.db"


def init_database():
    """Initialize the SQLite database with required tables."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Articles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT,
            url TEXT NOT NULL,
            source TEXT,
            fetch_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            keywords TEXT,
            published_at TEXT
        )
    """)

    # Preferences table (keyword weights)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preferences (
            keyword TEXT PRIMARY KEY,
            weight REAL NOT NULL DEFAULT 0.0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # User reactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_reactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id TEXT NOT NULL,
            reaction TEXT NOT NULL CHECK (reaction IN ('like', 'dislike')),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (article_id) REFERENCES articles (id)
        )
    """)

    conn.commit()
    conn.close()


def get_connection():
    """Get a database connection."""
    return sqlite3.connect(DATABASE_PATH)


class DatabaseManager:
    """Database operations manager."""

    @staticmethod
    def insert_article(
        article_id: str,
        title: str,
        content: str,
        url: str,
        source: str,
        published_at: str,
        keywords: str = "",
    ):
        """Insert a new article into the database."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO articles (id, title, content, url, source, published_at, keywords)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (article_id, title, content, url, source, published_at, keywords),
        )

        conn.commit()
        conn.close()

    @staticmethod
    def get_article(article_id: str) -> Optional[Dict]:
        """Get an article by ID."""
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    @staticmethod
    def insert_reaction(article_id: str, reaction: str):
        """Insert a user reaction (like/dislike) for an article."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO user_reactions (article_id, reaction)
            VALUES (?, ?)
        """,
            (article_id, reaction),
        )

        conn.commit()
        conn.close()

    @staticmethod
    def get_preference_weight(keyword: str) -> float:
        """Get the weight for a specific keyword preference."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT weight FROM preferences WHERE keyword = ?", (keyword,))
        row = cursor.fetchone()
        conn.close()

        return row[0] if row else 0.0

    @staticmethod
    def update_preference_weight(keyword: str, weight: float):
        """Update or insert a keyword preference weight."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO preferences (keyword, weight, last_updated)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """,
            (keyword, weight),
        )

        conn.commit()
        conn.close()

    @staticmethod
    def get_all_preferences() -> List[Dict]:
        """Get all user preferences."""
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM preferences ORDER BY weight DESC")
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    @staticmethod
    def get_top_keywords(limit: int = 5) -> List[str]:
        """Get top positive keywords by weight."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT keyword FROM preferences
            WHERE weight > 0
            ORDER BY weight DESC
            LIMIT ?
        """,
            (limit,),
        )

        rows = cursor.fetchall()
        conn.close()

        return [row[0] for row in rows]

    @staticmethod
    def clear_all_preferences():
        """Clear all user preferences (for reset functionality)."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM preferences")
        cursor.execute("DELETE FROM user_reactions")

        conn.commit()
        conn.close()


# Initialize database when module is imported
if __name__ == "__main__":
    init_database()
    print("Database initialized successfully!")
