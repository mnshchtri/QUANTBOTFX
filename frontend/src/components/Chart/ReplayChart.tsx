import * as React from 'react';
import { useState, useEffect, useMemo } from 'react';

// Import Plotly dynamically
let Plot: any = null;
if (typeof window !== 'undefined') {
  Plot = require('react-plotly.js').default;
}

export interface CandleData {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

export interface SignalData {
  index: number;
  timestamp: number;
  type: 'buy' | 'sell';
  price: number;
  confidence: number;
  reason: string;
}

interface ReplayState {
  is_playing: boolean;
  current_index: number;
  total_candles: number;
  speed_multiplier: number;
  current_date: string;
}

interface ReplayChartProps {
  data: CandleData[];
  signals?: SignalData[];
  timeframe: string;
  symbol: string;
  replayState?: ReplayState;
  onReplayControl: (action: string, value?: any) => void;
  showLevels?: boolean;
}

const ReplayChart: React.FC<ReplayChartProps> = ({
  data,
  signals = [],
  timeframe,
  symbol,
  replayState,
  onReplayControl,
  showLevels = true,
}) => {
  console.log('🎯 ReplayChart received props:', { 
    dataLength: data?.length, 
    dataSample: data?.slice(0, 2),
    timeframe,
    symbol,
    replayState: replayState ? {
      current_index: replayState.current_index,
      is_playing: replayState.is_playing,
      total_candles: replayState.total_candles
    } : null
  });

  const [loading] = useState(false);
  // Chart interaction state management
  const [chartLayout, setChartLayout] = useState<{
    'xaxis.range'?: [number, number];
    'yaxis.range'?: [number, number];
    'xaxis.autorange'?: boolean;
    'yaxis.autorange'?: boolean;
  }>({});

  // Update replay position when state changes
  useEffect(() => {
    if (replayState?.is_playing && replayState?.current_index !== undefined) {
      console.log(`Replay position updated: ${replayState.current_index}`);
    }
  }, [replayState?.current_index, replayState?.is_playing]);

  // Chart data preparation with progressive replay
  const chartData = useMemo(() => {
    console.log('🔄 Processing chart data:', { 
      dataLength: data?.length, 
      replayPlaying: replayState?.is_playing,
      currentIndex: replayState?.current_index,
      dataSample: data?.slice(0, 2)
    });
    
    if (!data || data.length === 0) {
      console.log('❌ No data available for chart');
      return [];
    }

    // Progressive replay: show candles up to current position (whether playing or paused)
    let displayData = data;
    if (replayState?.current_index !== undefined && replayState.current_index < data.length - 1) {
      // Show only candles up to current position (whether playing or paused)
      displayData = data.slice(0, replayState.current_index + 1);
      console.log(`🎬 Replay position ${replayState.current_index}: showing ${displayData.length} candles (playing: ${replayState.is_playing})`);
    } else {
      console.log(`📊 Full view: showing all ${data.length} candles`);
    }

    const traces: any[] = [
      // Candlestick chart (using working TradingDashboard configuration)
      {
        x: displayData.map((_, index) => index), // Continuous indices for even spacing
        open: displayData.map(d => d.open),
        high: displayData.map(d => d.high),
        low: displayData.map(d => d.low),
        close: displayData.map(d => d.close),
        type: 'candlestick',
        name: `${symbol} (${timeframe})`,
        increasing: { line: { color: '#10b981' }, fillcolor: '#10b981' },
        decreasing: { line: { color: '#ef4444' }, fillcolor: '#ef4444' },
        customdata: displayData.map(d => d.timestamp), // Keep timestamps for hover (same as TradingDashboard)
        hovertemplate: '<b>%{customdata|%Y-%m-%d %H:%M}</b><br>Open: %{open}<br>High: %{high}<br>Low: %{low}<br>Close: %{close}<extra></extra>'
      }
    ];

    // Add signals if available (progressive for replay)
    if (signals && signals.length > 0) {
      // Filter signals based on replay position (whether playing or paused)
      let visibleSignals = signals;
      if (replayState?.current_index !== undefined && replayState.current_index < data.length - 1) {
        // Only show signals up to current position
        visibleSignals = signals.filter(signal => {
          const signalIndex = data.findIndex(d => d.timestamp === signal.timestamp);
          return signalIndex <= replayState.current_index;
        });
        console.log(`🎯 Replay signals: showing ${visibleSignals.length} / ${signals.length} signals up to index ${replayState.current_index}`);
      }

      const buySignals = visibleSignals.filter(s => s.type === 'buy').map(signal => {
        const signalIndex = data.findIndex(d => d.timestamp === signal.timestamp);
        return {
          x: [signalIndex],
          y: [signal.price],
          type: 'scatter',
          mode: 'markers',
          marker: {
            symbol: 'triangle-up',
            size: 12,
            color: '#10b981',
            line: { width: 2, color: '#059669' }
          },
          name: 'Buy Signal',
          text: `Buy: ${signal.reason} (${signal.confidence}%)`,
          hoverinfo: 'text'
        };
      });

      const sellSignals = visibleSignals.filter(s => s.type === 'sell').map(signal => {
        const signalIndex = data.findIndex(d => d.timestamp === signal.timestamp);
        return {
          x: [signalIndex],
          y: [signal.price],
          type: 'scatter',
          mode: 'markers',
          marker: {
            symbol: 'triangle-down',
            size: 12,
            color: '#ef4444',
            line: { width: 2, color: '#dc2626' }
          },
          name: 'Sell Signal',
          text: `Sell: ${signal.reason} (${signal.confidence}%)`,
          hoverinfo: 'text'
        };
      });

      console.log('📊 Chart traces with signals:', { 
        totalTraces: [...traces, ...buySignals, ...sellSignals].length,
        candlestickTrace: traces[0],
        signalsCount: buySignals.length + sellSignals.length
      });
      return [...traces, ...buySignals, ...sellSignals];
    }

    console.log('📊 Chart traces without signals:', { 
      totalTraces: traces.length,
      candlestickTrace: traces[0]
    });
    return traces;
  }, [data, signals, symbol, timeframe, replayState?.is_playing, replayState?.current_index]);

  // Chart layout configuration
  const layout = useMemo(() => {
    // Calculate price range for better y-axis
    const prices = data.flatMap(d => [d.open, d.high, d.low, d.close]);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const priceRange = maxPrice - minPrice;
    const padding = priceRange * 0.1; // 10% padding
    
    const baseLayout = {
      title: `${symbol} Replay Chart (${timeframe})`,
      xaxis: {
        title: 'Candles',
        showgrid: true,
        gridcolor: '#f3f4f6',
        type: 'linear',
        rangeslider: { visible: false },
        tickmode: 'auto',
        nticks: 10,
        autorange: chartLayout['xaxis.range'] ? false : true,
        range: chartLayout['xaxis.range'] || undefined
      },
      yaxis: {
        title: 'Price',
        side: 'left',
        showgrid: true,
        gridcolor: '#f3f4f6',
        range: chartLayout['yaxis.range'] || [minPrice - padding, maxPrice + padding],
        tickformat: '.4f',
        zeroline: false,
        autorange: chartLayout['yaxis.range'] ? false : true
      },
      plot_bgcolor: '#ffffff',
      paper_bgcolor: '#ffffff',
      font: { color: '#374151' },
      legend: {
        x: 0.02,
        y: 0.98,
        bgcolor: 'rgba(255,255,255,0.8)',
        bordercolor: '#d1d5db',
        borderwidth: 1
      },
      margin: { l: 60, r: 60, t: 60, b: 60 },
      height: 700
    };

    return baseLayout;
  }, [symbol, timeframe, chartLayout, data]);

  // Chart configuration
  const config = {
    displayModeBar: true,
    modeBarButtonsToRemove: ['lasso2d', 'select2d'],
    displaylogo: false,
    responsive: true,
    scrollZoom: false // Disable scroll zoom, pan is default (same as TradingDashboard)
  };

  // Handle chart relayout (zoom/pan)
  const handleChartRelayout = (eventData: any) => {
    console.log('Chart relayout event:', eventData);
    setChartLayout({
      'xaxis.range': eventData['xaxis.range'],
      'yaxis.range': eventData['yaxis.range'],
      'xaxis.autorange': eventData['xaxis.autorange'],
      'yaxis.autorange': eventData['yaxis.autorange']
    });
  };

  if (loading) {
    return (
      <div className="bg-white p-8 rounded-lg shadow-md border border-gray-200">
        <div className="text-center">
          <div className="text-blue-500 text-lg mb-2">Loading replay data...</div>
          <div className="text-gray-400 text-sm">Initializing replay session</div>
        </div>
      </div>
    );
  }

  if (!Plot) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-900 rounded-lg">
        <div className="text-white text-lg">Loading chart component...</div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-white p-8 rounded-lg shadow-md border border-gray-200">
        <div className="text-center">
          <div className="text-gray-500 text-lg mb-2">No replay data available</div>
          <div className="text-gray-400 text-sm">Unable to load chart data</div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white p-4 rounded-lg shadow-md border border-gray-200">
      {/* Data Source Info */}
      <div className="mb-4 flex items-center justify-between">
        <div className="text-sm text-gray-600">
          Data Source: <span className="font-medium">Replay Engine</span>
        </div>
        <div className="text-sm text-gray-600">
          Displaying {data.length} candles
          {replayState && (
            <span className="ml-2">
              • Position: {replayState.current_index + 1} / {replayState.total_candles}
              {replayState.is_playing ? ' (▶️ Playing)' : ' (⏸️ Paused)'}
            </span>
          )}
        </div>
      </div>
      




      {/* Chart Container */}
      
      <Plot
        data={chartData}
        layout={layout}
        config={config}
        style={{ width: '100%', height: '700px' }}
        useResizeHandler={true}
        onRelayout={handleChartRelayout}
      />

      {/* Chart Legend */}
      <div className="mt-6 flex items-center justify-center space-x-6 text-sm">
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-green-500 rounded"></div>
          <span>Bullish Candles</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-red-500 rounded"></div>
          <span>Bearish Candles</span>
        </div>

        {signals && signals.length > 0 && (
          <>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-green-600 rounded" style={{ clipPath: 'polygon(50% 0%, 0% 100%, 100% 100%)' }}></div>
              <span>Buy Signals</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-red-600 rounded" style={{ clipPath: 'polygon(50% 100%, 0% 0%, 100% 0%)' }}></div>
              <span>Sell Signals</span>
            </div>
          </>
        )}
        {replayState && (
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-blue-500 rounded"></div>
            <span>Replay Progress: {((replayState.current_index + 1) / replayState.total_candles * 100).toFixed(1)}%</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReplayChart;

