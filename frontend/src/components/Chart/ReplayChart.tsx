import * as React from 'react';
import { useState, useMemo } from 'react';

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

interface ReplayChartProps {
  data: CandleData[];
  signals?: SignalData[];
  timeframe: string;
  symbol: string;
  onControl?: (action: string, value?: any) => void;
}

const ReplayChart: React.FC<ReplayChartProps> = ({
  data,
  signals = [],
  timeframe,
  symbol
}) => {
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return [];

    const traces: any[] = [
      {
        x: data.map((_, index) => index),
        open: data.map(d => d.open),
        high: data.map(d => d.high),
        low: data.map(d => d.low),
        close: data.map(d => d.close),
        type: 'candlestick',
        name: symbol,
        increasing: { line: { color: '#22c55e' }, fillcolor: '#22c55e' },
        decreasing: { line: { color: '#ef4444' }, fillcolor: '#ef4444' },
        customdata: data.map(d => d.timestamp),
        hovertemplate: '<b>%{customdata|%Y-%m-%d %H:%M}</b><br>O: %{open}<br>H: %{high}<br>L: %{low}<br>C: %{close}<extra></extra>'
      }
    ];

    if (signals.length > 0) {
      const buySignals = signals.filter(s => s.type === 'buy');
      const sellSignals = signals.filter(s => s.type === 'sell');

      if (buySignals.length) {
        traces.push({
          x: buySignals.map(s => data.findIndex(d => d.timestamp === s.timestamp)),
          y: buySignals.map(s => s.price),
          type: 'scatter',
          mode: 'markers',
          marker: { symbol: 'triangle-up', size: 12, color: '#22c55e', line: { width: 1, color: '#ffffff' } },
          name: 'Buy',
          hoverinfo: 'text',
          text: buySignals.map(s => `BUY: ${s.reason}`)
        });
      }

      if (sellSignals.length) {
        traces.push({
          x: sellSignals.map(s => data.findIndex(d => d.timestamp === s.timestamp)),
          y: sellSignals.map(s => s.price),
          type: 'scatter',
          mode: 'markers',
          marker: { symbol: 'triangle-down', size: 12, color: '#ef4444', line: { width: 1, color: '#ffffff' } },
          name: 'Sell',
          hoverinfo: 'text',
          text: sellSignals.map(s => `SELL: ${s.reason}`)
        });
      }
    }

    return traces;
  }, [data, signals, symbol]);

  const layout = useMemo(() => {
    const prices = data.flatMap(d => [d.open, d.high, d.low, d.close]);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const padding = (maxPrice - minPrice) * 0.1;

    return {
      dragmode: 'pan',
      xaxis: {
        showgrid: true,
        gridcolor: '#212631',
        tickfont: { color: '#8b949e', size: 10 },
        tickmode: 'array',
        tickvals: data
          .filter((_, i) => i % Math.max(1, Math.floor(data.length / 8)) === 0)
          .map((_, i) => i * Math.max(1, Math.floor(data.length / 8))),
        ticktext: data
          .filter((_, i) => i % Math.max(1, Math.floor(data.length / 8)) === 0)
          .map(d => {
            const date = new Date(d.timestamp * 1000);
            return timeframe.includes('M') || timeframe.includes('H') 
              ? `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
              : `${date.getMonth() + 1}/${date.getDate()}`;
          }),
        rangeslider: { visible: false }
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
      autosize: true
    };
  }, [data, symbol]);

  if (!Plot) return <div className="h-full flex items-center justify-center text-[var(--text-muted)]">Loading Engine...</div>;

  return (
    <div className="absolute inset-0">
      <Plot
        data={chartData}
        layout={layout}
        config={{
          displayModeBar: false,
          responsive: true,
          scrollZoom: true
        }}
        style={{ width: '100%', height: '100%' }}
        useResizeHandler={true}
      />
    </div>
  );
};

export default ReplayChart;
