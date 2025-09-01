import React, { useState, useEffect } from 'react';

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
  const [selectedStrategy, setSelectedStrategy] = useState<StrategyConfig | null>(null);
  const [backtestResults, setBacktestResults] = useState<BacktestResult[]>([]);
  const [optimizationResults, setOptimizationResults] = useState<OptimizationResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [systemStatus, setSystemStatus] = useState<any>(null);

  // Strategy configuration
  const [strategyConfig, setStrategyConfig] = useState<StrategyConfig>({
    name: '',
    type: 'momentum',
    parameters: {},
    indicators: [],
    timeframes: []
  });

  // Backtest configuration
  const [backtestConfig, setBacktestConfig] = useState({
    symbol: 'EUR_GBP',
    timeframe: 'H1',
    start_date: '',
    end_date: '',
    strategy_config: {} as StrategyConfig
  });

  // Optimization configuration
  const [optimizationConfig, setOptimizationConfig] = useState({
    strategy_name: '',
    symbol: 'EUR_GBP',
    timeframe: 'H1',
    optimization_days: 30
  });

  const strategyTypes = [
    { value: 'momentum', label: 'Momentum Following' },
    { value: 'trend', label: 'Trend Following' },
    { value: 'mean_reversion', label: 'Mean Reversion' },
    { value: 'breakout', label: 'Breakout' },
    { value: 'custom', label: 'Custom' }
  ];

  const availableIndicators = [
    'SMA_20', 'SMA_50', 'EMA_12', 'EMA_26',
    'RSI', 'MACD', 'BB_Upper', 'BB_Lower',
    'Stoch_K', 'Stoch_D', 'ATR', 'ADX'
  ];

  const availableTimeframes = [
    'M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1'
  ];

  useEffect(() => {
    loadSystemStatus();
    loadStrategies();
  }, []);

  const loadSystemStatus = async () => {
    try {
              const response = await fetch('/api/strategy/status');
      if (response.ok) {
        const status = await response.json();
        setSystemStatus(status);
      }
    } catch (error) {
      console.error('Failed to load system status:', error);
    }
  };

  const loadStrategies = async () => {
    try {
              const response = await fetch('/api/strategy/active');
      if (response.ok) {
        const data = await response.json();
        // Load strategy configurations (this would be from a database in production)
        setStrategies([
          {
            name: 'Momentum Following Strategy',
            type: 'momentum',
            parameters: {
              stoch_period: 14,
              stoch_k_period: 3,
              stoch_d_period: 3,
              rsi_period: 14,
              stoch_overbought: 80,
              stoch_oversold: 20
            },
            indicators: ['Stoch_K', 'Stoch_D', 'RSI'],
            timeframes: ['M15', 'H1', 'H4']
          }
        ]);
      }
    } catch (error) {
      console.error('Failed to load strategies:', error);
    }
  };

  const registerStrategy = async () => {
    setLoading(true);
    try {
              const response = await fetch('/api/strategy/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          strategy_name: strategyConfig.name,
          strategy_config: strategyConfig
        }),
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Strategy ${strategyConfig.name} registered successfully!`);
        setStrategyConfig({
          name: '',
          type: 'momentum',
          parameters: {},
          indicators: [],
          timeframes: []
        });
        loadStrategies();
      }
    } catch (error) {
      console.error('Failed to register strategy:', error);
      alert('Failed to register strategy');
    } finally {
      setLoading(false);
    }
  };

  const executeStrategy = async (strategyName: string, symbol: string, timeframe: string) => {
    setLoading(true);
    try {
              const response = await fetch(`/api/strategy/execute/${strategyName}/${symbol}/${timeframe}`);
      if (response.ok) {
        const result = await response.json();
        console.log('Strategy execution result:', result);
        alert(`Strategy ${strategyName} executed successfully!`);
      }
    } catch (error) {
      console.error('Failed to execute strategy:', error);
      alert('Failed to execute strategy');
    } finally {
      setLoading(false);
    }
  };

  const backtestStrategy = async () => {
    setLoading(true);
    try {
              const response = await fetch('/api/strategy/backtest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(backtestConfig),
      });

      if (response.ok) {
        const result = await response.json();
        setBacktestResults([result, ...backtestResults]);
        alert('Backtest completed successfully!');
      }
    } catch (error) {
      console.error('Failed to backtest strategy:', error);
      alert('Failed to backtest strategy');
    } finally {
      setLoading(false);
    }
  };

  const optimizeStrategy = async () => {
    setLoading(true);
    try {
      const response = await fetch(
                  `/api/strategy/optimize/${optimizationConfig.strategy_name}/${optimizationConfig.symbol}/${optimizationConfig.timeframe}?optimization_days=${optimizationConfig.optimization_days}`
      );

      if (response.ok) {
        const result = await response.json();
        setOptimizationResults([result, ...optimizationResults]);
        alert('Strategy optimization completed successfully!');
      }
    } catch (error) {
      console.error('Failed to optimize strategy:', error);
      alert('Failed to optimize strategy');
    } finally {
      setLoading(false);
    }
  };

  const getIntegratedData = async (symbol: string, timeframe: string) => {
    try {
              const response = await fetch(`/api/strategy/integrated-data/${symbol}/${timeframe}`);
      if (response.ok) {
        const data = await response.json();
        console.log('Integrated data:', data);
        return data;
      }
    } catch (error) {
      console.error('Failed to get integrated data:', error);
    }
  };

  const updateStrategyConfig = (field: string, value: any) => {
    setStrategyConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const updateParameter = (param: string, value: any) => {
    setStrategyConfig(prev => ({
      ...prev,
      parameters: {
        ...prev.parameters,
        [param]: value
      }
    }));
  };

  const formatPerformance = (performance: any) => {
    return {
      'Total Return': `${(performance.total_return * 100).toFixed(2)}%`,
      'Sharpe Ratio': performance.sharpe_ratio.toFixed(3),
      'Max Drawdown': `${(performance.max_drawdown * 100).toFixed(2)}%`,
      'Win Rate': `${(performance.win_rate * 100).toFixed(1)}%`,
      'Total Trades': performance.total_trades
    };
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Strategy Development</h2>
        <div className="flex space-x-2">
          <button
            onClick={() => setActiveTab('build')}
            className={`px-4 py-2 rounded-lg font-medium ${
              activeTab === 'build'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Build Strategy
          </button>
          <button
            onClick={() => setActiveTab('test')}
            className={`px-4 py-2 rounded-lg font-medium ${
              activeTab === 'test'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Backtest
          </button>
          <button
            onClick={() => setActiveTab('optimize')}
            className={`px-4 py-2 rounded-lg font-medium ${
              activeTab === 'optimize'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Optimize
          </button>
          <button
            onClick={() => setActiveTab('integrated')}
            className={`px-4 py-2 rounded-lg font-medium ${
              activeTab === 'integrated'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Integrated Data
          </button>
        </div>
      </div>

      {/* System Status */}
      {systemStatus && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-lg font-semibold mb-2">System Status</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <span className="text-sm text-gray-600">Active Strategies:</span>
              <p className="font-medium">{systemStatus.active_strategies}</p>
            </div>
            <div>
              <span className="text-sm text-gray-600">Registered Strategies:</span>
              <p className="font-medium">{systemStatus.registered_strategies}</p>
            </div>
            <div>
              <span className="text-sm text-gray-600">Data Management AI:</span>
              <p className="font-medium text-green-600">Active</p>
            </div>
            <div>
              <span className="text-sm text-gray-600">Backup Sources:</span>
              <p className="font-medium text-green-600">Available</p>
            </div>
          </div>
        </div>
      )}

      {/* Build Strategy Tab */}
      {activeTab === 'build' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Strategy Name
              </label>
              <input
                type="text"
                value={strategyConfig.name}
                onChange={(e) => updateStrategyConfig('name', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter strategy name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Strategy Type
              </label>
              <select
                value={strategyConfig.type}
                onChange={(e) => updateStrategyConfig('type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {strategyTypes.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Indicators
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {availableIndicators.map(indicator => (
                <label key={indicator} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={strategyConfig.indicators.includes(indicator)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        updateStrategyConfig('indicators', [...strategyConfig.indicators, indicator]);
                      } else {
                        updateStrategyConfig('indicators', strategyConfig.indicators.filter(i => i !== indicator));
                      }
                    }}
                    className="mr-2"
                  />
                  {indicator}
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Timeframes
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {availableTimeframes.map(timeframe => (
                <label key={timeframe} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={strategyConfig.timeframes.includes(timeframe)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        updateStrategyConfig('timeframes', [...strategyConfig.timeframes, timeframe]);
                      } else {
                        updateStrategyConfig('timeframes', strategyConfig.timeframes.filter(t => t !== timeframe));
                      }
                    }}
                    className="mr-2"
                  />
                  {timeframe}
                </label>
              ))}
            </div>
          </div>

          {/* Strategy Parameters */}
          {strategyConfig.type === 'momentum' && (
            <div>
              <h4 className="text-lg font-medium mb-3">Momentum Strategy Parameters</h4>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Stochastic Period
                  </label>
                  <input
                    type="number"
                    value={strategyConfig.parameters.stoch_period || 14}
                    onChange={(e) => updateParameter('stoch_period', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    RSI Period
                  </label>
                  <input
                    type="number"
                    value={strategyConfig.parameters.rsi_period || 14}
                    onChange={(e) => updateParameter('rsi_period', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Stochastic Overbought
                  </label>
                  <input
                    type="number"
                    value={strategyConfig.parameters.stoch_overbought || 80}
                    onChange={(e) => updateParameter('stoch_overbought', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
            </div>
          )}

          <button
            onClick={registerStrategy}
            disabled={loading || !strategyConfig.name}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Registering...' : 'Register Strategy'}
          </button>
        </div>
      )}

      {/* Backtest Tab */}
      {activeTab === 'test' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Symbol
              </label>
              <input
                type="text"
                value={backtestConfig.symbol}
                onChange={(e) => setBacktestConfig(prev => ({ ...prev, symbol: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Timeframe
              </label>
              <select
                value={backtestConfig.timeframe}
                onChange={(e) => setBacktestConfig(prev => ({ ...prev, timeframe: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                {availableTimeframes.map(timeframe => (
                  <option key={timeframe} value={timeframe}>{timeframe}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Start Date
              </label>
              <input
                type="date"
                value={backtestConfig.start_date}
                onChange={(e) => setBacktestConfig(prev => ({ ...prev, start_date: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                End Date
              </label>
              <input
                type="date"
                value={backtestConfig.end_date}
                onChange={(e) => setBacktestConfig(prev => ({ ...prev, end_date: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>
          </div>

          <button
            onClick={backtestStrategy}
            disabled={loading || !backtestConfig.start_date || !backtestConfig.end_date}
            className="w-full bg-green-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Running Backtest...' : 'Run Backtest'}
          </button>

          {/* Backtest Results */}
          {backtestResults.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-4">Backtest Results</h3>
              <div className="space-y-4">
                {backtestResults.map((result, index) => (
                  <div key={index} className="p-4 border border-gray-200 rounded-lg">
                    <div className="flex justify-between items-center mb-3">
                      <h4 className="font-medium">{result.strategy_name}</h4>
                      <span className="text-sm text-gray-500">
                        {result.symbol} {result.timeframe}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                      {Object.entries(formatPerformance(result.performance)).map(([key, value]) => (
                        <div key={key}>
                          <span className="text-sm text-gray-600">{key}:</span>
                          <p className="font-medium">{value}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Optimize Tab */}
      {activeTab === 'optimize' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Strategy Name
              </label>
              <input
                type="text"
                value={optimizationConfig.strategy_name}
                onChange={(e) => setOptimizationConfig(prev => ({ ...prev, strategy_name: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                placeholder="Enter strategy name to optimize"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Symbol
              </label>
              <input
                type="text"
                value={optimizationConfig.symbol}
                onChange={(e) => setOptimizationConfig(prev => ({ ...prev, symbol: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Timeframe
              </label>
              <select
                value={optimizationConfig.timeframe}
                onChange={(e) => setOptimizationConfig(prev => ({ ...prev, timeframe: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                {availableTimeframes.map(timeframe => (
                  <option key={timeframe} value={timeframe}>{timeframe}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Optimization Days
              </label>
              <input
                type="number"
                value={optimizationConfig.optimization_days}
                onChange={(e) => setOptimizationConfig(prev => ({ ...prev, optimization_days: parseInt(e.target.value) }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                min="7"
                max="365"
              />
            </div>
          </div>

          <button
            onClick={optimizeStrategy}
            disabled={loading || !optimizationConfig.strategy_name}
            className="w-full bg-purple-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Optimizing...' : 'Optimize Strategy'}
          </button>

          {/* Optimization Results */}
          {optimizationResults.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-4">Optimization Results</h3>
              <div className="space-y-4">
                {optimizationResults.map((result, index) => (
                  <div key={index} className="p-4 border border-gray-200 rounded-lg">
                    <h4 className="font-medium mb-3">{result.strategy_name}</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h5 className="font-medium text-gray-700 mb-2">Original Performance</h5>
                        <div className="space-y-1">
                          {Object.entries(formatPerformance(result.original_performance)).map(([key, value]) => (
                            <div key={key} className="flex justify-between">
                              <span className="text-sm text-gray-600">{key}:</span>
                              <span className="font-medium">{value}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                      <div>
                        <h5 className="font-medium text-gray-700 mb-2">Optimized Performance</h5>
                        <div className="space-y-1">
                          {Object.entries(formatPerformance(result.optimized_performance)).map(([key, value]) => (
                            <div key={key} className="flex justify-between">
                              <span className="text-sm text-gray-600">{key}:</span>
                              <span className="font-medium text-green-600">{value}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                      <h6 className="font-medium text-blue-800 mb-2">Best Parameters</h6>
                      <pre className="text-sm text-blue-700">
                        {JSON.stringify(result.best_parameters, null, 2)}
                      </pre>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Integrated Data Tab */}
      {activeTab === 'integrated' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Symbol
              </label>
              <input
                type="text"
                defaultValue="EUR_GBP"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Timeframe
              </label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-lg">
                {availableTimeframes.map(timeframe => (
                  <option key={timeframe} value={timeframe}>{timeframe}</option>
                ))}
              </select>
            </div>
          </div>

          <button
            onClick={() => getIntegratedData('EUR_GBP', 'H1')}
            className="w-full bg-orange-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-orange-700"
          >
            Get Integrated Data
          </button>

          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium mb-2">Available Data Sources</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-white rounded-lg">
                <div className="text-2xl mb-1">🤖</div>
                <div className="text-sm font-medium">Data Management AI</div>
                <div className="text-xs text-green-600">Primary</div>
              </div>
              <div className="text-center p-3 bg-white rounded-lg">
                <div className="text-2xl mb-1">📊</div>
                <div className="text-sm font-medium">OANDA API</div>
                <div className="text-xs text-green-600">Backup</div>
              </div>
              <div className="text-center p-3 bg-white rounded-lg">
                <div className="text-2xl mb-1">⚡</div>
                <div className="text-sm font-medium">Free Forex API</div>
                <div className="text-xs text-green-600">Backup</div>
              </div>
              <div className="text-center p-3 bg-white rounded-lg">
                <div className="text-2xl mb-1">🔬</div>
                <div className="text-sm font-medium">Indicator AI</div>
                <div className="text-xs text-green-600">Analysis</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StrategyDevelopment; 