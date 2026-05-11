import React, { useState, useEffect } from 'react';
import {
  MagnifyingGlassIcon,
  BellIcon,
  UserCircleIcon,
  AdjustmentsHorizontalIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/react/24/outline';
import { fetchAccount, type AccountSummary, type User } from '../../services/api';

interface HeaderProps {
  symbol: string;
  setSymbol: (s: string) => void;
  timeframe: string;
  setTimeframe: (t: string) => void;
  symbols: string[];
  timeframes: { value: string; label: string }[];
  user: User | null;
  onLogout: () => void;
}

const Header: React.FC<HeaderProps> = ({
  symbol, setSymbol, timeframe, setTimeframe, symbols, timeframes, user, onLogout
}) => {
  const [latency, setLatency]   = useState(14);
  const [account, setAccount]   = useState<AccountSummary | null>(null);

  useEffect(() => {
    const load = async () => {
      try { setAccount(await fetchAccount()); } catch { /* backend may be starting */ }
    };
    load();
    const id = setInterval(() => {
      setLatency(12 + Math.floor(Math.random() * 5));
      load();
    }, 5000);
    return () => clearInterval(id);
  }, []);

  return (
    <header className="h-20 bg-white border-b border-slate-100 flex items-center px-8 justify-between z-40">
      <div className="flex items-center gap-8 flex-1">
        <div className="relative group w-96">
          <MagnifyingGlassIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within:text-blue-600 transition-colors" />
          <input 
            type="text" 
            placeholder="Search symbols..."
            className="w-full bg-slate-50 border border-slate-100 rounded-2xl py-2.5 pl-12 pr-4 text-xs font-bold focus:outline-none focus:ring-2 focus:ring-blue-600/10 focus:border-blue-600 transition-all text-slate-900 placeholder:text-slate-400"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
          />
          <div className="absolute right-3 top-1/2 -translate-y-1/2 px-1.5 py-0.5 rounded-md bg-white border border-slate-200 text-[9px] font-black text-slate-400 uppercase tracking-widest">
            ⌘ K
          </div>
        </div>

        <div className="flex items-center gap-12 ml-4">
          <div className="flex flex-col">
            <span className="text-[9px] font-black text-slate-400 uppercase tracking-[0.2em] mb-1">Balance / Equity</span>
            <div className="flex items-center gap-3">
              <span className="text-lg font-black tracking-tight text-slate-900">$100,000.00</span>
              <span className="text-sm font-bold text-blue-600">$100,000.00</span>
            </div>
          </div>
          
          <div className="flex flex-col border-l border-slate-100 pl-8">
            <span className="text-[9px] font-black text-slate-400 uppercase tracking-[0.2em] mb-1">Daily PnL</span>
            <div className="flex items-center gap-3">
              <span className="text-sm font-black text-emerald-600">+$0.00</span>
              <span className="text-[10px] font-bold px-2 py-0.5 bg-emerald-50 text-emerald-600 rounded-md">+0.00%</span>
            </div>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-8">
        <div className="flex bg-slate-50 p-1.5 rounded-2xl border border-slate-100 shadow-inner">
          {timeframes.map((tf) => (
            <button
              key={tf.value}
              onClick={() => setTimeframe(tf.value)}
              className={`px-6 py-2 rounded-xl text-[10px] font-black transition-all duration-300 uppercase tracking-widest ${
                timeframe === tf.value 
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20' 
                : 'text-slate-400 hover:text-slate-900'
              }`}
            >
              {tf.value}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-4 border-l border-slate-100 pl-8">
          <button className="p-2.5 text-slate-400 hover:text-blue-600 transition-all relative">
            <BellIcon className="w-5 h-5" />
            <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-blue-600 rounded-full border-2 border-white" />
          </button>
          
          <div className="flex items-center gap-4 group cursor-pointer">
            <div className="flex flex-col items-end">
              <span className="text-[11px] font-black text-slate-900 group-hover:text-blue-600 transition-colors uppercase tracking-tight">
                {user?.username || 'Trader'}
              </span>
              <span className="text-[9px] text-blue-600 font-black tracking-[0.1em] uppercase">Quant Pro</span>
            </div>
            <div className="w-10 h-10 rounded-2xl border border-slate-100 group-hover:border-blue-200 transition-all bg-slate-50 flex items-center justify-center overflow-hidden shadow-sm">
               <UserCircleIcon className="w-6 h-6 text-slate-400" />
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
