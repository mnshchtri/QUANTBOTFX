import React, { useState, useEffect } from 'react';
import { 
  BeakerIcon, 
  CpuChipIcon, 
  PlayIcon, 
  ArrowPathIcon, 
  ChartBarIcon,
  Cog6ToothIcon,
  ShieldCheckIcon,
  CircleStackIcon
} from '@heroicons/react/24/outline';

interface StrategyConfig {
  name: string;
  type: string;
  parameters: Record<string, any>;
  indicators: string[];
  timeframes: string[];
}

interface BacktestResult {
  strategy_name: string;
  symbol: string;
  timeframe: string;
  performance: {
    total_return: number;
    sharpe_ratio: number;
    max_drawdown: number;
    win_rate: number;
    total_trades: number;
  };
  signals: any[];
  analysis: any;
}

interface OptimizationResult {
  strategy_name: string;
  original_performance: Record<string, number>;
  optimized_performance: Record<string, number>;
  best_parameters: Record<string, any>;
  optimization_metrics: Record<string, number>;
}

const StrategyDevelopment: React.FC = () => {
  const [activeTab, setActiveTab] = useState('build');
  const [strategies, setStrategies] = useState<StrategyConfig[]>([]);
  const [backtestResults, setBacktestResults] = useState<BacktestResult[]>([]);
  const [optimizationResults, setOptimizationResults] = useState<OptimizationResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [systemStatus, setSystemStatus] = useState<any>(null);

  const [strategyConfig, setStrategyConfig] = useState<StrategyConfig>({
    name: '',
    type: 'momentum',
    parameters: {
      stoch_period: 14,
      rsi_period: 14,
      stoch_overbought: 80,
      stoch_oversold: 20
    },
    indicators: ['RSI', 'Stochastic'],
    timeframes: ['M15', 'H1']
  });

  const [backtestConfig, setBacktestConfig] = useState({
    symbol: 'EUR_GBP',
    timeframe: 'H1',
    start_date: '2023-01-01',
    end_date: '2023-12-31'
  });

  const strategyTypes = [
    { value: 'momentum', label: 'Momentum Following' },
    { value: 'trend', label: 'Trend Following' },
    { value: 'mean_reversion', label: 'Mean Reversion' },
    { value: 'breakout', label: 'Breakout' }
  ];

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('/api/strategy/status');
        if (res.ok) setSystemStatus(await res.json());
      } catch (e) {}
    };
    fetchData();
  }, []);

  const runAction = async (msg: string, callback: () => Promise<void>) => {
    setLoading(true);
    try {
      await callback();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const TabButton = ({ id, label, icon: Icon }: any) => (
    <button
      onClick={() => setActiveTab(id)}
      className={`flex items-center gap-2 px-6 py-3 border-b-2 transition-all ${
        activeTab === id 
        ? 'border-blue-500 text-blue-400 bg-blue-500/5' 
        : 'border-transparent text-[var(--text-muted)] hover:text-white hover:bg-white/5'
      }`}
    >
      <Icon className="w-4 h-4" />
      <span className="text-xs font-black uppercase tracking-widest">{label}</span>
    </button>
  );

  return (
    <div className="flex flex-col h-full bg-[var(--bg-main)] animate-fade-in">
      {/* HEADER SECTION */}
      <div className="p-6 border-b border-[var(--border-subtle)] bg-[var(--bg-surface)]">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-blue-600/20 rounded-xl flex items-center justify-center border border-blue-500/30">
              <BeakerIcon className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <h1 className="text-xl font-black text-white tracking-tight uppercase">Quant Labs <span className="text-blue-500">v2</span></h1>
              <p className="text-[10px] text-[var(--text-muted)] font-bold uppercase tracking-[0.2em]">Strategy Development & ML Optimization</p>
            </div>
          </div>

          <div className="flex gap-4">
             <div className="glass px-4 py-2 rounded-xl flex items-center gap-6">
                <div className="flex flex-col">
                   <span className="text-[9px] text-[var(--text-muted)] font-black uppercase">Nodes Active</span>
                   <span className="text-xs font-black text-white">4 / 8</span>
                </div>
                <div className="flex flex-col border-l border-white/5 pl-6">
                   <span className="text-[9px] text-[var(--text-muted)] font-black uppercase">Engine Status</span>
                   <span className="text-xs font-black text-green-400 flex items-center gap-1.5">
                     <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                     OPTIMIZED
                   </span>
                </div>
             </div>
          </div>
        </div>

        <div className="flex border-b border-[var(--border-subtle)]">
          <TabButton id="build" label="Build Strategy" icon={CpuChipIcon} />
          <TabButton id="test" label="Backtest Engine" icon={PlayIcon} />
          <TabButton id="optimize" label="AI Optimization" icon={ArrowPathIcon} />
          <TabButton id="integrated" label="Data Streams" icon={CircleStackIcon} />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-8">
        {activeTab === 'build' && (
          <div className="max-w-4xl space-y-8">
            <div className="grid grid-cols-2 gap-8">
              <div className="space-y-6">
                <div className="panel-header"><Cog6ToothIcon className="w-4 h-4" /> Core Parameters</div>
                <div className="space-y-4">
                  <div>
                    <label className="text-[10px] text-[var(--text-muted)] font-black uppercase mb-1.5 block">Strategy Name</label>
                    <input 
                      type="text" 
                      className="input-trading w-full py-2.5 font-bold" 
                      placeholder="e.g. BTC_MOMENTUM_ALPHA"
                      value={strategyConfig.name}
                      onChange={e => setStrategyConfig({...strategyConfig, name: e.target.value})}
                    />
                  </div>
                  <div>
                    <label className="text-[10px] text-[var(--text-muted)] font-black uppercase mb-1.5 block">Execution Logic</label>
                    <select className="input-trading w-full py-2.5 font-bold">
                      {strategyTypes.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                    </select>
                  </div>
                </div>
              </div>

              <div className="space-y-6">
                <div className="panel-header"><ShieldCheckIcon className="w-4 h-4" /> Risk Controls</div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-[10px] text-[var(--text-muted)] font-black uppercase mb-1.5 block">Stop Loss (Pips)</label>
                    <input type="number" className="input-trading w-full py-2.5 data-value" defaultValue={25} />
                  </div>
                  <div>
                    <label className="text-[10px] text-[var(--text-muted)] font-black uppercase mb-1.5 block">Take Profit (Pips)</label>
                    <input type="number" className="input-trading w-full py-2.5 data-value" defaultValue={75} />
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-4">
               <div className="panel-header"><CircleStackIcon className="w-4 h-4" /> Indicator Weights</div>
               <div className="grid grid-cols-4 gap-4">
                  {['RSI', 'MACD', 'SMA', 'EMA', 'BB', 'ATR', 'STOCH', 'ADX'].map(ind => (
                    <div key={ind} className="glass p-3 rounded-xl border border-white/5 hover:border-blue-500/50 transition-all cursor-pointer group">
                       <span className="text-[10px] font-black text-[var(--text-muted)] group-hover:text-blue-400">{ind}</span>
                       <div className="h-1 w-full bg-white/5 rounded-full mt-2">
                          <div className="h-full bg-blue-500 w-2/3 rounded-full" />
                       </div>
                    </div>
                  ))}
               </div>
            </div>

            <button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-black text-xs py-4 rounded-xl uppercase tracking-[0.2em] transition-all shadow-xl shadow-blue-500/10">
              Compile & Register Strategy
            </button>
          </div>
        )}

        {activeTab === 'test' && (
          <div className="space-y-8">
            <div className="grid grid-cols-4 gap-6">
               <div className="glass p-6 rounded-2xl border border-white/5 col-span-1 space-y-6">
                  <div className="panel-header">Engine Config</div>
                  <div className="space-y-4">
                    <div>
                      <label className="text-[10px] text-[var(--text-muted)] font-black uppercase mb-1.5 block">Instrument</label>
                      <input type="text" className="input-trading w-full py-2.5 font-bold" value="GBP_JPY" readOnly />
                    </div>
                    <div>
                      <label className="text-[10px] text-[var(--text-muted)] font-black uppercase mb-1.5 block">Timespan</label>
                      <input type="date" className="input-trading w-full py-2.5 data-value" />
                    </div>
                    <button className="w-full py-3 bg-white text-black font-black text-[10px] rounded-xl uppercase tracking-widest hover:bg-blue-500 hover:text-white transition-all">
                      Initialize Backtest
                    </button>
                  </div>
               </div>

               <div className="col-span-3 glass p-6 rounded-2xl border border-white/5 relative overflow-hidden flex items-center justify-center">
                  <div className="absolute inset-0 bg-blue-500/5" />
                  <div className="z-10 text-center space-y-4">
                    <ChartBarIcon className="w-16 h-16 text-blue-500/30 mx-auto" />
                    <p className="text-xs font-black text-[var(--text-muted)] uppercase tracking-widest">No backtest data in buffer. Run engine to visualize performance metrics.</p>
                  </div>
               </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StrategyDevelopment;