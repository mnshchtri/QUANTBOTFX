import React, { useEffect, useState } from 'react';

interface NewsPanelProps {
  symbol: string;
}

interface NewsArticle {
  title: string;
  summary: string;
  source: string;
  published_at: string;
  url: string;
  sentiment: 'positive' | 'negative' | 'neutral';
}

const NewsPanel: React.FC<NewsPanelProps> = ({ symbol }) => {
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchNews = async () => {
      try {
        // No mock data - news functionality not implemented yet
        console.log('News functionality not implemented yet');
        setNews([]);
      } catch (error) {
        console.error('Error fetching news:', error);
        setNews([]);
      }
    };

    fetchNews();
  }, [symbol]);

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return 'text-green-600 bg-green-100';
      case 'negative':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) {
      return `${diffMins}m ago`;
    } else if (diffHours < 24) {
      return `${diffHours}h ago`;
    } else {
      return `${diffDays}d ago`;
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md border border-gray-200">
        <div className="p-4">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Market News</h3>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/4"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200">
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Market News</h3>
        
        {news.length === 0 ? (
          <p className="text-gray-500 text-center py-4">No news available</p>
        ) : (
          <div className="space-y-4">
            {news.map((article, index) => (
              <div key={index} className="border-b border-gray-100 pb-4 last:border-b-0">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-medium text-gray-900 text-sm leading-tight">
                    {article.title}
                  </h4>
                  <span className={`text-xs px-2 py-1 rounded-full ${getSentimentColor(article.sentiment)}`}>
                    {article.sentiment}
                  </span>
                </div>
                
                <p className="text-xs text-gray-600 mb-2 line-clamp-2">
                  {article.summary}
                </p>
                
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>{article.source}</span>
                  <span>{formatTime(article.published_at)}</span>
                </div>
              </div>
            ))}
          </div>
        )}
        
        <div className="mt-4 text-center">
          <button className="text-sm text-blue-600 hover:text-blue-800">
            View More News →
          </button>
        </div>
      </div>
    </div>
  );
};

export default NewsPanel; 