import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import ReplayChart, { CandleData } from '../Chart/ReplayChart';
import ReplayLevelsPanel from '../Dashboard/ReplayLevelsPanel';
import { 
  PlayIcon, 
  PauseIcon, 
  ForwardIcon, 
  BackwardIcon, 
  ArrowPathIcon,
  CalendarDaysIcon,
  ClockIcon,
  TableCellsIcon,
  ChevronLeftIcon,
  ChevronRightIcon
} from '@heroicons/react/24/solid';

interface IndicatorData {
  name: string;
  data: Array<{ timestamp: number; value: number }>;
  color: string;
  type: 'line' | 'histogram';
  overlay: boolean;
}

interface ReplayState {
  is_playing: boolean;
  current_index: number;
  total_candles: number;
  speed_multiplier: number;
  current_date: string;
}

interface PerformanceMetrics {
  current_balance: number;
  peak_balance: number;
  max_drawdown: number;
  total_trades: number;
  win_rate: number;
  total_profit_loss: number;
}

interface ReplayInterfaceProps {
  instrument?: string;
}

const ReplayInterface: React.FC<ReplayInterfaceProps> = ({ 
  instrument = "GBP_JPY"
}) => {
  const [replayState, setReplayState] = useState<ReplayState | null>(null);
  const [performance, setPerformance] = useState<PerformanceMetrics | null>(null);
  const [chartData, setChartData] = useState<any>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Layout state
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [bottomOpen, setBottomOpen] = useState(false);

  const [jumpDate, setJumpDate] = useState('');
  const [jumpTime, setJumpTime] = useState('');
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const retryCountRef = useRef(0);

  const initializeReplay = async () => {
    try {
      setIsInitialized(false);
      const response = await axios.post(`/replay/initialize`, {
        instrument,
        timeframe: "M15"
      });
      if (response.data.success) {
        setIsInitialized(true);
        await updateAll();
      }
    } catch (err) {
      console.error('Replay Initialization Error:', err);
      if (retryCountRef.current < 3) {
        retryCountRef.current++;
        setTimeout(initializeReplay, 2000);
      } else {
        setError('Connection to Replay Engine failed. Ensure backend is running.');
      }
    }
  };

  const updateAll = async () => {
    await Promise.all([
      updateReplayStatus(),
      updateChartData(),
      updatePerformance()
    ]);
  };

  const updateReplayStatus = async () => {
    try {
      const response = await axios.get(`/replay/status`);
      if (response.data.success) setReplayState(response.data.data);
    } catch (e) {}
  };

  const updateChartData = async () => {
    try {
      const response = await axios.get(`/replay/data`);
      if (response.data.success) {
        setChartData(response.data.data.candles.map((c: any) => ({
          timestamp: c.timestamp,
          open: parseFloat(c.open),
          high: parseFloat(c.high),
          low: parseFloat(c.low),
          close: parseFloat(c.close),
          volume: parseFloat(c.volume || 0)
        })));
      }
    } catch (e) {}
  };

  const updatePerformance = async () => {
    try {
      const response = await axios.get(`/replay/performance`);
      if (response.data.success) setPerformance(response.data.data);
    } catch (e) {}
  };

  const controlReplay = async (action: string, speed?: number) => {
    try {
      await axios.post(`/replay/control`, { action, speed });
      await updateReplayStatus();
    } catch (e) {}
  };

  const setStartPosition = async (params: { date?: string; position?: number }) => {
    try {
      await axios.post(`/replay/set-start-position`, params);
      await updateAll();
    } catch (e) {}
  };

  useEffect(() => {
    initializeReplay();
    return () => { if (intervalRef.current) clearInterval(intervalRef.current); };
  }, [instrument]);

  useEffect(() => {
    if (replayState?.is_playing) {
      intervalRef.current = setInterval(async () => {
        await updateReplayStatus();
        await updateChartData();
      }, 800);
    } else if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
  }, [replayState?.is_playing]);

  if (error) return <div className="p-10 text-red-400 font-bold bg-black h-full flex items-center justify-center">{error}</div>;

  return (
    <div className="flex flex-1 overflow-hidden h-full bg-black relative">
      {/* LEFT TOOLBAR - Control Drawer */}
      <div className={`transition-all duration-300 ease-in-out border-r border-[var(--border-subtle)] bg-[var(--bg-surface)] overflow-y-auto ${sidebarOpen ? 'w-80' : 'w-0 opacity-0 overflow-hidden'}`}>
        <div className="p-6 space-y-8 w-80">
          <div>
            <div className="panel-header">Replay Processor</div>
            <div className="space-y-4">
              <div className="bg-white/5 p-4 rounded-xl border border-white/10">
                <div className="text-[10px] text-[var(--text-muted)] font-bold uppercase mb-2">Target Date/Time</div>
                <div className="flex gap-2 mb-3">
                  <div className="flex-1 bg-black/40 px-3 py-2 rounded border border-white/5 flex items-center gap-2">
                    <CalendarDaysIcon className="w-4 h-4 text-blue-400" />
                    <input 
                      type="date" 
                      className="bg-transparent text-xs text-white outline-none w-full"
                      value={jumpDate}
                      onChange={e => setJumpDate(e.target.value)}
                    />
                  </div>
                </div>
                <div className="flex gap-2">
                  <div className="flex-1 bg-black/40 px-3 py-2 rounded border border-white/5 flex items-center gap-2">
                    <ClockIcon className="w-4 h-4 text-orange-400" />
                    <input 
                      type="time" 
                      className="bg-transparent text-xs text-white outline-none w-full"
                      value={jumpTime}
                      onChange={e => setJumpTime(e.target.value)}
                    />
                  </div>
                </div>
                <button 
                  onClick={() => setStartPosition({ date: `${jumpDate}T${jumpTime}` })}
                  className="w-full mt-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded font-bold text-[10px] uppercase tracking-widest transition-all"
                >
                  Jump to coordinate
                </button>
              </div>

              <ReplayLevelsPanel symbol={instrument} timeframe="M15" />
            </div>
          </div>

          {performance && (
            <div className="space-y-3">
              <div className="panel-header">Performance Analytics</div>
              <div className="grid grid-cols-2 gap-2">
                <div className="bg-white/5 p-3 rounded-lg">
                  <div className="text-[9px] text-[var(--text-muted)] uppercase">Balance</div>
                  <div className="text-sm font-bold data-value">${performance.current_balance.toFixed(0)}</div>
                </div>
                <div className="bg-white/5 p-3 rounded-lg">
                  <div className="text-[9px] text-[var(--text-muted)] uppercase">Win Rate</div>
                  <div className="text-sm font-bold data-value text-green-400">{(performance.win_rate * 100).toFixed(1)}%</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* CENTER CHART DISPLAY */}
      <div className="flex-1 flex flex-col relative overflow-hidden">
        <button 
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="absolute left-0 top-1/2 -translate-y-1/2 z-20 bg-[var(--bg-surface)] border border-[var(--border-subtle)] p-1 rounded-r-md text-[var(--text-muted)] hover:text-white"
        >
          {sidebarOpen ? <ChevronLeftIcon className="w-3 h-3" /> : <ChevronRightIcon className="w-3 h-3" />}
        </button>

        <div className="flex-1 relative">
          {chartData ? (
             <ReplayChart 
                data={chartData} 
                symbol={instrument} 
                timeframe="M15"
                onControl={async (action, val) => {
                   if (action === 'set_start_position') await setStartPosition(val);
                   else await controlReplay(action, val);
                }}
             />
          ) : (
             <div className="h-full flex flex-col items-center justify-center gap-4">
                <ArrowPathIcon className="w-10 h-10 text-blue-500 animate-spin" />
                <span className="text-xs uppercase font-bold tracking-widest text-blue-400">Synchronizing Replay Buffers...</span>
             </div>
          )}
        </div>

        {/* REPLAY CONTROL HUD */}
        <div className="h-16 glass border-t border-[var(--border-subtle)] flex items-center px-6 gap-6 z-30">
          <div className="flex items-center gap-1 bg-black/40 p-1 rounded-xl border border-white/5 shadow-inner">
            <button 
              onClick={() => controlReplay('step', -1)}
              className="p-2 text-[var(--text-muted)] hover:text-white hover:bg-white/5 rounded-lg transition-all"
            >
              <BackwardIcon className="w-5 h-5" />
            </button>
            <button 
              onClick={() => controlReplay(replayState?.is_playing ? 'pause' : 'play')}
              className={`p-3 rounded-xl transition-all shadow-lg ${replayState?.is_playing ? 'bg-orange-500/20 text-orange-400 shadow-orange-500/10' : 'bg-blue-600 text-white shadow-blue-500/20'}`}
            >
              {replayState?.is_playing ? <PauseIcon className="w-6 h-6" /> : <PlayIcon className="w-6 h-6" />}
            </button>
            <button 
              onClick={() => controlReplay('step', 1)}
              className="p-2 text-[var(--text-muted)] hover:text-white hover:bg-white/5 rounded-lg transition-all"
            >
              <ForwardIcon className="w-5 h-5" />
            </button>
          </div>

          <div className="flex flex-col">
            <span className="text-[10px] text-[var(--text-muted)] uppercase font-bold tracking-tighter">Engine Speed</span>
            <div className="flex gap-2">
              {[1, 5, 20, 100].map(s => (
                <button 
                  key={s}
                  onClick={() => controlReplay('set_speed', s)}
                  className={`text-[10px] font-bold px-2 py-0.5 rounded transition-all ${replayState?.speed_multiplier === s ? 'bg-blue-500 text-white' : 'bg-white/5 text-[var(--text-muted)] hover:text-white'}`}
                >
                  {s}x
                </button>
              ))}
            </div>
          </div>

          <div className="h-8 w-[1px] bg-[var(--border-subtle)]" />

          {replayState && (
            <div className="flex items-center gap-8">
               <div className="flex flex-col">
                  <span className="text-[10px] text-[var(--text-muted)] uppercase font-bold tracking-tighter">Current Step</span>
                  <span className="text-xs font-bold text-[var(--text-main)] data-value leading-none">{replayState.current_index} / {replayState.total_candles}</span>
               </div>
               <div className="flex flex-col">
                  <span className="text-[10px] text-[var(--text-muted)] uppercase font-bold tracking-tighter">Engine Horizon</span>
                  <span className="text-xs font-bold text-blue-400 data-value leading-none">{replayState.current_date.split('T')[0]}</span>
               </div>
            </div>
          )}

          <div className="ml-auto flex gap-2">
             <button className="px-5 py-2 bg-green-500/10 text-green-400 border border-green-500/20 rounded font-bold text-[10px] uppercase hover:bg-green-500 hover:text-white transition-all">Buy</button>
             <button className="px-5 py-2 bg-red-500/10 text-red-400 border border-red-500/20 rounded font-bold text-[10px] uppercase hover:bg-red-500 hover:text-white transition-all">Sell</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReplayInterface;