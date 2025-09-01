import React, { useEffect, useState } from 'react';

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
      try {
        const response = await fetch(`/api/market-info?symbol=${symbol}`);
        if (response.ok) {
          const data = await response.json();
          setMarketData({
            symbol: data.symbol,
            current_price: data.price,
            change: data.change,
            change_percent: data.changePercent,
            high: data.high,
            low: data.low,
            volume: data.volume,
            spread: data.spread,
          });
        } else {
          // Remove fallback to mock data - fail properly if API is not available
          setMarketData(null);
        }
      } catch (error) {
        console.error('Error fetching market info:', error);
      }
    };

    fetchMarketInfo();
  }, [symbol]);

  if (loading) {
    return (
      <div className="bg-white p-4 rounded-lg shadow-md border border-gray-200">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
          <div className="h-6 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>
    );
  }

  if (!marketData) {
    return (
      <div className="bg-white p-4 rounded-lg shadow-md border border-gray-200">
        <p className="text-gray-500">No market data available</p>
      </div>
    );
  }

  const isPositive = marketData.change >= 0;

  return (
    <div className="bg-white p-4 rounded-lg shadow-md border border-gray-200">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold text-gray-800">{marketData.symbol}</h3>
        <span className="text-sm text-gray-600">{timeframe}</span>
      </div>

      <div className="space-y-3">
        {/* Current Price */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Current Price:</span>
          <span className="text-xl font-bold text-gray-900">
            {marketData.current_price.toFixed(4)}
          </span>
        </div>

        {/* Change */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Change:</span>
          <div className="flex items-center space-x-2">
            <span className={`text-sm font-medium ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {isPositive ? '+' : ''}{marketData.change.toFixed(4)}
            </span>
            <span className={`text-xs px-2 py-1 rounded ${isPositive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
              {isPositive ? '+' : ''}{marketData.change_percent.toFixed(2)}%
            </span>
          </div>
        </div>

        {/* High/Low */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <span className="text-sm text-gray-600">High:</span>
            <div className="text-sm font-medium text-green-600">
              {marketData.high.toFixed(4)}
            </div>
          </div>
          <div>
            <span className="text-sm text-gray-600">Low:</span>
            <div className="text-sm font-medium text-red-600">
              {marketData.low.toFixed(4)}
            </div>
          </div>
        </div>

        {/* Volume & Spread */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <span className="text-sm text-gray-600">Volume:</span>
            <div className="text-sm font-medium text-gray-900">
              {marketData.volume.toLocaleString()}
            </div>
          </div>
          <div>
            <span className="text-sm text-gray-600">Spread:</span>
            <div className="text-sm font-medium text-gray-900">
              {marketData.spread.toFixed(4)}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarketInfo; 