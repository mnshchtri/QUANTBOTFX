"""
Simple Candlestick Strategy Viewer
Clean, reliable candlestick charts with strategy signals
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import seaborn as sns
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

# Set style for better charts
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

@dataclass
class BarData:
    """Market bar data structure"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

@dataclass
class SignalData:
    """Trading signal data"""
    timestamp: datetime
    signal: str  # BUY, SELL, HOLD
    confidence: float
    price: float
    rsi: float
    ema_fast: float
    ema_slow: float
    macd: float
    macd_signal: float

class SimpleCandlestickViewer:
    """Simple and reliable candlestick chart viewer"""
    
    def __init__(self, symbol: str = "EURUSD"):
        self.symbol = symbol
        self.bars: List[BarData] = []
        self.signals: List[SignalData] = []
        
        # Strategy parameters
        self.ema_fast_period = 12
        self.ema_slow_period = 26
        self.rsi_period = 14
        self.confidence_threshold = 0.4
        
    def add_bar(self, bar: BarData):
        """Add new market bar"""
        self.bars.append(bar)
        self._process_bar(bar)
    
    def _process_bar(self, bar: BarData):
        """Process new bar and generate signals"""
        if len(self.bars) < 50:  # Need minimum data
            return
        
        # Calculate indicators
        prices = np.array([b.close for b in self.bars])
        highs = np.array([b.high for b in self.bars])
        lows = np.array([b.low for b in self.bars])
        
        ema_fast = self._calculate_ema(prices, self.ema_fast_period)
        ema_slow = self._calculate_ema(prices, self.ema_slow_period)
        rsi = self._calculate_rsi(prices, self.rsi_period)
        macd_line, signal_line = self._calculate_macd(prices)
        
        # Current values
        current_idx = len(prices) - 1
        
        # Generate signal
        signal, confidence = self._generate_signal(
            prices[current_idx], ema_fast[current_idx], ema_slow[current_idx], 
            rsi[current_idx], macd_line[current_idx], signal_line[current_idx]
        )
        
        # Create signal data
        signal_data = SignalData(
            timestamp=bar.timestamp,
            signal=signal,
            confidence=confidence,
            price=bar.close,
            rsi=rsi[current_idx],
            ema_fast=ema_fast[current_idx],
            ema_slow=ema_slow[current_idx],
            macd=macd_line[current_idx],
            macd_signal=signal_line[current_idx]
        )
        
        self.signals.append(signal_data)
    
    def _calculate_ema(self, prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate Exponential Moving Average"""
        alpha = 2 / (period + 1)
        ema_values = np.zeros_like(prices)
        ema_values[0] = prices[0]
        
        for i in range(1, len(prices)):
            ema_values[i] = alpha * prices[i] + (1 - alpha) * ema_values[i-1]
        
        return ema_values
    
    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> np.ndarray:
        """Calculate Relative Strength Index"""
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gains = np.zeros_like(prices)
        avg_losses = np.zeros_like(prices)
        
        # First average
        avg_gains[period] = np.mean(gains[:period])
        avg_losses[period] = np.mean(losses[:period])
        
        # Subsequent averages
        for i in range(period + 1, len(prices)):
            avg_gains[i] = (avg_gains[i-1] * (period-1) + gains[i-1]) / period
            avg_losses[i] = (avg_losses[i-1] * (period-1) + losses[i-1]) / period
        
        rs = avg_gains / (avg_losses + 1e-10)
        rsi_values = 100 - (100 / (1 + rs))
        
        return rsi_values
    
    def _calculate_macd(self, prices: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate MACD"""
        ema_fast = self._calculate_ema(prices, fast)
        ema_slow = self._calculate_ema(prices, slow)
        macd_line = ema_fast - ema_slow
        signal_line = self._calculate_ema(macd_line, signal)
        
        return macd_line, signal_line
    
    def _generate_signal(self, price: float, ema_fast: float, ema_slow: float, 
                        rsi: float, macd: float, macd_signal: float) -> Tuple[str, float]:
        """Generate trading signal"""
        # Technical rules
        ema_bullish = ema_fast > ema_slow
        rsi_oversold = rsi < 30
        rsi_overbought = rsi > 70
        macd_bullish = macd > macd_signal
        
        # Calculate confidence based on multiple factors
        confidence = 0.5  # Base confidence
        
        if ema_bullish:
            confidence += 0.2
        if not rsi_overbought:
            confidence += 0.1
        if macd_bullish:
            confidence += 0.1
        if rsi_oversold:
            confidence += 0.1
        
        # Generate signal
        if ema_bullish and not rsi_overbought and macd_bullish:
            return "BUY", min(confidence, 0.9)
        elif not ema_bullish and not rsi_oversold and not macd_bullish:
            return "SELL", min(confidence, 0.9)
        else:
            return "HOLD", 0.5
    
    def create_candlestick_chart(self, save_path: str = "simple_candlestick.png"):
        """Create beautiful candlestick chart with signals"""
        if not self.bars or not self.signals:
            print("No data to plot!")
            return
        
        # Create figure with subplots
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(16, 12), sharex=True)
        fig.suptitle(f'Candlestick Strategy Analysis - {self.symbol}', fontsize=16, fontweight='bold')
        
        # Prepare data
        timestamps = [b.timestamp for b in self.bars]
        opens = [b.open for b in self.bars]
        highs = [b.high for b in self.bars]
        lows = [b.low for b in self.bars]
        closes = [b.close for b in self.bars]
        
        # 1. Main candlestick chart
        for i, (timestamp, open_price, high, low, close) in enumerate(zip(timestamps, opens, highs, lows, closes)):
            color = 'green' if close >= open_price else 'red'
            
            # Draw candlestick body
            body_height = abs(close - open_price)
            body_bottom = min(open_price, close)
            
            ax1.add_patch(plt.Rectangle(
                (i - 0.3, body_bottom), 0.6, body_height,
                facecolor=color, alpha=0.8, edgecolor='black', linewidth=0.5
            ))
            
            # Draw wicks
            ax1.plot([i, i], [low, high], color='black', linewidth=1)
        
        # Plot EMAs
        signal_timestamps = [s.timestamp for s in self.signals]
        ema_fast_values = [s.ema_fast for s in self.signals]
        ema_slow_values = [s.ema_slow for s in self.signals]
        
        # Map signal timestamps to bar indices
        signal_indices = []
        for signal_ts in signal_timestamps:
            try:
                idx = timestamps.index(signal_ts)
                signal_indices.append(idx)
            except ValueError:
                continue
        
        if signal_indices:
            ax1.plot(signal_indices, ema_fast_values, label='EMA Fast', color='blue', linewidth=2)
            ax1.plot(signal_indices, ema_slow_values, label='EMA Slow', color='orange', linewidth=2)
        
        # Plot buy/sell signals
        buy_signals = [s for s in self.signals if s.signal == 'BUY']
        sell_signals = [s for s in self.signals if s.signal == 'SELL']
        
        if buy_signals:
            buy_times = [s.timestamp for s in buy_signals]
            buy_prices = [s.price for s in buy_signals]
            buy_indices = [timestamps.index(ts) for ts in buy_times if ts in timestamps]
            buy_prices_filtered = [price for i, price in enumerate(buy_prices) if buy_times[i] in timestamps]
            
            if buy_indices:
                ax1.scatter(buy_indices, buy_prices_filtered, 
                           marker='^', color='green', s=150, label='Buy Signal', zorder=5)
        
        if sell_signals:
            sell_times = [s.timestamp for s in sell_signals]
            sell_prices = [s.price for s in sell_signals]
            sell_indices = [timestamps.index(ts) for ts in sell_times if ts in timestamps]
            sell_prices_filtered = [price for i, price in enumerate(sell_prices) if sell_times[i] in timestamps]
            
            if sell_indices:
                ax1.scatter(sell_indices, sell_prices_filtered, 
                           marker='v', color='red', s=150, label='Sell Signal', zorder=5)
        
        ax1.set_ylabel('Price')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_title('Price Action with Signals')
        
        # 2. RSI subplot
        if signal_indices:
            rsi_values = [s.rsi for s in self.signals]
            ax2.plot(signal_indices, rsi_values, label='RSI', color='purple', linewidth=2)
            ax2.axhline(y=70, color='r', linestyle='--', alpha=0.5, label='Overbought')
            ax2.axhline(y=30, color='g', linestyle='--', alpha=0.5, label='Oversold')
            ax2.set_ylabel('RSI')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            ax2.set_title('RSI Indicator')
        
        # 3. MACD subplot
        if signal_indices:
            macd_values = [s.macd for s in self.signals]
            macd_signal_values = [s.macd_signal for s in self.signals]
            ax3.plot(signal_indices, macd_values, label='MACD', color='blue', linewidth=2)
            ax3.plot(signal_indices, macd_signal_values, label='Signal', color='orange', linewidth=2)
            ax3.bar(signal_indices, 
                   [m - s for m, s in zip(macd_values, macd_signal_values)], 
                   alpha=0.3, label='Histogram', color='gray')
            ax3.set_ylabel('MACD')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            ax3.set_title('MACD Indicator')
        
        # Format x-axis
        ax3.set_xlabel('Time')
        
        # Set x-axis ticks
        if len(timestamps) > 0:
            step = max(1, len(timestamps) // 10)
            tick_positions = range(0, len(timestamps), step)
            tick_labels = [timestamps[i].strftime('%H:%M') for i in tick_positions]
            ax3.set_xticks(tick_positions)
            ax3.set_xticklabels(tick_labels, rotation=45)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        # Print statistics
        self._print_statistics()
    
    def _print_statistics(self):
        """Print detailed strategy statistics"""
        if not self.signals:
            return
        
        print("\n" + "="*60)
        print("CANDLESTICK STRATEGY STATISTICS")
        print("="*60)
        
        # Signal statistics
        total_signals = len(self.signals)
        buy_signals = len([s for s in self.signals if s.signal == 'BUY'])
        sell_signals = len([s for s in self.signals if s.signal == 'SELL'])
        hold_signals = len([s for s in self.signals if s.signal == 'HOLD'])
        
        print(f"Total Signals: {total_signals}")
        print(f"Buy Signals: {buy_signals} ({buy_signals/total_signals*100:.1f}%)")
        print(f"Sell Signals: {sell_signals} ({sell_signals/total_signals*100:.1f}%)")
        print(f"Hold Signals: {hold_signals} ({hold_signals/total_signals*100:.1f}%)")
        
        # Price statistics
        prices = [b.close for b in self.bars]
        print(f"\nPrice Statistics:")
        print(f"Starting Price: {prices[0]:.5f}")
        print(f"Ending Price: {prices[-1]:.5f}")
        print(f"Price Change: {((prices[-1] - prices[0]) / prices[0] * 100):.2f}%")
        print(f"Highest Price: {max(prices):.5f}")
        print(f"Lowest Price: {min(prices):.5f}")
        
        # Indicator statistics
        if self.signals:
            rsi_values = [s.rsi for s in self.signals]
            ema_ratios = [s.ema_fast/s.ema_slow for s in self.signals]
            
            print(f"\nIndicator Statistics:")
            print(f"Average RSI: {np.mean(rsi_values):.1f}")
            print(f"RSI Range: {np.min(rsi_values):.1f} - {np.max(rsi_values):.1f}")
            print(f"Average EMA Ratio: {np.mean(ema_ratios):.5f}")
            print(f"EMA Ratio Range: {np.min(ema_ratios):.5f} - {np.max(ema_ratios):.5f}")
        
        print("="*60)

def generate_sample_data(symbol: str = "EURUSD", days: int = 3) -> List[BarData]:
    """Generate sample forex data for testing"""
    bars = []
    start_date = datetime(2024, 1, 1)
    base_price = 1.1000  # EURUSD starting price
    
    for i in range(days * 24 * 60):  # Minute data
        timestamp = start_date + timedelta(minutes=i)
        
        # Simulate realistic price movement
        trend = np.sin(i / (24 * 60 * 7)) * 0.001  # Weekly trend
        noise = np.random.normal(0, 0.0002)  # Random noise
        volatility = 0.0001 + 0.0001 * np.sin(i / (24 * 60))  # Daily volatility cycle
        
        price_change = trend + noise * volatility
        base_price += price_change
        
        # Generate OHLC
        open_price = base_price
        high_price = open_price + abs(np.random.normal(0, 0.0005))
        low_price = open_price - abs(np.random.normal(0, 0.0005))
        close_price = open_price + np.random.normal(0, 0.0003)
        
        # Ensure OHLC relationship
        high_price = max(high_price, open_price, close_price)
        low_price = min(low_price, open_price, close_price)
        
        bar = BarData(
            timestamp=timestamp,
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            volume=np.random.randint(1000, 10000)
        )
        
        bars.append(bar)
    
    return bars

def main():
    """Main function to demonstrate the candlestick viewer"""
    print("🚀 Starting Simple Candlestick Strategy Viewer")
    print("="*50)
    
    # Initialize viewer
    viewer = SimpleCandlestickViewer("EURUSD")
    
    # Generate sample data
    print("Generating sample data...")
    bars = generate_sample_data("EURUSD", days=2)  # 2 days of minute data
    
    # Process bars
    print("Processing bars and generating signals...")
    for i, bar in enumerate(bars):
        viewer.add_bar(bar)
        
        # Print progress every 100 bars
        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1}/{len(bars)} bars...")
    
    # Create candlestick chart
    print("\nCreating candlestick chart...")
    viewer.create_candlestick_chart()
    
    print("\n✅ Candlestick analysis complete!")
    print("📊 Check 'simple_candlestick.png' for the chart")

if __name__ == "__main__":
    main() 