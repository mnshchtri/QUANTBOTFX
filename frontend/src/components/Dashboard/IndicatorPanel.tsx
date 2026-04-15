import React, { useState, useEffect } from 'react';
import { 
  PlusIcon, 
  MinusIcon, 
  AdjustmentsHorizontalIcon,
  ChartBarIcon,
  VariableIcon,
  ArrowTrendingUpIcon,
  ArrowsRightLeftIcon,
  PresentationChartLineIcon
} from '@heroicons/react/24/outline';

interface IndicatorPanelProps {
  onIndicatorToggle: (indicator: string, enabled: boolean, parameters?: any, overlay?: boolean) => void;
  activeIndicators: string[];
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

interface Indicator {
  name: string;
  label: string;
  color: string;
  description: string;
  category: string;
  overlay: boolean;
  parameters?: Parameter[];
  defaultParams?: any;
}

export const indicators: Indicator[] = [
  // Moving Averages
  {
    name: 'SMA',
    label: 'Simple Moving Average',
    color: '#3b82f6',
    description: 'Price average over period',
    category: 'Trend',
    overlay: true,
    parameters: [{ name: 'period', label: 'Period', type: 'number', defaultValue: 20, min: 1, max: 200, step: 1 }],
    defaultParams: { period: 20 }
  },
  {
    name: 'EMA',
    label: 'Exponential MA',
    color: '#10b981',
    description: 'Weighted average giving more importance to recent prices',
    category: 'Trend',
    overlay: true,
    parameters: [{ name: 'period', label: 'Period', type: 'number', defaultValue: 20, min: 1, max: 200, step: 1 }],
    defaultParams: { period: 20 }
  },
  {
    name: 'RSI',
    label: 'Relative Strength Index',
    color: '#f97316',
    description: 'Momentum oscillator measuring speed and change of price movements',
    category: 'Oscillators',
    overlay: false,
    parameters: [{ name: 'period', label: 'Period', type: 'number', defaultValue: 14, min: 1, max: 100, step: 1 }],
    defaultParams: { period: 14 }
  },
  {
    name: 'MACD',
    label: 'MACD',
    color: '#8b5cf6',
    description: 'Trend-following momentum indicator',
    category: 'Trend',
    overlay: false,
    parameters: [
      { name: 'fast', label: 'Fast Period', type: 'number', defaultValue: 12 },
      { name: 'slow', label: 'Slow Period', type: 'number', defaultValue: 26 },
      { name: 'signal', label: 'Signal', type: 'number', defaultValue: 9 }
    ],
    defaultParams: { fast: 12, slow: 26, signal: 9 }
  },
  {
    name: 'Bollinger_Bands',
    label: 'Bollinger Bands',
    color: '#6366f1',
    description: 'Volatility bands around moving average',
    category: 'Volatility',
    overlay: true,
    parameters: [
      { name: 'period', label: 'Period', type: 'number', defaultValue: 20 },
      { name: 'std_dev', label: 'Std Dev', type: 'float', defaultValue: 2.0 }
    ],
    defaultParams: { period: 20, std_dev: 2.0 }
  }
];

const categoryIcons: Record<string, any> = {
  'Trend': ArrowTrendingUpIcon,
  'Oscillators': VariableIcon,
  'Volatility': PresentationChartLineIcon,
  'Volume': ChartBarIcon,
  'Support/Resistance': ArrowsRightLeftIcon
};

const IndicatorPanel: React.FC<IndicatorPanelProps> = ({ onIndicatorToggle, activeIndicators }) => {
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set(['Trend']));

  const toggleCategory = (category: string) => {
    setExpandedCategories(prev => {
      const next = new Set(prev);
      if (next.has(category)) next.delete(category);
      else next.add(category);
      return next;
    });
  };

  const groupedIndicators = indicators.reduce((acc, indicator) => {
    if (!acc[indicator.category]) acc[indicator.category] = [];
    acc[indicator.category].push(indicator);
    return acc;
  }, {} as Record<string, Indicator[]>);

  return (
    <div className="glass rounded-2xl overflow-hidden border border-[var(--border-subtle)] flex flex-col h-[500px]">
      <div className="p-4 border-b border-[var(--border-subtle)] flex items-center justify-between">
        <div className="panel-header mb-0 flex items-center gap-2">
          <AdjustmentsHorizontalIcon className="w-4 h-4" />
          <span>Technical Indicators</span>
        </div>
        <span className="text-[10px] bg-blue-500/10 text-blue-400 px-2 py-0.5 rounded-full font-bold">
          {activeIndicators.length} ACTIVE
        </span>
      </div>

      <div className="flex-1 overflow-y-auto px-2 py-3 space-y-2">
        {Object.entries(groupedIndicators).map(([category, items]) => {
          const Icon = categoryIcons[category] || ChartBarIcon;
          const isExpanded = expandedCategories.has(category);
          return (
            <div key={category} className="space-y-0.5">
              <button 
                onClick={() => toggleCategory(category)}
                className="w-full flex items-center justify-between px-3 py-1.5 rounded-lg hover:bg-white/5 transition-colors group"
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-4 h-4 text-[var(--text-muted)] group-hover:text-[var(--text-main)]" />
                  <span className="text-xs font-bold text-[var(--text-main)] uppercase tracking-wider">{category}</span>
                </div>
                {isExpanded ? <MinusIcon className="w-3 h-3 text-[var(--text-muted)]" /> : <PlusIcon className="w-3 h-3 text-[var(--text-muted)]" />}
              </button>

              {isExpanded && (
                <div className="space-y-1 ml-4 pl-4 border-l border-[var(--border-subtle)]">
                  {items.map((ind) => {
                    const isActive = activeIndicators.includes(ind.name);
                    return (
                      <div key={ind.name} className="flex flex-col gap-2 p-2 rounded-lg hover:bg-white/5 group/ind">
                        <div className="flex items-center justify-between">
                          <div className="flex flex-col">
                            <span className="text-xs font-semibold group-hover/ind:text-blue-400 transition-colors">{ind.name}</span>
                            <span className="text-[10px] text-[var(--text-muted)] truncate max-w-[120px]">{ind.description}</span>
                          </div>
                          <button
                            onClick={() => onIndicatorToggle(ind.name, !isActive, ind.defaultParams, ind.overlay)}
                            className={`w-8 h-4 rounded-full relative transition-colors ${isActive ? 'bg-blue-500' : 'bg-gray-700'}`}
                          >
                            <div className={`absolute top-0.5 w-3 h-3 rounded-full bg-white transition-all ${isActive ? 'translate-x-4' : 'translate-x-0.5'}`} />
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default IndicatorPanel;