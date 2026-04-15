import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import axios from 'axios';
import tradingLevelsService, { TradingLevel } from '../../services/tradingLevelsService';

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

export interface IndicatorData {
  name: string;
  data: Array<{ timestamp: number; value: number }>;
  color: string;
  type: 'line' | 'histogram';
  overlay: boolean;
}

interface TradingDashboardChartProps {
  data: CandleData[];
  indicators: IndicatorData[];
  timeframe: string;
  symbol: string;
  onDataUpdate?: (data: CandleData[]) => void;
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
  const [realData, setRealData] = useState<CandleData[]>([]);
  const [loading, setLoading] = useState(false);
  const [dataSource, setDataSource] = useState<string>('');
  const [isRealData, setIsRealData] = useState(false);

  // Cache for storing fetched data to prevent unnecessary re-fetches
  const [dataCache, setDataCache] = useState<{[key: string]: CandleData[]}>({});
  const [lastFetchTime, setLastFetchTime] = useState<{[key: string]: number}>({});
  
  // Fetch real OANDA data with consistent caching
  const fetchRealData = useCallback(async (forceRefresh = false) => {
    if (!symbol || !timeframe) return;
    
    const cacheKey = `${symbol}_${timeframe}`;
    const now = Date.now();
    const cacheAge = now - (lastFetchTime[cacheKey] || 0);
    const cacheValid = cacheAge < 30000; // 30 seconds cache
    
    // Use cached data if available and not expired
    if (!forceRefresh && dataCache[cacheKey] && cacheValid) {
      console.log(`✅ Using cached data for ${cacheKey} (${dataCache[cacheKey].length} candles)`);
      setRealData(dataCache[cacheKey]);
      setDataSource('Backend API (Cached)');
      setIsRealData(true);
      return;
    }
    
    setLoading(true);
    try {
      const response = await axios.get(`/api/candles/${symbol}/${timeframe}`, {
        params: {
          limit: 1000 // Increased limit for more data
        }
      });
      
      if (response.data && response.data.data && Array.isArray(response.data.data)) {
        const oandaData = response.data.data.map((candle: any) => ({
          timestamp: candle.timestamp,
          open: candle.open,
          high: candle.high,
          low: candle.low,
          close: candle.close,
          volume: candle.volume || 0
        }));

        // Cache the data
        setDataCache(prev => ({ ...prev, [cacheKey]: oandaData }));
        setLastFetchTime(prev => ({ ...prev, [cacheKey]: now }));
        
        setRealData(oandaData);
        setDataSource('Backend API');
        setIsRealData(true);
        
        if (onDataUpdate) {
          onDataUpdate(oandaData);
        }
        console.log(`✅ Fetched ${oandaData.length} candles from Backend API (${forceRefresh ? 'forced refresh' : 'new data'})`);
      } else {
        console.warn('⚠️ Invalid data format from Backend API');
        setRealData([]);
        setDataSource('Invalid Data');
        setIsRealData(false);
      }
    } catch (error) {
      console.error('❌ Error fetching real data:', error);
      setRealData([]);
      setDataSource('Error');
      setIsRealData(false);
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

  // Separate overlay and non-overlay indicators
  const overlayIndicators = useMemo(() => 
    indicators.filter(indicator => indicator.overlay), [indicators]
  );
  
  const nonOverlayIndicators = useMemo(() => 
    indicators.filter(indicator => !indicator.overlay), [indicators]
  );

  // Calculate number of subplots needed
  const numSubplots = useMemo(() => {
    let subplots = 1; // Main price chart
    if (nonOverlayIndicators.length > 0) {
      subplots += 1; // One subplot for all non-overlay indicators
    }
    return subplots;
  }, [nonOverlayIndicators.length]);

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

    // Add overlay indicators
    overlayIndicators.forEach(indicator => {
      traces.push({
        x: indicator.data.map((_, index) => index), // Continuous indices for even spacing
        y: indicator.data.map(d => d.value),
        type: 'scatter',
        mode: 'lines',
        name: indicator.name,
        line: { color: indicator.color, width: 2 },
        yaxis: 'y',
        customdata: indicator.data.map(d => d.timestamp), // Keep timestamps for hover
        hovertemplate: `<b>${indicator.name}</b><br>Time: %{customdata|%Y-%m-%d %H:%M}<br>Value: %{y}<extra></extra>`
      });
    });

    // Add non-overlay indicators to subplot
    if (nonOverlayIndicators.length > 0) {
      nonOverlayIndicators.forEach(indicator => {
        traces.push({
          x: indicator.data.map((_, index) => index), // Continuous indices for even spacing
          y: indicator.data.map(d => d.value),
          type: indicator.type === 'histogram' ? 'bar' : 'scatter',
          mode: indicator.type === 'histogram' ? undefined : 'lines',
          name: indicator.name,
          line: indicator.type === 'histogram' ? undefined : { color: indicator.color, width: 2 },
          marker: indicator.type === 'histogram' ? { color: indicator.color, opacity: 0.8 } : undefined,
          yaxis: 'y3',
          customdata: indicator.data.map(d => d.timestamp), // Keep timestamps for hover
          hovertemplate: `<b>${indicator.name}</b><br>Time: %{customdata|%Y-%m-%d %H:%M}<br>Value: %{y}<extra></extra>`
        });
      });
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
  }, [displayData, symbol, timeframe, overlayIndicators, nonOverlayIndicators, levels, showLevels]);

  // Chart layout
  const layout = useMemo(() => {
    // Calculate price range for better y-axis
    const prices = displayData.flatMap(d => [d.open, d.high, d.low, d.close]);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const priceRange = maxPrice - minPrice;
    const padding = priceRange * 0.1; // 10% padding
    
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
      plot_bgcolor: 'transparent',
      paper_bgcolor: 'transparent',
      font: { family: 'Inter, sans-serif' },
      showlegend: false,
      margin: { l: 10, r: 50, t: 30, b: 30 },
      height: 700
    };

    // Add subplot for non-overlay indicators
    if (nonOverlayIndicators.length > 0) {
      baseLayout.yaxis3 = {
        title: 'Indicators',
        side: 'right',
        overlaying: 'y',
        position: 0.95,
        showgrid: false
      };
    }

    return baseLayout;
  }, [symbol, timeframe, nonOverlayIndicators.length, displayData]);

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
