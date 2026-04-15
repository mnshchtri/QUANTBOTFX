import React from 'react';
import { ChartBarIcon, ArrowTrendingUpIcon, ArrowTrendingDownIcon } from '@heroicons/react/24/outline';

interface WatchlistProps {
  currentSymbol: string;
  onSelectSymbol: (symbol: string) => void;
  symbols: string[];
}

const Watchlist: React.FC<WatchlistProps> = ({ currentSymbol, onSelectSymbol, symbols }) => {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="panel-header flex items-center gap-2">
          <ChartBarIcon className="w-4 h-4 text-blue-400" />
          Market Watchlist
        </div>
        <span className="text-[9px] font-black text-blue-500/50 uppercase tracking-widest">Live</span>
      </div>

      <div className="space-y-1">
        {symbols.map((sym) => {
          const isSelected = currentSymbol === sym;
          // Mock data for variation
          const change = (Math.random() * 0.5 * (Math.random() > 0.5 ? 1 : -1)).toFixed(2);
          const price = (1.0 + Math.random() * 150).toFixed(4);
          const isPositive = parseFloat(change) >= 0;

          return (
            <div 
              key={sym}
              onClick={() => onSelectSymbol(sym)}
              className={`group flex items-center justify-between px-3 py-1.5 rounded-lg cursor-pointer transition-all duration-300 ${
                isSelected 
                ? 'bg-blue-600/30 border border-blue-500/50 shadow-[0_4px_15px_rgba(37,99,235,0.15)]' 
                : 'hover:bg-white/5 border border-transparent'
              }`}
            >
              <div className="flex flex-col">
                <span className={`text-xs font-black tracking-tight uppercase truncate max-w-[120px] ${isSelected ? 'text-white' : 'text-[var(--text-main)] group-hover:text-blue-400'}`}>
                  {sym.replace(/_/g, ' / ')}
                </span>
                <span className={`text-[9px] font-bold ${isSelected ? 'text-blue-100' : 'text-[var(--text-muted)]'}`}>
                  Forex • Spot
                </span>
              </div>

              <div className="flex flex-col items-end">
                <span className={`text-xs font-mono font-bold ${isSelected ? 'text-white' : 'text-[var(--text-main)]'}`}>
                  {price}
                </span>
                <div className="flex items-center gap-1">
                  {isPositive ? (
                    <ArrowTrendingUpIcon className={`w-2.5 h-2.5 ${isSelected ? 'text-blue-200' : 'text-green-400'}`} />
                  ) : (
                    <ArrowTrendingDownIcon className={`w-2.5 h-2.5 ${isSelected ? 'text-red-200' : 'text-red-400'}`} />
                  )}
                  <span className={`text-[10px] font-black ${
                    isSelected ? 'text-white' : (isPositive ? 'text-green-400' : 'text-red-400')
                  }`}>
                    {isPositive ? '+' : ''}{change}%
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <button className="w-full py-2 border border-dashed border-[var(--border-subtle)] rounded-xl text-[10px] font-black text-[var(--text-muted)] uppercase tracking-plus hover:border-blue-500/50 hover:text-blue-400 transition-all mt-2">
        + Add Instrument
      </button>
    </div>
  );
};

export default Watchlist;
