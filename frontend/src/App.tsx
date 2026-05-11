import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import TradingDashboardChart from './components/Chart/TradingDashboardChart';
import IndicatorPanel from './components/Dashboard/IndicatorPanel';
import TradingLevelsPanel from './components/Dashboard/TradingLevelsPanel';
import NewsPanel from './components/Dashboard/NewsPanel';
import Sidebar from './components/Layout/Sidebar';
import Header from './components/Layout/Header';
import AuthPage from './components/Auth/AuthPage';
import { motion, AnimatePresence } from 'framer-motion';
import { fetchCandles, fetchIndicators, executeTrade as apiExecuteTrade,
         type Candle, type Indicators, type User } from './services/api';
import { 
  ChevronLeft, 
  ChevronRight, 
  Terminal,
  Cpu,
  Lock,
  Globe,
  Activity
} from 'lucide-react';
import Watchlist from './components/Dashboard/Watchlist';

function App() {
  const [symbol, setSymbol] = useState('GBP_JPY');
  const [timeframe, setTimeframe] = useState('M15');
  const [activeIndicators] = useState<string[]>([]);
  const [chartData, setChartData] = useState<Candle[]>([]);
  const [indicators, setIndicators] = useState<Indicators | null>(null);
  const [activeView, setActiveView] = useState('trading');
  const [leftPanelOpen, setLeftPanelOpen] = useState(true);
  const [rightPanelOpen, setRightPanelOpen] = useState(true);
  const [bottomPanelOpen, setBottomPanelOpen] = useState(false);
  const [isTerminalReady, setIsTerminalReady] = useState(false);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [user, setUser] = useState<User | null>(null);
  const [authModalOpen, setAuthModalOpen] = useState(false);

  // Check for stored user on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('quantbot_user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const handleAuthSuccess = (userData: User) => {
    setUser(userData);
    localStorage.setItem('quantbot_user', JSON.stringify(userData));
    addNotification(`Welcome back, ${userData.username}!`);
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('quantbot_user');
    addNotification('Logged out successfully');
  };

  const symbols = ['GBP_JPY', 'EUR_USD', 'USD_JPY', 'GBP_USD', 'EUR_GBP', 'USD_CHF', 'AUD_USD', 'USD_CAD'];
  const timeframes = [
    { value: 'M1', label: '1m' }, { value: 'M5', label: '5m' },
    { value: 'M15', label: '15m' }, { value: 'H1', label: '1h' },
    { value: 'H4', label: '4h' }, { value: 'D1', label: '1d' }
  ];

  const addNotification = (msg: string) => {
    const id = Date.now();
    setNotifications(prev => [{ id, msg }, ...prev].slice(0, 5));
    setTimeout(() => setNotifications(prev => prev.filter(n => n.id !== id)), 5000);
  };

  const handleInitialize = () => {
    if (!user) {
      setAuthModalOpen(true);
      addNotification("Access Denied: Authentication Required");
    } else {
      setIsTerminalReady(true);
    }
  };

  const loadMarketData = useCallback(async () => {
    try {
      const [candles, inds] = await Promise.all([
        fetchCandles(symbol, timeframe),
        fetchIndicators(symbol, timeframe)
      ]);
      setChartData(candles);
      setIndicators(inds);
    } catch (err) {
      console.error('Market data fetch failed:', err);
    }
  }, [symbol, timeframe]);

  useEffect(() => { loadMarketData(); }, [loadMarketData]);

  const executeTrade = async (type: 'buy' | 'sell') => {
    try {
      const price = chartData.length > 0 ? chartData[chartData.length - 1].close : 0;
      const result = await apiExecuteTrade(symbol, type, 0.1, price);
      if (result.success) {
        addNotification(`Order Filled: ${type.toUpperCase()} ${symbol} @ ${price.toFixed(5)}`);
        setBottomPanelOpen(true);
      } else {
        addNotification(`Order Failed: ${result.message}`);
      }
    } catch (error) {
      console.error('Trade execution failed:', error);
    }
  };

  const renderTradingView = () => (
    <div className="flex flex-1 overflow-hidden relative h-full bg-[#020408]">
      {/* Background Ambient Glows */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-blue-600/10 blur-[120px] rounded-full animate-pulse-slow" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-indigo-600/10 blur-[120px] rounded-full animate-pulse-slow" />
      </div>

      {/* LEFT PANEL */}
      <AnimatePresence>
        {leftPanelOpen && (
          <motion.div 
            initial={{ x: -300, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -300, opacity: 0 }}
            className="absolute left-6 top-6 bottom-6 w-80 z-40"
          >
            <div className="h-full premium-card flex flex-col overflow-hidden">
              <div className="flex-1 overflow-y-auto custom-scrollbar space-y-8">
                <Watchlist currentSymbol={symbol} onSelectSymbol={setSymbol} symbols={symbols} />
                <div className="border-t border-white/5 pt-8">
                  <IndicatorPanel onIndicatorToggle={() => {}} activeIndicators={activeIndicators} />
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* CENTER - CHART */}
      <div className="flex-1 relative">
        <TradingDashboardChart
          data={chartData}
          indicators={indicators}
          timeframe={timeframe}
          symbol={symbol}
          showLevels={true}
        />
      </div>

      {/* RIGHT PANEL */}
      <AnimatePresence>
        {rightPanelOpen && (
          <motion.div 
            initial={{ x: 300, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 300, opacity: 0 }}
            className="absolute right-6 top-6 bottom-6 w-80 z-40"
          >
            <div className="h-full premium-card flex flex-col overflow-hidden">
              <div className="flex-1 overflow-y-auto custom-scrollbar space-y-8">
                <TradingLevelsPanel symbol={symbol} timeframe={timeframe} />
                <NewsPanel symbol={symbol} />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* BOTTOM HUD */}
      <div className="absolute bottom-10 left-1/2 -translate-x-1/2 z-40 flex items-center gap-4">
        <motion.div 
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="glass rounded-[32px] h-20 flex items-center px-8 gap-8 border-white/10 shadow-[0_20px_50px_rgba(0,0,0,0.5)] backdrop-blur-3xl min-w-[700px]"
        >
          <div className="flex items-center gap-4">
            <button onClick={() => setLeftPanelOpen(!leftPanelOpen)} className={`p-2.5 rounded-xl transition-all ${leftPanelOpen ? 'bg-blue-500/20 text-blue-400' : 'text-gray-500 hover:text-white'}`}>
              <ChevronLeft className="w-5 h-5" />
            </button>
            <button onClick={() => setRightPanelOpen(!rightPanelOpen)} className={`p-2.5 rounded-xl transition-all ${rightPanelOpen ? 'bg-blue-500/20 text-blue-400' : 'text-gray-500 hover:text-white'}`}>
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
          
          <div className="h-10 w-[1px] bg-white/5" />
          
          <div className="flex gap-4">
            <button onClick={() => executeTrade('buy')} className="btn-trading-primary px-8">Buy Long</button>
            <button onClick={() => executeTrade('sell')} className="btn-trading px-8 bg-red-500/10 border border-red-500/20 text-red-500 hover:bg-red-500/20">Sell Short</button>
          </div>
          
          <div className="h-10 w-[1px] bg-white/5" />
          
          <div className="flex gap-6">
            <div className="flex flex-col">
              <span className="text-[10px] text-gray-500 font-black uppercase tracking-widest">Lot</span>
              <span className="text-sm font-bold font-mono text-white">0.10</span>
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] text-gray-500 font-black uppercase tracking-widest">Margin</span>
              <span className="text-sm font-bold font-mono text-blue-400">1:500</span>
            </div>
          </div>

          <button onClick={() => setBottomPanelOpen(!bottomPanelOpen)} className="ml-auto p-3 bg-white/5 rounded-2xl text-gray-400 hover:text-white transition-colors">
            <Terminal className="w-5 h-5" />
          </button>
        </motion.div>
      </div>
    </div>
  );

  if (!user) {
    return <AuthPage onAuthSuccess={handleAuthSuccess} />;
  }

  return (
    <div className="flex bg-[#020408] h-screen overflow-hidden text-white">
      <Sidebar activeView={activeView} setActiveView={setActiveView} />
      
      <main className="flex-1 ml-[var(--sidebar-width)] flex flex-col h-screen overflow-hidden">
        <Header 
          symbol={symbol} setSymbol={setSymbol} 
          timeframe={timeframe} setTimeframe={setTimeframe}
          symbols={symbols} timeframes={timeframes}
          user={user} onLogout={handleLogout}
        />
        <div className="flex-1 overflow-hidden">{renderTradingView()}</div>
      </main>

      <AnimatePresence>
        {notifications.map(n => (
          <motion.div
            key={n.id}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="fixed top-20 right-6 z-50 bg-blue-600/90 backdrop-blur-md px-6 py-3 rounded-full border border-white/20 text-xs font-bold uppercase tracking-widest shadow-2xl shadow-blue-600/20"
          >
            {n.msg}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}

export default App;
