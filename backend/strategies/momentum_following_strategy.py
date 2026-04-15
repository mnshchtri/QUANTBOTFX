#!/usr/bin/env python3
"""
Range of the Day Strategy - Pure Algorithm Version
This strategy should only process data provided to it, not fetch data.
"""

import pandas as pd
import numpy as np
import pytz
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Import base strategy
from .base_strategy import BaseStrategy


class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class TradeSignal:
    timestamp: datetime
    signal_type: SignalType
    price: float
    strength: float
    reason: str
    index: int


@dataclass
class StrategyResult:
    signals: List[TradeSignal]
    total_signals: int
    buy_signals: int
    sell_signals: int
    success_rate: float
    analysis_summary: str


class RangeOfTheDayStrategy(BaseStrategy):
    """
    Range of the Day Strategy - Pure Algorithm

    This strategy processes provided data and generates signals based on:
    - Stochastic momentum analysis
    - Multi-timeframe alignment
    - Range breakout detection
    """

    def __init__(self):
        super().__init__(
            "Range of the Day Strategy",
            "Momentum following strategy with stochastic analysis",
        )

    def get_required_indicators(self) -> List[str]:
        """Get list of required indicators for this strategy"""
        return ["stochastic", "rsi", "sma"]

    def generate_signals(self, data: pd.DataFrame) -> List[Dict]:
        """
        Generate signals for replay engine compatibility

        Args:
            data: DataFrame with OHLCV data

        Returns:
            List of signal dictionaries compatible with replay engine
        """
        try:
            # Use the existing analyze method
            result = self.analyze(data)

            # Convert TradeSignal objects to dictionaries for replay engine
            signals = []
            for signal in result.signals:
                signals.append(
                    {
                        "type": signal.signal_type.value,
                        "timestamp": signal.timestamp,
                        "price": signal.price,
                        "strength": signal.strength,
                        "reason": signal.reason,
                        "index": signal.index,
                        "confidence": signal.strength * 100,  # Convert to percentage
                    }
                )

            return signals

        except Exception as e:
            print(f"Error generating signals: {e}")
            return []

    def analyze(self, data: pd.DataFrame) -> StrategyResult:
        """
        Analyze provided data and generate signals

        Args:
            data: DataFrame with OHLCV data

        Returns:
            StrategyResult with signals and analysis
        """
        if data is None or len(data) == 0:
            return StrategyResult(
                signals=[],
                total_signals=0,
                buy_signals=0,
                sell_signals=0,
                success_rate=0.0,
                analysis_summary="No data provided",
            )

        # Calculate indicators
        stoch_k, stoch_d = self.calculate_stochastic(
            data["high"], data["low"], data["close"]
        )
        rsi = self.calculate_rsi(data["close"])

        # Generate signals
        signals = self._generate_signals(data, stoch_k, stoch_d, rsi)

        # Calculate statistics
        buy_signals = len([s for s in signals if s.signal_type == SignalType.BUY])
        sell_signals = len([s for s in signals if s.signal_type == SignalType.SELL])
        total_signals = len(signals)

        success_rate = 0.0  # Would need historical validation
        analysis_summary = f"Generated {total_signals} signals ({buy_signals} buy, {sell_signals} sell)"

        return StrategyResult(
            signals=signals,
            total_signals=total_signals,
            buy_signals=buy_signals,
            sell_signals=sell_signals,
            success_rate=success_rate,
            analysis_summary=analysis_summary,
        )

    def _generate_signals(
        self, data: pd.DataFrame, stoch_k: pd.Series, stoch_d: pd.Series, rsi: pd.Series
    ) -> List[TradeSignal]:
        """
        Generate trading signals based on stochastic analysis

        Args:
            data: OHLCV data
            stoch_k: Stochastic %K values
            stoch_d: Stochastic %D values
            rsi: RSI values

        Returns:
            List of TradeSignal objects
        """
        signals = []

        for i in range(1, len(data)):
            if i < 20:  # Wait for indicators to stabilize
                continue

            current_price = data["close"].iloc[i]
            current_time = data.index[i]

            # Get current indicator values
            k_curr = stoch_k.iloc[i]
            d_curr = stoch_d.iloc[i]
            k_prev = stoch_k.iloc[i - 1]
            d_prev = stoch_d.iloc[i - 1]
            rsi_curr = rsi.iloc[i]

            # Detect crossovers
            bullish_crossover = k_prev <= d_prev and k_curr > d_curr
            bearish_crossover = k_prev >= d_prev and k_curr < d_curr

            # Generate signals
            if bullish_crossover and k_curr < 30 and rsi_curr < 40:
                signal = TradeSignal(
                    timestamp=current_time,
                    signal_type=SignalType.BUY,
                    price=current_price,
                    strength=0.9,
                    reason="Stochastic bullish crossover + oversold conditions",
                    index=i,
                )
                signals.append(signal)

            elif bearish_crossover and k_curr > 70 and rsi_curr > 60:
                signal = TradeSignal(
                    timestamp=current_time,
                    signal_type=SignalType.SELL,
                    price=current_price,
                    strength=0.9,
                    reason="Stochastic bearish crossover + overbought conditions",
                    index=i,
                )
                signals.append(signal)

        return signals

    def calculate_stochastic(self, high, low, close, period=14, k_period=3, d_period=3):
        """
        Calculate stochastic oscillator

        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: Lookback period
            k_period: %K smoothing period
            d_period: %D smoothing period

        Returns:
            Tuple of (%K, %D) series
        """
        # Calculate %K
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()

        k_raw = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        k_smooth = k_raw.rolling(window=k_period).mean()

        # Calculate %D
        d_smooth = k_smooth.rolling(window=d_period).mean()

        return k_smooth, d_smooth

    def calculate_rsi(self, prices, period=14):
        """
        Calculate RSI indicator

        Args:
            prices: Price series
            period: RSI period

        Returns:
            RSI series
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def process_historical_data(
        self, df: pd.DataFrame, instrument: str, granularity: str = "M15"
    ) -> pd.DataFrame:
        """
        Process provided historical data (pure algorithm)

        Args:
            df: Input DataFrame
            instrument: Instrument name
            granularity: Timeframe

        Returns:
            Processed DataFrame
        """
        try:
            if df is not None and len(df) > 0:
                df_clean = self._remove_non_trading_gaps(df, instrument, granularity)
                self.validate_historical_data(df_clean, instrument, granularity)
                return df_clean
            return df
        except Exception as e:
            print(f"Historical data processing error: {e}")
            return None

    def validate_historical_data(self, df, instrument, granularity):
        """Validate historical data quality"""

        if df is None or len(df) == 0:
            print(f"❌ No data received for {instrument} {granularity}")
            return False

        # Check for remaining data gaps (should be minimal after cleaning)
        expected_interval = self.get_expected_interval(granularity)
        actual_intervals = df.index.to_series().diff()
        gaps = actual_intervals[actual_intervals > expected_interval * 2]

        if len(gaps) > 0:
            print(
                f"⚠️  Found {len(gaps)} remaining data gaps in {instrument} {granularity}"
            )
            print(f"   Largest gap: {gaps.max()}")

        print(
            f"✅ {instrument} {granularity}: {len(df)} candles from {df.index[0]} to {df.index[-1]}"
        )
        return True

    def _remove_non_trading_gaps(self, df, instrument, granularity):
        """Remove data gaps for non-trading days (weekends and holidays)"""
        if df is None or len(df) == 0:
            return df

        # Convert to EST for proper trading day detection
        est = pytz.timezone("US/Eastern")
        df_est = df.copy()
        df_est["est_time"] = df_est.index.tz_convert(est)

        # Remove weekend data (Saturday = 5, Sunday = 6)
        weekend_mask = df_est["est_time"].dt.weekday >= 5
        df_clean = df_est[~weekend_mask].copy()

        # Remove holiday data (major forex market holidays)
        holidays_2025 = [
            "2025-01-01",  # New Year's Day
            "2025-01-20",  # Martin Luther King Jr. Day
            "2025-02-17",  # Presidents' Day
            "2025-04-18",  # Good Friday
            "2025-05-26",  # Memorial Day
            "2025-07-04",  # Independence Day
            "2025-09-01",  # Labor Day
            "2025-11-27",  # Thanksgiving Day
            "2025-12-25",  # Christmas Day
        ]

        # Convert holiday dates to datetime
        holiday_dates = [
            datetime.strptime(date, "%Y-%m-%d").date() for date in holidays_2025
        ]

        # Remove holiday data
        holiday_mask = df_clean["est_time"].dt.date.isin(holiday_dates)
        df_clean = df_clean[~holiday_mask].copy()

        # Remove the temporary est_time column and reset index
        df_clean = df_clean.drop("est_time", axis=1)

        # Sort by timestamp to ensure proper order
        df_clean = df_clean.sort_index()

        # Log the cleaning results
        original_count = len(df)
        cleaned_count = len(df_clean)
        removed_count = original_count - cleaned_count

        if removed_count > 0:
            print(
                f"🧹 Removed {removed_count} non-trading candles from {instrument} {granularity}"
            )
            print(f"   Original: {original_count} candles")
            print(f"   Cleaned: {cleaned_count} candles")

        return df_clean

    def get_expected_interval(self, granularity):
        """Get expected time interval for granularity"""
        intervals = {
            "M1": timedelta(minutes=1),
            "M5": timedelta(minutes=5),
            "M15": timedelta(minutes=15),
            "M30": timedelta(minutes=30),
            "H1": timedelta(hours=1),
            "H4": timedelta(hours=4),
            "D1": timedelta(days=1),
        }
        return intervals.get(granularity, timedelta(minutes=15))

    def get_candles_df(
        self, instrument, count=5000, granularity="M15", from_time=None, to_time=None
    ):
        """Get candle data - PURE ALGORITHM VERSION (no data fetching)"""
        # This method should only be used when data is provided externally
        # For backtesting, data should be passed in directly
        raise NotImplementedError(
            "Strategy should not fetch data. Use process_historical_data() with provided data instead."
        )

    def get_extended_historical_data(self, instrument, granularity="M15", days_back=30):
        """Get extended historical data - PURE ALGORITHM VERSION (no data fetching)"""
        # This method should only be used when data is provided externally
        # For backtesting, data should be passed in directly
        raise NotImplementedError(
            "Strategy should not fetch data. Use process_historical_data() with provided data instead."
        )
