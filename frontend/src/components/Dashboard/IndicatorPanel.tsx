import React, { useState, useEffect } from 'react';

interface IndicatorPanelProps {
  onIndicatorToggle: (indicator: string, enabled: boolean, parameters?: any, overlay?: boolean) => void;
  activeIndicators: string[];
}

interface Indicator {
  name: string;
  label: string;
  color: string;
  description: string;
  category: string;
  overlay: boolean; // Whether indicator should be overlaid on main chart
  parameters?: Parameter[];
  defaultParams?: any;
}

interface Parameter {
  name: string;
  label: string;
  type: 'number' | 'float';
  defaultValue: number;
  min?: number;
  max?: number;
  step?: number;
}

// All available indicators organized by category
export const indicators: Indicator[] = [
  // Moving Averages
  {
    name: 'SMA',
    label: 'Simple Moving Average',
    color: '#3b82f6',
    description: 'Average of closing prices over a period',
    category: 'Moving Averages',
    overlay: true, // Overlay on main chart
    parameters: [
      { name: 'period', label: 'Period', type: 'number', defaultValue: 20, min: 1, max: 200, step: 1 }
    ],
    defaultParams: { period: 20 }
  },
  {
    name: 'EMA',
    label: 'Exponential Moving Average',
    color: '#10b981',
    description: 'Weighted average giving more importance to recent prices',
    category: 'Moving Averages',
    overlay: true, // Overlay on main chart
    parameters: [
      { name: 'period', label: 'Period', type: 'number', defaultValue: 20, min: 1, max: 200, step: 1 }
    ],
    defaultParams: { period: 20 }
  },
  
  // Oscillators
  {
    name: 'RSI',
    label: 'Relative Strength Index',
    color: '#f59e0b',
    description: 'Momentum oscillator measuring speed and change of price movements',
    category: 'Oscillators',
    overlay: false, // Separate subplot
    parameters: [
      { name: 'period', label: 'Period', type: 'number', defaultValue: 14, min: 1, max: 100, step: 1 }
    ],
    defaultParams: { period: 14 }
  },
  {
    name: 'Stochastic',
    label: 'Stochastic Oscillator',
    color: '#ef4444',
    description: 'Momentum indicator comparing closing price to price range',
    category: 'Oscillators',
    overlay: false, // Separate subplot
    parameters: [
      { name: 'k_period', label: 'K Period', type: 'number', defaultValue: 14, min: 1, max: 100, step: 1 },
      { name: 'd_period', label: 'D Period', type: 'number', defaultValue: 3, min: 1, max: 50, step: 1 }
    ],
    defaultParams: { k_period: 14, d_period: 3 }
  },
  {
    name: 'CCI',
    label: 'Commodity Channel Index',
    color: '#8b5cf6',
    description: 'Momentum oscillator measuring current price relative to average',
    category: 'Oscillators',
    overlay: false, // Separate subplot
    parameters: [
      { name: 'period', label: 'Period', type: 'number', defaultValue: 20, min: 1, max: 100, step: 1 }
    ],
    defaultParams: { period: 20 }
  },
  {
    name: 'Williams_R',
    label: 'Williams %R',
    color: '#f97316',
    description: 'Momentum oscillator measuring overbought/oversold levels',
    category: 'Oscillators',
    overlay: false, // Separate subplot
    parameters: [
      { name: 'period', label: 'Period', type: 'number', defaultValue: 14, min: 1, max: 100, step: 1 }
    ],
    defaultParams: { period: 14 }
  },
  {
    name: 'Momentum',
    label: 'Momentum',
    color: '#ec4899',
    description: 'Rate of change in price over a specified period',
    category: 'Oscillators',
    overlay: false, // Separate subplot
    parameters: [
      { name: 'period', label: 'Period', type: 'number', defaultValue: 10, min: 1, max: 100, step: 1 }
    ],
    defaultParams: { period: 10 }
  },
  {
    name: 'ROC',
    label: 'Rate of Change',
    color: '#06b6d4',
    description: 'Momentum oscillator measuring percentage change in price',
    category: 'Oscillators',
    overlay: false, // Separate subplot
    parameters: [
      { name: 'period', label: 'Period', type: 'number', defaultValue: 10, min: 1, max: 100, step: 1 }
    ],
    defaultParams: { period: 10 }
  },
  
  // Volatility
  {
    name: 'Bollinger_Bands',
    label: 'Bollinger Bands',
    color: '#6366f1',
    description: 'Volatility indicator with upper and lower bands around moving average',
    category: 'Volatility',
    overlay: true, // Overlay on main chart
    parameters: [
      { name: 'period', label: 'Period', type: 'number', defaultValue: 20, min: 1, max: 100, step: 1 },
      { name: 'std_dev', label: 'Std Dev', type: 'float', defaultValue: 2.0, min: 0.1, max: 5.0, step: 0.1 }
    ],
    defaultParams: { period: 20, std_dev: 2.0 }
  },
  {
    name: 'ATR',
    label: 'Average True Range',
    color: '#84cc16',
    description: 'Volatility indicator measuring market volatility',
    category: 'Volatility',
    overlay: false, // Separate subplot
    parameters: [
      { name: 'period', label: 'Period', type: 'number', defaultValue: 14, min: 1, max: 100, step: 1 }
    ],
    defaultParams: { period: 14 }
  },
  
  // Trend
  {
    name: 'MACD',
    label: 'MACD',
    color: '#8b5cf6',
    description: 'Moving Average Convergence Divergence - Trend-following momentum indicator',
    category: 'Trend',
    overlay: false, // Separate subplot
    parameters: [
      { name: 'fast', label: 'Fast Period', type: 'number', defaultValue: 12, min: 1, max: 100, step: 1 },
      { name: 'slow', label: 'Slow Period', type: 'number', defaultValue: 26, min: 1, max: 100, step: 1 },
      { name: 'signal', label: 'Signal Period', type: 'number', defaultValue: 9, min: 1, max: 50, step: 1 }
    ],
    defaultParams: { fast: 12, slow: 26, signal: 9 }
  },
  {
    name: 'ADX',
    label: 'Average Directional Index',
    color: '#f59e0b',
    description: 'Trend strength indicator',
    category: 'Trend',
    overlay: false, // Separate subplot
    parameters: [
      { name: 'period', label: 'Period', type: 'number', defaultValue: 14, min: 1, max: 100, step: 1 }
    ],
    defaultParams: { period: 14 }
  },
  {
    name: 'Parabolic_SAR',
    label: 'Parabolic SAR',
    color: '#ef4444',
    description: 'Trend-following indicator for stop-loss placement',
    category: 'Trend',
    overlay: true, // Overlay on main chart
    parameters: [
      { name: 'acceleration', label: 'Acceleration', type: 'float', defaultValue: 0.02, min: 0.01, max: 0.5, step: 0.01 },
      { name: 'maximum', label: 'Maximum', type: 'float', defaultValue: 0.2, min: 0.1, max: 1.0, step: 0.1 }
    ],
    defaultParams: { acceleration: 0.02, maximum: 0.2 }
  },
  {
    name: 'Ichimoku',
    label: 'Ichimoku Cloud',
    color: '#06b6d4',
    description: 'Comprehensive indicator showing support, resistance, momentum, and trend',
    category: 'Trend',
    overlay: true, // Overlay on main chart
    parameters: [
      { name: 'tenkan', label: 'Tenkan', type: 'number', defaultValue: 9, min: 1, max: 50, step: 1 },
      { name: 'kijun', label: 'Kijun', type: 'number', defaultValue: 26, min: 1, max: 100, step: 1 },
      { name: 'senkou_b', label: 'Senkou B', type: 'number', defaultValue: 52, min: 1, max: 200, step: 1 }
    ],
    defaultParams: { tenkan: 9, kijun: 26, senkou_b: 52 }
  },
  
  // Volume
  {
    name: 'OBV',
    label: 'On Balance Volume',
    color: '#84cc16',
    description: 'Volume-based indicator measuring buying and selling pressure',
    category: 'Volume',
    overlay: false, // Separate subplot
    parameters: [],
    defaultParams: {}
  },
  {
    name: 'VWAP',
    label: 'VWAP',
    color: '#f97316',
    description: 'Volume Weighted Average Price - Average price weighted by volume',
    category: 'Volume',
    overlay: true, // Overlay on main chart
    parameters: [],
    defaultParams: {}
  },
  
  // Support/Resistance
  {
    name: 'Session_Levels',
    label: 'Session Levels',
    color: '#8b5cf6',
    description: 'Rolling high and low levels over a time window',
    category: 'Support/Resistance',
    overlay: true, // Overlay on main chart
    parameters: [
      { name: 'window', label: 'Window', type: 'number', defaultValue: 96, min: 1, max: 500, step: 1 },
      { name: 'min_periods', label: 'Min Periods', type: 'number', defaultValue: 1, min: 1, max: 100, step: 1 }
    ],
    defaultParams: { window: 96, min_periods: 1 }
  },
  {
    name: 'Pivot_Points',
    label: 'Pivot Points',
    color: '#06b6d4',
    description: 'Traditional Pivot Points - Support and resistance levels',
    category: 'Support/Resistance',
    overlay: true, // Overlay on main chart
    parameters: [],
    defaultParams: {}
  }
];

// Group indicators by category
const groupedIndicators = indicators.reduce((acc, indicator) => {
  if (!acc[indicator.category]) {
    acc[indicator.category] = [];
  }
  acc[indicator.category].push(indicator);
  return acc;
}, {} as Record<string, Indicator[]>);

const IndicatorPanel: React.FC<IndicatorPanelProps> = ({
  onIndicatorToggle,
  activeIndicators
}) => {
  const [expanded, setExpanded] = useState(false);
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());
  const [indicatorParams, setIndicatorParams] = useState<Record<string, any>>({});
  const [indicatorOverlays, setIndicatorOverlays] = useState<Record<string, boolean>>({});
  const [editingIndicator, setEditingIndicator] = useState<string | null>(null);

  const handleToggle = (indicatorName: string) => {
    const isActive = activeIndicators.includes(indicatorName);
    const params = indicatorParams[indicatorName] || getDefaultParameters(indicatorName);
    const overlay = indicatorOverlays[indicatorName] ?? getDefaultOverlay(indicatorName);
    onIndicatorToggle(indicatorName, !isActive, params, overlay);
  };

  const getDefaultParameters = (indicatorName: string) => {
    const indicator = indicators.find(i => i.name === indicatorName);
    return indicator?.defaultParams || {};
  };

  const getDefaultOverlay = (indicatorName: string) => {
    const indicator = indicators.find(i => i.name === indicatorName);
    return indicator?.overlay ?? true;
  };

  const handleOverlayToggle = (indicatorName: string) => {
    const newOverlay = !(indicatorOverlays[indicatorName] ?? getDefaultOverlay(indicatorName));
    
    // Update local state
    setIndicatorOverlays(prev => ({
      ...prev,
      [indicatorName]: newOverlay
    }));
    
    // If indicator is active, immediately apply the overlay change
    if (activeIndicators.includes(indicatorName)) {
      const params = indicatorParams[indicatorName] || getDefaultParameters(indicatorName);
      onIndicatorToggle(indicatorName, true, params, newOverlay);
    }
  };

  const handleParameterChange = (indicatorName: string, paramName: string, value: number) => {
    setIndicatorParams(prev => ({
      ...prev,
      [indicatorName]: {
        ...prev[indicatorName],
        [paramName]: value
      }
    }));
  };

  const handleApplyParameters = (indicatorName: string) => {
    const params = indicatorParams[indicatorName] || getDefaultParameters(indicatorName);
    const overlay = indicatorOverlays[indicatorName] ?? getDefaultOverlay(indicatorName);
    onIndicatorToggle(indicatorName, true, params, overlay);
    setEditingIndicator(null);
  };

  const toggleCategory = (category: string) => {
    setExpandedCategories(prev => {
      const newSet = new Set(prev);
      if (newSet.has(category)) {
        newSet.delete(category);
      } else {
        newSet.add(category);
      }
      return newSet;
    });
  };

  const renderParameterInputs = (indicator: Indicator) => {
    if (!indicator.parameters || indicator.parameters.length === 0) {
      return null;
    }

    return (
      <div className="mt-2 space-y-2">
        {indicator.parameters.map(param => (
          <div key={param.name} className="flex items-center space-x-2">
            <label className="text-xs text-gray-600 min-w-0 flex-1">
              {param.label}:
            </label>
            <input
              type="number"
              min={param.min}
              max={param.max}
              step={param.step}
              value={indicatorParams[indicator.name]?.[param.name] ?? param.defaultValue}
              onChange={(e) => handleParameterChange(indicator.name, param.name, Number(e.target.value))}
              className="w-16 text-xs border border-gray-300 rounded px-1 py-0.5"
            />
          </div>
        ))}
        <button
          onClick={() => handleApplyParameters(indicator.name)}
          className="w-full text-xs bg-blue-600 text-white rounded px-2 py-1 hover:bg-blue-700"
        >
          Apply
        </button>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200">
      <div className="p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-800">Technical Indicators</h3>
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            {expanded ? 'Show Less' : 'Show More'}
          </button>
        </div>

        <div className="space-y-4">
          {Object.entries(groupedIndicators).map(([category, categoryIndicators]) => (
            <div key={category} className="border border-gray-200 rounded-lg">
              <button
                onClick={() => toggleCategory(category)}
                className="w-full p-3 text-left bg-gray-50 hover:bg-gray-100 flex items-center justify-between"
              >
                <span className="font-medium text-gray-900">{category}</span>
                <span className="text-gray-500">
                  {expandedCategories.has(category) ? '▼' : '▶'}
                </span>
              </button>
              
              {expandedCategories.has(category) && (
                <div className="p-3 space-y-3">
                  {categoryIndicators.map((indicator) => {
            const isActive = activeIndicators.includes(indicator.name);
                    const isEditing = editingIndicator === indicator.name;
                    
            return (
                      <div key={indicator.name} className="border border-gray-200 rounded-lg p-3">
                        <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: indicator.color }}
                  />
                  <div>
                    <div className="font-medium text-gray-900">{indicator.label}</div>
                      <div className="text-xs text-gray-600">{indicator.description}</div>
                  </div>
                </div>
                          <div className="flex items-center space-x-2">
                            {/* Overlay Toggle */}
                            <div className="flex items-center space-x-1">
                              <span className="text-xs text-gray-600">Overlay:</span>
                              <label className="relative inline-flex items-center cursor-pointer">
                                <input
                                  type="checkbox"
                                  checked={indicatorOverlays[indicator.name] ?? indicator.overlay}
                                  onChange={() => handleOverlayToggle(indicator.name)}
                                  className="sr-only peer"
                                />
                                <div className="w-8 h-4 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[1px] after:left-[1px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-3 after:w-3 after:transition-all peer-checked:bg-blue-600"></div>
                              </label>
                            </div>
                            
                            {indicator.parameters && indicator.parameters.length > 0 && (
                              <button
                                onClick={() => setEditingIndicator(isEditing ? null : indicator.name)}
                                className="text-xs text-blue-600 hover:text-blue-800"
                              >
                                {isEditing ? 'Cancel' : 'Settings'}
                              </button>
                            )}
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isActive}
                    onChange={() => handleToggle(indicator.name)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
                          </div>
                        </div>
                        
                        {isEditing && renderParameterInputs(indicator)}
              </div>
            );
          })}
                </div>
              )}
            </div>
          ))}
        </div>

        {!expanded && (
          <div className="mt-3 text-center">
            <span className="text-sm text-gray-600">
              Click "Show More" to see all {indicators.length} indicators
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default IndicatorPanel; 