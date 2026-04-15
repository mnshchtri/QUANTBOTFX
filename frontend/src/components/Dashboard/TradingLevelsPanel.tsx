import React, { useState, useEffect } from 'react';
import tradingLevelsService, { TradingLevel } from '../../services/tradingLevelsService';
import { QueueListIcon, PlusCircleIcon } from '@heroicons/react/24/outline';

interface TradingLevelsPanelProps {
  symbol: string;
  timeframe: string;
}

const TradingLevelsPanel: React.FC<TradingLevelsPanelProps> = ({ symbol, timeframe }) => {
  const [levels, setLevels] = useState<TradingLevel[]>([]);

  useEffect(() => {
    const unsubscribe = tradingLevelsService.subscribe(() => {
      setLevels(tradingLevelsService.getMultiTimeframeLevels(symbol));
    });
    setLevels(tradingLevelsService.getMultiTimeframeLevels(symbol));
    return unsubscribe;
  }, [symbol]);

  return (
    <div className="glass rounded-2xl overflow-hidden flex flex-col h-[400px]">
      <div className="p-4 border-b border-[var(--border-subtle)] flex items-center justify-between">
        <div className="panel-header mb-0 flex items-center gap-2">
          <QueueListIcon className="w-4 h-4" />
          <span>Key Price Levels</span>
        </div>
        <button className="text-[var(--text-muted)] hover:text-white transition-colors">
          <PlusCircleIcon className="w-5 h-5" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        <table className="w-full text-left border-collapse">
          <thead className="sticky top-0 bg-[var(--bg-surface)] z-10">
            <tr className="border-b border-[var(--border-subtle)]">
              <th className="px-4 py-3 text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider">Level</th>
              <th className="px-4 py-3 text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider">Price</th>
              <th className="px-4 py-3 text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider">TF</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--border-subtle)]">
            {levels.map((level, idx) => (
              <tr key={idx} className="hover:bg-white/5 transition-colors group">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full shadow-[0_0_8px_rgba(255,255,255,0.2)]" style={{ backgroundColor: level.color }} />
                    <span className="text-xs font-medium text-[var(--text-main)] uppercase">{level.type}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-xs data-value font-bold text-[var(--text-main)] group-hover:text-blue-400 transition-colors">
                  {level.price.toFixed(5)}
                </td>
                <td className="px-4 py-3">
                  <span className="text-[9px] bg-white/5 px-1.5 py-0.5 rounded font-bold text-[var(--text-muted)] group-hover:text-blue-200">
                    {level.timeframe}
                  </span>
                </td>
              </tr>
            ))}
            {levels.length === 0 && (
              <tr>
                <td colSpan={3} className="px-4 py-20 text-center text-xs text-[var(--text-muted)]">
                  <div className="flex flex-col items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center">
                      <QueueListIcon className="w-4 h-4 opacity-50" />
                    </div>
                    <span>No institutional levels detected for {symbol}</span>
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TradingLevelsPanel;
