"""
Detailed Trade Analyzer
Comprehensive trade analysis with first-hour levels, breakouts, and reversals
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
class FirstHourLevels:
    """First hour high/low levels for each day"""

    date: datetime
    first_hour_high: float
    first_hour_low: float
    first_hour_open: float
    first_hour_close: float
    breakout_high: bool = False
    breakout_low: bool = False


@dataclass
class TradeSignal:
    """Detailed trade signal with all analysis"""

    timestamp: datetime
    signal: str  # BUY, SELL, HOLD
    confidence: float
    price: float
    signal_type: str  # BREAKOUT, REVERSAL, TREND_FOLLOWING
    first_hour_high: float
    first_hour_low: float
    breakout_confirmed: bool
    reversal_15min: bool
    rsi: float
    ema_fast: float
    ema_slow: float
    macd: float
    macd_signal: float
    atr: float
    bb_upper: float
    bb_lower: float
    bb_middle: float
    volume_ratio: float
    price_momentum: float
    support_level: float
    resistance_level: float
    trade_reason: str
    risk_reward_ratio: float


class DetailedTradeAnalyzer:
    """Comprehensive trade analyzer with detailed insights"""

    def __init__(self, symbol: str = "EURUSD"):
        self.symbol = symbol
        self.bars: List[BarData] = []
        self.signals: List[TradeSignal] = []
        self.first_hour_levels: List[FirstHourLevels] = []

        # Strategy parameters
        self.ema_fast_period = 12
        self.ema_slow_period = 26
        self.rsi_period = 14
        self.bb_period = 20
        self.bb_std = 2
        self.atr_period = 14
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
            "first_hour_high": "#ff5722",
            "first_hour_low": "#4caf50",
            "breakout": "#ffeb3b",
            "reversal": "#e91e63",
        }

    def add_bar(self, bar: BarData):
        """Add new market bar"""
        self.bars.append(bar)
        self._process_bar(bar)

    def _process_bar(self, bar: BarData):
        """Process new bar and generate detailed signals"""
        if len(self.bars) < 50:  # Need minimum data
            return

        # Update first hour levels
        self._update_first_hour_levels(bar)

        # Calculate indicators
        prices = np.array([b.close for b in self.bars])
        highs = np.array([b.high for b in self.bars])
        lows = np.array([b.low for b in self.bars])
        volumes = np.array([b.volume for b in self.bars])

        ema_fast = self._calculate_ema(prices, self.ema_fast_period)
        ema_slow = self._calculate_ema(prices, self.ema_slow_period)
        rsi = self._calculate_rsi(prices, self.rsi_period)
        macd_line, signal_line = self._calculate_macd(prices)
        atr = self._calculate_atr(highs, lows, prices)
        bb_upper, bb_lower, bb_middle = self._calculate_bollinger_bands(prices)

        # Current values
        current_idx = len(prices) - 1

        # Get first hour levels for current day
        first_hour_levels = self._get_first_hour_levels(bar.timestamp)

        # Analyze breakouts and reversals
        breakout_analysis = self._analyze_breakouts(bar, first_hour_levels)
        reversal_analysis = self._analyze_15min_reversal(bar, prices, current_idx)

        # Generate comprehensive signal
        (
            signal,
            confidence,
            signal_type,
            trade_reason,
        ) = self._generate_comprehensive_signal(
            bar,
            prices[current_idx],
            ema_fast[current_idx],
            ema_slow[current_idx],
            rsi[current_idx],
            macd_line[current_idx],
            signal_line[current_idx],
            bb_upper[current_idx],
            bb_lower[current_idx],
            atr[current_idx],
            breakout_analysis,
            reversal_analysis,
            first_hour_levels,
        )

        # Calculate additional metrics
        volume_ratio = self._calculate_volume_ratio(volumes, current_idx)
        price_momentum = self._calculate_price_momentum(prices, current_idx)
        support_resistance = self._calculate_support_resistance(prices, current_idx)
        risk_reward = self._calculate_risk_reward_ratio(bar, signal, atr[current_idx])

        # Create detailed signal
        signal_data = TradeSignal(
            timestamp=bar.timestamp,
            signal=signal,
            confidence=confidence,
            price=bar.close,
            signal_type=signal_type,
            first_hour_high=first_hour_levels.first_hour_high
            if first_hour_levels
            else 0,
            first_hour_low=first_hour_levels.first_hour_low if first_hour_levels else 0,
            breakout_confirmed=breakout_analysis["confirmed"],
            reversal_15min=reversal_analysis["detected"],
            rsi=rsi[current_idx],
            ema_fast=ema_fast[current_idx],
            ema_slow=ema_slow[current_idx],
            macd=macd_line[current_idx],
            macd_signal=signal_line[current_idx],
            atr=atr[current_idx],
            bb_upper=bb_upper[current_idx],
            bb_lower=bb_lower[current_idx],
            bb_middle=bb_middle[current_idx],
            volume_ratio=volume_ratio,
            price_momentum=price_momentum,
            support_level=support_resistance["support"],
            resistance_level=support_resistance["resistance"],
            trade_reason=trade_reason,
            risk_reward_ratio=risk_reward,
        )

        self.signals.append(signal_data)

    def _update_first_hour_levels(self, bar: BarData):
        """Update first hour high/low levels"""
        current_date = bar.timestamp.date()

        # Check if we need to create new day levels
        if (
            not self.first_hour_levels
            or self.first_hour_levels[-1].date.date() != current_date
        ):
            # Find first hour bars for this day
            day_start = datetime.combine(current_date, datetime.min.time())
            day_end = day_start + timedelta(days=1)

            day_bars = [b for b in self.bars if day_start <= b.timestamp < day_end]
            first_hour_bars = [b for b in day_bars if b.timestamp.hour == 0]

            if first_hour_bars:
                first_hour_high = max(b.high for b in first_hour_bars)
                first_hour_low = min(b.low for b in first_hour_bars)
                first_hour_open = first_hour_bars[0].open
                first_hour_close = first_hour_bars[-1].close

                levels = FirstHourLevels(
                    date=datetime.combine(current_date, datetime.min.time()),
                    first_hour_high=first_hour_high,
                    first_hour_low=first_hour_low,
                    first_hour_open=first_hour_open,
                    first_hour_close=first_hour_close,
                )

                self.first_hour_levels.append(levels)

    def _get_first_hour_levels(self, timestamp: datetime) -> Optional[FirstHourLevels]:
        """Get first hour levels for a specific timestamp"""
        current_date = timestamp.date()
        for levels in self.first_hour_levels:
            if levels.date == current_date:
                return levels
        return None

    def _analyze_breakouts(
        self, bar: BarData, first_hour_levels: Optional[FirstHourLevels]
    ) -> Dict:
        """Analyze breakout patterns"""
        if not first_hour_levels:
            return {"confirmed": False, "type": None, "strength": 0}

        breakout_high = bar.close > first_hour_levels.first_hour_high
        breakout_low = bar.close < first_hour_levels.first_hour_low

        # Calculate breakout strength
        if breakout_high:
            strength = (
                bar.close - first_hour_levels.first_hour_high
            ) / first_hour_levels.first_hour_high
            return {"confirmed": True, "type": "HIGH", "strength": strength}
        elif breakout_low:
            strength = (
                first_hour_levels.first_hour_low - bar.close
            ) / first_hour_levels.first_hour_low
            return {"confirmed": True, "type": "LOW", "strength": strength}
        else:
            return {"confirmed": False, "type": None, "strength": 0}

    def _analyze_15min_reversal(
        self, bar: BarData, prices: np.ndarray, current_idx: int
    ) -> Dict:
        """Analyze 15-minute reversal patterns"""
        if current_idx < 15:
            return {"detected": False, "type": None, "strength": 0}

        # Get last 15 bars (15 minutes)
        recent_prices = prices[current_idx - 14 : current_idx + 1]
        recent_highs = [b.high for b in self.bars[current_idx - 14 : current_idx + 1]]
        recent_lows = [b.low for b in self.bars[current_idx - 14 : current_idx + 1]]

        # Calculate reversal indicators
        price_change = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
        high_reversal = max(recent_highs) == recent_highs[-3]  # High 3 bars ago
        low_reversal = min(recent_lows) == recent_lows[-3]  # Low 3 bars ago

        # Volume confirmation (if available)
        recent_volumes = [
            b.volume for b in self.bars[current_idx - 14 : current_idx + 1]
        ]
        volume_spike = recent_volumes[-1] > np.mean(recent_volumes) * 1.5

        if high_reversal and price_change < -0.001:  # Bearish reversal
            return {"detected": True, "type": "BEARISH", "strength": abs(price_change)}
        elif low_reversal and price_change > 0.001:  # Bullish reversal
            return {"detected": True, "type": "BULLISH", "strength": abs(price_change)}
        else:
            return {"detected": False, "type": None, "strength": 0}

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

    def _calculate_volume_ratio(self, volumes: np.ndarray, current_idx: int) -> float:
        """Calculate volume ratio compared to recent average"""
        if current_idx < 20:
            return 1.0

        recent_volume = volumes[current_idx]
        avg_volume = np.mean(volumes[current_idx - 20 : current_idx])

        return recent_volume / avg_volume if avg_volume > 0 else 1.0

    def _calculate_price_momentum(self, prices: np.ndarray, current_idx: int) -> float:
        """Calculate price momentum"""
        if current_idx < 5:
            return 0.0

        recent_prices = prices[current_idx - 4 : current_idx + 1]
        return (recent_prices[-1] - recent_prices[0]) / recent_prices[0]

    def _calculate_support_resistance(
        self, prices: np.ndarray, current_idx: int
    ) -> Dict[str, float]:
        """Calculate support and resistance levels"""
        if current_idx < 20:
            return {"support": prices[current_idx], "resistance": prices[current_idx]}

        recent_prices = prices[current_idx - 20 : current_idx + 1]
        support = np.percentile(recent_prices, 10)
        resistance = np.percentile(recent_prices, 90)

        return {"support": support, "resistance": resistance}

    def _calculate_risk_reward_ratio(
        self, bar: BarData, signal: str, atr: float
    ) -> float:
        """Calculate risk/reward ratio"""
        if signal == "HOLD":
            return 0.0

        # Simple risk/reward calculation
        if signal == "BUY":
            risk = atr * 2  # Stop loss at 2 ATR
            reward = atr * 3  # Take profit at 3 ATR
        else:  # SELL
            risk = atr * 2
            reward = atr * 3

        return reward / risk if risk > 0 else 0.0

    def _generate_comprehensive_signal(
        self,
        bar: BarData,
        price: float,
        ema_fast: float,
        ema_slow: float,
        rsi: float,
        macd: float,
        macd_signal: float,
        bb_upper: float,
        bb_lower: float,
        atr: float,
        breakout_analysis: Dict,
        reversal_analysis: Dict,
        first_hour_levels: Optional[FirstHourLevels],
    ) -> Tuple[str, float, str, str]:
        """Generate comprehensive trading signal with detailed analysis"""

        # Technical conditions
        ema_bullish = ema_fast > ema_slow
        rsi_oversold = rsi < 30
        rsi_overbought = rsi > 70
        macd_bullish = macd > macd_signal
        bb_squeeze = (bb_upper - bb_lower) / bb_lower < 0.01
        bb_breakout_up = price > bb_upper
        bb_breakout_down = price < bb_lower

        # Initialize signal components
        signal = "HOLD"
        confidence = 0.5
        signal_type = "TREND_FOLLOWING"
        trade_reason = "No clear signal"

        # Breakout analysis
        if breakout_analysis["confirmed"]:
            if breakout_analysis["type"] == "HIGH":
                signal = "BUY"
                confidence = 0.8 + breakout_analysis["strength"]
                signal_type = "BREAKOUT"
                trade_reason = f"First hour high breakout (strength: {breakout_analysis['strength']:.3f})"
            elif breakout_analysis["type"] == "LOW":
                signal = "SELL"
                confidence = 0.8 + breakout_analysis["strength"]
                signal_type = "BREAKOUT"
                trade_reason = f"First hour low breakout (strength: {breakout_analysis['strength']:.3f})"

        # Reversal analysis
        elif reversal_analysis["detected"]:
            if reversal_analysis["type"] == "BULLISH":
                signal = "BUY"
                confidence = 0.7 + reversal_analysis["strength"]
                signal_type = "REVERSAL"
                trade_reason = f"15-min bullish reversal (strength: {reversal_analysis['strength']:.3f})"
            elif reversal_analysis["type"] == "BEARISH":
                signal = "SELL"
                confidence = 0.7 + reversal_analysis["strength"]
                signal_type = "REVERSAL"
                trade_reason = f"15-min bearish reversal (strength: {reversal_analysis['strength']:.3f})"

        # Technical trend following
        elif ema_bullish and not rsi_overbought and macd_bullish:
            if bb_breakout_up:
                signal = "BUY"
                confidence = 0.75
                signal_type = "TREND_FOLLOWING"
                trade_reason = "EMA bullish + MACD bullish + BB breakout"
            else:
                signal = "BUY"
                confidence = 0.65
                signal_type = "TREND_FOLLOWING"
                trade_reason = "EMA bullish + MACD bullish"

        elif not ema_bullish and not rsi_oversold and not macd_bullish:
            if bb_breakout_down:
                signal = "SELL"
                confidence = 0.75
                signal_type = "TREND_FOLLOWING"
                trade_reason = "EMA bearish + MACD bearish + BB breakdown"
            else:
                signal = "SELL"
                confidence = 0.65
                signal_type = "TREND_FOLLOWING"
                trade_reason = "EMA bearish + MACD bearish"

        # Limit confidence
        confidence = min(confidence, 0.95)

        return signal, confidence, signal_type, trade_reason

    def create_detailed_trade_chart(
        self, save_path: str = "detailed_trade_analysis.png"
    ):
        """Create detailed trade analysis chart with all insights"""
        if not self.bars or not self.signals:
            print("No data to plot!")
            return

        # Create figure with subplots
        fig = plt.figure(figsize=(20, 16), facecolor=self.colors["background"])
        gs = fig.add_gridspec(5, 1, height_ratios=[4, 1, 1, 1, 1], hspace=0.1)

        # Main price chart with first hour levels
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1])  # RSI
        ax3 = fig.add_subplot(gs[2])  # MACD
        ax4 = fig.add_subplot(gs[3])  # Volume
        ax5 = fig.add_subplot(gs[4])  # Trade signals

        # Prepare data
        timestamps = [b.timestamp for b in self.bars]
        opens = [b.open for b in self.bars]
        highs = [b.high for b in self.bars]
        lows = [b.low for b in self.bars]
        closes = [b.close for b in self.bars]
        volumes = [b.volume for b in self.bars]

        # 1. Main candlestick chart with first hour levels
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

        # Plot first hour levels
        for i, bar in enumerate(self.bars):
            first_hour_levels = self._get_first_hour_levels(bar.timestamp)
            if first_hour_levels:
                # Plot first hour high/low as horizontal lines
                ax1.axhline(
                    y=first_hour_levels.first_hour_high,
                    color=self.colors["first_hour_high"],
                    alpha=0.7,
                    linestyle="--",
                    linewidth=1,
                    label="First Hour High" if i == 0 else "",
                )
                ax1.axhline(
                    y=first_hour_levels.first_hour_low,
                    color=self.colors["first_hour_low"],
                    alpha=0.7,
                    linestyle="--",
                    linewidth=1,
                    label="First Hour Low" if i == 0 else "",
                )

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

        # Plot trade signals with different colors for different types
        buy_signals = [s for s in self.signals if s.signal == "BUY"]
        sell_signals = [s for s in self.signals if s.signal == "SELL"]

        if buy_signals:
            buy_indices = [
                timestamps.index(s.timestamp)
                for s in buy_signals
                if s.timestamp in timestamps
            ]
            buy_prices = [s.price for s in buy_signals if s.timestamp in timestamps]
            buy_types = [
                s.signal_type for s in buy_signals if s.timestamp in timestamps
            ]

            # Color code by signal type
            for i, (idx, price, signal_type) in enumerate(
                zip(buy_indices, buy_prices, buy_types)
            ):
                if signal_type == "BREAKOUT":
                    color = self.colors["breakout"]
                    marker = "^"
                elif signal_type == "REVERSAL":
                    color = self.colors["reversal"]
                    marker = "s"
                else:
                    color = self.colors["candle_green"]
                    marker = "o"

                ax1.scatter(
                    idx,
                    price,
                    marker=marker,
                    color=color,
                    s=200,
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
            sell_types = [
                s.signal_type for s in sell_signals if s.timestamp in timestamps
            ]

            for i, (idx, price, signal_type) in enumerate(
                zip(sell_indices, sell_prices, sell_types)
            ):
                if signal_type == "BREAKOUT":
                    color = self.colors["breakout"]
                    marker = "v"
                elif signal_type == "REVERSAL":
                    color = self.colors["reversal"]
                    marker = "s"
                else:
                    color = self.colors["candle_red"]
                    marker = "o"

                ax1.scatter(
                    idx,
                    price,
                    marker=marker,
                    color=color,
                    s=200,
                    zorder=5,
                    edgecolors="white",
                    linewidth=1,
                )

        # Format main chart
        ax1.set_title(
            f"{self.symbol} - Detailed Trade Analysis",
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
        ax4.grid(True, alpha=0.2, color=self.colors["grid"])
        ax4.set_facecolor(self.colors["background"])

        # 5. Trade signals subplot
        if signal_indices:
            signal_strengths = [s.confidence for s in self.signals]
            signal_colors = []
            for s in self.signals:
                if s.signal == "BUY":
                    if s.signal_type == "BREAKOUT":
                        color = self.colors["breakout"]
                    elif s.signal_type == "REVERSAL":
                        color = self.colors["reversal"]
                    else:
                        color = self.colors["candle_green"]
                elif s.signal == "SELL":
                    if s.signal_type == "BREAKOUT":
                        color = self.colors["breakout"]
                    elif s.signal_type == "REVERSAL":
                        color = self.colors["reversal"]
                    else:
                        color = self.colors["candle_red"]
                else:
                    color = self.colors["text"]
                signal_colors.append(color)

            ax5.bar(signal_indices, signal_strengths, color=signal_colors, alpha=0.7)
            ax5.set_ylabel("Signal Strength", color=self.colors["text"])
            ax5.set_xlabel("Time", color=self.colors["text"])
            ax5.grid(True, alpha=0.2, color=self.colors["grid"])
            ax5.set_facecolor(self.colors["background"])

        # Format x-axis
        if len(timestamps) > 0:
            step = max(1, len(timestamps) // 10)
            tick_positions = range(0, len(timestamps), step)
            tick_labels = [timestamps[i].strftime("%H:%M") for i in tick_positions]
            ax5.set_xticks(tick_positions)
            ax5.set_xticklabels(tick_labels, rotation=45, color=self.colors["text"])

        # Color all spines
        for ax in [ax1, ax2, ax3, ax4, ax5]:
            for spine in ax.spines.values():
                spine.set_color(self.colors["grid"])

        plt.tight_layout()
        plt.savefig(
            save_path, dpi=300, bbox_inches="tight", facecolor=self.colors["background"]
        )
        plt.show()

        # Print detailed trade insights
        self._print_detailed_trade_insights()

    def _print_detailed_trade_insights(self):
        """Print comprehensive trade insights"""
        if not self.signals:
            return

        print("\n" + "=" * 80)
        print("DETAILED TRADE ANALYSIS INSIGHTS")
        print("=" * 80)

        # Signal breakdown
        total_signals = len(self.signals)
        buy_signals = [s for s in self.signals if s.signal == "BUY"]
        sell_signals = [s for s in self.signals if s.signal == "SELL"]
        hold_signals = [s for s in self.signals if s.signal == "HOLD"]

        print(f"📊 SIGNAL BREAKDOWN:")
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

        # Signal type breakdown
        breakout_signals = [s for s in self.signals if s.signal_type == "BREAKOUT"]
        reversal_signals = [s for s in self.signals if s.signal_type == "REVERSAL"]
        trend_signals = [s for s in self.signals if s.signal_type == "TREND_FOLLOWING"]

        print(f"\n🎯 SIGNAL TYPE ANALYSIS:")
        print(
            f"   Breakout Signals: {len(breakout_signals)} ({len(breakout_signals)/total_signals*100:.1f}%)"
        )
        print(
            f"   Reversal Signals: {len(reversal_signals)} ({len(reversal_signals)/total_signals*100:.1f}%)"
        )
        print(
            f"   Trend Following: {len(trend_signals)} ({len(trend_signals)/total_signals*100:.1f}%)"
        )

        # First hour level analysis
        breakout_confirmed = [s for s in self.signals if s.breakout_confirmed]
        reversal_detected = [s for s in self.signals if s.reversal_15min]

        print(f"\n📈 PATTERN ANALYSIS:")
        print(
            f"   Breakout Confirmed: {len(breakout_confirmed)} ({len(breakout_confirmed)/total_signals*100:.1f}%)"
        )
        print(
            f"   15-min Reversals: {len(reversal_detected)} ({len(reversal_detected)/total_signals*100:.1f}%)"
        )

        # Performance metrics
        if buy_signals or sell_signals:
            avg_buy_confidence = (
                np.mean([s.confidence for s in buy_signals]) if buy_signals else 0
            )
            avg_sell_confidence = (
                np.mean([s.confidence for s in sell_signals]) if sell_signals else 0
            )
            avg_risk_reward = np.mean(
                [s.risk_reward_ratio for s in buy_signals + sell_signals]
            )

            print(f"\n📊 PERFORMANCE METRICS:")
            print(f"   Average Buy Confidence: {avg_buy_confidence:.3f}")
            print(f"   Average Sell Confidence: {avg_sell_confidence:.3f}")
            print(f"   Average Risk/Reward Ratio: {avg_risk_reward:.2f}")

        # Detailed trade examples
        if buy_signals or sell_signals:
            print(f"\n🔍 DETAILED TRADE EXAMPLES:")
            for i, signal in enumerate(buy_signals[:3] + sell_signals[:3]):
                print(
                    f"   Trade {i+1}: {signal.signal} at {signal.timestamp.strftime('%H:%M')}"
                )
                print(f"     Type: {signal.signal_type}")
                print(f"     Confidence: {signal.confidence:.3f}")
                print(f"     Reason: {signal.trade_reason}")
                print(f"     RSI: {signal.rsi:.1f}")
                print(f"     Risk/Reward: {signal.risk_reward_ratio:.2f}")
                print()

        print("=" * 80)


def generate_sample_data(symbol: str = "EURUSD", days: int = 7) -> List[BarData]:
    """Generate sample forex data with realistic patterns"""
    bars = []
    start_date = datetime(2024, 1, 1)
    base_price = 1.1000  # EURUSD starting price

    for i in range(days * 24 * 60):  # Minute data
        timestamp = start_date + timedelta(minutes=i)

        # Simulate realistic price movement with breakouts and reversals
        trend = np.sin(i / (24 * 60 * 7)) * 0.001  # Weekly trend
        noise = np.random.normal(0, 0.0002)  # Random noise
        volatility = 0.0001 + 0.0001 * np.sin(i / (24 * 60))  # Daily volatility cycle

        # Add breakout patterns at specific times
        if i % (24 * 60) == 60:  # 1 hour after market open
            trend += np.random.choice([-0.003, 0.003])  # Breakout

        # Add reversal patterns
        if i % (24 * 60) == 120:  # 2 hours after market open
            trend += np.random.choice([-0.002, 0.002])  # Reversal

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
            volume=np.random.randint(1000, 10000),
        )

        bars.append(bar)

    return bars


def main():
    """Main function to demonstrate the detailed trade analyzer"""
    print("🚀 Starting Detailed Trade Analyzer")
    print("=" * 60)

    # Initialize analyzer
    analyzer = DetailedTradeAnalyzer("EURUSD")

    # Generate sample data
    print("Generating sample data with breakouts and reversals...")
    bars = generate_sample_data("EURUSD", days=2)

    # Process bars with progress bar
    print("Processing bars and generating detailed signals...")
    for bar in tqdm(bars, desc="Processing bars", ncols=80):
        analyzer.add_bar(bar)

    # Create detailed trade chart
    print("\nCreating detailed trade analysis chart...")
    analyzer.create_detailed_trade_chart()

    print("\n✅ Detailed trade analysis complete!")
    print("📊 Check 'detailed_trade_analysis.png' for comprehensive analysis")


if __name__ == "__main__":
    main()
