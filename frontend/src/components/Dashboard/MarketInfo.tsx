import React, { useEffect, useState } from 'react';
import { ChartBarSquareIcon, ArrowTrendingUpIcon, ArrowTrendingDownIcon } from '@heroicons/react/24/solid';

interface MarketInfoProps {
  symbol: string;
  timeframe: string;
}

interface MarketData {
  symbol: string;
  current_price: number;
  change: number;
  change_percent: number;
  high: number;
  low: number;
  volume: number;
  spread: number;
}

const MarketInfo: React.FC<MarketInfoProps> = ({ symbol, timeframe }) => {
  const [marketData, setMarketData] = useState<MarketData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMarketInfo = async () => {
      setLoading(true);
      try {
        const response = await fetch(`/api/market-info?symbol=${symbol}`);
        if (response.ok) {
          const data = await response.json();
          setMarketData({
            symbol: data.symbol,
            current_price: data.current_price,
            change: data.change,
            change_percent: data.change_percent,
            high: data.high,
            low: data.low,
            volume: data.volume,
            spread: data.spread,
          });
        }
      } catch (error) {
        console.error('Error fetching market info:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMarketInfo();
    const interval = setInterval(fetchMarketInfo, 10000);
    return () => clearInterval(interval);
  }, [symbol]);

  if (loading && !marketData) {
    return (
      <div className="glass rounded-2xl p-6 h-[200px] animate-pulse flex flex-col gap-4">
        <div className="h-4 bg-white/5 rounded w-1/3" />
        <div className="h-10 bg-white/5 rounded w-full" />
        <div className="grid grid-cols-2 gap-4">
          <div className="h-8 bg-white/5 rounded" />
          <div className="h-8 bg-white/5 rounded" />
        </div>
      </div>
    );
  }

  if (!marketData) return null;

  const isPositive = marketData.change >= 0;

  return (
    <div className="glass rounded-2xl p-5 border border-[var(--border-subtle)] relative overflow-hidden group">
      <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
        <ChartBarSquareIcon className="w-16 h-16 text-white" />
      </div>

      <div className="flex items-center gap-2 mb-4">
        <div className={`w-2 h-2 rounded-full ${isPositive ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]' : 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]'}`} />
        <span className="panel-header mb-0">Market Highlights</span>
      </div>

      <div className="mb-6">
        <div className="text-[10px] text-[var(--text-muted)] font-bold uppercase tracking-wider mb-1">Live Price</div>
        <div className="flex items-baseline gap-3">
          <span className="text-3xl font-bold data-value tracking-tighter text-[var(--text-main)]">
            {marketData.current_price.toFixed(5)}
          </span>
          <div className={`flex items-center gap-1 text-sm font-bold ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
            {isPositive ? <ArrowTrendingUpIcon className="w-4 h-4" /> : <ArrowTrendingDownIcon className="w-4 h-4" />}
            <span>{isPositive ? '+' : ''}{marketData.change_percent.toFixed(2)}%</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="bg-[#ffffff03] rounded-xl p-3 border border-[var(--border-subtle)]">
          <div className="text-[9px] text-[var(--text-muted)] font-bold uppercase mb-1">24h High</div>
          <div className="text-sm font-bold data-value text-green-400">{marketData.high.toFixed(5)}</div>
        </div>
        <div className="bg-[#ffffff03] rounded-xl p-3 border border-[var(--border-subtle)]">
          <div className="text-[9px] text-[var(--text-muted)] font-bold uppercase mb-1">24h Low</div>
          <div className="text-sm font-bold data-value text-red-400">{marketData.low.toFixed(5)}</div>
        </div>
        <div className="bg-[#ffffff03] rounded-xl p-3 border border-[var(--border-subtle)]">
          <div className="text-[9px] text-[var(--text-muted)] font-bold uppercase mb-1">Spread</div>
          <div className="text-sm font-bold data-value text-blue-400">{(marketData.spread * 10).toFixed(1)} <span className="text-[8px] text-[var(--text-muted)]">PIPS</span></div>
        </div>
        <div className="bg-[#ffffff03] rounded-xl p-3 border border-[var(--border-subtle)]">
          <div className="text-[9px] text-[var(--text-muted)] font-bold uppercase mb-1">Volume</div>
          <div className="text-sm font-bold data-value text-[var(--text-main)]">{(marketData.volume / 1000).toFixed(1)}K</div>
        </div>
      </div>
    </div>
  );
};

export default MarketInfo;