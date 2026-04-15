import React, { useState, useEffect } from 'react';
import { 
  MagnifyingGlassIcon, 
  BellIcon, 
  UserCircleIcon,
  ChevronDownIcon,
  WifiIcon,
  CpuChipIcon,
  CreditCardIcon,
  ArrowUpRightIcon,
  AdjustmentsHorizontalIcon
} from '@heroicons/react/24/outline';

interface HeaderProps {
  symbol: string;
  setSymbol: (s: string) => void;
  timeframe: string;
  setTimeframe: (t: string) => void;
  symbols: string[];
  timeframes: { value: string; label: string }[];
}

const Header: React.FC<HeaderProps> = ({ 
  symbol, setSymbol, timeframe, setTimeframe, symbols, timeframes 
}) => {
  const [latency, setLatency] = useState(14);
  const [account, setAccount] = useState<any>(null);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('/api/trading/summary');
        if (res.ok) {
          const data = await res.json();
          setAccount(data.data);
        }
      } catch (e) {}
    };
    fetchData();
    const interval = setInterval(() => {
      setLatency(12 + Math.floor(Math.random() * 5));
      fetchData();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-16 px-6 glass border-b border-[var(--border-subtle)] flex items-center justify-between sticky top-0 z-40 backdrop-blur-xl shrink-0">
      <div className="flex items-center gap-8">
        {/* BRANDING / SEARCH */}
        <div className="flex items-center gap-4 bg-black/30 border border-white/5 rounded-xl px-3 py-1.5 focus-within:border-blue-500/50 transition-all w-64 group">
          <MagnifyingGlassIcon className="w-4 h-4 text-[var(--text-muted)] group-focus-within:text-blue-400" />
          <input 
            type="text" 
            placeholder="Search assets, symbols..." 
            className="bg-transparent border-none outline-none text-xs font-bold text-[var(--text-main)] w-full placeholder:text-[var(--text-muted)] placeholder:font-medium"
          />
          <span className="text-[10px] font-black text-[var(--text-muted)] bg-white/5 px-1.5 py-0.5 rounded border border-white/5">⌘K</span>
        </div>

        <div className="w-[1px] h-6 bg-[var(--border-subtle)] opacity-50" />

        {/* ACCOUNT HUD */}
        <div className="flex items-center gap-6">
          <div className="flex flex-col">
            <span className="text-[9px] text-[var(--text-muted)] font-black uppercase tracking-widest opacity-70">Balance / Equity</span>
            <div className="flex items-center gap-2">
              <span className="text-xs font-black text-white">${account?.balance?.toLocaleString() || '100,000.00'}</span>
              <span className="text-xs font-black text-blue-400">${account?.equity?.toLocaleString() || '100,000.00'}</span>
            </div>
          </div>
          
          <div className="flex flex-col border-l border-white/5 pl-6">
            <span className="text-[9px] text-[var(--text-muted)] font-black uppercase tracking-widest opacity-70">Daily PnL</span>
            <div className="flex items-center gap-2">
              <span className={`text-xs font-black ${account?.pnl_today >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {account?.pnl_today >= 0 ? '+' : ''}${account?.pnl_today?.toLocaleString() || '0.00'}
              </span>
              <span className={`text-[10px] font-black px-1.5 rounded-full ${account?.pnl_percent >= 0 ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
                {account?.pnl_percent >= 0 ? '+' : ''}{account?.pnl_percent?.toFixed(2) || '0.00'}%
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-6">
        {/* TIMEFRAME SELECTOR */}
        <div className="flex items-center gap-1 p-1 bg-white/5 rounded-xl border border-white/5">
          {timeframes.map((tf) => (
            <button
              key={tf.value}
              onClick={() => setTimeframe(tf.value)}
              className={`px-3 py-1 rounded-lg text-[10px] font-black transition-all ${
                timeframe === tf.value 
                ? 'bg-blue-600 text-white shadow-lg' 
                : 'text-[var(--text-muted)] hover:text-white hover:bg-white/5'
              }`}
            >
              {tf.value}
            </button>
          ))}
        </div>

        <div className="w-[1px] h-6 bg-[var(--border-subtle)]" />

        {/* SYSTEM STATUS */}
        <div className="flex items-center gap-4">
          <div className="flex flex-col items-end">
            <div className="flex items-center gap-1.5">
              <span className="text-[9px] font-black text-[var(--text-main)] uppercase">Node-1</span>
              <div className="w-1.5 h-1.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)] animate-pulse" />
            </div>
            <span className="text-[9px] text-[var(--text-muted)] font-bold tracking-tight">{latency}ms Delay</span>
          </div>
          
          <BellIcon className="w-5 h-5 text-[var(--text-muted)] hover:text-white cursor-pointer transition-colors" />
          <AdjustmentsHorizontalIcon className="w-5 h-5 text-[var(--text-muted)] hover:text-white cursor-pointer transition-colors" />
        </div>
        
        <button className="flex items-center gap-3 pl-4 border-l border-white/10 group">
          <div className="flex flex-col items-end">
            <span className="text-xs font-black text-[var(--text-main)] group-hover:text-blue-400 transition-colors uppercase tracking-tight">Alpha_Trader</span>
            <span className="text-[9px] text-blue-500 font-black tracking-[0.1em] uppercase opacity-70">Gold Tier</span>
          </div>
          <div className="w-8 h-8 rounded-full overflow-hidden border-2 border-white/10 group-hover:border-blue-500/50 transition-all bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center">
             <UserCircleIcon className="w-6 h-6 text-white" />
          </div>
        </button>
      </div>
    </header>
  );
};

export default Header;
