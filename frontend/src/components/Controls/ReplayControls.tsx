import React, { useState, useEffect } from 'react';
import { replayService, ReplayState, ReplayEngineState, ReplayPerformance } from '../../services/replayService';

interface ReplayControlsProps {
  symbol: string;
  timeframe: string;
  isPlaying: boolean;
  currentIndex: number;
  totalCandles: number;
  speed: number;
  onPlay: () => void;
  onPause: () => void;
  onStepForward: () => void;
  onStepBackward: () => void;
  onSpeedChange: (speed: number) => void;
  onReset: () => void;
}

const ReplayControls: React.FC<ReplayControlsProps> = ({
  symbol,
  timeframe,
  isPlaying,
  currentIndex,
  totalCandles,
  speed,
  onPlay,
  onPause,
  onStepForward,
  onStepBackward,
  onSpeedChange,
  onReset,
}) => {
  const [replayState, setReplayState] = useState<ReplayState | null>(null);
  const [engineState, setEngineState] = useState<ReplayEngineState | null>(null);
  const [performance, setPerformance] = useState<ReplayPerformance | null>(null);
  const [autoTrade, setAutoTrade] = useState(false);
  const [riskManagement, setRiskManagement] = useState(true);
  const [loading, setLoading] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const progress = totalCandles > 0 ? (currentIndex / totalCandles) * 100 : 0;

  // Sync with backend replay engine
  useEffect(() => {
    const syncReplayState = async () => {
      try {
        const state = await replayService.getReplayState(symbol, timeframe, currentIndex, isPlaying, speed);
        if (state) {
          setReplayState(state);
        }

        const engineState = await replayService.getReplayEngineState();
        if (engineState) {
          setEngineState(engineState);
          setAutoTrade(engineState.auto_trade);
          setRiskManagement(engineState.risk_management);
        }

        const perf = await replayService.getPerformance();
        if (perf) {
          setPerformance(perf);
        }
      } catch (error) {
        console.error('Error syncing replay state:', error);
      }
    };

    syncReplayState();
    const interval = setInterval(syncReplayState, 2000); // Sync every 2 seconds

    return () => clearInterval(interval);
  }, [symbol, timeframe, currentIndex, isPlaying, speed]);

  const handlePlay = async () => {
    setLoading(true);
    try {
      const success = await replayService.playReplay();
      if (success) {
        onPlay();
      }
    } catch (error) {
      console.error('Error starting replay:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePause = async () => {
    setLoading(true);
    try {
      const success = await replayService.pauseReplay();
      if (success) {
        onPause();
      }
    } catch (error) {
      console.error('Error pausing replay:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStepForward = async () => {
    setLoading(true);
    try {
      const success = await replayService.stepForward();
      if (success) {
        onStepForward();
      }
    } catch (error) {
      console.error('Error stepping forward:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStepBackward = async () => {
    setLoading(true);
    try {
      const success = await replayService.stepBackward();
      if (success) {
        onStepBackward();
      }
    } catch (error) {
      console.error('Error stepping backward:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSpeedChange = async (newSpeed: number) => {
    setLoading(true);
    try {
      const success = await replayService.setSpeed(newSpeed);
      if (success) {
        onSpeedChange(newSpeed);
      }
    } catch (error) {
      console.error('Error setting speed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleAutoTrade = async () => {
    setLoading(true);
    try {
      const result = await replayService.toggleAutoTrade();
      if (result) {
        setAutoTrade(result.auto_trade);
      }
    } catch (error) {
      console.error('Error toggling auto trade:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleRiskManagement = async () => {
    setLoading(true);
    try {
      const result = await replayService.toggleRiskManagement();
      if (result) {
        setRiskManagement(result.risk_management);
      }
    } catch (error) {
      console.error('Error toggling risk management:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSimulateStrategy = async () => {
    setLoading(true);
    try {
      await replayService.simulateStrategy();
    } catch (error) {
      console.error('Error simulating strategy:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow-md border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Replay Controls</h3>
        <div className="text-sm text-gray-600">
          {currentIndex} / {totalCandles} candles
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Control Buttons */}
      <div className="flex items-center space-x-2 mb-4">
        <button
          onClick={handleStepBackward}
          disabled={loading}
          className="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-gray-700 transition-colors disabled:opacity-50"
          title="Step Backward"
        >
          ⏮️
        </button>
        
        <button
          onClick={isPlaying ? handlePause : handlePlay}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50"
          title={isPlaying ? "Pause" : "Play"}
        >
          {isPlaying ? "⏸️ Pause" : "▶️ Play"}
        </button>
        
        <button
          onClick={handleStepForward}
          disabled={loading}
          className="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-gray-700 transition-colors disabled:opacity-50"
          title="Step Forward"
        >
          ⏭️
        </button>
        
        <button
          onClick={onReset}
          disabled={loading}
          className="px-3 py-2 bg-red-100 hover:bg-red-200 rounded-lg text-red-700 transition-colors disabled:opacity-50"
          title="Reset"
        >
          🔄 Reset
        </button>
      </div>

      {/* Speed Control */}
      <div className="flex items-center space-x-3 mb-4">
        <span className="text-sm font-medium text-gray-700">Speed:</span>
        <div className="flex space-x-1">
          {[0.25, 0.5, 1, 2, 4].map((speedOption) => (
            <button
              key={speedOption}
              onClick={() => handleSpeedChange(speedOption)}
              disabled={loading}
              className={`px-2 py-1 rounded text-xs font-medium transition-colors disabled:opacity-50 ${
                speed === speedOption
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {speedOption}x
            </button>
          ))}
        </div>
      </div>

      {/* Advanced Controls Toggle */}
      <div className="mb-4">
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          {showAdvanced ? '▼' : '▶'} Advanced Controls
        </button>
      </div>

      {/* Advanced Controls */}
      {showAdvanced && (
        <div className="space-y-3 p-3 bg-gray-50 rounded-lg">
          {/* Auto Trade Toggle */}
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Auto Trade:</span>
            <button
              onClick={handleToggleAutoTrade}
              disabled={loading}
              className={`px-3 py-1 rounded text-xs font-medium transition-colors disabled:opacity-50 ${
                autoTrade
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-300 text-gray-700'
              }`}
            >
              {autoTrade ? 'ON' : 'OFF'}
            </button>
          </div>

          {/* Risk Management Toggle */}
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Risk Management:</span>
            <button
              onClick={handleToggleRiskManagement}
              disabled={loading}
              className={`px-3 py-1 rounded text-xs font-medium transition-colors disabled:opacity-50 ${
                riskManagement
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-300 text-gray-700'
              }`}
            >
              {riskManagement ? 'ON' : 'OFF'}
            </button>
          </div>

          {/* Strategy Simulation */}
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Strategy:</span>
            <button
              onClick={handleSimulateStrategy}
              disabled={loading}
              className="px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white rounded text-xs font-medium transition-colors disabled:opacity-50"
            >
              Simulate
            </button>
          </div>

          {/* Performance Summary */}
          {performance && (
            <div className="mt-3 p-2 bg-white rounded border">
              <h4 className="text-xs font-semibold text-gray-700 mb-2">Performance Summary</h4>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-gray-600">Trades:</span>
                  <span className="ml-1 font-medium">{performance.total_trades}</span>
                </div>
                <div>
                  <span className="text-gray-600">Win Rate:</span>
                  <span className="ml-1 font-medium">{(performance.win_rate * 100).toFixed(1)}%</span>
                </div>
                <div>
                  <span className="text-gray-600">P&L:</span>
                  <span className={`ml-1 font-medium ${performance.total_profit_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {performance.total_profit_loss.toFixed(2)}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Drawdown:</span>
                  <span className="ml-1 font-medium text-red-600">{performance.max_drawdown.toFixed(2)}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Loading Indicator */}
      {loading && (
        <div className="mt-2 text-center">
          <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-xs text-gray-600">Processing...</span>
        </div>
      )}
    </div>
  );
};

export default ReplayControls; 