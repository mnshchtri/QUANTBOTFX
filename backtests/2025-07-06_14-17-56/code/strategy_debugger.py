"""
Comprehensive Strategy Debugger with Charting
Local testing framework for forex strategy development
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import json
from typing import Dict, List, Tuple, Optional
import seaborn as sns
from dataclasses import dataclass
import warnings

warnings.filterwarnings("ignore")

# Set style for better charts
plt.style.use("seaborn-v0_8")
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
    indicators: Dict[str, float]
    features: Dict[str, float]
    ai_prediction: Optional[str] = None
    ai_confidence: Optional[float] = None


class TechnicalIndicators:
    """Technical indicators calculator"""

    @staticmethod
    def ema(prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate Exponential Moving Average"""
        alpha = 2 / (period + 1)
        ema_values = np.zeros_like(prices)
        ema_values[0] = prices[0]

        for i in range(1, len(prices)):
            ema_values[i] = alpha * prices[i] + (1 - alpha) * ema_values[i - 1]

        return ema_values

    @staticmethod
    def rsi(prices: np.ndarray, period: int = 14) -> np.ndarray:
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

        rs = avg_gains / (avg_losses + 1e-10)  # Avoid division by zero
        rsi_values = 100 - (100 / (1 + rs))

        return rsi_values

    @staticmethod
    def macd(
        prices: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calculate MACD"""
        ema_fast = TechnicalIndicators.ema(prices, fast)
        ema_slow = TechnicalIndicators.ema(prices, slow)
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicators.ema(macd_line, signal)
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram

    @staticmethod
    def atr(
        high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14
    ) -> np.ndarray:
        """Calculate Average True Range"""
        tr1 = high - low
        tr2 = np.abs(high - np.roll(close, 1))
        tr3 = np.abs(low - np.roll(close, 1))

        true_range = np.maximum(tr1, np.maximum(tr2, tr3))
        atr_values = TechnicalIndicators.ema(true_range, period)

        return atr_values


class StrategyDebugger:
    """Comprehensive strategy debugging and visualization framework"""

    def __init__(self, symbol: str = "EURUSD"):
        self.symbol = symbol
        self.bars: List[BarData] = []
        self.signals: List[SignalData] = []
        self.trades: List[Dict] = []

        # Strategy parameters
        self.ema_fast_period = 12
        self.ema_slow_period = 26
        self.rsi_period = 14
        self.confidence_threshold = 0.4
        self.max_position_size = 0.02

        # Performance tracking
        self.portfolio_value = 10000
        self.current_position = 0
        self.total_pnl = 0

        # Logging
        self.debug_log = []

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

        ema_fast = TechnicalIndicators.ema(prices, self.ema_fast_period)
        ema_slow = TechnicalIndicators.ema(prices, self.ema_slow_period)
        rsi = TechnicalIndicators.rsi(prices, self.rsi_period)
        macd_line, signal_line, histogram = TechnicalIndicators.macd(prices)
        atr = TechnicalIndicators.atr(highs, lows, prices)

        # Current values
        current_idx = len(prices) - 1
        indicators = {
            "ema_fast": ema_fast[current_idx],
            "ema_slow": ema_slow[current_idx],
            "rsi": rsi[current_idx],
            "macd": macd_line[current_idx],
            "macd_signal": signal_line[current_idx],
            "macd_histogram": histogram[current_idx],
            "atr": atr[current_idx],
        }

        # Extract features for AI
        features = self._extract_features(prices, indicators)

        # Generate signals
        technical_signal = self._generate_technical_signal(indicators)
        ai_signal, ai_confidence = self._generate_ai_signal(features)
        final_signal, confidence = self._combine_signals(
            technical_signal, ai_signal, ai_confidence
        )

        # Create signal data
        signal_data = SignalData(
            timestamp=bar.timestamp,
            signal=final_signal,
            confidence=confidence,
            price=bar.close,
            indicators=indicators,
            features=features,
            ai_prediction=ai_signal,
            ai_confidence=ai_confidence,
        )

        self.signals.append(signal_data)

        # Execute trades
        self._execute_trades(signal_data)

        # Log detailed information
        self._log_step(bar, signal_data)

    def _extract_features(
        self, prices: np.ndarray, indicators: Dict[str, float]
    ) -> Dict[str, float]:
        """Extract features for AI model"""
        features = {}

        # Price-based features
        if len(prices) > 1:
            returns = (prices[-1] - prices[-2]) / prices[-2]
            features["returns"] = returns

            # Volatility
            if len(prices) >= 20:
                volatility = np.std(prices[-20:]) / np.mean(prices[-20:])
                features["volatility"] = volatility
            else:
                features["volatility"] = 0
        else:
            features["returns"] = 0
            features["volatility"] = 0

        # Technical features
        features["ema_ratio"] = indicators["ema_fast"] / indicators["ema_slow"]
        features["ema_cross"] = (
            1.0 if indicators["ema_fast"] > indicators["ema_slow"] else -1.0
        )
        features["rsi"] = indicators["rsi"] / 100  # Normalize to 0-1
        features["macd"] = indicators["macd"]
        features["macd_signal"] = indicators["macd_signal"]
        features["atr"] = indicators["atr"]

        # Breakout features
        if len(prices) >= 20:
            resistance = np.max(prices[-20:])
            support = np.min(prices[-20:])
            current_price = prices[-1]

            features["resistance_distance"] = (
                resistance - current_price
            ) / current_price
            features["support_distance"] = (current_price - support) / current_price
            features["breakout_strength"] = (
                current_price - (resistance + support) / 2
            ) / ((resistance - support) / 2)
        else:
            features["resistance_distance"] = 0
            features["support_distance"] = 0
            features["breakout_strength"] = 0

        return features

    def _generate_technical_signal(self, indicators: Dict[str, float]) -> str:
        """Generate signal based on technical indicators"""
        ema_fast = indicators["ema_fast"]
        ema_slow = indicators["ema_slow"]
        rsi = indicators["rsi"]
        macd = indicators["macd"]
        macd_signal = indicators["macd_signal"]

        # Technical rules
        ema_bullish = ema_fast > ema_slow
        rsi_oversold = rsi < 30
        rsi_overbought = rsi > 70
        macd_bullish = macd > macd_signal

        if ema_bullish and not rsi_overbought and macd_bullish:
            return "BUY"
        elif not ema_bullish and not rsi_oversold and not macd_bullish:
            return "SELL"
        else:
            return "HOLD"

    def _generate_ai_signal(self, features: Dict[str, float]) -> Tuple[str, float]:
        """Simulate AI signal generation"""
        # Simple rule-based AI for demonstration
        # In real implementation, this would use your trained ML model

        score = 0.0

        # Feature scoring
        if features["ema_ratio"] > 1.001:  # Strong uptrend
            score += 0.3
        elif features["ema_ratio"] < 0.999:  # Strong downtrend
            score -= 0.3

        if features["rsi"] < 0.3:  # Oversold
            score += 0.2
        elif features["rsi"] > 0.7:  # Overbought
            score -= 0.2

        if features["breakout_strength"] > 0.1:  # Bullish breakout
            score += 0.2
        elif features["breakout_strength"] < -0.1:  # Bearish breakout
            score -= 0.2

        if features["volatility"] > 0.02:  # High volatility
            score += 0.1

        # Convert score to signal
        if score > 0.3:
            return "BUY", min(abs(score), 0.9)
        elif score < -0.3:
            return "SELL", min(abs(score), 0.9)
        else:
            return "HOLD", 0.5

    def _combine_signals(
        self, technical_signal: str, ai_signal: str, ai_confidence: float
    ) -> Tuple[str, float]:
        """Combine technical and AI signals"""
        if ai_confidence > 0.8:
            # High confidence AI overrides technical
            return ai_signal, ai_confidence
        elif ai_confidence > self.confidence_threshold:
            # Medium confidence - use weighted combination
            if technical_signal == ai_signal:
                return ai_signal, ai_confidence
            else:
                return "HOLD", 0.5  # Conflicting signals
        else:
            # Low confidence - rely on technical
            return technical_signal, 0.6

    def _execute_trades(self, signal_data: SignalData):
        """Execute trades based on signals"""
        if signal_data.signal == "HOLD":
            return

        # Calculate position size
        position_size = self.max_position_size * signal_data.confidence

        if signal_data.signal == "BUY" and self.current_position <= 0:
            # Buy signal
            trade_value = self.portfolio_value * position_size
            self.current_position = trade_value / signal_data.price
            self.trades.append(
                {
                    "timestamp": signal_data.timestamp,
                    "action": "BUY",
                    "price": signal_data.price,
                    "size": self.current_position,
                    "value": trade_value,
                    "confidence": signal_data.confidence,
                }
            )

        elif signal_data.signal == "SELL" and self.current_position >= 0:
            # Sell signal
            trade_value = self.portfolio_value * position_size
            self.current_position = -trade_value / signal_data.price
            self.trades.append(
                {
                    "timestamp": signal_data.timestamp,
                    "action": "SELL",
                    "price": signal_data.price,
                    "size": self.current_position,
                    "value": trade_value,
                    "confidence": signal_data.confidence,
                }
            )

    def _log_step(self, bar: BarData, signal_data: SignalData):
        """Log detailed information for debugging"""
        log_entry = {
            "timestamp": str(bar.timestamp),
            "price": bar.close,
            "signal": signal_data.signal,
            "confidence": signal_data.confidence,
            "indicators": signal_data.indicators,
            "features": signal_data.features,
            "ai_prediction": signal_data.ai_prediction,
            "ai_confidence": signal_data.ai_confidence,
            "position": self.current_position,
            "portfolio_value": self.portfolio_value,
        }

        self.debug_log.append(log_entry)

        # Print to console for real-time monitoring
        print(
            f"[{bar.timestamp}] {signal_data.signal} @ {bar.close:.5f} "
            f"(Conf: {signal_data.confidence:.3f}, "
            f"RSI: {signal_data.indicators['rsi']:.1f}, "
            f"EMA Ratio: {signal_data.indicators['ema_fast']/signal_data.indicators['ema_slow']:.5f})"
        )

    def create_comprehensive_charts(self, save_path: str = "strategy_analysis.html"):
        """Create comprehensive strategy analysis charts"""
        if not self.bars or not self.signals:
            print("No data to plot!")
            return

        # Prepare data
        df_bars = pd.DataFrame(
            [
                {
                    "timestamp": b.timestamp,
                    "open": b.open,
                    "high": b.high,
                    "low": b.low,
                    "close": b.close,
                    "volume": b.volume,
                }
                for b in self.bars
            ]
        )

        df_signals = pd.DataFrame(
            [
                {
                    "timestamp": s.timestamp,
                    "signal": s.signal,
                    "confidence": s.confidence,
                    "price": s.price,
                    "rsi": s.indicators["rsi"],
                    "ema_fast": s.indicators["ema_fast"],
                    "ema_slow": s.indicators["ema_slow"],
                    "macd": s.indicators["macd"],
                    "macd_signal": s.indicators["macd_signal"],
                    "atr": s.indicators["atr"],
                    "ai_prediction": s.ai_prediction,
                    "ai_confidence": s.ai_confidence,
                }
                for s in self.signals
            ]
        )

        # Create comprehensive chart
        fig, axes = plt.subplots(4, 1, figsize=(15, 12), sharex=True)
        fig.suptitle(
            f"Strategy Analysis - {self.symbol}", fontsize=16, fontweight="bold"
        )

        # 1. Price and EMAs
        ax1 = axes[0]
        ax1.plot(
            df_bars["timestamp"],
            df_bars["close"],
            label="Price",
            linewidth=1,
            alpha=0.8,
        )
        ax1.plot(
            df_signals["timestamp"],
            df_signals["ema_fast"],
            label="EMA Fast",
            linewidth=1,
        )
        ax1.plot(
            df_signals["timestamp"],
            df_signals["ema_slow"],
            label="EMA Slow",
            linewidth=1,
        )

        # Plot buy/sell signals
        buy_signals = df_signals[df_signals["signal"] == "BUY"]
        sell_signals = df_signals[df_signals["signal"] == "SELL"]

        ax1.scatter(
            buy_signals["timestamp"],
            buy_signals["price"],
            marker="^",
            color="green",
            s=100,
            label="Buy Signal",
            zorder=5,
        )
        ax1.scatter(
            sell_signals["timestamp"],
            sell_signals["price"],
            marker="v",
            color="red",
            s=100,
            label="Sell Signal",
            zorder=5,
        )

        ax1.set_ylabel("Price")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 2. RSI
        ax2 = axes[1]
        ax2.plot(
            df_signals["timestamp"], df_signals["rsi"], label="RSI", color="purple"
        )
        ax2.axhline(y=70, color="r", linestyle="--", alpha=0.5, label="Overbought")
        ax2.axhline(y=30, color="g", linestyle="--", alpha=0.5, label="Oversold")
        ax2.set_ylabel("RSI")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # 3. MACD
        ax3 = axes[2]
        ax3.plot(
            df_signals["timestamp"], df_signals["macd"], label="MACD", color="blue"
        )
        ax3.plot(
            df_signals["timestamp"],
            df_signals["macd_signal"],
            label="Signal",
            color="orange",
        )
        ax3.bar(
            df_signals["timestamp"],
            df_signals["macd"] - df_signals["macd_signal"],
            alpha=0.3,
            label="Histogram",
        )
        ax3.set_ylabel("MACD")
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # 4. Confidence and ATR
        ax4 = axes[3]
        ax4_twin = ax4.twinx()

        ax4.plot(
            df_signals["timestamp"],
            df_signals["confidence"],
            label="Signal Confidence",
            color="green",
            linewidth=2,
        )
        ax4_twin.plot(
            df_signals["timestamp"],
            df_signals["atr"],
            label="ATR",
            color="red",
            alpha=0.7,
        )

        ax4.set_ylabel("Confidence")
        ax4_twin.set_ylabel("ATR")
        ax4.set_xlabel("Time")

        # Combine legends
        lines1, labels1 = ax4.get_legend_handles_labels()
        lines2, labels2 = ax4_twin.get_legend_handles_labels()
        ax4.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
        ax4.grid(True, alpha=0.3)

        # Format x-axis
        ax4.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax4.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)

        plt.tight_layout()
        plt.savefig("strategy_analysis.png", dpi=300, bbox_inches="tight")
        plt.show()

        # Create detailed statistics
        self._print_statistics()

    def _print_statistics(self):
        """Print detailed strategy statistics"""
        if not self.signals:
            return

        print("\n" + "=" * 60)
        print("STRATEGY STATISTICS")
        print("=" * 60)

        # Signal statistics
        total_signals = len(self.signals)
        buy_signals = len([s for s in self.signals if s.signal == "BUY"])
        sell_signals = len([s for s in self.signals if s.signal == "SELL"])
        hold_signals = len([s for s in self.signals if s.signal == "HOLD"])

        print(f"Total Signals: {total_signals}")
        print(f"Buy Signals: {buy_signals} ({buy_signals/total_signals*100:.1f}%)")
        print(f"Sell Signals: {sell_signals} ({sell_signals/total_signals*100:.1f}%)")
        print(f"Hold Signals: {hold_signals} ({hold_signals/total_signals*100:.1f}%)")

        # Trade statistics
        if self.trades:
            print(f"\nTotal Trades: {len(self.trades)}")
            buy_trades = [t for t in self.trades if t["action"] == "BUY"]
            sell_trades = [t for t in self.trades if t["action"] == "SELL"]
            print(f"Buy Trades: {len(buy_trades)}")
            print(f"Sell Trades: {len(sell_trades)}")

            avg_confidence = np.mean([t["confidence"] for t in self.trades])
            print(f"Average Trade Confidence: {avg_confidence:.3f}")

        # Indicator statistics
        rsi_values = [s.indicators["rsi"] for s in self.signals]
        ema_ratios = [
            s.indicators["ema_fast"] / s.indicators["ema_slow"] for s in self.signals
        ]

        print(f"\nIndicator Statistics:")
        print(f"Average RSI: {np.mean(rsi_values):.1f}")
        print(f"RSI Range: {np.min(rsi_values):.1f} - {np.max(rsi_values):.1f}")
        print(f"Average EMA Ratio: {np.mean(ema_ratios):.5f}")
        print(f"EMA Ratio Range: {np.min(ema_ratios):.5f} - {np.max(ema_ratios):.5f}")

        print("=" * 60)

    def export_debug_log(self, filename: str = "debug_log.json"):
        """Export detailed debug log to JSON file"""
        with open(filename, "w") as f:
            json.dump(self.debug_log, f, indent=2, default=str)
        print(f"Debug log exported to {filename}")


def generate_sample_data(symbol: str = "EURUSD", days: int = 30) -> List[BarData]:
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
            volume=np.random.randint(1000, 10000),
        )

        bars.append(bar)

    return bars


def main():
    """Main function to demonstrate the strategy debugger"""
    print("🚀 Starting Strategy Debugger")
    print("=" * 50)

    # Initialize debugger
    debugger = StrategyDebugger("EURUSD")

    # Generate sample data
    print("Generating sample data...")
    bars = generate_sample_data("EURUSD", days=7)  # 7 days of minute data

    # Process bars
    print("Processing bars and generating signals...")
    for i, bar in enumerate(bars):
        debugger.add_bar(bar)

        # Print progress every 100 bars
        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1}/{len(bars)} bars...")

    # Create comprehensive charts
    print("\nCreating comprehensive charts...")
    debugger.create_comprehensive_charts()

    # Export debug log
    debugger.export_debug_log()

    print("\n✅ Strategy analysis complete!")
    print("📊 Check 'strategy_analysis.png' for charts")
    print("📝 Check 'debug_log.json' for detailed logs")


if __name__ == "__main__":
    main()
