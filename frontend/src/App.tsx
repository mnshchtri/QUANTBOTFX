import React, { useState, useEffect } from 'react';
import './App.css';
import TradingDashboardChart from './components/Chart/TradingDashboardChart';
import ReplayControls from './components/Controls/ReplayControls';
import MarketInfo from './components/Dashboard/MarketInfo';
import IndicatorPanel, { indicators } from './components/Dashboard/IndicatorPanel';
import TradingLevelsPanel from './components/Dashboard/TradingLevelsPanel';
import NewsPanel from './components/Dashboard/NewsPanel';
import StrategyDevelopment from './components/Dashboard/StrategyDevelopment';
import ReplayInterface from './components/Replay/ReplayInterface';

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
  overlay: boolean; // Whether indicator should be overlaid on main chart
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
  const [activeView, setActiveView] = useState('trading'); // 'trading', 'strategy', or 'replay'
  const [indicatorUpdateTrigger, setIndicatorUpdateTrigger] = useState(0);

  const symbols = [
    'GBP_JPY', 'EUR_USD', 'USD_JPY', 'GBP_USD', 
    'EUR_GBP', 'USD_CHF', 'AUD_USD', 'USD_CAD'
  ];

  const timeframes = [
    { value: 'M1', label: '1 Minute' },
    { value: 'M5', label: '5 Minutes' },
    { value: 'M15', label: '15 Minutes' },
    { value: 'H1', label: '1 Hour' },
    { value: 'H4', label: '4 Hours' },
    { value: 'D1', label: '1 Day' }
  ];

  // Fetch chart data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`/api/candles/${symbol}/${timeframe}?limit=1000`);
        if (response.ok) {
          const data = await response.json();
          if (data && data.data && Array.isArray(data.data)) {
          setChartData(data.data || []);
          } else {
            console.warn('No real data available');
            setChartData([]);
          }
        }
      } catch (error) {
        console.error('Error fetching chart data:', error);
        setChartData([]);
      }
    };

    fetchData();
  }, [symbol, timeframe]);

  // Fetch indicators data
  useEffect(() => {
    const fetchIndicators = async () => {
      if (activeIndicators.length === 0) {
        setIndicators([]);
        return;
      }

      try {
        const indicatorList = activeIndicators.join(',');
        
        // Build parameters object for active indicators
        const parameters: { [key: string]: any } = {};
        activeIndicators.forEach(indicatorName => {
          if (indicatorParameters[indicatorName]) {
            parameters[indicatorName] = indicatorParameters[indicatorName];
          }
        });

        // Convert parameters to JSON string for URL
        const parametersJson = Object.keys(parameters).length > 0 ? JSON.stringify(parameters) : null;
        const paramsUrl = parametersJson ? `&parameters=${encodeURIComponent(parametersJson)}` : '';
        
        console.log(`Fetching indicators: ${indicatorList} with params:`, parameters);
        
        const response = await fetch(
          `/api/indicators/${symbol}/${timeframe}?indicators=${indicatorList}${paramsUrl}`
        );
        
        if (response.ok) {
          const data = await response.json();
          if (data.success && data.data.indicators) {
            // Transform indicator data for frontend plotting - simplified approach like Replay Mode
            const transformedIndicators = Object.entries(data.data.indicators)
              .map(([name, indicatorData]: [string, any]): IndicatorData | null => {
                if (indicatorData.error) {
                  console.warn(`Indicator ${name} has error:`, indicatorData.error);
                  return null; // Skip indicators with errors
                }

                // Get indicator definition to determine overlay property
                const baseIndicatorName = name.split('_')[0];
                const indicatorDefinition = indicators.find(ind => ind.name === baseIndicatorName);
                const overlay = indicatorOverlays[name] ?? indicatorDefinition?.overlay ?? true;

                // Simplified processing - handle all indicators uniformly
                let indicatorValues: Array<{ timestamp: number; value: number }> = [];
                
                if (indicatorData.values) {
                  // Standard single-value indicators
                  indicatorValues = indicatorData.values.map((value: number, index: number) => ({
                    timestamp: index,
                    value: value
                  })).filter((point: any) => 
                    point.value !== null && 
                    !isNaN(point.value) && 
                    point.value !== 0 // Filter out zero values that indicate no calculation yet
                  );
                } else if (indicatorData.upper && indicatorData.middle && indicatorData.lower) {
                  // Bollinger Bands - use upper band as main indicator
                  indicatorValues = indicatorData.upper.map((value: number, index: number) => ({
                    timestamp: index,
                    value: value
                  })).filter((point: any) => 
                    point.value !== null && 
                    !isNaN(point.value) && 
                    point.value !== 0
                  );
                } else if (indicatorData.macd_line) {
                  // MACD - use MACD line as main indicator
                  indicatorValues = indicatorData.macd_line.map((value: number, index: number) => ({
                    timestamp: index,
                    value: value
                  })).filter((point: any) => 
                    point.value !== null && 
                    !isNaN(point.value) && 
                    point.value !== 0
                  );
                } else if (indicatorData.k_values) {
                  // Stochastic - use K values
                  indicatorValues = indicatorData.k_values.map((value: number, index: number) => ({
                    timestamp: index,
                    value: value
                  })).filter((point: any) => 
                    point.value !== null && 
                    !isNaN(point.value) && 
                    point.value !== 0
                  );
                }

                if (indicatorValues.length === 0) {
                  console.warn(`No valid values for indicator ${name}`);
                  return null;
                }

                console.log(`Indicator ${name}: ${indicatorValues.length} valid values, sample:`, indicatorValues.slice(0, 3));

                return {
                  name: name,
                  data: indicatorValues,
                  color: getIndicatorColor(baseIndicatorName),
                  type: 'line',
                  overlay: overlay
                };
            })
              .filter((indicator): indicator is IndicatorData => indicator !== null);
          
            setIndicators(transformedIndicators);
            console.log(`Trading Dashboard: Processed ${transformedIndicators.length} indicators`);
          }
        }
      } catch (error) {
        console.error('Error fetching indicators:', error);
        setIndicators([]);
      }
    };

    fetchIndicators();
  }, [activeIndicators, symbol, timeframe, indicatorParameters, indicatorOverlays, indicatorUpdateTrigger]);

  const getIndicatorColor = (name: string): string => {
    const colors: { [key: string]: string } = {
      'SMA': '#3b82f6',
      'EMA': '#10b981',
      'RSI': '#f97316',
      'STOCHASTIC': '#ec4899',
      'BOLLINGER_BANDS': '#6366f1',
      'MACD': '#8b5cf6',
      'CCI': '#8b5cf6',
      'WILLIAMS_R': '#f97316',
      'MOMENTUM': '#ec4899',
      'ROC': '#06b6d4',
      'ATR': '#84cc16',
      'PARABOLIC_SAR': '#ef4444',
      'ICHIMOKU': '#06b6d4',
      'OBV': '#84cc16',
      'VWAP': '#f97316',
      'SESSION_LEVELS': '#8b5cf6',
      'PIVOT_POINTS': '#06b6d4'
    };
    return colors[name.toUpperCase()] || '#6b7280';
  };



  // Enhanced indicator toggles with parameter support
  const handleIndicatorToggle = (indicatorName: string, enabled: boolean, parameters?: any, overlay?: boolean) => {
    if (enabled) {
      // Check if indicator is already active (for updates)
      const isAlreadyActive = activeIndicators.includes(indicatorName);
      
      if (!isAlreadyActive) {
        // Add new indicator
      setActiveIndicators(prev => [...prev, indicatorName]);
      }
      
      if (parameters) {
        setIndicatorParameters(prev => ({
          ...prev,
          [indicatorName]: parameters
        }));
      }
      if (overlay !== undefined) {
        setIndicatorOverlays(prev => ({
          ...prev,
          [indicatorName]: overlay
        }));
      }
      
      // If indicator is already active and we're updating it, trigger a re-fetch
      if (isAlreadyActive) {
        setIndicatorUpdateTrigger(prev => prev + 1);
      }
    } else {
      setActiveIndicators(prev => prev.filter(name => name !== indicatorName));
      setIndicatorParameters(prev => {
        const newParams = { ...prev };
        delete newParams[indicatorName];
        return newParams;
      });
      setIndicatorOverlays(prev => {
        const newOverlays = { ...prev };
        delete newOverlays[indicatorName];
        return newOverlays;
      });
    }
  };



  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-8">
              <h1 className="text-2xl font-bold text-gray-900">TrimurtiFX</h1>
              
              {/* View Toggle */}
              <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => setActiveView('trading')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeView === 'trading'
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Trading Dashboard
                </button>
                <button
                  onClick={() => setActiveView('strategy')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeView === 'strategy'
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Strategy Development
                </button>
                <button
                  onClick={() => setActiveView('replay')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeView === 'replay'
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Replay Mode
                </button>
              </div>
            </div>

            {/* Symbol and Timeframe Selectors */}
            {activeView === 'trading' && (
              <div className="flex items-center space-x-4">
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">Symbol</label>
                  <select
                    value={symbol}
                    onChange={(e) => setSymbol(e.target.value)}
                    className="text-sm border border-gray-300 rounded-md px-3 py-1"
                  >
                    {symbols.map(s => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">Timeframe</label>
                  <select
                    value={timeframe}
                    onChange={(e) => setTimeframe(e.target.value)}
                    className="text-sm border border-gray-300 rounded-md px-3 py-1"
                  >
                    {timeframes.map(tf => (
                      <option key={tf.value} value={tf.value}>{tf.label}</option>
                    ))}
                  </select>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeView === 'trading' ? (
          // Trading Dashboard View
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Left Sidebar - Controls */}
            <div className="lg:col-span-1 space-y-6">
              {/* Market Info */}
              <MarketInfo symbol={symbol} timeframe={timeframe} />

              {/* Indicator Panel */}
              <IndicatorPanel
                onIndicatorToggle={handleIndicatorToggle}
                activeIndicators={activeIndicators}
              />
            </div>

            {/* Main Chart Area */}
            <div className="lg:col-span-2 space-y-4">
              {/* Price Chart */}
              <div className="bg-white p-4 rounded-lg shadow-md border border-gray-200">
                <TradingDashboardChart
                  data={chartData}
                  indicators={indicators}
                  timeframe={timeframe}
                  symbol={symbol}
                  showLevels={true}
                />
              </div>
              

            </div>

            {/* Right Sidebar - Workflow and News */}
            <div className="lg:col-span-1 space-y-6">
              {/* Levels Panel */}
              <TradingLevelsPanel
                symbol={symbol}
                timeframe={timeframe}
              />

              {/* News Panel */}
              <NewsPanel symbol={symbol} />
            </div>
          </div>
        ) : activeView === 'strategy' ? (
          // Strategy Development View
          <StrategyDevelopment />
        ) : (
          // Replay Mode View
          <ReplayInterface instrument={symbol} />
        )}
      </div>
    </div>
  );
}

export default App;
