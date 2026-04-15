"""
Multi-Timeframe Strategy
1-Hour Breakout + Stochastic RSI + 15-Minute Reversal
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
import pytz
import os

# Set EST timezone
EST = pytz.timezone("US/Eastern")

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
    """Multi-timeframe signal data"""

    timestamp: datetime
    signal: str  # BUY, SELL, HOLD
    confidence: float
    price: float

    # 1-Hour Analysis
    hour_breakout: str  # BULLISH, BEARISH, NONE
    hour_stoch_k: float
    hour_stoch_d: float
    hour_stoch_condition: str  # BULLISH, BEARISH, NONE

    # 15-Minute Analysis
    min15_reversal: str  # BULLISH, BEARISH, NONE
    min15_stoch_k: float
    min15_stoch_d: float
    min15_stoch_crossover: str  # BULLISH, BEARISH, NONE

    # Trade Execution
    trade_executed: bool
    trade_reason: str


@dataclass
class TradeLog:
    """Trade log entry with detailed day/time tracking"""

    entry_date: str
    entry_time: str
    exit_date: str
    exit_time: str
    symbol: str
    direction: str  # BUY, SELL
    entry_price: float
    exit_price: float
    profit_loss: float
    profit_loss_pips: float
    trade_reason: str
    duration_minutes: int


class MultiTimeframeStrategy:
    """Multi-timeframe strategy with 1-hour breakout + Stochastic RSI + 15-min reversal"""

    def __init__(self, symbol: str = "EURUSD"):
        self.symbol = symbol
        self.bars_15min: List[BarData] = []
        self.bars_1hour: List[BarData] = []
        self.signals: List[SignalData] = []
        self.trade_log: List[TradeLog] = []
        self.current_position = None  # Track current open position
        self.daily_trades = {}  # Track trades by day

        # Strategy parameters
        self.stoch_period = 14
        self.stoch_k_period = 3
        self.stoch_d_period = 3
        self.rsi_period = 14

        # TradingView colors
        self.colors = {
            "background": "#1e222d",
            "grid": "#2a2e39",
            "text": "#d1d4dc",
            "candle_green": "#26a69a",
            "candle_red": "#ef5350",
            "breakout_bullish": "#4caf50",
            "breakout_bearish": "#f44336",
            "stoch_k": "#2196f3",
            "stoch_d": "#ff9800",
            "volume": "#607d8b",
            "buy_signal": "#4caf50",
            "sell_signal": "#f44336",
        }

    def add_15min_bar(self, bar: BarData):
        """Add new 15-minute bar"""
        self.bars_15min.append(bar)
        self._process_15min_bar(bar)
        self._check_daily_close(bar)

    def add_1hour_bar(self, bar: BarData):
        """Add new 1-hour bar"""
        self.bars_1hour.append(bar)

    def _check_daily_close(self, bar: BarData):
        """Check if we need to close trades at end of day"""
        current_date = bar.timestamp.date()
        current_time = bar.timestamp.time()

        # Close all positions at end of trading day (23:59)
        if current_time >= datetime.strptime("23:59", "%H:%M").time():
            if self.current_position:
                self._close_position(bar, "Daily Close")

    def _open_position(self, signal: SignalData, bar: BarData):
        """Open a new position"""
        if self.current_position:
            return  # Already have a position

        # Convert to EST for logging
        entry_time_est = bar.timestamp.astimezone(EST)
        entry_date = entry_time_est.strftime("%Y-%m-%d")
        entry_time = entry_time_est.strftime("%H:%M")

        self.current_position = {
            "entry_date": entry_date,
            "entry_time": entry_time,
            "direction": signal.signal,
            "entry_price": bar.close,
            "trade_reason": signal.trade_reason,
            "entry_bar": bar,
        }

        print(
            f"🟢 OPEN {signal.signal} at {entry_date} {entry_time} EST @ {bar.close:.5f}"
        )
        print(f"   Reason: {signal.trade_reason}")

    def _close_position(self, bar: BarData, close_reason: str):
        """Close current position"""
        if not self.current_position:
            return

        exit_price = bar.close
        entry_price = self.current_position["entry_price"]
        direction = self.current_position["direction"]

        # Calculate profit/loss
        if direction == "BUY":
            profit_loss = exit_price - entry_price
            profit_loss_pips = (exit_price - entry_price) * 10000  # For forex
        else:  # SELL
            profit_loss = entry_price - exit_price
            profit_loss_pips = (entry_price - exit_price) * 10000  # For forex

        # Calculate duration
        entry_timestamp = self.current_position["entry_bar"].timestamp
        duration_minutes = int((bar.timestamp - entry_timestamp).total_seconds() / 60)

        # Convert exit time to EST
        exit_time_est = bar.timestamp.astimezone(EST)
        exit_date = exit_time_est.strftime("%Y-%m-%d")
        exit_time = exit_time_est.strftime("%H:%M")

        # Create trade log entry
        trade_log = TradeLog(
            entry_date=self.current_position["entry_date"],
            entry_time=self.current_position["entry_time"],
            exit_date=exit_date,
            exit_time=exit_time,
            symbol=self.symbol,
            direction=direction,
            entry_price=entry_price,
            exit_price=exit_price,
            profit_loss=profit_loss,
            profit_loss_pips=profit_loss_pips,
            trade_reason=self.current_position["trade_reason"],
            duration_minutes=duration_minutes,
        )

        self.trade_log.append(trade_log)

        # Add to daily trades
        day_key = exit_date
        if day_key not in self.daily_trades:
            self.daily_trades[day_key] = []
        self.daily_trades[day_key].append(trade_log)

        print(f"🔴 CLOSE {direction} at {exit_date} {exit_time} EST @ {exit_price:.5f}")
        print(f"   P&L: {profit_loss_pips:.1f} pips ({profit_loss:.5f})")
        print(f"   Duration: {duration_minutes} minutes")
        print(f"   Reason: {close_reason}")
        print()

        self.current_position = None

    def _process_15min_bar(self, bar: BarData):
        """Process 15-minute bar and generate signals"""
        if len(self.bars_15min) < 50 or len(self.bars_1hour) < 20:
            return

        # Get 1-hour analysis
        hour_breakout, hour_stoch_k, hour_stoch_d = self._analyze_1hour_conditions(bar)

        # Get 15-minute reversal analysis
        min15_reversal, min15_stoch_k, min15_stoch_d = self._analyze_15min_reversal(bar)

        # Generate signal based on multi-timeframe logic
        signal, confidence, trade_reason = self._generate_multi_timeframe_signal(
            hour_breakout,
            hour_stoch_k,
            hour_stoch_d,
            min15_reversal,
            min15_stoch_k,
            min15_stoch_d,
        )

        # Create signal data
        signal_data = SignalData(
            timestamp=bar.timestamp,
            signal=signal,
            confidence=confidence,
            price=bar.close,
            hour_breakout=hour_breakout,
            hour_stoch_k=hour_stoch_k,
            hour_stoch_d=hour_stoch_d,
            hour_stoch_condition=self._get_stoch_condition(hour_stoch_k, hour_stoch_d),
            min15_reversal=min15_reversal,
            min15_stoch_k=min15_stoch_k,
            min15_stoch_d=min15_stoch_d,
            min15_stoch_crossover=self._get_stoch_crossover(
                min15_stoch_k, min15_stoch_d
            ),
            trade_executed=signal in ["BUY", "SELL"],
            trade_reason=trade_reason,
        )

        self.signals.append(signal_data)

        # Execute trades
        if signal in ["BUY", "SELL"] and not self.current_position:
            self._open_position(signal_data, bar)
        elif signal in ["BUY", "SELL"] and self.current_position:
            # Close existing position and open new one
            self._close_position(bar, "Signal Change")
            self._open_position(signal_data, bar)

    def _analyze_1hour_conditions(
        self, current_bar: BarData
    ) -> Tuple[str, float, float]:
        """Analyze 1st hour (22:00 EST) and 2nd hour (23:00 EST) breakout and Stochastic RSI conditions"""
        # Get current date in EST
        current_date = current_bar.timestamp.date()
        day_start = datetime.combine(current_date, datetime.min.time())
        day_start_est = EST.localize(day_start)
        day_end_est = day_start_est + timedelta(days=1)

        # Get bars for the current day in EST (for breakout logic)
        # Ensure all timestamps are timezone-aware for comparison
        day_bars = []
        for b in self.bars_15min:
            # Make timestamp timezone-aware if it isn't already
            if b.timestamp.tzinfo is None:
                b_timestamp = EST.localize(b.timestamp)
            else:
                b_timestamp = b.timestamp.astimezone(EST)

            if day_start_est <= b_timestamp < day_end_est:
                day_bars.append(b)

        if len(day_bars) < 8:
            return "NONE", 50.0, 50.0

        # First two hours bars (22:00-23:59 EST) - bars 0-7
        first_two_hours_bars = day_bars[:8]

        # Calculate highest high and lowest low of first two hours
        highest_high = max(b.high for b in first_two_hours_bars)
        lowest_low = min(b.low for b in first_two_hours_bars)

        # Check breakout against the highest high and lowest low of first two hours
        breakout = "NONE"
        if current_bar.close > highest_high:
            breakout = "BULLISH"
        elif current_bar.close < lowest_low:
            breakout = "BEARISH"

        # Log breakout detection with EST time
        if breakout != "NONE":
            current_time_est = current_bar.timestamp.astimezone(EST)
            print(f"🔍 BREAKOUT DETECTED: {breakout}")
            print(f"   Date: {current_time_est.strftime('%Y-%m-%d')}")
            print(f"   Time (EST): {current_time_est.strftime('%H:%M')}")
            print(f"   Current Price: {current_bar.close:.5f}")
            print(f"   First 2 Hours High: {highest_high:.5f}, Low: {lowest_low:.5f}")
            print()

        # Calculate 1-hour Stochastic RSI using more historical data
        hour_prices = [
            b.close for b in self.bars_1hour[-50:]
        ]  # Use last 50 hours for better calculation
        if len(hour_prices) < 28:  # Need at least 28 periods for RSI + Stochastic
            return breakout, 50.0, 50.0

        stoch_k, stoch_d = self._calculate_stochastic_rsi(hour_prices)

        return breakout, stoch_k, stoch_d

    def _analyze_15min_reversal(self, current_bar: BarData) -> Tuple[str, float, float]:
        """Analyze 15-minute reversal using Stochastic crossover"""
        if len(self.bars_15min) < 50:  # Need more data for proper calculation
            return "NONE", 50.0, 50.0

        # Get recent 15-minute prices (use more data for better calculation)
        recent_prices = [b.close for b in self.bars_15min[-100:]]  # Use last 100 bars

        # Calculate 15-minute Stochastic RSI
        stoch_k, stoch_d = self._calculate_stochastic_rsi(recent_prices)

        # Check for reversal patterns
        reversal = "NONE"

        # Bullish reversal: K crosses above D and K > 20
        if stoch_k > stoch_d and stoch_k > 20:
            # Check if this is a crossover (previous K < D)
            if len(self.bars_15min) >= 2:
                prev_prices = [b.close for b in self.bars_15min[-101:-1]]
                prev_stoch_k, prev_stoch_d = self._calculate_stochastic_rsi(prev_prices)
                if prev_stoch_k < prev_stoch_d:
                    reversal = "BULLISH"

        # Bearish reversal: K crosses below D and K < 80
        elif stoch_k < stoch_d and stoch_k < 80:
            # Check if this is a crossover (previous K > D)
            if len(self.bars_15min) >= 2:
                prev_prices = [b.close for b in self.bars_15min[-101:-1]]
                prev_stoch_k, prev_stoch_d = self._calculate_stochastic_rsi(prev_prices)
                if prev_stoch_k > prev_stoch_d:
                    reversal = "BEARISH"

        return reversal, stoch_k, stoch_d

    def _calculate_stochastic_rsi(self, prices: List[float]) -> Tuple[float, float]:
        """Calculate Stochastic RSI exactly like TradingView"""
        if len(prices) < 14:  # Need at least 14 periods for RSI
            return 50.0, 50.0

        # Calculate RSI using TradingView's method
        rsi_values = self._calculate_rsi_tradingview(prices, 14)

        if len(rsi_values) < 14:  # Need at least 14 RSI values for Stochastic
            return 50.0, 50.0

        # TradingView Stochastic RSI settings
        stoch_period = 14  # %K period
        k_smooth = 3  # %K smoothing
        d_period = 3  # %D period

        # Calculate %K values
        k_values = []
        for i in range(stoch_period - 1, len(rsi_values)):
            recent_rsi = rsi_values[i - stoch_period + 1 : i + 1]
            highest_high = max(recent_rsi)
            lowest_low = min(recent_rsi)

            if highest_high == lowest_low:
                k_val = 50.0
            else:
                k_val = (
                    (recent_rsi[-1] - lowest_low) / (highest_high - lowest_low)
                ) * 100
            k_values.append(k_val)

        if not k_values:
            return 50.0, 50.0

        # Apply %K smoothing (SMA of k_smooth periods)
        smoothed_k = []
        for i in range(len(k_values)):
            if i < k_smooth - 1:
                smoothed_k.append(k_values[i])
            else:
                avg_k = sum(k_values[i - k_smooth + 1 : i + 1]) / k_smooth
                smoothed_k.append(avg_k)

        # Current %K is the last smoothed value
        stoch_k = smoothed_k[-1]

        # Calculate %D as SMA of %K over d_period
        if len(smoothed_k) >= d_period:
            stoch_d = sum(smoothed_k[-d_period:]) / d_period
        else:
            stoch_d = stoch_k

        return stoch_k, stoch_d

    def _calculate_rsi_tradingview(
        self, prices: List[float], period: int = 14
    ) -> List[float]:
        """Calculate RSI exactly like TradingView"""
        if len(prices) < period + 1:
            return []

        # Calculate price changes
        deltas = []
        for i in range(1, len(prices)):
            deltas.append(prices[i] - prices[i - 1])

        # Separate gains and losses
        gains = [delta if delta > 0 else 0 for delta in deltas]
        losses = [-delta if delta < 0 else 0 for delta in deltas]

        # Calculate initial averages using simple average
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period

        rsi_values = []

        # Calculate RSI for each period
        for i in range(period, len(prices)):
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            rsi_values.append(rsi)

            # Update averages using Wilder's smoothing
            if i < len(prices) - 1:
                avg_gain = (avg_gain * (period - 1) + gains[i]) / period
                avg_loss = (avg_loss * (period - 1) + losses[i]) / period

        return rsi_values

    def _get_stoch_condition(self, k: float, d: float) -> str:
        """Get Stochastic condition for 1-hour analysis"""
        if k > d and k > 80:
            return "BULLISH"
        elif k < d and k < 20:
            return "BEARISH"
        else:
            return "NONE"

    def _get_stoch_crossover(self, k: float, d: float) -> str:
        """Get Stochastic crossover for 15-minute analysis"""
        if k > d:
            return "BULLISH"
        elif k < d:
            return "BEARISH"
        else:
            return "NONE"

    def _generate_multi_timeframe_signal(
        self,
        hour_breakout: str,
        hour_stoch_k: float,
        hour_stoch_d: float,
        min15_reversal: str,
        min15_stoch_k: float,
        min15_stoch_d: float,
    ) -> Tuple[str, float, str]:
        """Generate signal based on multi-timeframe logic"""

        # Check 1-hour conditions
        hour_stoch_condition = self._get_stoch_condition(hour_stoch_k, hour_stoch_d)

        # Multi-timeframe logic
        if hour_breakout == "BULLISH" and hour_stoch_condition == "BULLISH":
            # Bullish breakout + bullish Stochastic RSI
            if min15_reversal == "BULLISH":
                return (
                    "BUY",
                    0.9,
                    "Bullish breakout + bullish Stoch RSI + 15min bullish reversal",
                )
            else:
                return (
                    "HOLD",
                    0.7,
                    "Bullish breakout + bullish Stoch RSI (waiting for 15min reversal)",
                )

        elif hour_breakout == "BEARISH" and hour_stoch_condition == "BEARISH":
            # Bearish breakout + bearish Stochastic RSI
            if min15_reversal == "BEARISH":
                return (
                    "SELL",
                    0.9,
                    "Bearish breakout + bearish Stoch RSI + 15min bearish reversal",
                )
            else:
                return (
                    "HOLD",
                    0.7,
                    "Bearish breakout + bearish Stoch RSI (waiting for 15min reversal)",
                )

        else:
            return "HOLD", 0.5, "No clear multi-timeframe signal"

    def create_combined_chart(self, save_path: str = "combined_timeframe_chart.png"):
        """Create combined chart with both 1-hour and 15-minute timeframes"""
        if not self.bars_15min or not self.bars_1hour or not self.signals:
            print("No data to plot!")
            return

        # Use last 24 1-hour bars and last 96 15-minute bars
        bars_1hour = self.bars_1hour[-24:]
        bars_15min = (
            self.bars_15min[-96:] if len(self.bars_15min) > 96 else self.bars_15min
        )
        signals_1hour = self.signals[-24:]
        signals_15min = self.signals[-len(bars_15min) :]

        print(f"Combined chart: 1H={len(bars_1hour)} bars, 15M={len(bars_15min)} bars")

        # Create figure with 4 subplots: 1H price, 1H stoch, 15M price, 15M stoch
        fig = plt.figure(figsize=(20, 12), facecolor=self.colors["background"])
        gs = fig.add_gridspec(4, 2, height_ratios=[3, 1, 3, 1], hspace=0.15, wspace=0.1)

        # 1-Hour Chart (Left side)
        ax1_1hour = fig.add_subplot(gs[0, 0])  # 1H Price
        ax2_1hour = fig.add_subplot(gs[1, 0])  # 1H Stochastic

        # 15-Minute Chart (Right side)
        ax1_15min = fig.add_subplot(gs[0, 1])  # 15M Price
        ax2_15min = fig.add_subplot(gs[1, 1])  # 15M Stochastic

        # ===== 1-HOUR CHART (LEFT) =====

        # Prepare 1-hour data
        timestamps_1h = [b.timestamp for b in bars_1hour]
        opens_1h = [b.open for b in bars_1hour]
        highs_1h = [b.high for b in bars_1hour]
        lows_1h = [b.low for b in bars_1hour]
        closes_1h = [b.close for b in bars_1hour]

        # Plot 1-hour candlesticks
        for i, (timestamp, open_price, high, low, close) in enumerate(
            zip(timestamps_1h, opens_1h, highs_1h, lows_1h, closes_1h)
        ):
            color = (
                self.colors["candle_green"]
                if close >= open_price
                else self.colors["candle_red"]
            )

            from matplotlib.patches import Rectangle

            ax1_1hour.add_patch(
                Rectangle(
                    (i - 0.3, min(open_price, close)),
                    0.6,
                    abs(close - open_price),
                    facecolor=color,
                    alpha=0.8,
                    edgecolor=color,
                    linewidth=1,
                )
            )
            ax1_1hour.plot([i, i], [low, high], color=color, linewidth=1.5)

        # Plot breakout levels for 1-hour chart
        current_date = None
        for i, bar in enumerate(bars_1hour):
            bar_date = bar.timestamp.date()

            if bar_date != current_date:
                current_date = bar_date
                day_start = datetime.combine(bar_date, datetime.min.time())
                day_start_est = EST.localize(day_start)
                day_end_est = day_start_est + timedelta(days=1)

                # Get 15-minute bars for this day
                day_15min_bars = []
                for b in self.bars_15min:
                    if b.timestamp.tzinfo is None:
                        b_timestamp = EST.localize(b.timestamp)
                    else:
                        b_timestamp = b.timestamp.astimezone(EST)

                    if day_start_est <= b_timestamp < day_end_est:
                        day_15min_bars.append(b)

                # First two hours = first 8 bars (22:00-23:59 EST)
                if len(day_15min_bars) >= 8:
                    first_two_hours_high = max(b.high for b in day_15min_bars[:8])
                    first_two_hours_low = min(b.low for b in day_15min_bars[:8])

                    # Draw breakout levels for this day
                    ax1_1hour.axhline(
                        y=first_two_hours_high,
                        color="#ff9800",
                        linestyle="--",
                        linewidth=2,
                        alpha=0.7,
                        label=f"First 2H High ({bar_date})" if i == 0 else "",
                    )
                    ax1_1hour.axhline(
                        y=first_two_hours_low,
                        color="#ff9800",
                        linestyle=":",
                        linewidth=2,
                        alpha=0.7,
                        label=f"First 2H Low ({bar_date})" if i == 0 else "",
                    )

        # Plot 1-hour buy/sell signals
        buy_signals_1h = [s for s in signals_1hour if s.signal == "BUY"]
        sell_signals_1h = [s for s in signals_1hour if s.signal == "SELL"]

        if buy_signals_1h:
            buy_indices = [
                timestamps_1h.index(s.timestamp)
                for s in buy_signals_1h
                if s.timestamp in timestamps_1h
            ]
            buy_prices = [
                s.price for s in buy_signals_1h if s.timestamp in timestamps_1h
            ]
            if buy_indices:
                ax1_1hour.scatter(
                    buy_indices,
                    buy_prices,
                    marker="^",
                    color=self.colors["buy_signal"],
                    s=150,
                    label="Buy Signal",
                    zorder=5,
                    edgecolors="white",
                    linewidth=2,
                )

        if sell_signals_1h:
            sell_indices = [
                timestamps_1h.index(s.timestamp)
                for s in sell_signals_1h
                if s.timestamp in timestamps_1h
            ]
            sell_prices = [
                s.price for s in sell_signals_1h if s.timestamp in timestamps_1h
            ]
            if sell_indices:
                ax1_1hour.scatter(
                    sell_indices,
                    sell_prices,
                    marker="v",
                    color=self.colors["sell_signal"],
                    s=150,
                    label="Sell Signal",
                    zorder=5,
                    edgecolors="white",
                    linewidth=2,
                )

        # Format 1-hour price chart
        ax1_1hour.set_title(
            "1-Hour Breakout Analysis",
            color=self.colors["text"],
            fontsize=14,
            fontweight="bold",
        )
        ax1_1hour.set_ylabel("Price", color=self.colors["text"])
        ax1_1hour.legend(loc="upper left", framealpha=0.8, fontsize=8)
        ax1_1hour.grid(True, alpha=0.2, color=self.colors["grid"])
        ax1_1hour.set_facecolor(self.colors["background"])

        # 1-Hour Stochastic RSI
        hour_stoch_k_values = []
        hour_stoch_d_values = []

        for signal in signals_1hour:
            hour_stoch_k_values.append(signal.hour_stoch_k)
            hour_stoch_d_values.append(signal.hour_stoch_d)

        # Pad if needed
        while len(hour_stoch_k_values) < len(bars_1hour):
            if hour_stoch_k_values:
                hour_stoch_k_values.append(hour_stoch_k_values[-1])
                hour_stoch_d_values.append(hour_stoch_d_values[-1])
            else:
                hour_stoch_k_values.append(50.0)
                hour_stoch_d_values.append(50.0)

        # Plot 1-Hour Stochastic RSI
        ax2_1hour.plot(
            range(len(bars_1hour)),
            hour_stoch_k_values,
            label="1H Stoch K",
            color="#2196f3",
            linewidth=1.5,
        )
        ax2_1hour.plot(
            range(len(bars_1hour)),
            hour_stoch_d_values,
            label="1H Stoch D",
            color="#f44336",
            linewidth=1.5,
        )

        # Overbought/oversold zones
        ax2_1hour.axhspan(80, 100, alpha=0.1, color="#ff9800", label="Overbought Zone")
        ax2_1hour.axhspan(0, 20, alpha=0.1, color="#ff9800", label="Oversold Zone")
        ax2_1hour.axhline(y=80, color="#ff9800", linestyle="--", alpha=0.7, linewidth=1)
        ax2_1hour.axhline(y=20, color="#ff9800", linestyle="--", alpha=0.7, linewidth=1)
        ax2_1hour.axhline(
            y=50, color="#9e9e9e", linestyle=":", alpha=0.5, linewidth=0.5
        )

        ax2_1hour.set_ylabel("1H Stoch RSI", color=self.colors["text"])
        ax2_1hour.set_ylim(0, 100)
        ax2_1hour.legend(loc="upper left", framealpha=0.8, fontsize=8)
        ax2_1hour.grid(True, alpha=0.2, color=self.colors["grid"])
        ax2_1hour.set_facecolor(self.colors["background"])

        # ===== 15-MINUTE CHART (RIGHT) =====

        # Prepare 15-minute data
        timestamps_15m = [b.timestamp for b in bars_15min]
        opens_15m = [b.open for b in bars_15min]
        highs_15m = [b.high for b in bars_15min]
        lows_15m = [b.low for b in bars_15min]
        closes_15m = [b.close for b in bars_15min]

        # Plot 15-minute candlesticks
        for i, (timestamp, open_price, high, low, close) in enumerate(
            zip(timestamps_15m, opens_15m, highs_15m, lows_15m, closes_15m)
        ):
            color = (
                self.colors["candle_green"]
                if close >= open_price
                else self.colors["candle_red"]
            )

            from matplotlib.patches import Rectangle

            ax1_15min.add_patch(
                Rectangle(
                    (i - 0.3, min(open_price, close)),
                    0.6,
                    abs(close - open_price),
                    facecolor=color,
                    alpha=0.8,
                    edgecolor=color,
                    linewidth=1,
                )
            )
            ax1_15min.plot([i, i], [low, high], color=color, linewidth=1.5)

        # Plot 15-minute buy/sell signals
        buy_signals_15m = [s for s in signals_15min if s.signal == "BUY"]
        sell_signals_15m = [s for s in signals_15min if s.signal == "SELL"]

        if buy_signals_15m:
            buy_indices = [
                timestamps_15m.index(s.timestamp)
                for s in buy_signals_15m
                if s.timestamp in timestamps_15m
            ]
            buy_prices = [
                s.price for s in buy_signals_15m if s.timestamp in timestamps_15m
            ]
            if buy_indices:
                ax1_15min.scatter(
                    buy_indices,
                    buy_prices,
                    marker="^",
                    color=self.colors["buy_signal"],
                    s=150,
                    label="Buy Signal",
                    zorder=5,
                    edgecolors="white",
                    linewidth=2,
                )

        if sell_signals_15m:
            sell_indices = [
                timestamps_15m.index(s.timestamp)
                for s in sell_signals_15m
                if s.timestamp in timestamps_15m
            ]
            sell_prices = [
                s.price for s in sell_signals_15m if s.timestamp in timestamps_15m
            ]
            if sell_indices:
                ax1_15min.scatter(
                    sell_indices,
                    sell_prices,
                    marker="v",
                    color=self.colors["sell_signal"],
                    s=150,
                    label="Sell Signal",
                    zorder=5,
                    edgecolors="white",
                    linewidth=2,
                )

        # Format 15-minute price chart
        ax1_15min.set_title(
            "15-Minute Reversal Analysis",
            color=self.colors["text"],
            fontsize=14,
            fontweight="bold",
        )
        ax1_15min.set_ylabel("Price", color=self.colors["text"])
        ax1_15min.legend(loc="upper left", framealpha=0.8, fontsize=8)
        ax1_15min.grid(True, alpha=0.2, color=self.colors["grid"])
        ax1_15min.set_facecolor(self.colors["background"])

        # 15-Minute Stochastic RSI
        min15_stoch_k_values = []
        min15_stoch_d_values = []

        for signal in signals_15min:
            min15_stoch_k_values.append(signal.min15_stoch_k)
            min15_stoch_d_values.append(signal.min15_stoch_d)

        # Ensure we have the same number of values as bars
        while len(min15_stoch_k_values) < len(bars_15min):
            if min15_stoch_k_values:
                min15_stoch_k_values.append(min15_stoch_k_values[-1])
                min15_stoch_d_values.append(min15_stoch_d_values[-1])
            else:
                min15_stoch_k_values.append(50.0)
                min15_stoch_d_values.append(50.0)

        # Plot 15-Minute Stochastic RSI
        ax2_15min.plot(
            range(len(bars_15min)),
            min15_stoch_k_values,
            label="15M Stoch K",
            color="#2196f3",
            linewidth=1.5,
        )
        ax2_15min.plot(
            range(len(bars_15min)),
            min15_stoch_d_values,
            label="15M Stoch D",
            color="#f44336",
            linewidth=1.5,
        )

        # Overbought/oversold zones
        ax2_15min.axhspan(80, 100, alpha=0.1, color="#ff9800", label="Overbought Zone")
        ax2_15min.axhspan(0, 20, alpha=0.1, color="#ff9800", label="Oversold Zone")
        ax2_15min.axhline(y=80, color="#ff9800", linestyle="--", alpha=0.7, linewidth=1)
        ax2_15min.axhline(y=20, color="#ff9800", linestyle="--", alpha=0.7, linewidth=1)
        ax2_15min.axhline(
            y=50, color="#9e9e9e", linestyle=":", alpha=0.5, linewidth=0.5
        )

        ax2_15min.set_ylabel("15M Stoch RSI", color=self.colors["text"])
        ax2_15min.set_ylim(0, 100)
        ax2_15min.legend(loc="upper left", framealpha=0.8, fontsize=8)
        ax2_15min.grid(True, alpha=0.2, color=self.colors["grid"])
        ax2_15min.set_facecolor(self.colors["background"])

        # Format x-axes
        if len(timestamps_1h) > 0:
            step_1h = max(1, len(timestamps_1h) // 6)
            tick_positions_1h = range(0, len(timestamps_1h), step_1h)
            tick_labels_1h = [
                timestamps_1h[i].strftime("%H:%M") for i in tick_positions_1h
            ]
            ax2_1hour.set_xticks(tick_positions_1h)
            ax2_1hour.set_xticklabels(
                tick_labels_1h, rotation=45, color=self.colors["text"]
            )

        if len(timestamps_15m) > 0:
            step_15m = max(1, len(timestamps_15m) // 8)
            tick_positions_15m = range(0, len(timestamps_15m), step_15m)
            tick_labels_15m = [
                timestamps_15m[i].strftime("%H:%M") for i in tick_positions_15m
            ]
            ax2_15min.set_xticks(tick_positions_15m)
            ax2_15min.set_xticklabels(
                tick_labels_15m, rotation=45, color=self.colors["text"]
            )

        # Color all spines
        for ax in [ax1_1hour, ax2_1hour, ax1_15min, ax2_15min]:
            for spine in ax.spines.values():
                spine.set_color(self.colors["grid"])

        # Add main title
        fig.suptitle(
            f"{self.symbol} - Multi-Timeframe Analysis",
            color=self.colors["text"],
            fontsize=18,
            fontweight="bold",
            y=0.98,
        )

        plt.tight_layout()
        plt.savefig(
            save_path, dpi=300, bbox_inches="tight", facecolor=self.colors["background"]
        )
        plt.show()


def generate_multi_timeframe_data(
    symbol: str = "EURUSD", days: int = 7
) -> Tuple[List[BarData], List[BarData]]:
    """Generate multi-timeframe sample data with more historical data for proper indicator calculation"""
    print(f"Generating {days} days of multi-timeframe sample data...")

    # Generate more data for proper indicator calculation
    total_hours = days * 24
    total_15min_bars = days * 24 * 4  # 4 15-min bars per hour

    # Generate 1-hour bars
    bars_1hour = []
    base_price = 1.1000
    current_price = base_price

    for hour in range(total_hours):
        # Create some realistic price movement
        timestamp = datetime.now() - timedelta(hours=total_hours - hour)

        # Add some volatility
        price_change = np.random.normal(0, 0.002)  # 2 pips average movement
        current_price += price_change

        # Ensure price stays in reasonable range
        current_price = max(1.0500, min(1.2000, current_price))

        # Create OHLC data
        high = current_price + abs(np.random.normal(0, 0.001))
        low = current_price - abs(np.random.normal(0, 0.001))
        open_price = current_price - np.random.normal(0, 0.0005)
        close_price = current_price

        bar = BarData(
            timestamp=timestamp,
            open=open_price,
            high=high,
            low=low,
            close=close_price,
            volume=np.random.uniform(1000, 5000),
        )
        bars_1hour.append(bar)

    # Generate 15-minute bars
    bars_15min = []
    current_price = base_price

    for bar_15min in range(total_15min_bars):
        # Create some realistic price movement
        timestamp = datetime.now() - timedelta(
            minutes=15 * total_15min_bars - bar_15min * 15
        )

        # Add some volatility
        price_change = np.random.normal(0, 0.001)  # 1 pip average movement
        current_price += price_change

        # Ensure price stays in reasonable range
        current_price = max(1.0500, min(1.2000, current_price))

        # Create OHLC data
        high = current_price + abs(np.random.normal(0, 0.0005))
        low = current_price - abs(np.random.normal(0, 0.0005))
        open_price = current_price - np.random.normal(0, 0.0002)
        close_price = current_price

        bar = BarData(
            timestamp=timestamp,
            open=open_price,
            high=high,
            low=low,
            close=close_price,
            volume=np.random.uniform(500, 2000),
        )
        bars_15min.append(bar)

    print(
        f"Generated {len(bars_1hour)} 1-hour bars and {len(bars_15min)} 15-minute bars"
    )
    return bars_1hour, bars_15min


def main():
    """Main function to demonstrate the multi-timeframe strategy"""
    print("🚀 Starting Multi-Timeframe Strategy")
    print("=" * 60)

    # Initialize strategy
    strategy = MultiTimeframeStrategy("EURUSD")

    # Generate sample data
    print("Generating multi-timeframe sample data...")
    bars_15min, bars_1hour = generate_multi_timeframe_data("EURUSD", days=7)

    # Add 1-hour bars first
    print("Processing 1-hour bars...")
    for bar in tqdm(bars_1hour, desc="Processing 1H bars", ncols=80):
        strategy.add_1hour_bar(bar)

    # Process 15-minute bars
    print("Processing 15-minute bars and generating signals...")
    for bar in tqdm(bars_15min, desc="Processing 15M bars", ncols=80):
        strategy.add_15min_bar(bar)

    # Create combined chart
    print("\nCreating combined multi-timeframe analysis chart...")
    strategy.create_combined_chart()

    print("\n✅ Multi-timeframe analysis complete!")
    print("📊 Check 'combined_timeframe_chart.png' for the analysis")


if __name__ == "__main__":
    main()
