import { useState, useEffect } from "react";
import type { Route } from "./+types/home";

interface Article {
  id: string;
  title: string;
  content: string;
  url: string;
  source: string;
  keywords: string;
  published_at: string;
}

export function meta({ }: Route.MetaArgs) {
  return [
    { title: "News curator" },
    { name: "description", content: "Your personalized news feed" },
  ];
}

function ArticleCard({ article, onReaction }: { article: Article; onReaction: (id: string, reaction: string) => void }) {
  const [reacting, setReacting] = useState(false);

  const handleReaction = async (reaction: string, event: React.MouseEvent) => {
    event.stopPropagation(); // Prevent card click when clicking reaction buttons
    setReacting(true);
    await onReaction(article.id, reaction);
    setReacting(false);
  };

  const handleCardClick = () => {
    window.open(article.url, '_blank', 'noopener,noreferrer');
  };

  const formatTimestamp = (timestamp: string) => {
    if (!timestamp) return '';

    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));

      if (diffInMinutes < 60) {
        return `${diffInMinutes}m ago`;
      } else if (diffInMinutes < 1440) { // 24 hours
        const hours = Math.floor(diffInMinutes / 60);
        return `${hours}h ago`;
      } else {
        const days = Math.floor(diffInMinutes / 1440);
        if (days < 7) {
          return `${days}d ago`;
        } else {
          return date.toLocaleDateString();
        }
      }
    } catch (error) {
      return '';
    }
  };

  return (
    <div
      className="bg-white rounded-lg shadow-md p-6 mb-4 cursor-pointer hover:shadow-lg transition-shadow duration-200 relative"
      onClick={handleCardClick}
    >
      {article.published_at && (
        <div className="absolute top-4 right-4 text-xs text-gray-400">
          {formatTimestamp(article.published_at)}
        </div>
      )}
      <h2 className="text-xl font-bold mb-2 text-gray-900 pr-16">{article.title}</h2>
      <p className="text-gray-600 mb-3">{article.content}</p>
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-500">
          <span className="font-medium">{article.source}</span>
          {article.keywords && (
            <span className="ml-2">• {article.keywords}</span>
          )}
        </div>
        <div className="flex gap-2">
          <button
            onClick={(e) => handleReaction('like', e)}
            disabled={reacting}
            className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
          >
            👍 Like
          </button>
          <button
            onClick={(e) => handleReaction('dislike', e)}
            disabled={reacting}
            className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-50"
          >
            👎 Dislike
          </button>
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchArticles = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/articles/recommended');
      if (!response.ok) {
        throw new Error('Failed to fetch articles');
      }
      const data = await response.json();
      setArticles(data.articles);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleReaction = async (articleId: string, reaction: string) => {
    try {
      const response = await fetch(`http://localhost:8000/articles/${articleId}/reaction`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ reaction }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit reaction');
      }

      // Optionally refresh articles to get updated recommendations
      await fetchArticles();
    } catch (err) {
      console.error('Error submitting reaction:', err);
    }
  };

  useEffect(() => {
    fetchArticles();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
          <div className="text-xl font-semibold text-gray-700">Loading your news...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-red-600">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">News for you</h1>
        <div className="max-w-4xl mx-auto">
          {articles.length === 0 ? (
            <div className="text-center text-gray-600">
              No articles found.
            </div>
          ) : (
            articles.map((article) => (
              <ArticleCard
                key={article.id}
                article={article}
                onReaction={handleReaction}
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
}
