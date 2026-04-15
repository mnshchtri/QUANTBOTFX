import React, { useState, useEffect } from 'react';
import './App.css';
import TradingDashboardChart from './components/Chart/TradingDashboardChart';
import MarketInfo from './components/Dashboard/MarketInfo';
import IndicatorPanel from './components/Dashboard/IndicatorPanel';
import TradingLevelsPanel from './components/Dashboard/TradingLevelsPanel';
import NewsPanel from './components/Dashboard/NewsPanel';
import StrategyDevelopment from './components/Dashboard/StrategyDevelopment';
import ReplayInterface from './components/Replay/ReplayInterface';
import Sidebar from './components/Layout/Sidebar';
import Header from './components/Layout/Header';
import { 
  ChevronLeftIcon, 
  ChevronRightIcon, 
  TableCellsIcon,
  NewspaperIcon,
  PresentationChartBarIcon
} from '@heroicons/react/24/outline';
import Watchlist from './components/Dashboard/Watchlist';

interface CandleData {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

interface IndicatorData {
  name: string;
  data: Array<{ timestamp: number; value: number }>;
  color: string;
  type: 'line' | 'histogram';
  overlay: boolean;
}

interface IndicatorParameters {
  [indicatorName: string]: any;
}

function App() {
  const [symbol, setSymbol] = useState('GBP_JPY');
  const [timeframe, setTimeframe] = useState('M15');
  const [activeIndicators, setActiveIndicators] = useState<string[]>([]);
  const [indicatorParameters, setIndicatorParameters] = useState<IndicatorParameters>({});
  const [indicatorOverlays, setIndicatorOverlays] = useState<Record<string, boolean>>({});
  const [chartData, setChartData] = useState<CandleData[]>([]);
  const [indicators, setIndicators] = useState<IndicatorData[]>([]);
  const [activeView, setActiveView] = useState('trading');
  
  // Enterprise Layout State
  const [leftPanelOpen, setLeftPanelOpen] = useState(true);
  const [rightPanelOpen, setRightPanelOpen] = useState(true);
  const [bottomPanelOpen, setBottomPanelOpen] = useState(false);

  const symbols = [
    'GBP_JPY', 'EUR_USD', 'USD_JPY', 'GBP_USD', 
    'EUR_GBP', 'USD_CHF', 'AUD_USD', 'USD_CAD'
  ];

  const [isTerminalReady, setIsTerminalReady] = useState(false);
  const [notifications, setNotifications] = useState<any[]>([]);

  const addNotification = (msg: string) => {
    const id = Date.now();
    setNotifications(prev => [{ id, msg }, ...prev].slice(0, 5));
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 5000);
  };

  const timeframes = [
    { value: 'M1', label: '1m' },
    { value: 'M5', label: '5m' },
    { value: 'M15', label: '15m' },
    { value: 'H1', label: '1h' },
    { value: 'H4', label: '4h' },
    { value: 'D1', label: '1d' }
  ];

  // Fetch chart data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`/api/candles/${symbol}/${timeframe}?limit=1000`);
        if (response.ok) {
          const data = await response.json();
          if (data && data.data) {
            setChartData(data.data || []);
          }
        }
      } catch (error) {
        console.error('Error fetching chart data:', error);
      }
    };
    fetchData();
  }, [symbol, timeframe]);

  const handleIndicatorToggle = (indicatorName: string, enabled: boolean, parameters?: any, overlay?: boolean) => {
    if (enabled) {
      if (!activeIndicators.includes(indicatorName)) {
        setActiveIndicators(prev => [...prev, indicatorName]);
      }
    } else {
      setActiveIndicators(prev => prev.filter(name => name !== indicatorName));
    }
  };

  const executeTrade = async (type: 'buy' | 'sell') => {
    try {
      const price = chartData.length > 0 ? chartData[chartData.length - 1].close : 0;
      const response = await fetch('/api/trading/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol,
          type,
          volume: 0.1,
          price,
          timestamp: Date.now() / 1000
        })
      });
      if (response.ok) {
        addNotification(`Position Opened: ${type.toUpperCase()} ${symbol} @ ${price.toFixed(5)}`);
        setBottomPanelOpen(true); // Open orders panel to show feedback
      }
    } catch (error) {
      console.error('Trade execution failed:', error);
    }
  };

  const [positions, setPositions] = useState<any[]>([]);

  useEffect(() => {
    if (bottomPanelOpen) {
      const fetchPositions = async () => {
        try {
          const res = await fetch('/api/trading/positions');
          if (res.ok) {
            const data = await res.json();
            setPositions(data.data || []);
          }
        } catch (e) {}
      };
      fetchPositions();
      const interval = setInterval(fetchPositions, 5000);
      return () => clearInterval(interval);
    }
  }, [bottomPanelOpen]);

  const renderTradingView = () => (
    <div className="flex flex-1 overflow-hidden relative h-full bg-[var(--bg-main)]">
      {/* FLOATING LEFT PANEL - Market Intelligence */}
      <div className={`absolute left-4 top-4 bottom-4 z-40 transition-all duration-500 ease-in-out ${leftPanelOpen ? 'w-72 opacity-100' : 'w-0 opacity-0 pointer-events-none'}`}>
        <div className="h-full glass rounded-2xl flex flex-col overflow-hidden shadow-2xl border-white/10 backdrop-blur-2xl">
          <div className="flex-1 overflow-y-auto p-4 custom-scrollbar space-y-6">
            <Watchlist currentSymbol={symbol} onSelectSymbol={setSymbol} symbols={symbols} />
            <div className="border-t border-white/5 pt-6">
              <IndicatorPanel
                onIndicatorToggle={handleIndicatorToggle}
                activeIndicators={activeIndicators}
              />
            </div>
          </div>
        </div>
      </div>

      {/* CENTER AREA - The Chart */}
        {/* Main Chart background */}
        <div className="absolute inset-0 z-0">
          <TradingDashboardChart
            data={chartData}
            indicators={indicators}
            timeframe={timeframe}
            symbol={symbol}
            showLevels={true}
          />
        </div>

        {/* Toggle Buttons Floating */}
        <div className="absolute top-1/2 -translate-y-1/2 left-0 z-50 flex flex-col gap-2">
          {!leftPanelOpen && (
            <button 
              onClick={() => setLeftPanelOpen(true)}
              className="bg-blue-600/20 hover:bg-blue-600/40 border border-blue-500/30 p-2 rounded-r-xl text-blue-400 transition-all backdrop-blur-md"
            >
              <ChevronRightIcon className="w-5 h-5" />
            </button>
          )}
        </div>

        <div className="absolute top-1/2 -translate-y-1/2 right-0 z-50 flex flex-col gap-2">
          {!rightPanelOpen && (
            <button 
              onClick={() => setRightPanelOpen(true)}
              className="bg-blue-600/20 hover:bg-blue-600/40 border border-blue-500/30 p-2 rounded-l-xl text-blue-400 transition-all backdrop-blur-md"
            >
              <ChevronLeftIcon className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* BOTTOM HUD - Floating Trading Controls */}
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-40 glass rounded-2xl h-16 flex items-center px-6 gap-8 shadow-2xl border-white/10 backdrop-blur-3xl min-w-[600px]">
          <div className="flex items-center gap-3">
            <button 
              onClick={() => setLeftPanelOpen(!leftPanelOpen)}
              className={`p-2 rounded-lg transition-all ${leftPanelOpen ? 'bg-blue-500/20 text-blue-400' : 'text-gray-500 hover:text-white'}`}
            >
              <ChevronLeftIcon className="w-5 h-5" />
            </button>
            <button 
              onClick={() => setRightPanelOpen(!rightPanelOpen)}
              className={`p-2 rounded-lg transition-all ${rightPanelOpen ? 'bg-blue-500/20 text-blue-400' : 'text-gray-500 hover:text-white'}`}
            >
              <ChevronRightIcon className="w-5 h-5" />
            </button>
          </div>
          
          <div className="h-8 w-[1px] bg-white/5" />
          <div className="flex gap-2">
            <button 
              onClick={() => executeTrade('buy')}
              className="px-6 py-2 bg-green-500 hover:bg-green-600 text-white font-bold text-xs rounded uppercase tracking-widest transition-all glow-green"
            >
              Buy / Long
            </button>
            <button 
              onClick={() => executeTrade('sell')}
              className="px-6 py-2 bg-red-500 hover:bg-red-600 text-white font-bold text-xs rounded uppercase tracking-widest transition-all glow-red"
            >
              Sell / Short
            </button>
          </div>
          
          <div className="h-6 w-[1px] bg-[var(--border-subtle)]" />
          
          <div className="flex gap-4">
            <div className="flex flex-col">
              <span className="text-[9px] text-[var(--text-muted)] uppercase font-bold tracking-wider">Lot Size</span>
              <span className="text-xs font-bold data-value">0.10</span>
            </div>
            <div className="flex flex-col">
              <span className="text-[9px] text-[var(--text-muted)] uppercase font-bold tracking-wider">Spread</span>
              <span className="text-xs font-bold data-value text-blue-400">1.2 Pips</span>
            </div>
          </div>

          <button 
            onClick={() => setBottomPanelOpen(!bottomPanelOpen)}
            className="ml-auto flex items-center gap-2 text-[var(--text-muted)] hover:text-white transition-colors"
          >
            <TableCellsIcon className="w-5 h-5" />
            <span className="text-[10px] uppercase font-bold tracking-widest">Orders</span>
          </button>
        </div>

        {/* EXPANDABLE BOTTOM PANEL - Re-styled as an overlay */}
        <div className={`absolute bottom-24 left-1/2 -translate-x-1/2 z-40 glass rounded-2xl transition-all duration-500 ease-in-out overflow-hidden shadow-2xl border-white/10 backdrop-blur-3xl ${bottomPanelOpen ? 'h-80 w-[90%] opacity-100' : 'h-0 w-0 opacity-0'}`}>
          <div className="p-4 h-full flex flex-col">
            <div className="panel-header mb-4">Active Positions & Orders</div>
            <div className="flex-1 overflow-y-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-[var(--border-subtle)]">
                    <th className="px-4 py-2 text-[10px] font-bold text-[var(--text-muted)] uppercase">ID</th>
                    <th className="px-4 py-2 text-[10px] font-bold text-[var(--text-muted)] uppercase">Type</th>
                    <th className="px-4 py-2 text-[10px] font-bold text-[var(--text-muted)] uppercase">Symbol</th>
                    <th className="px-4 py-2 text-[10px] font-bold text-[var(--text-muted)] uppercase">Price</th>
                    <th className="px-4 py-2 text-[10px] font-bold text-[var(--text-muted)] uppercase">Size</th>
                    <th className="px-4 py-2 text-[10px] font-bold text-[var(--text-muted)] uppercase">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[var(--border-subtle)]">
                  {positions.map((pos) => (
                    <tr key={pos.id} className="hover:bg-white/5 transition-colors">
                      <td className="px-4 py-2 text-xs text-[var(--text-muted)] data-value">#{pos.id.slice(-6)}</td>
                      <td className="px-4 py-2 text-xs">
                        <span className={`px-2 py-0.5 rounded-full font-bold text-[9px] uppercase ${pos.type === 'buy' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
                          {pos.type}
                        </span>
                      </td>
                      <td className="px-4 py-2 text-xs font-bold text-[var(--text-main)] uppercase">{pos.symbol}</td>
                      <td className="px-4 py-2 text-xs data-value text-[var(--text-main)]">{pos.price.toFixed(5)}</td>
                      <td className="px-4 py-2 text-xs data-value text-[var(--text-main)]">{pos.volume}</td>
                      <td className="px-4 py-2 text-xs">
                        <span className="flex items-center gap-1.5 text-blue-400 font-bold text-[9px] uppercase">
                          <div className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
                          Live
                        </span>
                      </td>
                    </tr>
                  ))}
                  {positions.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-4 py-20 text-center text-xs text-[var(--text-muted)]">
                        <div className="flex flex-col items-center gap-2">
                          <TableCellsIcon className="w-5 h-5 opacity-30" />
                          <span className="uppercase tracking-widest font-bold opacity-30">No active positions for {symbol}</span>
                        </div>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

      {/* FLOATING RIGHT PANEL - Macro & Levels */}
      <div className={`absolute right-4 top-4 bottom-4 z-40 transition-all duration-500 ease-in-out ${rightPanelOpen ? 'w-72 opacity-100' : 'w-0 opacity-0 pointer-events-none'}`}>
        <div className="h-full glass rounded-2xl flex flex-col overflow-hidden shadow-2xl border-white/10 backdrop-blur-2xl">
          <div className="flex-1 overflow-y-auto p-4 custom-scrollbar space-y-6">
            <TradingLevelsPanel symbol={symbol} timeframe={timeframe} />
            <NewsPanel symbol={symbol} />
          </div>
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeView) {
      case 'trading':
        return renderTradingView();
      case 'strategy':
        return <div className="p-6 animate-fade-in"><StrategyDevelopment /></div>;
      case 'replay':
        return <div className="p-0 animate-fade-in h-full"><ReplayInterface instrument={symbol} /></div>;
      default:
        return <div className="text-center p-20 text-[var(--text-muted)]">Enterprise Component Initializing...</div>;
    }
  };

  if (!isTerminalReady) {
    return (
      <div className="h-screen w-screen bg-[#06070a] flex flex-col items-center justify-center relative overflow-hidden">
        <div className="absolute inset-0 bg-blue-600/5 transition-opacity" />
        <div className="z-10 flex flex-col items-center gap-8 animate-fade-in">
          <div className="w-24 h-24 bg-blue-600 rounded-2xl flex items-center justify-center shadow-[0_0_50px_rgba(37,99,235,0.4)] animate-pulse">
            <PresentationChartBarIcon className="w-12 h-12 text-white" />
          </div>
          <div className="text-center">
            <h1 className="text-4xl font-black text-white tracking-tighter mb-2">QuantBot<span className="text-blue-500">FX</span></h1>
            <p className="text-[10px] text-[var(--text-muted)] font-black uppercase tracking-[0.5em] opacity-50">Precision Algorithmic Terminal</p>
          </div>
          <button 
            onClick={() => setIsTerminalReady(true)}
            className="mt-4 px-12 py-3 bg-white text-black font-black text-xs rounded-full uppercase tracking-widest hover:bg-blue-500 hover:text-white transition-all transform hover:scale-105 shadow-xl"
          >
            Enter Mainframe
          </button>
          <div className="mt-8 flex gap-8 text-[9px] font-bold text-[var(--text-muted)]">
            <span>v2.0.4-STABLE</span>
            <span>SECURE-TUNNEL: ACTIVE</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex bg-[var(--bg-main)] h-screen overflow-hidden">
      {/* Notifications Layer */}
      <div className="fixed top-20 right-6 z-[100] flex flex-col gap-2">
        {notifications.map(n => (
          <div key={n.id} className="glass px-4 py-3 border-l-4 border-blue-500 rounded-r-xl shadow-2xl animate-slide-in">
            <span className="text-xs font-bold text-white uppercase tracking-tight">{n.msg}</span>
          </div>
        ))}
      </div>
      <Sidebar activeView={activeView} setActiveView={setActiveView} />
      
      <main className="flex-1 ml-[var(--sidebar-width)] flex flex-col h-screen overflow-hidden">
        <Header 
          symbol={symbol} 
          setSymbol={setSymbol} 
          timeframe={timeframe} 
          setTimeframe={setTimeframe}
          symbols={symbols}
          timeframes={timeframes}
        />
        
        <div className="flex-1 overflow-hidden">
          {renderContent()}
        </div>
      </main>
    </div>
  );
}

export default App;
