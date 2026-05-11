import React from 'react';
import { ChartBarIcon, ArrowTrendingUpIcon, ArrowTrendingDownIcon } from '@heroicons/react/24/outline';

interface WatchlistProps {
  currentSymbol: string;
  onSelectSymbol: (symbol: string) => void;
  symbols: string[];
}

const Watchlist: React.FC<WatchlistProps> = ({ currentSymbol, onSelectSymbol, symbols }) => {
  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-center justify-between px-1">
        <div className="flex items-center gap-2.5 text-[11px] font-black uppercase tracking-[0.2em] text-slate-900">
          <ChartBarIcon className="w-4 h-4 text-blue-600" />
          Market Watchlist
        </div>
        <span className="text-[9px] font-black text-blue-600 px-2 py-0.5 bg-blue-50 rounded-md uppercase tracking-widest">Live</span>
      </div>

      <div className="space-y-1.5">
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
              className={`group flex items-center justify-between px-4 py-3 rounded-2xl cursor-pointer transition-all duration-300 border ${
                isSelected 
                ? 'bg-blue-600 border-blue-600 shadow-lg shadow-blue-600/20' 
                : 'bg-white border-slate-50 hover:border-blue-100 hover:shadow-md hover:shadow-slate-200/50'
              }`}
            >
              <div className="flex flex-col">
                <span className={`text-[11px] font-black tracking-tight uppercase truncate max-w-[120px] ${isSelected ? 'text-white' : 'text-slate-900 group-hover:text-blue-600'}`}>
                  {sym.replace(/_/g, ' / ')}
                </span>
                <span className={`text-[9px] font-bold ${isSelected ? 'text-blue-100' : 'text-slate-400'}`}>
                  Forex • Spot
                </span>
              </div>

              <div className="flex flex-col items-end">
                <span className={`text-[11px] font-mono font-bold ${isSelected ? 'text-white' : 'text-slate-900'}`}>
                  {price}
                </span>
                <div className="flex items-center gap-1.5">
                  {isPositive ? (
                    <ArrowTrendingUpIcon className={`w-3 h-3 ${isSelected ? 'text-blue-200' : 'text-emerald-500'}`} />
                  ) : (
                    <ArrowTrendingDownIcon className={`w-3 h-3 ${isSelected ? 'text-blue-200' : 'text-rose-500'}`} />
                  )}
                  <span className={`text-[10px] font-black ${
                    isSelected ? 'text-white' : (isPositive ? 'text-emerald-500' : 'text-rose-500')
                  }`}>
                    {isPositive ? '+' : ''}{change}%
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <button className="w-full py-3 border-2 border-dashed border-slate-100 rounded-2xl text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] hover:border-blue-200 hover:text-blue-600 hover:bg-blue-50 transition-all mt-2">
        + Add Instrument
      </button>
    </div>
  );
};

export default Watchlist;
