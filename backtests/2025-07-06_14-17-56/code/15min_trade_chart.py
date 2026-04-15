"""
15-Minute Trade Chart
Focused candlestick chart with buy/sell signals and separate indicator panels
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

warnings.filterwarnings("ignore")
from tqdm import tqdm

# Set professional appearance
plt.style.use("dark_background")
plt.rcParams["figure.facecolor"] = "#1e222d"
plt.rcParams["axes.facecolor"] = "#1e222d"
plt.rcParams["savefig.facecolor"] = "#1e222d"


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
    atr: float
    bb_upper: float
    bb_lower: float
    bb_middle: float


class FifteenMinuteChart:
    """15-minute focused candlestick chart with signals and indicators"""

    def __init__(self, symbol: str = "EURUSD"):
        self.symbol = symbol
        self.bars: List[BarData] = []
        self.signals: List[SignalData] = []

        # Strategy parameters
        self.ema_fast_period = 12
        self.ema_slow_period = 26
        self.rsi_period = 14
        self.bb_period = 20
        self.bb_std = 2
        self.confidence_threshold = 0.4

        # TradingView colors
        self.colors = {
            "background": "#1e222d",
            "grid": "#2a2e39",
            "text": "#d1d4dc",
            "candle_green": "#26a69a",
            "candle_red": "#ef5350",
            "ema_fast": "#2196f3",
            "ema_slow": "#ff9800",
            "rsi": "#9c27b0",
            "macd": "#4caf50",
            "macd_signal": "#ff5722",
            "bb_upper": "#ff9800",
            "bb_lower": "#ff9800",
            "bb_middle": "#ffc107",
            "volume": "#607d8b",
            "buy_signal": "#4caf50",
            "sell_signal": "#f44336",
        }

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
        atr = self._calculate_atr(highs, lows, prices)
        bb_upper, bb_lower, bb_middle = self._calculate_bollinger_bands(prices)

        # Current values
        current_idx = len(prices) - 1

        # Generate signal
        signal, confidence = self._generate_signal(
            prices[current_idx],
            ema_fast[current_idx],
            ema_slow[current_idx],
            rsi[current_idx],
            macd_line[current_idx],
            signal_line[current_idx],
            bb_upper[current_idx],
            bb_lower[current_idx],
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
            macd_signal=signal_line[current_idx],
            atr=atr[current_idx],
            bb_upper=bb_upper[current_idx],
            bb_lower=bb_lower[current_idx],
            bb_middle=bb_middle[current_idx],
        )

        self.signals.append(signal_data)

    def _calculate_ema(self, prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate Exponential Moving Average"""
        alpha = 2 / (period + 1)
        ema_values = np.zeros_like(prices)
        ema_values[0] = prices[0]

        for i in range(1, len(prices)):
            ema_values[i] = alpha * prices[i] + (1 - alpha) * ema_values[i - 1]

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
            avg_gains[i] = (avg_gains[i - 1] * (period - 1) + gains[i - 1]) / period
            avg_losses[i] = (avg_losses[i - 1] * (period - 1) + losses[i - 1]) / period

        rs = avg_gains / (avg_losses + 1e-10)
        rsi_values = 100 - (100 / (1 + rs))

        return rsi_values

    def _calculate_macd(
        self, prices: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate MACD"""
        ema_fast = self._calculate_ema(prices, fast)
        ema_slow = self._calculate_ema(prices, slow)
        macd_line = ema_fast - ema_slow
        signal_line = self._calculate_ema(macd_line, signal)

        return macd_line, signal_line

    def _calculate_atr(
        self, high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14
    ) -> np.ndarray:
        """Calculate Average True Range"""
        tr1 = high - low
        tr2 = np.abs(high - np.roll(close, 1))
        tr3 = np.abs(low - np.roll(close, 1))

        true_range = np.maximum(tr1, np.maximum(tr2, tr3))
        atr_values = self._calculate_ema(true_range, period)

        return atr_values

    def _calculate_bollinger_bands(
        self, prices: np.ndarray, period: int = 20, std_dev: int = 2
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calculate Bollinger Bands"""
        sma = np.zeros_like(prices)
        for i in range(len(prices)):
            if i < period - 1:
                sma[i] = prices[i]
            else:
                sma[i] = np.mean(prices[i - period + 1 : i + 1])

        std = np.zeros_like(prices)
        for i in range(len(prices)):
            if i < period - 1:
                std[i] = 0
            else:
                std[i] = np.std(prices[i - period + 1 : i + 1])

        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)

        return upper_band, lower_band, sma

    def _generate_signal(
        self,
        price: float,
        ema_fast: float,
        ema_slow: float,
        rsi: float,
        macd: float,
        macd_signal: float,
        bb_upper: float,
        bb_lower: float,
    ) -> Tuple[str, float]:
        """Generate trading signal"""
        # Technical conditions
        ema_bullish = ema_fast > ema_slow
        rsi_oversold = rsi < 30
        rsi_overbought = rsi > 70
        macd_bullish = macd > macd_signal
        bb_breakout_up = price > bb_upper
        bb_breakout_down = price < bb_lower

        # Calculate confidence
        confidence = 0.5  # Base confidence

        if ema_bullish:
            confidence += 0.15
        if not rsi_overbought:
            confidence += 0.1
        if macd_bullish:
            confidence += 0.1
        if rsi_oversold:
            confidence += 0.1
        if bb_breakout_up:
            confidence += 0.2

        # Generate signal
        if ema_bullish and not rsi_overbought and macd_bullish:
            if bb_breakout_up:
                return "BUY", min(confidence, 0.95)
            else:
                return "BUY", min(confidence, 0.8)
        elif not ema_bullish and not rsi_oversold and not macd_bullish:
            if bb_breakout_down:
                return "SELL", min(confidence, 0.95)
            else:
                return "SELL", min(confidence, 0.8)
        else:
            return "HOLD", 0.5

    def create_15min_chart(self, save_path: str = "15min_trade_chart.png"):
        """Create focused 15-minute candlestick chart with signals and indicators"""
        if not self.bars or not self.signals:
            print("No data to plot!")
            return

        # Only use the last 96 bars (24 hours)
        bars = self.bars[-96:]
        signals = self.signals[-96:]
        timestamps = [b.timestamp for b in bars]
        opens = [b.open for b in bars]
        highs = [b.high for b in bars]
        lows = [b.low for b in bars]
        closes = [b.close for b in bars]
        volumes = [b.volume for b in bars]

        # Get 1st and 2nd hour high/low
        first_hour_high, first_hour_low = self.get_hour_levels(bars, 0)
        second_hour_high, second_hour_low = self.get_hour_levels(bars, 1)

        # Track breakouts
        breakout_events = []
        above_first = below_first = above_second = below_second = False
        for i, b in enumerate(bars):
            if not above_first and b.close > first_hour_high:
                breakout_events.append((b.timestamp, "Break 1st Hour High", b.close))
                above_first = True
            if not below_first and b.close < first_hour_low:
                breakout_events.append((b.timestamp, "Break 1st Hour Low", b.close))
                below_first = True
            if not above_second and b.close > second_hour_high:
                breakout_events.append((b.timestamp, "Break 2nd Hour High", b.close))
                above_second = True
            if not below_second and b.close < second_hour_low:
                breakout_events.append((b.timestamp, "Break 2nd Hour Low", b.close))
                below_second = True

        # Create figure with subplots
        fig = plt.figure(figsize=(16, 12), facecolor=self.colors["background"])
        gs = fig.add_gridspec(4, 1, height_ratios=[3, 1, 1, 1], hspace=0.1)

        # Main price chart
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1])  # RSI
        ax3 = fig.add_subplot(gs[2])  # MACD
        ax4 = fig.add_subplot(gs[3])  # Volume

        # Candlesticks
        for i, (timestamp, open_price, high, low, close) in enumerate(
            zip(timestamps, opens, highs, lows, closes)
        ):
            color = (
                self.colors["candle_green"]
                if close >= open_price
                else self.colors["candle_red"]
            )

            # Draw candlestick body
            body_height = abs(close - open_price)
            body_bottom = min(open_price, close)

            from matplotlib.patches import Rectangle

            ax1.add_patch(
                Rectangle(
                    (i - 0.3, body_bottom),
                    0.6,
                    body_height,
                    facecolor=color,
                    alpha=0.8,
                    edgecolor=color,
                    linewidth=1,
                )
            )

            # Draw wicks
            ax1.plot([i, i], [low, high], color=color, linewidth=1.5)

        # Plot 1st and 2nd hour high/low
        ax1.axhline(
            y=first_hour_high,
            color="#ffeb3b",
            linestyle="--",
            linewidth=1.5,
            label="1st Hour High",
        )
        ax1.axhline(
            y=first_hour_low,
            color="#ffeb3b",
            linestyle=":",
            linewidth=1.5,
            label="1st Hour Low",
        )
        ax1.axhline(
            y=second_hour_high,
            color="#00bcd4",
            linestyle="--",
            linewidth=1.5,
            label="2nd Hour High",
        )
        ax1.axhline(
            y=second_hour_low,
            color="#00bcd4",
            linestyle=":",
            linewidth=1.5,
            label="2nd Hour Low",
        )

        # Mark breakouts
        for event in breakout_events:
            idx = timestamps.index(event[0])
            ax1.scatter(
                idx,
                event[2],
                marker="*",
                color="yellow",
                s=250,
                zorder=6,
                label=event[1],
            )

        # Plot EMAs and Bollinger Bands
        signal_indices = []
        for signal in signals:
            try:
                idx = timestamps.index(signal.timestamp)
                signal_indices.append(idx)
            except ValueError:
                continue

        if signal_indices:
            ema_fast_values = [s.ema_fast for s in signals]
            ema_slow_values = [s.ema_slow for s in signals]
            bb_upper_values = [s.bb_upper for s in signals]
            bb_lower_values = [s.bb_lower for s in signals]
            bb_middle_values = [s.bb_middle for s in signals]

            ax1.plot(
                signal_indices,
                ema_fast_values,
                label="EMA Fast",
                color=self.colors["ema_fast"],
                linewidth=2,
            )
            ax1.plot(
                signal_indices,
                ema_slow_values,
                label="EMA Slow",
                color=self.colors["ema_slow"],
                linewidth=2,
            )
            ax1.plot(
                signal_indices,
                bb_upper_values,
                label="BB Upper",
                color=self.colors["bb_upper"],
                linewidth=1,
                alpha=0.7,
            )
            ax1.plot(
                signal_indices,
                bb_lower_values,
                label="BB Lower",
                color=self.colors["bb_lower"],
                linewidth=1,
                alpha=0.7,
            )
            ax1.plot(
                signal_indices,
                bb_middle_values,
                label="BB Middle",
                color=self.colors["bb_middle"],
                linewidth=1,
                alpha=0.5,
            )

        # Plot buy/sell signals
        buy_signals = [s for s in signals if s.signal == "BUY"]
        sell_signals = [s for s in signals if s.signal == "SELL"]

        if buy_signals:
            buy_indices = [
                timestamps.index(s.timestamp)
                for s in buy_signals
                if s.timestamp in timestamps
            ]
            buy_prices = [s.price for s in buy_signals if s.timestamp in timestamps]
            if buy_indices:
                ax1.scatter(
                    buy_indices,
                    buy_prices,
                    marker="^",
                    color=self.colors["buy_signal"],
                    s=200,
                    label="Buy Signal",
                    zorder=5,
                    edgecolors="white",
                    linewidth=2,
                )

        if sell_signals:
            sell_indices = [
                timestamps.index(s.timestamp)
                for s in sell_signals
                if s.timestamp in timestamps
            ]
            sell_prices = [s.price for s in sell_signals if s.timestamp in timestamps]
            if sell_indices:
                ax1.scatter(
                    sell_indices,
                    sell_prices,
                    marker="v",
                    color=self.colors["sell_signal"],
                    s=200,
                    label="Sell Signal",
                    zorder=5,
                    edgecolors="white",
                    linewidth=2,
                )

        # Format main chart
        ax1.set_title(
            f"{self.symbol} - 15-Minute Trade Chart (24h)",
            color=self.colors["text"],
            fontsize=16,
            fontweight="bold",
        )
        ax1.set_ylabel("Price", color=self.colors["text"])
        ax1.legend(loc="upper left", framealpha=0.8)
        ax1.grid(True, alpha=0.2, color=self.colors["grid"])
        ax1.set_facecolor(self.colors["background"])

        # 2. RSI subplot
        if signal_indices:
            rsi_values = [s.rsi for s in signals]
            ax2.plot(
                signal_indices,
                rsi_values,
                label="RSI",
                color=self.colors["rsi"],
                linewidth=2,
            )
            ax2.axhline(
                y=70,
                color=self.colors["candle_red"],
                linestyle="--",
                alpha=0.5,
                label="Overbought",
            )
            ax2.axhline(
                y=30,
                color=self.colors["candle_green"],
                linestyle="--",
                alpha=0.5,
                label="Oversold",
            )
            ax2.set_ylabel("RSI", color=self.colors["text"])
            ax2.legend(loc="upper left", framealpha=0.8)
            ax2.grid(True, alpha=0.2, color=self.colors["grid"])
            ax2.set_facecolor(self.colors["background"])

        # 3. MACD subplot
        if signal_indices:
            macd_values = [s.macd for s in signals]
            macd_signal_values = [s.macd_signal for s in signals]
            ax3.plot(
                signal_indices,
                macd_values,
                label="MACD",
                color=self.colors["macd"],
                linewidth=2,
            )
            ax3.plot(
                signal_indices,
                macd_signal_values,
                label="Signal",
                color=self.colors["macd_signal"],
                linewidth=2,
            )
            ax3.bar(
                signal_indices,
                [m - s for m, s in zip(macd_values, macd_signal_values)],
                alpha=0.3,
                label="Histogram",
                color=self.colors["volume"],
            )
            ax3.set_ylabel("MACD", color=self.colors["text"])
            ax3.legend(loc="upper left", framealpha=0.8)
            ax3.grid(True, alpha=0.2, color=self.colors["grid"])
            ax3.set_facecolor(self.colors["background"])

        # 4. Volume subplot
        ax4.bar(range(len(volumes)), volumes, alpha=0.7, color=self.colors["volume"])
        ax4.set_ylabel("Volume", color=self.colors["text"])
        ax4.set_xlabel("Time", color=self.colors["text"])
        ax4.grid(True, alpha=0.2, color=self.colors["grid"])
        ax4.set_facecolor(self.colors["background"])

        # Format x-axis
        if len(timestamps) > 0:
            step = max(1, len(timestamps) // 10)
            tick_positions = range(0, len(timestamps), step)
            tick_labels = [timestamps[i].strftime("%H:%M") for i in tick_positions]
            ax4.set_xticks(tick_positions)
            ax4.set_xticklabels(tick_labels, rotation=45, color=self.colors["text"])

        # Color all spines
        for ax in [ax1, ax2, ax3, ax4]:
            for spine in ax.spines.values():
                spine.set_color(self.colors["grid"])

        plt.tight_layout()
        plt.savefig(
            save_path, dpi=300, bbox_inches="tight", facecolor=self.colors["background"]
        )
        plt.show()

        # Print breakout details
        print("\nBreakout Events:")
        for event in breakout_events:
            print(f"{event[0].strftime('%H:%M')} - {event[1]} at {event[2]:.5f}")
        self._print_signal_summary()

    def _print_signal_summary(self):
        """Print signal summary"""
        if not self.signals:
            return

        print("\n" + "=" * 60)
        print("15-MINUTE TRADE CHART SUMMARY")
        print("=" * 60)

        # Signal statistics
        total_signals = len(self.signals)
        buy_signals = [s for s in self.signals if s.signal == "BUY"]
        sell_signals = [s for s in self.signals if s.signal == "SELL"]
        hold_signals = [s for s in self.signals if s.signal == "HOLD"]

        print(f"📊 SIGNAL SUMMARY:")
        print(f"   Total Signals: {total_signals}")
        print(
            f"   Buy Signals: {len(buy_signals)} ({len(buy_signals)/total_signals*100:.1f}%)"
        )
        print(
            f"   Sell Signals: {len(sell_signals)} ({len(sell_signals)/total_signals*100:.1f}%)"
        )
        print(
            f"   Hold Signals: {len(hold_signals)} ({len(hold_signals)/total_signals*100:.1f}%)"
        )

        # Price statistics
        prices = [b.close for b in self.bars]
        print(f"\n📈 PRICE ACTION:")
        print(f"   Starting Price: {prices[0]:.5f}")
        print(f"   Ending Price: {prices[-1]:.5f}")
        print(f"   Price Change: {((prices[-1] - prices[0]) / prices[0] * 100):.2f}%")
        print(f"   Highest Price: {max(prices):.5f}")
        print(f"   Lowest Price: {min(prices):.5f}")

        # Recent signals
        if buy_signals or sell_signals:
            print(f"\n🎯 RECENT SIGNALS:")
            recent_signals = sorted(
                buy_signals + sell_signals, key=lambda x: x.timestamp
            )[-5:]
            for signal in recent_signals:
                print(
                    f"   {signal.timestamp.strftime('%H:%M')} - {signal.signal} @ {signal.price:.5f} (Confidence: {signal.confidence:.3f})"
                )

        print("=" * 60)

    def get_hour_levels(self, bars: list, hour: int) -> tuple:
        """Get high and low for a specific hour (0-based) from 15-min bars."""
        start_idx = hour * 4
        end_idx = (hour + 1) * 4
        hour_bars = bars[start_idx:end_idx]
        high = max(b.high for b in hour_bars)
        low = min(b.low for b in hour_bars)
        return high, low


def generate_15min_data(symbol: str = "EURUSD", hours: int = 24) -> List[BarData]:
    """Generate 15-minute sample data"""
    bars = []
    start_date = datetime(2024, 1, 1)
    base_price = 1.1000  # EURUSD starting price

    for i in range(hours * 4):  # 4 bars per hour (15-minute intervals)
        timestamp = start_date + timedelta(minutes=i * 15)

        # Simulate realistic price movement
        trend = np.sin(i / 24) * 0.001  # Hourly trend
        noise = np.random.normal(0, 0.0003)  # Random noise
        volatility = 0.0002 + 0.0001 * np.sin(i / 4)  # 15-min volatility cycle

        price_change = trend + noise * volatility
        base_price += price_change

        # Generate OHLC
        open_price = base_price
        high_price = open_price + abs(np.random.normal(0, 0.0008))
        low_price = open_price - abs(np.random.normal(0, 0.0008))
        close_price = open_price + np.random.normal(0, 0.0005)

        # Ensure OHLC relationship
        high_price = max(high_price, open_price, close_price)
        low_price = min(low_price, open_price, close_price)

        bar = BarData(
            timestamp=timestamp,
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            volume=np.random.randint(1000, 10000),
        )

        bars.append(bar)

    return bars


def main():
    """Main function to demonstrate the 15-minute chart"""
    print("🚀 Starting 15-Minute Trade Chart")
    print("=" * 50)

    # Initialize chart
    chart = FifteenMinuteChart("EURUSD")

    # Generate 15-minute sample data
    print("Generating 15-minute sample data...")
    bars = generate_15min_data("EURUSD", hours=24)  # 24 hours of 15-min data (96 bars)

    # Process bars with progress bar
    print("Processing bars and generating signals...")
    for bar in tqdm(bars, desc="Processing bars", ncols=80):
        chart.add_bar(bar)

    # Create 15-minute chart
    print("\nCreating 15-minute trade chart...")
    chart.create_15min_chart()

    print("\n✅ 15-minute chart complete!")
    print("📊 Check '15min_trade_chart.png' for the chart")


if __name__ == "__main__":
    main()
