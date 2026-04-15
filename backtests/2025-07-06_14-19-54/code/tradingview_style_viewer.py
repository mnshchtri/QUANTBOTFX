"""
TradingView Style Strategy Viewer
Professional multi-slide candlestick charts with weekly breakdowns
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

# Set professional TradingView-style appearance
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


class TradingViewStyleViewer:
    """Professional TradingView-style chart viewer with weekly slides"""

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
        """Generate trading signal with enhanced logic"""
        # Technical rules
        ema_bullish = ema_fast > ema_slow
        rsi_oversold = rsi < 30
        rsi_overbought = rsi > 70
        macd_bullish = macd > macd_signal
        bb_squeeze = (bb_upper - bb_lower) / bb_lower < 0.01  # Low volatility
        bb_breakout_up = price > bb_upper
        bb_breakout_down = price < bb_lower

        # Calculate confidence based on multiple factors
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
        if not bb_squeeze:
            confidence += 0.05

        # Generate signal with enhanced logic
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

    def create_weekly_slides(self, save_path: str = "tradingview_weekly_slides.png"):
        """Create multiple weekly slides with TradingView-style charts"""
        if not self.bars or not self.signals:
            print("No data to plot!")
            return

        # Group data by weeks
        weekly_data = self._group_by_weeks()

        # Create slides
        num_weeks = len(weekly_data)
        fig, axes = plt.subplots(num_weeks, 1, figsize=(20, 6 * num_weeks))
        if num_weeks == 1:
            axes = [axes]

        fig.suptitle(
            f"{self.symbol} - Weekly Strategy Analysis",
            fontsize=20,
            fontweight="bold",
            color=self.colors["text"],
        )

        for week_idx, (week_start, week_data) in enumerate(weekly_data.items()):
            ax = axes[week_idx]
            self._create_weekly_chart(ax, week_data, week_start, week_idx + 1)

        plt.tight_layout()
        plt.savefig(
            save_path, dpi=300, bbox_inches="tight", facecolor=self.colors["background"]
        )
        plt.show()

        # Print comprehensive statistics
        self._print_comprehensive_statistics()

    def _group_by_weeks(self) -> Dict[datetime, List[Tuple[BarData, SignalData]]]:
        """Group bars and signals by weeks"""
        weekly_data = {}

        for bar in self.bars:
            # Find corresponding signal
            signal = None
            for s in self.signals:
                if s.timestamp == bar.timestamp:
                    signal = s
                    break

            if signal:
                week_start = bar.timestamp - timedelta(days=bar.timestamp.weekday())
                week_start = week_start.replace(
                    hour=0, minute=0, second=0, microsecond=0
                )

                if week_start not in weekly_data:
                    weekly_data[week_start] = []

                weekly_data[week_start].append((bar, signal))

        return weekly_data

    def _create_weekly_chart(
        self,
        ax,
        week_data: List[Tuple[BarData, SignalData]],
        week_start: datetime,
        week_num: int,
    ):
        """Create a single weekly chart with TradingView style"""
        bars = [item[0] for item in week_data]
        signals = [item[1] for item in week_data]

        # Set up the chart
        ax.set_facecolor(self.colors["background"])
        ax.grid(True, alpha=0.2, color=self.colors["grid"])

        # Prepare data
        timestamps = [b.timestamp for b in bars]
        opens = [b.open for b in bars]
        highs = [b.high for b in bars]
        lows = [b.low for b in bars]
        closes = [b.close for b in bars]
        volumes = [b.volume for b in bars]

        # Create candlesticks
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

            ax.add_patch(
                plt.Rectangle(
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
            ax.plot([i, i], [low, high], color=color, linewidth=1.5)

        # Plot EMAs
        if signals:
            ema_fast_values = [s.ema_fast for s in signals]
            ema_slow_values = [s.ema_slow for s in signals]

            ax.plot(
                range(len(signals)),
                ema_fast_values,
                label="EMA Fast",
                color=self.colors["ema_fast"],
                linewidth=2,
            )
            ax.plot(
                range(len(signals)),
                ema_slow_values,
                label="EMA Slow",
                color=self.colors["ema_slow"],
                linewidth=2,
            )

        # Plot Bollinger Bands
        if signals:
            bb_upper_values = [s.bb_upper for s in signals]
            bb_lower_values = [s.bb_lower for s in signals]
            bb_middle_values = [s.bb_middle for s in signals]

            ax.plot(
                range(len(signals)),
                bb_upper_values,
                label="BB Upper",
                color=self.colors["bb_upper"],
                linewidth=1,
                alpha=0.7,
            )
            ax.plot(
                range(len(signals)),
                bb_lower_values,
                label="BB Lower",
                color=self.colors["bb_lower"],
                linewidth=1,
                alpha=0.7,
            )
            ax.plot(
                range(len(signals)),
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
            buy_indices = [signals.index(s) for s in buy_signals]
            buy_prices = [s.price for s in buy_signals]
            ax.scatter(
                buy_indices,
                buy_prices,
                marker="^",
                color=self.colors["candle_green"],
                s=200,
                label="Buy Signal",
                zorder=5,
                edgecolors="white",
                linewidth=1,
            )

        if sell_signals:
            sell_indices = [signals.index(s) for s in sell_signals]
            sell_prices = [s.price for s in sell_signals]
            ax.scatter(
                sell_indices,
                sell_prices,
                marker="v",
                color=self.colors["candle_red"],
                s=200,
                label="Sell Signal",
                zorder=5,
                edgecolors="white",
                linewidth=1,
            )

        # Format chart
        ax.set_title(
            f'Week {week_num} - {week_start.strftime("%B %d, %Y")}',
            color=self.colors["text"],
            fontsize=14,
            fontweight="bold",
        )
        ax.set_ylabel("Price", color=self.colors["text"])
        ax.legend(loc="upper left", framealpha=0.8)

        # Set x-axis labels
        if len(timestamps) > 0:
            step = max(1, len(timestamps) // 5)
            tick_positions = range(0, len(timestamps), step)
            tick_labels = [timestamps[i].strftime("%H:%M") for i in tick_positions]
            ax.set_xticks(tick_positions)
            ax.set_xticklabels(tick_labels, rotation=45, color=self.colors["text"])

        # Color the spines
        for spine in ax.spines.values():
            spine.set_color(self.colors["grid"])

    def create_comprehensive_chart(
        self, save_path: str = "tradingview_comprehensive.png"
    ):
        """Create a comprehensive TradingView-style chart with all indicators"""
        if not self.bars or not self.signals:
            print("No data to plot!")
            return

        # Create figure with subplots
        fig = plt.figure(figsize=(20, 16), facecolor=self.colors["background"])
        gs = fig.add_gridspec(4, 1, height_ratios=[3, 1, 1, 1], hspace=0.1)

        # Main price chart
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1])  # RSI
        ax3 = fig.add_subplot(gs[2])  # MACD
        ax4 = fig.add_subplot(gs[3])  # Volume

        # Prepare data
        timestamps = [b.timestamp for b in self.bars]
        opens = [b.open for b in self.bars]
        highs = [b.high for b in self.bars]
        lows = [b.low for b in self.bars]
        closes = [b.close for b in self.bars]
        volumes = [b.volume for b in self.bars]

        # 1. Main candlestick chart
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

            ax1.add_patch(
                plt.Rectangle(
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

        # Plot EMAs and Bollinger Bands
        signal_indices = []
        for signal in self.signals:
            try:
                idx = timestamps.index(signal.timestamp)
                signal_indices.append(idx)
            except ValueError:
                continue

        if signal_indices:
            ema_fast_values = [s.ema_fast for s in self.signals]
            ema_slow_values = [s.ema_slow for s in self.signals]
            bb_upper_values = [s.bb_upper for s in self.signals]
            bb_lower_values = [s.bb_lower for s in self.signals]
            bb_middle_values = [s.bb_middle for s in self.signals]

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

        # Plot signals
        buy_signals = [s for s in self.signals if s.signal == "BUY"]
        sell_signals = [s for s in self.signals if s.signal == "SELL"]

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
                    color=self.colors["candle_green"],
                    s=200,
                    label="Buy Signal",
                    zorder=5,
                    edgecolors="white",
                    linewidth=1,
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
                    color=self.colors["candle_red"],
                    s=200,
                    label="Sell Signal",
                    zorder=5,
                    edgecolors="white",
                    linewidth=1,
                )

        # Format main chart
        ax1.set_title(
            f"{self.symbol} - Comprehensive Strategy Analysis",
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
            rsi_values = [s.rsi for s in self.signals]
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
            macd_values = [s.macd for s in self.signals]
            macd_signal_values = [s.macd_signal for s in self.signals]
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

    def _print_comprehensive_statistics(self):
        """Print comprehensive strategy statistics"""
        if not self.signals:
            return

        print("\n" + "=" * 80)
        print("TRADINGVIEW STYLE STRATEGY ANALYSIS")
        print("=" * 80)

        # Signal statistics
        total_signals = len(self.signals)
        buy_signals = len([s for s in self.signals if s.signal == "BUY"])
        sell_signals = len([s for s in self.signals if s.signal == "SELL"])
        hold_signals = len([s for s in self.signals if s.signal == "HOLD"])

        print(f"📊 SIGNAL STATISTICS:")
        print(f"   Total Signals: {total_signals}")
        print(f"   Buy Signals: {buy_signals} ({buy_signals/total_signals*100:.1f}%)")
        print(
            f"   Sell Signals: {sell_signals} ({sell_signals/total_signals*100:.1f}%)"
        )
        print(
            f"   Hold Signals: {hold_signals} ({hold_signals/total_signals*100:.1f}%)"
        )

        # Price statistics
        prices = [b.close for b in self.bars]
        print(f"\n📈 PRICE STATISTICS:")
        print(f"   Starting Price: {prices[0]:.5f}")
        print(f"   Ending Price: {prices[-1]:.5f}")
        print(f"   Price Change: {((prices[-1] - prices[0]) / prices[0] * 100):.2f}%")
        print(f"   Highest Price: {max(prices):.5f}")
        print(f"   Lowest Price: {min(prices):.5f}")
        print(f"   Average Price: {np.mean(prices):.5f}")
        print(f"   Price Volatility: {np.std(prices):.5f}")

        # Indicator statistics
        if self.signals:
            rsi_values = [s.rsi for s in self.signals]
            ema_ratios = [s.ema_fast / s.ema_slow for s in self.signals]
            atr_values = [s.atr for s in self.signals]

            print(f"\n📊 INDICATOR STATISTICS:")
            print(f"   Average RSI: {np.mean(rsi_values):.1f}")
            print(f"   RSI Range: {np.min(rsi_values):.1f} - {np.max(rsi_values):.1f}")
            print(f"   Average EMA Ratio: {np.mean(ema_ratios):.5f}")
            print(
                f"   EMA Ratio Range: {np.min(ema_ratios):.5f} - {np.max(ema_ratios):.5f}"
            )
            print(f"   Average ATR: {np.mean(atr_values):.5f}")
            print(f"   ATR Range: {np.min(atr_values):.5f} - {np.max(atr_values):.5f}")

        # Performance metrics
        if buy_signals > 0 or sell_signals > 0:
            print(f"\n🎯 PERFORMANCE METRICS:")
            print(
                f"   Signal Frequency: {(buy_signals + sell_signals) / total_signals * 100:.1f}%"
            )
            print(f"   Buy/Sell Ratio: {buy_signals / max(sell_signals, 1):.2f}")

            # Calculate potential profit (simplified)
            if buy_signals > 0:
                avg_buy_price = np.mean(
                    [s.price for s in self.signals if s.signal == "BUY"]
                )
                final_price = prices[-1]
                potential_profit = (final_price - avg_buy_price) / avg_buy_price * 100
                print(f"   Potential Buy Profit: {potential_profit:.2f}%")

        print("=" * 80)


def generate_sample_data(symbol: str = "EURUSD", weeks: int = 4) -> List[BarData]:
    """Generate sample forex data for multiple weeks"""
    bars = []
    start_date = datetime(2024, 1, 1)
    base_price = 1.1000  # EURUSD starting price

    for i in range(weeks * 7 * 24 * 60):  # Minute data for multiple weeks
        timestamp = start_date + timedelta(minutes=i)

        # Simulate realistic price movement with trends
        trend = np.sin(i / (24 * 60 * 7)) * 0.002  # Weekly trend
        noise = np.random.normal(0, 0.0003)  # Random noise
        volatility = 0.0002 + 0.0002 * np.sin(i / (24 * 60))  # Daily volatility cycle

        # Add some breakout patterns
        if i % (24 * 60 * 3) == 0:  # Every 3 days
            trend += np.random.choice([-0.005, 0.005])  # Random breakout

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
            volume=np.random.randint(1000, 15000),
        )

        bars.append(bar)

    return bars


def main():
    """Main function to demonstrate the TradingView-style viewer"""
    print("🚀 Starting TradingView Style Strategy Viewer")
    print("=" * 60)

    # Initialize viewer
    viewer = TradingViewStyleViewer("EURUSD")

    # Generate sample data for multiple weeks
    print("Generating sample data for 4 weeks...")
    bars = generate_sample_data("EURUSD", weeks=4)

    # Process bars
    print("Processing bars and generating signals...")
    for i, bar in enumerate(bars):
        viewer.add_bar(bar)

        # Print progress every 500 bars
        if (i + 1) % 500 == 0:
            print(f"Processed {i + 1}/{len(bars)} bars...")

    # Create weekly slides
    print("\nCreating weekly slides...")
    viewer.create_weekly_slides()

    # Create comprehensive chart
    print("\nCreating comprehensive TradingView-style chart...")
    viewer.create_comprehensive_chart()

    print("\n✅ TradingView-style analysis complete!")
    print("📊 Check 'tradingview_weekly_slides.png' for weekly breakdowns")
    print("📊 Check 'tradingview_comprehensive.png' for comprehensive analysis")


if __name__ == "__main__":
    main()
