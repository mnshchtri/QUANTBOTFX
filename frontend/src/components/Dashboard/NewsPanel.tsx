import React from 'react';
import { HashtagIcon, FireIcon } from '@heroicons/react/24/outline';

interface NewsItem {
  id: string;
  title: string;
  source: string;
  timestamp: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  impact: 'high' | 'medium' | 'low';
}

const NewsPanel: React.FC<{ symbol: string }> = ({ symbol }) => {
  // Mock data for UI demo
  const mockNews: NewsItem[] = [
    { id: '1', title: 'BOJ Governor Hints at Potential Rate Hike in Q3', source: 'Reuters', timestamp: '2m ago', sentiment: 'positive', impact: 'high' },
    { id: '2', title: 'GBP Faces Pressure Amid Slower Wage Growth Data', source: 'Bloomberg', timestamp: '15m ago', sentiment: 'negative', impact: 'medium' },
    { id: '3', title: 'OANDA Market Sentiment: 65% Long on GBP/JPY', source: 'OANDA', timestamp: '1h ago', sentiment: 'neutral', impact: 'low' },
  ];

  return (
    <div className="glass rounded-2xl overflow-hidden flex flex-col h-[350px]">
      <div className="p-4 border-b border-[var(--border-subtle)] flex items-center justify-between">
        <div className="panel-header mb-0 flex items-center gap-2">
          <HashtagIcon className="w-4 h-4" />
          <span>Macro Intel</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-4">
        {mockNews.map((item) => (
          <div key={item.id} className="group cursor-pointer">
            <div className="flex justify-between items-start mb-1">
              <span className="text-[10px] font-bold text-blue-400 uppercase tracking-tighter opacity-70 group-hover:opacity-100 transition-opacity">{item.source}</span>
              <span className="text-[10px] text-[var(--text-muted)]">{item.timestamp}</span>
            </div>
            <h4 className="text-xs font-medium text-[var(--text-main)] group-hover:text-blue-400 transition-colors leading-relaxed">
              {item.title}
            </h4>
            <div className="flex gap-2 mt-2">
              <div className={`text-[9px] px-1.5 py-0.5 rounded-full font-bold uppercase ${
                item.impact === 'high' ? 'bg-red-500/10 text-red-400 border border-red-500/20 shadow-[0_0_8px_rgba(239,68,68,0.1)]' : 'bg-orange-500/10 text-orange-400 border border-orange-500/10'
              }`}>
                {item.impact} impact
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="p-3 bg-red-500/5 border-t border-red-500/10 flex items-center gap-2">
        <FireIcon className="w-3 h-3 text-red-400 animate-pulse" />
        <span className="text-[10px] text-red-400 font-bold uppercase tracking-widest">Volatility Alert: High Impact News in 45m</span>
      </div>
    </div>
  );
};

export default NewsPanel;