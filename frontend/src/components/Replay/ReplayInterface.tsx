import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import ReplayChart, { CandleData } from '../Chart/ReplayChart';
import ReplayLevelsPanel from '../Dashboard/ReplayLevelsPanel';

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

interface Strategy {
  name: string;
  type: string;
  description: string;
  parameters: Record<string, any>;
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
  const [signals, setSignals] = useState<any[]>([]);
  const [activeIndicators, setActiveIndicators] = useState<string[]>([]);
  const [isInitialized, setIsInitialized] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentInstrument, setCurrentInstrument] = useState(instrument);
  const [currentTimeframe, setCurrentTimeframe] = useState("M15");
  const [dataRange, setDataRange] = useState<{
    start_date: string;
    end_date: string;
    start_time: string;
    end_time: string;
    total_candles: number;
  } | null>(null);

  
  // Strategy selection state (REAL strategies only)
  const [selectedStrategy, setSelectedStrategy] = useState<string>('RangeOfTheDay');
  const [availableStrategies] = useState<Strategy[]>([
    {
      name: 'RangeOfTheDay',
      type: 'momentum',
      description: 'Range of the Day strategy - follows higher timeframe momentum with stochastic crossovers',
      parameters: {
        stoch_period: 14,
        stoch_k: 3,
        stoch_d: 3,
        rsi_period: 14
      }
    }
  ]);
  const [strategyParameters, setStrategyParameters] = useState<Record<string, any>>({});
  const [isLoadingStrategy, setIsLoadingStrategy] = useState(false);
  
  // Strategy signals control
  const [showStrategySignals, setShowStrategySignals] = useState<boolean>(false);
  
  // Jump controls
  const [jumpDate, setJumpDate] = useState('');
  const [jumpTime, setJumpTime] = useState('');
  const [jumpPosition, setJumpPosition] = useState(0);
  
  const replayApiUrl = ''; // Use proxy configuration
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const instruments = [
    { value: 'EUR_USD', label: 'EUR/USD' },
    { value: 'GBP_USD', label: 'GBP/USD' },
    { value: 'USD_JPY', label: 'USD/JPY' },
    { value: 'GBP_JPY', label: 'GBP/JPY' },
    { value: 'EUR_JPY', label: 'EUR/JPY' },
    { value: 'AUD_USD', label: 'AUD/USD' },
    { value: 'USD_CAD', label: 'USD/CAD' },
    { value: 'NZD_USD', label: 'NZD/USD' },
    { value: 'USD_CHF', label: 'USD/CHF' },
    { value: 'EUR_GBP', label: 'EUR/GBP' }
  ];

  const timeframes = [
    { value: 'M1', label: '1 Minute' },
    { value: 'M5', label: '5 Minutes' },
    { value: 'M15', label: '15 Minutes' },
    { value: 'H1', label: '1 Hour' },
    { value: 'H4', label: '4 Hours' },
    { value: 'D1', label: '1 Day' }
  ];

  // Initialize replay session
  const initializeReplay = async (newInstrument?: string, newTimeframe?: string) => {
    try {
      console.log('ReplayInterface: Starting initialization...');
      console.log('ReplayInterface: Instrument:', newInstrument || instrument);
      console.log('ReplayInterface: Timeframe:', newTimeframe || currentTimeframe);
      setError(null);
      const initParams = {
        instrument: newInstrument || instrument,
        timeframe: newTimeframe || currentTimeframe
      };
      console.log(`🎬 Initializing replay with params:`, initParams);
      
      const response = await axios.post(`${replayApiUrl}/replay/initialize`, initParams);
      
      console.log('ReplayInterface: Initialization response:', response.data);
      
      if (response.data.success) {
        setIsInitialized(true);
        console.log('ReplayInterface: Initialization successful, updating data...');
        await updateReplayStatus();
        await updateChartData();
        await updatePerformance();
        await fetchDataRange();
      } else {
        setError('Failed to initialize replay session');
      }
    } catch (err) {
      console.error('ReplayInterface: Initialization error:', err);
      setError(`Error initializing replay: ${err}`);
    }
  };



  // Add strategy signals as overlays (doesn't change base data)
  const addStrategySignals = async () => {
    try {
      setIsLoadingStrategy(true);
      setError(null);
      
      console.log(`Adding strategy signals: ${selectedStrategy} for ${instrument} ${currentTimeframe}`);
      
      // Add strategy signals as overlays to existing chart data
      const response = await axios.post(`${replayApiUrl}/replay/add-strategy-signals`, {
        strategy_name: selectedStrategy
      });
      
      if (response.data.success) {
        console.log('Strategy signals added successfully:', response.data);
        
        // Update chart data to show signals as overlays
        await updateChartData();
        
      } else {
        setError('Failed to add strategy signals');
      }
    } catch (err) {
      console.error('Error adding strategy signals:', err);
      setError(`Error adding strategy signals: ${err}`);
    } finally {
      setIsLoadingStrategy(false);
    }
  };



  // Handle strategy selection
  const handleStrategyChange = async (strategyName: string) => {
    setSelectedStrategy(strategyName);
    
    // Update parameters for selected strategy
    const strategy = availableStrategies.find(s => s.name === strategyName);
    if (strategy) {
      setStrategyParameters(strategy.parameters);
    }
    
    // Add strategy signals as overlays
    await addStrategySignals();
  };

  // Handle parameter changes
  const handleParameterChange = (paramName: string, value: any) => {
    setStrategyParameters(prev => ({
      ...prev,
      [paramName]: value
    }));
  };

  // Update replay status
  const updateReplayStatus = async () => {
    try {
      console.log('🔄 Updating replay status...');
      const response = await axios.get(`${replayApiUrl}/replay/status`);
      
      if (response.data && response.data.success) {
        console.log('✅ Replay status updated:', response.data.data);
        setReplayState(response.data.data);
      } else {
        console.error('❌ Failed to update replay status:', response.data);
      }
    } catch (err) {
      console.error('❌ Error updating replay status:', err);
    }
  };

  // Update chart data - use replay data source
  const updateChartData = async () => {
    try {
      console.log(`📊 Updating chart data for ${currentInstrument} ${currentTimeframe}`);
      
      // Get replay data which includes candles and signals
      const endpoint = `${replayApiUrl}/replay/data`;
      console.log('🌐 Calling API endpoint:', endpoint);
      const replayResponse = await axios.get(endpoint);
      
      if (replayResponse.data.success && replayResponse.data.data) {
        const replayData = replayResponse.data.data;
        
        // Debug: Log raw API response
        console.log('🔍 RAW API Response:', {
          candlesLength: replayData.candles?.length || 0,
          signalsLength: replayData.signals?.length || 0,
          replayState: replayData.replay_state
        });
        
        // Convert candles to chart format and sort by timestamp
        const candles = replayData.candles || [];
        const chartData = candles
          .map((candle: any) => ({
            timestamp: candle.timestamp,
            open: parseFloat(candle.open),
            high: parseFloat(candle.high),
            low: parseFloat(candle.low),
            close: parseFloat(candle.close),
            volume: parseFloat(candle.volume || 0)
          }))
          .sort((a: any, b: any) => a.timestamp - b.timestamp); // Sort chronologically
        
        setChartData(chartData);
        console.log(`📊 Updated chart with ${chartData.length} candles from replay data for ${currentInstrument} ${currentTimeframe}`);
        console.log(`📊 ChartData sample:`, chartData.slice(0, 3));
        
        // Debug: Log first few candles to see if timeframe data is different
        if (chartData.length > 0) {
          console.log(`📊 First candle timestamp: ${new Date(chartData[0].timestamp * 1000).toISOString()}`);
          console.log(`📊 Last candle timestamp: ${new Date(chartData[chartData.length - 1].timestamp * 1000).toISOString()}`);
          console.log(`📊 Timeframe: ${currentTimeframe}`);
          console.log(`📊 Total candles: ${chartData.length}`);
          console.log(`📊 Sample candle data:`, chartData[0]);
        }
        
        // Update replay state
        if (replayData.replay_state) {
          setReplayState(replayData.replay_state);
        }
        
        // Handle signals based on toggle
        if (showStrategySignals) {
          const signalsData = replayData.signals || [];
          setSignals(signalsData);
          console.log(`🎯 Added ${signalsData.length} strategy signals to chart`);
        } else {
          // Clear signals if strategy signals are disabled
          setSignals([]);
        }
      } else {
        console.error('❌ Failed to get replay data:', replayResponse.data);
      }
    } catch (err) {
      console.error('Error updating chart data:', err);
    }
  };

  // Update performance metrics
  const updatePerformance = async () => {
    try {
      const response = await axios.get(`${replayApiUrl}/replay/performance`);
      if (response.data.success && response.data.data) {
        setPerformance(response.data.data);
      }
    } catch (err) {
      console.error('Error updating performance:', err);
    }
  };

  // Fetch data range
  const fetchDataRange = async () => {
    try {
      const response = await axios.get(`${replayApiUrl}/replay/data`);
      if (response.data.success && response.data.data && response.data.data.metadata) {
        const metadata = response.data.data.metadata;
        if (metadata.data_range) {
          setDataRange(metadata.data_range);
        }
      }
    } catch (err) {
      console.error('Error fetching data range:', err);
    }
  };

  // Control replay
  const controlReplay = async (action: string, speed?: number) => {
    try {
      console.log(`🎮 Controlling replay: ${action}${speed ? ` (speed: ${speed})` : ''}`);
      const response = await axios.post(`${replayApiUrl}/replay/control`, {
        action,
        speed
      });
      
      if (response.data.success) {
        console.log('✅ Replay control successful:', response.data);
        await updateReplayStatus();
      } else {
        console.error('❌ Replay control failed:', response.data);
      }
    } catch (err) {
      console.error('❌ Error controlling replay:', err);
    }
  };

  // Set start position
  const setStartPosition = async (params: { date?: string; context_candles?: number; position?: number }) => {
    try {
      console.log('Setting start position with params:', params);
      const response = await axios.post(`${replayApiUrl}/replay/set-start-position`, params);
      
      if (response.data.success) {
        console.log('✅ Position set successfully:', response.data);
        // Small delay to ensure backend state is fully updated
        await new Promise(resolve => setTimeout(resolve, 100));
        await updateReplayStatus();
        await updateChartData();
      } else {
        console.error('❌ Failed to set position:', response.data.message);
      }
    } catch (err) {
      console.error('Error setting start position:', err);
    }
  };

  // Add indicator
  const addIndicator = async (indicatorName: string) => {
    try {
      const response = await axios.post(`${replayApiUrl}/replay/add-indicator`, {
        indicator: indicatorName
      });
      
      if (response.data.success) {
        setActiveIndicators(prev => [...prev, indicatorName]);
      }
    } catch (err) {
      console.error('Error adding indicator:', err);
    }
  };

  // Remove indicator
  const removeIndicator = async (indicatorName: string) => {
    try {
      const response = await axios.post(`${replayApiUrl}/replay/remove-indicator`, {
        indicator: indicatorName
      });
      
      if (response.data.success) {
        setActiveIndicators(prev => prev.filter(ind => ind !== indicatorName));
      }
    } catch (err) {
      console.error('Error removing indicator:', err);
    }
  };

  // Execute trade
  const executeTrade = async (tradeType: 'buy' | 'sell') => {
    try {
      const response = await axios.post(`${replayApiUrl}/replay/execute-trade`, {
        type: tradeType
      });
      
      if (response.data.success) {
        await updatePerformance();
      }
    } catch (err) {
      console.error('Error executing trade:', err);
    }
  };

  // Convert candles to chart format
  const convertToCandleData = (candles: any[]): CandleData[] => {
    return candles.map(candle => ({
      timestamp: new Date(candle.time).getTime(),
      open: parseFloat(candle.open),
      high: parseFloat(candle.high),
      low: parseFloat(candle.low),
      close: parseFloat(candle.close),
      volume: parseFloat(candle.volume || 0)
    }));
  };

  // Convert indicators to chart format
  const convertToIndicatorData = (indicators: any): IndicatorData[] => {
    const indicatorData: IndicatorData[] = [];
    
    Object.entries(indicators).forEach(([name, data]: [string, any]) => {
      if (data && Array.isArray(data.values)) {
        indicatorData.push({
          name,
          data: data.values.map((value: number, index: number) => ({
            timestamp: index,
            value: value
          })),
          color: getIndicatorColor(name),
          type: 'line',
          overlay: ['SMA', 'EMA', 'BB_Upper', 'BB_Middle', 'BB_Lower'].includes(name)
        });
      }
    });
    
    return indicatorData;
  };

  // Get indicator color
  const getIndicatorColor = (name: string): string => {
    const colors: { [key: string]: string } = {
      'RSI': '#f97316',
      'MACD': '#8b5cf6',
      'Bollinger_Bands': '#6366f1',
      'Stochastic': '#ec4899',
      'ATR': '#06b6d4',
      'EMA': '#f59e0b',
      'SMA': '#3b82f6',
      'BB_Upper': '#6366f1',
      'BB_Middle': '#64748b',
      'BB_Lower': '#6366f1'
    };
    return colors[name] || '#666';
  };

  // Handle timeframe change
  const handleInstrumentChange = async (newInstrument: string) => {
    setCurrentInstrument(newInstrument);
    setIsInitialized(false);
    await initializeReplay(newInstrument, currentTimeframe);
  };

  const handleTimeframeChange = async (newTimeframe: string) => {
    console.log(`🔄 Changing timeframe from ${currentTimeframe} to ${newTimeframe} for ${currentInstrument}`);
    setCurrentTimeframe(newTimeframe);
    setIsInitialized(false);
    await initializeReplay(currentInstrument, newTimeframe);
  };

  // Handle replay control from chart
  const handleReplayControl = async (action: string, value?: any) => {
    switch (action) {
      case 'play':
      case 'pause':
      case 'stop':
      case 'reset':
        await controlReplay(action, value);
        break;
      case 'step_forward':
      case 'step_backward':
        // Map to backend 'step' action
        await controlReplay('step', value);
        break;
      case 'set_speed':
        await controlReplay('set_speed', value);
        break;
      case 'set_start_position':
        await setStartPosition(value);
        break;
      default:
        console.warn('Unknown replay action:', action);
    }
  };

  // Jump control functions
  const handleJumpToDateTime = async () => {
    if (!jumpDate || !jumpTime) {
      alert('Please select both date and time');
      return;
    }

    if (!/^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/.test(jumpTime)) {
      alert('Please enter a valid time (HH:MM format)');
      return;
    }

    const dateTime = `${jumpDate}T${jumpTime}`;
    await setStartPosition({ date: dateTime, context_candles: 14 });
  };

  const handleJumpToPosition = async () => {
    await setStartPosition({ position: jumpPosition });
  };

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setJumpDate(e.target.value);
  };

  const handleTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setJumpTime(e.target.value);
  };

  const handlePositionChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setJumpPosition(parseInt(e.target.value, 10));
  };

  const isJumpEnabled: boolean = Boolean(jumpDate && jumpTime && /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/.test(jumpTime));

  // Auto-update when playing (optimized polling with counters)
  const updateCounterRef = useRef(0);
  
  useEffect(() => {
    if (replayState?.is_playing) {
      // More responsive updates when playing
      intervalRef.current = setInterval(async () => {
        updateCounterRef.current++;
        
        // Always update status (lightweight)
        await updateReplayStatus();
        
        // Update chart data every 2nd tick (every 1 second)
        if (updateCounterRef.current % 2 === 0) {
          await updateChartData();
        }
        
        // Update performance every 6th tick (every 3 seconds)
        if (updateCounterRef.current % 6 === 0) {
          await updatePerformance();
        }
      }, 500); // 500ms for smoother replay experience
    } else {
      // Reset counter when not playing
      updateCounterRef.current = 0;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [replayState?.is_playing]);

  // Initialize on mount
  useEffect(() => {
    initializeReplay();
  }, []);

  // Note: Strategy signals are now only loaded when user explicitly toggles "Show Strategy Signals"
  // This ensures clean timeframe switching without interference from strategy data

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <div className="mt-2 text-sm text-red-700">{error}</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left Sidebar - Strategy Selection */}
        <div className="lg:col-span-1 space-y-6">
          {/* Strategy Selection */}
          <div className="bg-white p-4 rounded-lg shadow-md border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Strategy Selection</h3>
            
            {/* Strategy Dropdown */}
            <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-700">
                Select Strategy
              </label>
              <select
                value={selectedStrategy}
                onChange={(e) => handleStrategyChange(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                disabled={isLoadingStrategy}
              >
                {availableStrategies.map(strategy => (
                  <option key={strategy.name} value={strategy.name}>
                    {strategy.name}
                  </option>
                ))}
              </select>
              
              {/* Strategy Description */}
              {selectedStrategy && (
                <div className="mt-3 p-3 bg-gray-50 rounded-md">
                  <p className="text-sm text-gray-600">
                    {availableStrategies.find(s => s.name === selectedStrategy)?.description}
                  </p>
                </div>
              )}
              
              {/* Instrument Selection */}
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Instrument
                </label>
                <select
                  value={currentInstrument}
                  onChange={(e) => handleInstrumentChange(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  {instruments.map(inst => (
                    <option key={inst.value} value={inst.value}>
                      {inst.label}
                    </option>
                  ))}
                </select>
              </div>
              
              {/* Timeframe Selection */}
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Timeframe
                </label>
                <select
                  value={currentTimeframe}
                  onChange={(e) => handleTimeframeChange(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  {timeframes.map(tf => (
                    <option key={tf.value} value={tf.value}>
                      {tf.label}
                    </option>
                  ))}
                </select>
              </div>
              

              
              {/* Strategy Signals Toggle */}
              <div className="mt-4 p-3 bg-green-50 rounded-md border border-green-200">
                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-sm font-medium text-gray-700">
                      Show Strategy Signals
                    </label>
                    <p className="text-xs text-gray-500 mt-1">
                      Display buy/sell signals from strategy on chart
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={showStrategySignals}
                      onChange={(e) => {
                        setShowStrategySignals(e.target.checked);
                        updateChartData(); // Refresh chart with/without signals
                      }}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                  </label>
                </div>
                {showStrategySignals && (
                  <div className="mt-2 text-xs text-green-600">
                    🎯 Strategy signals enabled - buy/sell triangles will appear
                  </div>
                )}
              </div>

              {/* Levels Panel */}
              <div className="mt-4">
                <ReplayLevelsPanel
                  symbol={currentInstrument}
                  timeframe={currentTimeframe}
                />
              </div>
            </div>

            {/* Strategy Parameters */}
            {strategyParameters && Object.keys(strategyParameters).length > 0 && (
              <div className="mt-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Parameters</h4>
                <div className="space-y-2">
                  {Object.entries(strategyParameters).map(([param, value]) => (
                    <div key={param} className="flex items-center justify-between">
                      <label className="text-xs text-gray-600 capitalize">
                        {param.replace(/_/g, ' ')}
                      </label>
                      <input
                        type="number"
                        value={value}
                        onChange={(e) => handleParameterChange(param, parseFloat(e.target.value))}
                        className="w-20 px-2 py-1 text-xs border border-gray-300 rounded"
                        min="1"
                        max="100"
                      />
                    </div>
                  ))}
                </div>
                <button
                  onClick={addStrategySignals}
                  disabled={isLoadingStrategy}
                  className="mt-3 w-full px-3 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {isLoadingStrategy ? 'Adding Signals...' : 'Apply Parameters'}
                </button>
              </div>
            )}
          </div>



          {/* Performance Metrics */}
          {performance && (
            <div className="bg-white p-4 rounded-lg shadow-md border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Current Balance</span>
                  <span className="font-semibold">${performance.current_balance.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Total Trades</span>
                  <span className="font-semibold">{performance.total_trades}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Win Rate</span>
                  <span className="font-semibold">{(performance.win_rate * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Max Drawdown</span>
                  <span className="font-semibold text-red-600">-${performance.max_drawdown.toFixed(2)}</span>
                </div>
              </div>
            </div>
          )}


        </div>

        {/* Main Chart Area */}
        <div className="lg:col-span-3">
          {/* Replay Controls */}
          <div className="bg-white p-4 rounded-lg shadow-md border border-gray-200 mb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                {/* Play/Pause Button */}
                <button
                  onClick={() => handleReplayControl(replayState?.is_playing ? 'pause' : 'play')}
                  className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                  {replayState?.is_playing ? (
                    <>
                      <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                      Pause
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                      </svg>
                      Play
                    </>
                  )}
                </button>

                {/* Step Forward/Backward */}
                <button
                  onClick={() => handleReplayControl('step_backward')}
                  className="p-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
                  title="Step Backward"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </button>

                <button
                  onClick={() => handleReplayControl('step_forward')}
                  className="p-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
                  title="Step Forward"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                  </svg>
                </button>

                {/* Reset Button */}
                <button
                  onClick={() => handleReplayControl('reset')}
                  className="px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                >
                  Reset
                </button>
              </div>

              {/* Speed Control */}
              <div className="flex items-center space-x-2">
                <label className="text-sm font-medium text-gray-700">Speed:</label>
                <select
                  value={replayState?.speed_multiplier || 1}
                  onChange={(e) => handleReplayControl('set_speed', parseFloat(e.target.value))}
                  className="px-2 py-1 border border-gray-300 rounded-md text-sm"
                >
                  <option value={0.25}>0.25x</option>
                  <option value={0.5}>0.5x</option>
                  <option value={1}>1x</option>
                  <option value={2}>2x</option>
                  <option value={4}>4x</option>
                </select>
              </div>
            </div>

            {/* Progress Bar */}
            {replayState && (
              <div className="mt-3">
                <div className="flex justify-between text-sm text-gray-600 mb-1">
                  <span>Progress: {replayState.current_index + 1} / {replayState.total_candles}</span>
                  <span>{((replayState.current_index + 1) / replayState.total_candles * 100).toFixed(1)}%</span>
                  {replayState.current_date && (
                    <span className="text-blue-600">📅 {new Date(replayState.current_date).toLocaleString()}</span>
                  )}
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${((replayState.current_index + 1) / replayState.total_candles) * 100}%` }}
                  ></div>
                </div>
              </div>
            )}

            {/* Jump to Date/Time Controls */}
            <div className="mt-4 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
              <h5 className="text-sm font-medium text-gray-700 mb-2">🎯 Jump to Date & Time</h5>
              <div className="flex items-center space-x-2">
                <input
                  type="date"
                  value={jumpDate}
                  onChange={handleDateChange}
                  className="px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="time"
                  value={jumpTime}
                  onChange={handleTimeChange}
                  className="px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={handleJumpToDateTime}
                  disabled={!isJumpEnabled}
                  className="px-4 py-1 text-sm bg-orange-600 text-white rounded hover:bg-orange-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  Jump
                </button>
              </div>
              {!isJumpEnabled && jumpDate && jumpTime && (
                <p className="text-xs text-red-500 mt-1">Please enter a valid time format (HH:MM)</p>
              )}
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow-md border border-gray-200">
            {chartData ? (
              <ReplayChart
                key={`${currentInstrument}-${currentTimeframe}-${chartData.length}-${replayState?.current_index}`}
                data={chartData}
                signals={signals}
                timeframe={currentTimeframe}
                symbol={currentInstrument}
                replayState={replayState || undefined}
                onReplayControl={handleReplayControl}
                showLevels={true}
              />
            ) : (
              <div className="flex items-center justify-center h-96">
                <div className="text-center">
                  <div className="text-gray-500 text-lg mb-2">Loading chart data...</div>
                  <div className="text-gray-400 text-sm">Initializing replay session</div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReplayInterface; 