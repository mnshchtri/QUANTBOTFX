import React, { useState, useEffect, useMemo, useCallback } from 'react';
import tradingLevelsService, { TradingLevel } from '../../services/tradingLevelsService';
import { fetchCandles, type Candle, type Indicators } from '../../services/api';

// Import Plotly dynamically
let Plot: any = null;
if (typeof window !== 'undefined') {
  Plot = require('react-plotly.js').default;
}

interface TradingDashboardChartProps {
  data: Candle[];
  indicators: Indicators | null;
  timeframe: string;
  symbol: string;
  onDataUpdate?: (data: Candle[]) => void;
  showLevels?: boolean;
}

const TradingDashboardChart: React.FC<TradingDashboardChartProps> = ({
  data,
  indicators,
  timeframe,
  symbol,
  onDataUpdate,
  showLevels = true,
}) => {
  const [realData, setRealData] = useState<Candle[]>([]);
  const [loading, setLoading] = useState(false);

  // Cache for storing fetched data to prevent unnecessary re-fetches
  const [dataCache, setDataCache] = useState<{[key: string]: Candle[]}>({});
  const [lastFetchTime, setLastFetchTime] = useState<{[key: string]: number}>({});
  
  // Fetch real data with consistent caching
  const fetchRealData = useCallback(async (forceRefresh = false) => {
    if (!symbol || !timeframe) return;
    
    const cacheKey = `${symbol}_${timeframe}`;
    const now = Date.now();
    const cacheAge = now - (lastFetchTime[cacheKey] || 0);
    const cacheValid = cacheAge < 30000; // 30 seconds cache
    
    // Use cached data if available and not expired
    if (!forceRefresh && dataCache[cacheKey] && cacheValid) {
      setRealData(dataCache[cacheKey]);
      return;
    }
    
    setLoading(true);
    try {
      const oandaData = await fetchCandles(symbol, timeframe);
      
      if (Array.isArray(oandaData)) {
        // Cache the data
        setDataCache(prev => ({ ...prev, [cacheKey]: oandaData }));
        setLastFetchTime(prev => ({ ...prev, [cacheKey]: now }));
        
        setRealData(oandaData);
        
        if (onDataUpdate) {
          onDataUpdate(oandaData);
        }
      }
    } catch (error) {
      console.error('❌ Error fetching real data:', error);
      setRealData([]);
    } finally {
      setLoading(false);
    }
  }, [symbol, timeframe, dataCache, lastFetchTime, onDataUpdate]);

  // Auto-fetch data on mount and symbol/timeframe changes
  useEffect(() => {
    fetchRealData();
  }, [symbol, timeframe, fetchRealData]);

  // Use real data if available, otherwise fall back to provided data
  const displayData = useMemo(() => {
    return realData.length > 0 ? realData : data;
  }, [realData, data]);

  // Get levels for this symbol (multi-timeframe)
  const [levels, setLevels] = useState<TradingLevel[]>([]);

  useEffect(() => {
    if (!showLevels) return;

    // Subscribe to level changes
    const unsubscribe = tradingLevelsService.subscribe((allLevels) => {
      const symbolLevels = tradingLevelsService.getMultiTimeframeLevels(symbol);
      setLevels(symbolLevels);
    });

    // Get initial levels
    const symbolLevels = tradingLevelsService.getMultiTimeframeLevels(symbol);
    setLevels(symbolLevels);

    return unsubscribe;
  }, [symbol, showLevels]);


  // Prepare chart data
  const allData = useMemo(() => {
    const traces: any[] = [
      // Candlestick chart (price only) - continuous indices for no gaps
      {
        x: displayData.map((_, index) => index), // Continuous indices for even spacing
        open: displayData.map(d => d.open),
        high: displayData.map(d => d.high),
        low: displayData.map(d => d.low),
        close: displayData.map(d => d.close),
        type: 'candlestick',
        name: `${symbol} (${timeframe})`,
        increasing: { line: { color: '#22c55e' }, fillcolor: '#22c55e' },
        decreasing: { line: { color: '#ef4444' }, fillcolor: '#ef4444' },
        yaxis: 'y',
        customdata: displayData.map(d => d.timestamp), // Keep timestamps for hover
        hovertemplate: '<b>%{customdata|%Y-%m-%d %H:%M}</b><br>Open: %{open}<br>High: %{high}<br>Low: %{low}<br>Close: %{close}<extra></extra>'
      }
    ];

    // Add indicators from backend
    if (indicators) {
      // SMA 20 (Overlay)
      if (indicators.sma_20 && indicators.sma_20.length > 0) {
        traces.push({
          x: displayData.map((_, index) => index),
          y: indicators.sma_20,
          type: 'scatter',
          mode: 'lines',
          name: 'SMA 20',
          line: { color: '#3b82f6', width: 1.5 },
          yaxis: 'y'
        });
      }

      // EMA 50 (Overlay)
      if (indicators.ema_50 && indicators.ema_50.length > 0) {
        traces.push({
          x: displayData.map((_, index) => index),
          y: indicators.ema_50,
          type: 'scatter',
          mode: 'lines',
          name: 'EMA 50',
          line: { color: '#f59e0b', width: 1.5 },
          yaxis: 'y'
        });
      }

      // RSI 14 (Subplot)
      if (indicators.rsi_14 && indicators.rsi_14.length > 0) {
        traces.push({
          x: displayData.map((_, index) => index),
          y: indicators.rsi_14,
          type: 'scatter',
          mode: 'lines',
          name: 'RSI 14',
          line: { color: '#8b5cf6', width: 1.5 },
          yaxis: 'y3'
        });
      }

      // MACD (Subplot)
      if (indicators.macd && indicators.macd.length > 0) {
        traces.push({
          x: displayData.map((_, index) => index),
          y: indicators.macd,
          type: 'scatter',
          mode: 'lines',
          name: 'MACD',
          line: { color: '#ec4899', width: 1.5 },
          yaxis: 'y3'
        });
      }
    }

    // Add level traces (multi-timeframe)
    if (showLevels && levels.length > 0) {
      levels.forEach(level => {
        traces.push({
          x: displayData.length > 0 ? [displayData[0].timestamp, displayData[displayData.length - 1].timestamp] : [],
          y: [level.price, level.price],
          mode: 'lines',
          type: 'scatter',
          name: `${level.type} ${level.price.toFixed(4)} (${level.timeframe})`,
          line: {
            color: level.color,
            width: level.width,
            dash: level.style === 'dashed' ? 'dash' : level.style === 'dotted' ? 'dot' : 'solid'
          },
          yaxis: 'y',
          hovertemplate: `<b>${level.type.toUpperCase()}</b><br>Price: ${level.price.toFixed(4)}<br>Timeframe: ${level.timeframe}<br>${level.label ? `Label: ${level.label}<br>` : ''}<extra></extra>`
        });
      });
    }

    return traces;
  }, [displayData, symbol, timeframe, indicators, levels, showLevels]);

  // Chart layout
  const layout = useMemo(() => {
    // Calculate price range for better y-axis
    const prices = displayData.flatMap(d => [d.open, d.high, d.low, d.close]);
    const minPrice = prices.length > 0 ? Math.min(...prices) : 0;
    const maxPrice = prices.length > 0 ? Math.max(...prices) : 100;
    const priceRange = maxPrice - minPrice;
    const padding = priceRange * 0.1; 
    
    const baseLayout: any = {
      xaxis: {
        showgrid: true,
        gridcolor: '#212631',
        tickfont: { color: '#8b949e', size: 10 },
        type: 'linear',
        rangeslider: { visible: false },
        zeroline: false,
        tickmode: 'array',
        tickvals: displayData
          .filter((_, i) => i % Math.max(1, Math.floor(displayData.length / 8)) === 0)
          .map((_, i) => i * Math.max(1, Math.floor(displayData.length / 8))),
        ticktext: displayData
          .filter((_, i) => i % Math.max(1, Math.floor(displayData.length / 8)) === 0)
          .map(d => {
            const date = new Date(d.timestamp * 1000);
            return timeframe.includes('M') || timeframe.includes('H') 
              ? `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
              : `${date.getMonth() + 1}/${date.getDate()}`;
          })
      },
      yaxis: {
        side: 'right',
        showgrid: true,
        gridcolor: '#212631',
        tickfont: { color: '#8b949e', size: 10 },
        range: [minPrice - padding, maxPrice + padding],
        tickformat: '.5f',
        zeroline: false
      },
      yaxis3: {
        title: 'RSI / MACD',
        side: 'right',
        overlaying: 'y',
        position: 0.95,
        showgrid: false,
        tickfont: { color: '#8b949e', size: 8 }
      },
      plot_bgcolor: 'transparent',
      paper_bgcolor: 'transparent',
      font: { family: 'Inter, sans-serif' },
      showlegend: false,
      margin: { l: 10, r: 50, t: 30, b: 30 },
      height: 700
    };

    return baseLayout;
  }, [timeframe, displayData]);

  const config = {
    displayModeBar: true,
    modeBarButtonsToRemove: ['lasso2d', 'select2d'],
    displaylogo: false,
    responsive: true,
    scrollZoom: false // Disable scroll zoom, pan is default
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full bg-transparent">
        <div className="w-12 h-12 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin mb-4" />
        <div className="text-[var(--text-muted)] text-xs font-bold uppercase tracking-widest">Synchronizing Market Data...</div>
      </div>
    );
  }

  if (!Plot) {
    return (
      <div className="flex items-center justify-center h-full bg-transparent">
        <div className="text-[var(--text-muted)] text-sm">Initializing Graphics Engine...</div>
      </div>
    );
  }

  if (!displayData || displayData.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full bg-transparent border border-dashed border-[var(--border-subtle)] rounded-xl">
        <div className="text-[var(--text-muted)] text-sm font-bold uppercase tracking-widest mb-2">No Market Data</div>
        <div className="text-[var(--text-muted)] text-xs opacity-50">Select another instrument or timeframe</div>
      </div>
    );
  }

  return (
    <div className="absolute inset-0">
      <Plot
        data={allData}
        layout={{...layout, height: undefined, autosize: true}}
        config={config}
        style={{ width: '100%', height: '100%' }}
        useResizeHandler={true}
      />
    </div>
  );
};

export default TradingDashboardChart;
