#!/usr/bin/env python3
"""
TrimurtiFX - Technical Indicators Library
========================================

A comprehensive library of technical indicators for financial analysis.
This module provides various technical indicators commonly used in trading.

Usage:
    from indicators import IndicatorLibrary
    df = IndicatorLibrary.calculate_sma(df, period=20)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass
import warnings

# Try to import advanced technical analysis libraries in order of preference
try:
    import pandas_ta as pta

    PANDAS_TA_AVAILABLE = True
    print("✅ Using 'pandas-ta' library (MOST ADVANCED) - 130+ indicators")
except ImportError:
    PANDAS_TA_AVAILABLE = False
    print("⚠️  'pandas-ta' not available. Install: pip install pandas-ta")

try:
    import ta

    TA_AVAILABLE = True
    if not PANDAS_TA_AVAILABLE:
        print("✅ Using 'ta' library (ADVANCED) - 130+ indicators")
except ImportError:
    TA_AVAILABLE = False
    if not PANDAS_TA_AVAILABLE:
        print("⚠️  'ta' library not available. Install: pip install ta")

try:
    import finta

    FINTA_AVAILABLE = True
    if not PANDAS_TA_AVAILABLE and not TA_AVAILABLE:
        print("✅ Using 'finta' library (ADVANCED) - 100+ indicators")
except ImportError:
    FINTA_AVAILABLE = False
    if not PANDAS_TA_AVAILABLE and not TA_AVAILABLE:
        print("⚠️  'finta' library not available. Install: pip install finta")

# Legacy TA-Lib support (lowest priority)
try:
    import talib

    TALIB_AVAILABLE = True
    if not any([PANDAS_TA_AVAILABLE, TA_AVAILABLE, FINTA_AVAILABLE]):
        print("✅ Using TA-Lib (LEGACY) - Limited indicators")
except ImportError:
    TALIB_AVAILABLE = False
    if not any([PANDAS_TA_AVAILABLE, TA_AVAILABLE, FINTA_AVAILABLE]):
        print("⚠️  No technical analysis libraries available.")
        print("   Install with: pip install pandas-ta ta finta")

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")


class IndicatorType(Enum):
    """Enumeration of available indicator types"""

    SMA = "sma"
    EMA = "ema"
    RSI = "rsi"
    STOCHASTIC = "stochastic"
    BOLLINGER_BANDS = "bollinger_bands"
    MACD = "macd"
    ATR = "atr"
    ADX = "adx"
    CCI = "cci"
    WILLIAMS_R = "williams_r"
    MOMENTUM = "momentum"
    SESSION_LEVELS = "session_levels"
    SESSION_LEVELS_FADE = "session_levels_fade"
    ROC = "roc"
    OBV = "obv"
    VWAP = "vwap"
    PARABOLIC_SAR = "parabolic_sar"
    ICHIMOKU = "ichimoku"
    FIBONACCI = "fibonacci"
    PIVOT_POINTS = "pivot_points"
    SUPPLY_DEMAND = "supply_demand"
    RANGE_OF_DAY = "range_of_day"


@dataclass
class IndicatorConfig:
    """Configuration class for indicators"""

    type: IndicatorType
    parameters: Dict[str, Any]
    color: str = "#667eea"
    width: int = 2
    visible: bool = True
    name: str = ""


class IndicatorLibrary:
    """
    Comprehensive library of technical indicators

    WARNING: Do NOT use these methods to mutate or add indicator columns to the main DataFrame used for price data storage.
    Only use these methods to generate indicator values for plotting or temporary use.
    """

    # Color schemes for different indicator types
    COLORS = {
        "trend": ["#667eea", "#4facfe", "#00f2fe", "#43e97b", "#38f9d7"],
        "momentum": ["#f093fb", "#f5576c", "#ff6b6b", "#ffd700", "#ff8a80"],
        "volatility": ["#ff6b6b", "#4facfe", "#43e97b", "#f093fb", "#ffd700"],
        "volume": ["#667eea", "#4facfe", "#43e97b", "#f093fb", "#ff6b6b"],
        "support_resistance": ["#ffd700", "#ff6b6b", "#4facfe", "#43e97b", "#f093fb"],
    }

    @staticmethod
    def get_indicator_info() -> Dict[str, Dict]:
        """Get information about all available indicators"""
        return {
            # Basic Indicators
            "SMA": {
                "description": "Simple Moving Average - Average of closing prices over a period",
                "parameters": {"period": "int (default: 20)"},
                "type": "trend",
                "category": "Moving Averages",
            },
            "EMA": {
                "description": "Exponential Moving Average - Weighted average giving more importance to recent prices",
                "parameters": {"period": "int (default: 20)"},
                "type": "trend",
                "category": "Moving Averages",
            },
            "RSI": {
                "description": "Relative Strength Index - Momentum oscillator measuring speed and change of price movements",
                "parameters": {"period": "int (default: 14)"},
                "type": "momentum",
                "category": "Oscillators",
            },
            "Stochastic": {
                "description": "Stochastic Oscillator - Momentum indicator comparing closing price to price range",
                "parameters": {
                    "k_period": "int (default: 14)",
                    "d_period": "int (default: 3)",
                },
                "type": "momentum",
                "category": "Oscillators",
            },
            "Bollinger Bands": {
                "description": "Volatility indicator with upper and lower bands around moving average",
                "parameters": {
                    "period": "int (default: 20)",
                    "std_dev": "float (default: 2.0)",
                },
                "type": "volatility",
                "category": "Volatility",
            },
            "MACD": {
                "description": "Moving Average Convergence Divergence - Trend-following momentum indicator",
                "parameters": {
                    "fast": "int (default: 12)",
                    "slow": "int (default: 26)",
                    "signal": "int (default: 9)",
                },
                "type": "trend",
                "category": "Trend",
            },
            # Advanced Indicators (Modern Libraries Only)
            "ATR": {
                "description": "Average True Range - Volatility indicator measuring market volatility",
                "parameters": {"period": "int (default: 14)"},
                "type": "volatility",
                "category": "Volatility",
            },
            "NATR": {
                "description": "Normalized Average True Range - ATR expressed as percentage",
                "parameters": {"period": "int (default: 14)"},
                "type": "volatility",
                "category": "Volatility",
            },
            "ADX": {
                "description": "Average Directional Index - Trend strength indicator",
                "parameters": {"period": "int (default: 14)"},
                "type": "trend",
                "category": "Trend",
            },
            "CCI": {
                "description": "Commodity Channel Index - Momentum oscillator measuring current price relative to average",
                "parameters": {"period": "int (default: 20)"},
                "type": "momentum",
                "category": "Oscillators",
            },
            "Williams %R": {
                "description": "Williams %R - Momentum oscillator measuring overbought/oversold levels",
                "parameters": {"period": "int (default: 14)"},
                "type": "momentum",
                "category": "Oscillators",
            },
            "MFI": {
                "description": "Money Flow Index - Volume-weighted RSI measuring buying/selling pressure",
                "parameters": {"period": "int (default: 14)"},
                "type": "volume",
                "category": "Volume",
            },
            "OBV": {
                "description": "On Balance Volume - Volume-based indicator measuring buying and selling pressure",
                "parameters": {},
                "type": "volume",
                "category": "Volume",
            },
            "VWAP": {
                "description": "Volume Weighted Average Price - Average price weighted by volume",
                "parameters": {},
                "type": "volume",
                "category": "Volume",
            },
            "DPO": {
                "description": "Detrended Price Oscillator - Removes trend to show cycles",
                "parameters": {"period": "int (default: 20)"},
                "type": "trend",
                "category": "Trend",
            },
            "KST": {
                "description": "Know Sure Thing - Long-term momentum oscillator",
                "parameters": {},
                "type": "momentum",
                "category": "Oscillators",
            },
            "UO": {
                "description": "Ultimate Oscillator - Multi-timeframe momentum indicator",
                "parameters": {},
                "type": "momentum",
                "category": "Oscillators",
            },
            "Stoch RSI": {
                "description": "Stochastic RSI - RSI with stochastic calculation",
                "parameters": {},
                "type": "momentum",
                "category": "Oscillators",
            },
            "Momentum": {
                "description": "Momentum - Rate of change in price over a specified period",
                "parameters": {"period": "int (default: 10)"},
                "type": "momentum",
                "category": "Oscillators",
            },
            "Session Levels": {
                "description": "Session High/Low - Rolling high and low levels over a time window",
                "parameters": {
                    "window": "int (default: 96)",
                    "min_periods": "int (default: 1)",
                },
                "type": "support_resistance",
                "category": "Support/Resistance",
            },
            "Session Levels with Fade": {
                "description": "Session High/Low with fade-out effect over specified days",
                "parameters": {
                    "window": "int (default: 96)",
                    "fade_days": "int (default: 2)",
                },
                "type": "support_resistance",
                "category": "Support/Resistance",
            },
            "ROC": {
                "description": "Rate of Change - Momentum oscillator measuring percentage change in price",
                "parameters": {"period": "int (default: 10)"},
                "type": "momentum",
                "category": "Oscillators",
            },
            "Parabolic SAR": {
                "description": "Parabolic Stop and Reverse - Trend-following indicator for stop-loss placement",
                "parameters": {
                    "acceleration": "float (default: 0.02)",
                    "maximum": "float (default: 0.2)",
                },
                "type": "trend",
                "category": "Trend",
            },
            "Ichimoku": {
                "description": "Ichimoku Cloud - Comprehensive indicator showing support, resistance, momentum, and trend",
                "parameters": {
                    "tenkan": "int (default: 9)",
                    "kijun": "int (default: 26)",
                    "senkou_b": "int (default: 52)",
                },
                "type": "trend",
                "category": "Trend",
            },
            "Pivot Points": {
                "description": "Traditional Pivot Points - Support and resistance levels",
                "parameters": {},
                "type": "support_resistance",
                "category": "Support/Resistance",
            },
        }

    @staticmethod
    def calculate_sma(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """Calculate Simple Moving Average"""
        result = df.copy()
        if PANDAS_TA_AVAILABLE:
            result[f"sma_{period}"] = pta.sma(df["close"], length=period)
        elif TA_AVAILABLE:
            result[f"sma_{period}"] = ta.trend.sma_indicator(df["close"], window=period)
        else:
            result[f"sma_{period}"] = df["close"].rolling(window=period).mean()
        return result

    @staticmethod
    def calculate_ema(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """Calculate Exponential Moving Average"""
        result = df.copy()
        if PANDAS_TA_AVAILABLE:
            result[f"ema_{period}"] = pta.ema(df["close"], length=period)
        elif TA_AVAILABLE:
            result[f"ema_{period}"] = ta.trend.ema_indicator(df["close"], window=period)
        else:
            result[f"ema_{period}"] = df["close"].ewm(span=period).mean()
        return result

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate Relative Strength Index"""
        result = df.copy()
        if PANDAS_TA_AVAILABLE:
            result[f"rsi_{period}"] = pta.rsi(df["close"], length=period)
        elif TA_AVAILABLE:
            result[f"rsi_{period}"] = ta.momentum.rsi(df["close"], window=period)
        elif TALIB_AVAILABLE:
            try:
                result[f"rsi_{period}"] = talib.RSI(
                    df["close"].values, timeperiod=period
                )
            except:
                # Fallback calculation if talib fails
                delta = df["close"].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                rs = gain / loss
                result[f"rsi_{period}"] = 100 - (100 / (1 + rs))
        else:
            # Fallback calculation if no libraries available
            delta = df["close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            result[f"rsi_{period}"] = 100 - (100 / (1 + rs))
        return result

    @staticmethod
    def calculate_stochastic(
        df: pd.DataFrame, k_period: int = 14, d_period: int = 3
    ) -> pd.DataFrame:
        """Calculate Stochastic Oscillator"""
        result = df.copy()
        if PANDAS_TA_AVAILABLE:
            try:
                # Get stochastic data - may return DataFrame with multiple columns
                stoch_data = pta.stoch(
                    df["high"], df["low"], df["close"], length=k_period
                )
                if isinstance(stoch_data, pd.DataFrame):
                    # If multiple columns, take the first one (usually %K)
                    result[f"stoch_k_{k_period}"] = stoch_data.iloc[:, 0]
                else:
                    result[f"stoch_k_{k_period}"] = stoch_data

                # Get stochastic signal (%D)
                stoch_signal = pta.stoch_signal(
                    df["high"],
                    df["low"],
                    df["close"],
                    length=k_period,
                    smooth_length=d_period,
                )
                if isinstance(stoch_signal, pd.DataFrame):
                    result[f"stoch_d_{d_period}"] = stoch_signal.iloc[:, 0]
                else:
                    result[f"stoch_d_{d_period}"] = stoch_signal
            except Exception as e:
                print(f"pandas-ta stochastic failed: {e}, using fallback")
                # Fallback calculation
                lowest_low = df["low"].rolling(window=k_period).min()
                highest_high = df["high"].rolling(window=k_period).max()
                k_percent = 100 * (
                    (df["close"] - lowest_low) / (highest_high - lowest_low)
                )
                d_percent = k_percent.rolling(window=d_period).mean()
                result[f"stoch_k_{k_period}"] = k_percent
                result[f"stoch_d_{d_period}"] = d_percent
        elif TA_AVAILABLE:
            try:
                result[f"stoch_k_{k_period}"] = ta.momentum.stoch(
                    df["high"], df["low"], df["close"], window=k_period
                )
                result[f"stoch_d_{d_period}"] = ta.momentum.stoch_signal(
                    df["high"],
                    df["low"],
                    df["close"],
                    window=k_period,
                    smooth_window=d_period,
                )
            except Exception as e:
                print(f"ta library stochastic failed: {e}, using fallback")
                # Fallback calculation
                lowest_low = df["low"].rolling(window=k_period).min()
                highest_high = df["high"].rolling(window=k_period).max()
                k_percent = 100 * (
                    (df["close"] - lowest_low) / (highest_high - lowest_low)
                )
                d_percent = k_percent.rolling(window=d_period).mean()
                result[f"stoch_k_{k_period}"] = k_percent
                result[f"stoch_d_{d_period}"] = d_percent
        elif TALIB_AVAILABLE:
            try:
                k, d = talib.STOCH(
                    df["high"].values,
                    df["low"].values,
                    df["close"].values,
                    fastk_period=k_period,
                    slowk_period=d_period,
                    slowd_period=d_period,
                )
                result[f"stoch_k_{k_period}"] = k
                result[f"stoch_d_{d_period}"] = d
            except Exception as e:
                print(f"talib stochastic failed: {e}, using fallback")
                # Fallback calculation
                lowest_low = df["low"].rolling(window=k_period).min()
                highest_high = df["high"].rolling(window=k_period).max()
                k_percent = 100 * (
                    (df["close"] - lowest_low) / (highest_high - lowest_low)
                )
                d_percent = k_percent.rolling(window=d_period).mean()
                result[f"stoch_k_{k_period}"] = k_percent
                result[f"stoch_d_{d_period}"] = d_percent
        else:
            # Fallback calculation if no libraries available
            lowest_low = df["low"].rolling(window=k_period).min()
            highest_high = df["high"].rolling(window=k_period).max()
            k_percent = 100 * ((df["close"] - lowest_low) / (highest_high - lowest_low))
            d_percent = k_percent.rolling(window=d_period).mean()
            result[f"stoch_k_{k_period}"] = k_percent
            result[f"stoch_d_{d_period}"] = d_percent
        return result

    @staticmethod
    def calculate_bollinger_bands(
        df: pd.DataFrame, period: int = 20, std_dev: float = 2.0
    ) -> pd.DataFrame:
        """Calculate Bollinger Bands"""
        result = df.copy()
        if PANDAS_TA_AVAILABLE:
            bb_indicator = pta.bbands(df["close"], length=period, std=std_dev)
            # Debug: print available columns
            print(f"Bollinger Bands columns: {list(bb_indicator.columns)}")
            # Use the actual column names from pandas-ta
            result[f"bb_upper_{period}_{std_dev}"] = bb_indicator.iloc[
                :, 0
            ]  # First column is upper
            result[f"bb_middle_{period}"] = bb_indicator.iloc[
                :, 1
            ]  # Second column is middle
            result[f"bb_lower_{period}_{std_dev}"] = bb_indicator.iloc[
                :, 2
            ]  # Third column is lower
        elif TA_AVAILABLE:
            bb_indicator = ta.volatility.BollingerBands(
                df["close"], window=period, window_dev=std_dev
            )
            result[f"bb_upper_{period}_{std_dev}"] = bb_indicator.bollinger_hband()
            result[f"bb_middle_{period}"] = bb_indicator.bollinger_mavg()
            result[f"bb_lower_{period}_{std_dev}"] = bb_indicator.bollinger_lband()
        elif TALIB_AVAILABLE:
            try:
                upper, middle, lower = talib.BBANDS(
                    df["close"].values,
                    timeperiod=period,
                    nbdevup=std_dev,
                    nbdevdn=std_dev,
                    matype=0,
                )
                result[f"bb_upper_{period}_{std_dev}"] = upper
                result[f"bb_middle_{period}"] = middle
                result[f"bb_lower_{period}_{std_dev}"] = lower
            except:
                # Fallback calculation
                sma = df["close"].rolling(window=period).mean()
                std = df["close"].rolling(window=period).std()
                result[f"bb_upper_{period}_{std_dev}"] = sma + (std * std_dev)
                result[f"bb_middle_{period}"] = sma
                result[f"bb_lower_{period}_{std_dev}"] = sma - (std * std_dev)
        else:
            # Fallback calculation if no libraries available
            sma = df["close"].rolling(window=period).mean()
            std = df["close"].rolling(window=period).std()
            result[f"bb_upper_{period}_{std_dev}"] = sma + (std * std_dev)
            result[f"bb_middle_{period}"] = sma
            result[f"bb_lower_{period}_{std_dev}"] = sma - (std * std_dev)
        return result

    @staticmethod
    def calculate_macd(
        df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> pd.DataFrame:
        """Calculate MACD"""
        result = df.copy()
        if PANDAS_TA_AVAILABLE:
            macd_indicator = pta.macd(df["close"], fast=fast, slow=slow, signal=signal)
            # Debug: print available columns
            print(f"MACD indicator columns: {list(macd_indicator.columns)}")
            # Use the actual column names from pandas-ta
            result[f"macd_{fast}_{slow}"] = macd_indicator.iloc[
                :, 0
            ]  # First column is MACD line
            result[f"macd_signal_{signal}"] = macd_indicator.iloc[
                :, 1
            ]  # Second column is signal
            result[f"macd_histogram"] = macd_indicator.iloc[
                :, 2
            ]  # Third column is histogram
        elif TA_AVAILABLE:
            result[f"macd_{fast}_{slow}"] = ta.trend.macd(
                df["close"], window_fast=fast, window_slow=slow, window_sign=signal
            )
            result[f"macd_signal_{signal}"] = ta.trend.macd_signal(
                df["close"], window_fast=fast, window_slow=slow, window_sign=signal
            )
            result[f"macd_histogram"] = ta.trend.macd_diff(
                df["close"], window_fast=fast, window_slow=slow, window_sign=signal
            )
        elif FINTA_AVAILABLE:
            result[f"macd_{fast}_{slow}"] = finta.MACD(
                df, period_fast=fast, period_slow=slow, signal=signal
            )
        elif TALIB_AVAILABLE:
            try:
                macd, signal_line, histogram = talib.MACD(
                    df["close"].values,
                    fastperiod=fast,
                    slowperiod=slow,
                    signalperiod=signal,
                )
                result[f"macd_{fast}_{slow}"] = macd
                result[f"macd_signal_{signal}"] = signal_line
                result[f"macd_histogram"] = histogram
            except:
                # Fallback calculation
                ema_fast = df["close"].ewm(span=fast).mean()
                ema_slow = df["close"].ewm(span=slow).mean()
                macd_line = ema_fast - ema_slow
                signal_line = macd_line.ewm(span=signal).mean()
                histogram = macd_line - signal_line
                result[f"macd_{fast}_{slow}"] = macd_line
                result[f"macd_signal_{signal}"] = signal_line
                result[f"macd_histogram"] = histogram
        else:
            # Fallback calculation if no libraries available
            ema_fast = df["close"].ewm(span=fast).mean()
            ema_slow = df["close"].ewm(span=slow).mean()
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal).mean()
            histogram = macd_line - signal_line
            result[f"macd_{fast}_{slow}"] = macd_line
            result[f"macd_signal_{signal}"] = signal_line
            result[f"macd_histogram"] = histogram
        return result

    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate Average True Range"""
        result = df.copy()
        try:
            result[f"atr_{period}"] = talib.ATR(
                df["high"].values,
                df["low"].values,
                df["close"].values,
                timeperiod=period,
            )
        except:
            # Fallback calculation
            high_low = df["high"] - df["low"]
            high_close = np.abs(df["high"] - df["close"].shift())
            low_close = np.abs(df["low"] - df["close"].shift())
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(
                axis=1
            )
            result[f"atr_{period}"] = true_range.rolling(window=period).mean()
        return result

    @staticmethod
    def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate Average Directional Index"""
        result = df.copy()
        try:
            result[f"adx_{period}"] = talib.ADX(
                df["high"].values,
                df["low"].values,
                df["close"].values,
                timeperiod=period,
            )
        except:
            # Fallback calculation (simplified)
            result[f"adx_{period}"] = df["close"].rolling(window=period).std()
        return result

    @staticmethod
    def calculate_cci(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """Calculate Commodity Channel Index"""
        result = df.copy()
        try:
            result[f"cci_{period}"] = talib.CCI(
                df["high"].values,
                df["low"].values,
                df["close"].values,
                timeperiod=period,
            )
        except:
            # Fallback calculation
            typical_price = (df["high"] + df["low"] + df["close"]) / 3
            sma_tp = typical_price.rolling(window=period).mean()
            mean_deviation = typical_price.rolling(window=period).apply(
                lambda x: np.mean(np.abs(x - x.mean()))
            )
            result[f"cci_{period}"] = (typical_price - sma_tp) / (
                0.015 * mean_deviation
            )
        return result

    @staticmethod
    def calculate_williams_r(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate Williams %R"""
        result = df.copy()
        try:
            result[f"williams_r_{period}"] = talib.WILLR(
                df["high"].values,
                df["low"].values,
                df["close"].values,
                timeperiod=period,
            )
        except:
            # Fallback calculation
            highest_high = df["high"].rolling(window=period).max()
            lowest_low = df["low"].rolling(window=period).min()
            result[f"williams_r_{period}"] = -100 * (
                (highest_high - df["close"]) / (highest_high - lowest_low)
            )
        return result

    @staticmethod
    def calculate_momentum(df: pd.DataFrame, period: int = 10) -> pd.DataFrame:
        """Calculate Momentum"""
        result = df.copy()
        result[f"momentum_{period}"] = df["close"] - df["close"].shift(period)
        return result

    @staticmethod
    def calculate_session_levels(
        df: pd.DataFrame, window: int = 96, min_periods: int = 1
    ) -> pd.DataFrame:
        """
        Calculate Session High and Low levels

        Args:
            df: DataFrame with OHLC data
            window: Rolling window size (default 96 = 24 hours for 15-min candles)
            min_periods: Minimum periods required for calculation

        Returns:
            DataFrame with session_high and session_low columns
        """
        result = df.copy()

        # Calculate session high (rolling maximum of high prices)
        result["session_high"] = (
            df["high"].rolling(window=window, min_periods=min_periods).max()
        )

        # Calculate session low (rolling minimum of low prices)
        result["session_low"] = (
            df["low"].rolling(window=window, min_periods=min_periods).min()
        )

        return result

    @staticmethod
    def calculate_session_levels_with_fade(
        df: pd.DataFrame, window: int = 96, fade_days: int = 2
    ) -> pd.DataFrame:
        """
        Calculate Session High and Low levels with fade-out effect

        Args:
            df: DataFrame with OHLC data
            window: Rolling window size (default 96 = 24 hours for 15-min candles)
            fade_days: Number of days for fade-out effect

        Returns:
            DataFrame with session_high, session_low, and fade columns
        """
        result = df.copy()

        # Calculate basic session levels
        result = IndicatorLibrary.calculate_session_levels(result, window)

        # Calculate fade-out effect
        fade_periods = fade_days * 96  # 96 candles per day for 15-min data

        # Initialize fade columns
        result["session_high_fade"] = 1.0
        result["session_low_fade"] = 1.0

        # Calculate fade for each session high/low
        for i in range(len(result)):
            if i > 0:
                # Check if session high/low changed
                if result.iloc[i]["session_high"] != result.iloc[i - 1]["session_high"]:
                    # New session high - start fade countdown
                    result.loc[result.index[i], "session_high_fade"] = 1.0
                else:
                    # Continue fade
                    prev_fade = result.iloc[i - 1]["session_high_fade"]
                    fade_step = 1.0 / fade_periods
                    result.loc[result.index[i], "session_high_fade"] = max(
                        0.0, prev_fade - fade_step
                    )

                if result.iloc[i]["session_low"] != result.iloc[i - 1]["session_low"]:
                    # New session low - start fade countdown
                    result.loc[result.index[i], "session_low_fade"] = 1.0
                else:
                    # Continue fade
                    prev_fade = result.iloc[i - 1]["session_low_fade"]
                    fade_step = 1.0 / fade_periods
                    result.loc[result.index[i], "session_low_fade"] = max(
                        0.0, prev_fade - fade_step
                    )

        return result

    @staticmethod
    def calculate_roc(df: pd.DataFrame, period: int = 10) -> pd.DataFrame:
        """Calculate Rate of Change"""
        result = df.copy()
        result[f"roc_{period}"] = (
            (df["close"] - df["close"].shift(period)) / df["close"].shift(period)
        ) * 100
        return result

    @staticmethod
    def calculate_obv(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate On Balance Volume"""
        result = df.copy()
        try:
            result["obv"] = talib.OBV(
                df["close"].values,
                df["volume"].values if "volume" in df.columns else df["close"].values,
            )
        except:
            # Fallback calculation
            obv = pd.Series(index=df.index, dtype=float)
            obv.iloc[0] = 0
            for i in range(1, len(df)):
                if df["close"].iloc[i] > df["close"].iloc[i - 1]:
                    obv.iloc[i] = obv.iloc[i - 1] + (
                        df["volume"].iloc[i] if "volume" in df.columns else 1
                    )
                elif df["close"].iloc[i] < df["close"].iloc[i - 1]:
                    obv.iloc[i] = obv.iloc[i - 1] - (
                        df["volume"].iloc[i] if "volume" in df.columns else 1
                    )
                else:
                    obv.iloc[i] = obv.iloc[i - 1]
            result["obv"] = obv
        return result

    @staticmethod
    def calculate_vwap(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Volume Weighted Average Price"""
        result = df.copy()
        if "volume" in df.columns:
            typical_price = (df["high"] + df["low"] + df["close"]) / 3
            vwap = (typical_price * df["volume"]).cumsum() / df["volume"].cumsum()
            result["vwap"] = vwap
        else:
            # If no volume data, use typical price
            result["vwap"] = (df["high"] + df["low"] + df["close"]) / 3
        return result

    @staticmethod
    def calculate_parabolic_sar(
        df: pd.DataFrame, acceleration: float = 0.02, maximum: float = 0.2
    ) -> pd.DataFrame:
        """Calculate Parabolic SAR"""
        result = df.copy()
        try:
            result["parabolic_sar"] = talib.SAR(
                df["high"].values,
                df["low"].values,
                acceleration=acceleration,
                maximum=maximum,
            )
        except:
            # Fallback calculation (simplified)
            result["parabolic_sar"] = df["close"].rolling(window=5).mean()
        return result

    @staticmethod
    def calculate_ichimoku(
        df: pd.DataFrame, tenkan: int = 9, kijun: int = 26, senkou_b: int = 52
    ) -> pd.DataFrame:
        """Calculate Ichimoku Cloud components"""
        result = df.copy()

        if PANDAS_TA_AVAILABLE:
            ichimoku = pta.ichimoku(
                df["high"],
                df["low"],
                df["close"],
                tenkan=tenkan,
                kijun=kijun,
                senkou_b=senkou_b,
            )
            result["tenkan_sen"] = ichimoku["ITS"]
            result["kijun_sen"] = ichimoku["IKS"]
            result["senkou_span_a"] = ichimoku["ISA"]
            result["senkou_span_b"] = ichimoku["ISB"]
            result["chikou_span"] = ichimoku["ICS"]
        else:
            # Fallback calculation
            # Tenkan-sen (Conversion Line)
            high_tenkan = df["high"].rolling(window=tenkan).max()
            low_tenkan = df["low"].rolling(window=tenkan).min()
            result["tenkan_sen"] = (high_tenkan + low_tenkan) / 2

            # Kijun-sen (Base Line)
            high_kijun = df["high"].rolling(window=kijun).max()
            low_kijun = df["low"].rolling(window=kijun).min()
            result["kijun_sen"] = (high_kijun + low_kijun) / 2

            # Senkou Span A (Leading Span A)
            result["senkou_span_a"] = (
                (result["tenkan_sen"] + result["kijun_sen"]) / 2
            ).shift(kijun)

            # Senkou Span B (Leading Span B)
            high_senkou_b = df["high"].rolling(window=senkou_b).max()
            low_senkou_b = df["low"].rolling(window=senkou_b).min()
            result["senkou_span_b"] = ((high_senkou_b + low_senkou_b) / 2).shift(kijun)

            # Chikou Span (Lagging Span)
            result["chikou_span"] = df["close"].shift(-kijun)

        return result

    @staticmethod
    def calculate_fibonacci_retracements(
        df: pd.DataFrame, high_col: str = "high", low_col: str = "low"
    ) -> pd.DataFrame:
        """Calculate Fibonacci retracement levels"""
        result = df.copy()

        # Find swing high and low
        swing_high = df[high_col].rolling(window=20).max()
        swing_low = df[low_col].rolling(window=20).min()

        # Fibonacci levels
        levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]

        for level in levels:
            result[f"fib_{level:.3f}"] = swing_low + (swing_high - swing_low) * level

        return result

    @staticmethod
    def calculate_pivot_points(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Pivot Points"""
        result = df.copy()

        # Daily pivot points
        result["pivot"] = (df["high"] + df["low"] + df["close"]) / 3
        result["r1"] = 2 * result["pivot"] - df["low"]
        result["s1"] = 2 * result["pivot"] - df["high"]
        result["r2"] = result["pivot"] + (df["high"] - df["low"])
        result["s2"] = result["pivot"] - (df["high"] - df["low"])

        return result

    @staticmethod
    def calculate_supply_demand_zones(
        df: pd.DataFrame, window: int = 20, threshold: float = 0.02
    ) -> pd.DataFrame:
        """Calculate Supply and Demand zones"""
        result = df.copy()

        # Identify potential supply zones (resistance)
        high_peaks = df["high"].rolling(window=window, center=True).max()
        supply_zones = df["high"] >= high_peaks * (1 - threshold)

        # Identify potential demand zones (support)
        low_troughs = df["low"].rolling(window=window, center=True).min()
        demand_zones = df["low"] <= low_troughs * (1 + threshold)

        result["supply_zone"] = supply_zones
        result["demand_zone"] = demand_zones

        return result

    @staticmethod
    def calculate_range_of_day(
        df: pd.DataFrame,
        start_hour: int = 18,
        end_hour: int = 19,
        timezone: str = "US/Eastern",
    ) -> pd.DataFrame:
        """
        Calculate Range of the Day for specified time window (default 18:00-19:00 EST).
        Returns high and low values for drawing horizontal lines.
        Timeframe-aware calculation that works for M1, M15, H1, etc.
        """
        result = df.copy()

        # Convert index to specified timezone for time-based calculations
        if df.index.tz is None:
            df_tz = df.copy()
            df_tz.index = df_tz.index.tz_localize("UTC").tz_convert(timezone)
        else:
            df_tz = df.copy()
            df_tz.index = df_tz.index.tz_convert(timezone)

        # Initialize columns for range of day values
        result["rod_high"] = np.nan
        result["rod_low"] = np.nan
        result["rod_range"] = np.nan

        # Group data by date (EST timezone)
        df_tz["date"] = df_tz.index.date

        # Get unique dates
        unique_dates = df_tz["date"].drop_duplicates().tolist()

        # Calculate range for each trading day
        for date in unique_dates:
            # Get data for this specific date
            day_data = df_tz[df_tz["date"] == date]

            # Filter for the specified time window (18:00-19:00 EST)
            time_mask = (day_data.index.hour >= start_hour) & (
                day_data.index.hour < end_hour
            )
            window_data = day_data[time_mask]

            if len(window_data) > 0:
                # Calculate high and low for this time window
                window_high = window_data["high"].max()
                window_low = window_data["low"].min()
                window_range = window_high - window_low

                # Apply these values to all candles for this date
                date_mask = df_tz["date"] == date
                result.loc[date_mask, "rod_high"] = window_high
                result.loc[date_mask, "rod_low"] = window_low
                result.loc[date_mask, "rod_range"] = window_range

        # Clean up temporary column
        result = result.drop("date", axis=1, errors="ignore")

        return result

    @staticmethod
    def calculate_advanced_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate advanced indicators available only in modern libraries"""
        result = df.copy()

        if PANDAS_TA_AVAILABLE:
            # Advanced momentum indicators
            result["williams_r"] = pta.willr(
                df["high"], df["low"], df["close"], length=14
            )
            result["cci"] = pta.cci(df["high"], df["low"], df["close"], length=20)
            result["adx"] = pta.adx(df["high"], df["low"], df["close"], length=14)

            # Advanced volatility indicators
            result["atr"] = pta.atr(df["high"], df["low"], df["close"], length=14)
            result["natr"] = pta.natr(df["high"], df["low"], df["close"], length=14)

            # Advanced trend indicators
            result["dpo"] = pta.dpo(df["close"], length=20)
            result["kst"] = pta.kst(df["close"])
            result["kst_sig"] = pta.kst_sig(df["close"])

            # Advanced volume indicators
            if "volume" in df.columns:
                result["obv"] = pta.obv(df["close"], df["volume"])
                result["vwap"] = pta.vwap(
                    df["high"], df["low"], df["close"], df["volume"]
                )
                result["mfi"] = pta.mfi(
                    df["high"], df["low"], df["close"], df["volume"], length=14
                )
                result["ad"] = pta.ad(df["high"], df["low"], df["close"], df["volume"])

            # Advanced oscillators
            result["uo"] = pta.uo(df["high"], df["low"], df["close"])
            result["stoch_rsi"] = pta.stochrsi(df["close"])

            # Advanced support/resistance
            result["pivot_points"] = pta.pivots_traditional(
                df["high"], df["low"], df["close"]
            )

        elif TA_AVAILABLE:
            # Advanced momentum indicators
            result["williams_r"] = ta.momentum.williams_r(
                df["high"], df["low"], df["close"], window=14
            )
            result["cci"] = ta.trend.cci(df["high"], df["low"], df["close"], window=20)
            result["adx"] = ta.trend.adx(df["high"], df["low"], df["close"], window=14)

            # Advanced volatility indicators
            result["atr"] = ta.volatility.average_true_range(
                df["high"], df["low"], df["close"], window=14
            )

            # Advanced volume indicators
            if "volume" in df.columns:
                result["obv"] = ta.volume.on_balance_volume(df["close"], df["volume"])
                result["mfi"] = ta.volume.money_flow_index(
                    df["high"], df["low"], df["close"], df["volume"], window=14
                )

        elif FINTA_AVAILABLE:
            # Advanced indicators from finta
            result["williams_r"] = finta.WILLIAMS_R(df, period=14)
            result["cci"] = finta.CCI(df, period=20)
            result["adx"] = finta.ADX(df, period=14)
            result["atr"] = finta.ATR(df, period=14)

            if "volume" in df.columns:
                result["obv"] = finta.OBV(df)
                result["mfi"] = finta.MFI(df, period=14)

        return result

    @staticmethod
    def calculate_indicator(
        df: pd.DataFrame, indicator_type: IndicatorType, parameters: Dict[str, Any]
    ) -> pd.DataFrame:
        """Calculate indicator based on type and parameters"""
        if indicator_type == IndicatorType.SMA:
            period = parameters.get("period", 20)
            return IndicatorLibrary.calculate_sma(df, period)

        elif indicator_type == IndicatorType.EMA:
            period = parameters.get("period", 20)
            return IndicatorLibrary.calculate_ema(df, period)

        elif indicator_type == IndicatorType.RSI:
            period = parameters.get("period", 14)
            return IndicatorLibrary.calculate_rsi(df, period)

        elif indicator_type == IndicatorType.STOCHASTIC:
            k_period = parameters.get("k_period", 14)
            d_period = parameters.get("d_period", 3)
            return IndicatorLibrary.calculate_stochastic(df, k_period, d_period)

        elif indicator_type == IndicatorType.BOLLINGER_BANDS:
            period = parameters.get("period", 20)
            std_dev = parameters.get("std_dev", 2.0)
            return IndicatorLibrary.calculate_bollinger_bands(df, period, std_dev)

        elif indicator_type == IndicatorType.MACD:
            fast = parameters.get("fast", 12)
            slow = parameters.get("slow", 26)
            signal = parameters.get("signal", 9)
            return IndicatorLibrary.calculate_macd(df, fast, slow, signal)

        elif indicator_type == IndicatorType.ATR:
            period = parameters.get("period", 14)
            return IndicatorLibrary.calculate_atr(df, period)

        elif indicator_type == IndicatorType.ADX:
            period = parameters.get("period", 14)
            return IndicatorLibrary.calculate_adx(df, period)

        elif indicator_type == IndicatorType.CCI:
            period = parameters.get("period", 20)
            return IndicatorLibrary.calculate_cci(df, period)

        elif indicator_type == IndicatorType.WILLIAMS_R:
            period = parameters.get("period", 14)
            return IndicatorLibrary.calculate_williams_r(df, period)

        elif indicator_type == IndicatorType.MOMENTUM:
            period = parameters.get("period", 10)
            return IndicatorLibrary.calculate_momentum(df, period)

        elif indicator_type == IndicatorType.SESSION_LEVELS:
            window = parameters.get("window", 96)
            min_periods = parameters.get("min_periods", 1)
            return IndicatorLibrary.calculate_session_levels(df, window, min_periods)

        elif indicator_type == IndicatorType.SESSION_LEVELS_FADE:
            window = parameters.get("window", 96)
            fade_days = parameters.get("fade_days", 2)
            return IndicatorLibrary.calculate_session_levels_with_fade(
                df, window, fade_days
            )

        elif indicator_type == IndicatorType.ROC:
            period = parameters.get("period", 10)
            return IndicatorLibrary.calculate_roc(df, period)

        elif indicator_type == IndicatorType.OBV:
            return IndicatorLibrary.calculate_obv(df)

        elif indicator_type == IndicatorType.VWAP:
            return IndicatorLibrary.calculate_vwap(df)

        elif indicator_type == IndicatorType.PARABOLIC_SAR:
            acceleration = parameters.get("acceleration", 0.02)
            maximum = parameters.get("maximum", 0.2)
            return IndicatorLibrary.calculate_parabolic_sar(df, acceleration, maximum)

        elif indicator_type == IndicatorType.ICHIMOKU:
            tenkan = parameters.get("tenkan", 9)
            kijun = parameters.get("kijun", 26)
            senkou_b = parameters.get("senkou_b", 52)
            return IndicatorLibrary.calculate_ichimoku(df, tenkan, kijun, senkou_b)

        elif indicator_type == IndicatorType.FIBONACCI:
            return IndicatorLibrary.calculate_fibonacci_retracements(df)

        elif indicator_type == IndicatorType.PIVOT_POINTS:
            return IndicatorLibrary.calculate_pivot_points(df)

        elif indicator_type == IndicatorType.SUPPLY_DEMAND:
            window = parameters.get("window", 20)
            threshold = parameters.get("threshold", 0.02)
            return IndicatorLibrary.calculate_supply_demand_zones(df, window, threshold)

        elif indicator_type == IndicatorType.RANGE_OF_DAY:
            start_hour = parameters.get("start_hour", 18)
            end_hour = parameters.get("end_hour", 19)
            timezone = parameters.get("timezone", "US/Eastern")
            return IndicatorLibrary.calculate_range_of_day(
                df, start_hour, end_hour, timezone
            )

        else:
            raise ValueError(f"Unknown indicator type: {indicator_type}")

    @staticmethod
    def get_indicator_columns(df: pd.DataFrame) -> List[str]:
        """Get list of indicator columns in the dataframe"""
        indicator_columns = []
        for col in df.columns:
            if any(
                indicator in col.lower()
                for indicator in [
                    "sma",
                    "ema",
                    "rsi",
                    "stoch",
                    "bb_",
                    "macd",
                    "atr",
                    "adx",
                    "cci",
                    "williams",
                    "momentum",
                    "roc",
                    "obv",
                    "vwap",
                    "parabolic",
                    "tenkan",
                    "kijun",
                    "senkou",
                    "chikou",
                    "fib_",
                    "pivot",
                    "supply",
                    "demand",
                    "session_high",
                    "session_low",
                    "range_of_day",
                ]
            ):
                indicator_columns.append(col)
        return indicator_columns

    @staticmethod
    def remove_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Remove all indicator columns from dataframe"""
        indicator_columns = IndicatorLibrary.get_indicator_columns(df)
        return df.drop(columns=indicator_columns, errors="ignore")

    @staticmethod
    def get_indicator_summary(df: pd.DataFrame) -> Dict[str, Any]:
        """Get summary of all indicators in the dataframe"""
        indicator_columns = IndicatorLibrary.get_indicator_columns(df)
        summary = {
            "total_indicators": len(indicator_columns),
            "indicators": indicator_columns,
            "categories": {},
        }

        # Categorize indicators
        for col in indicator_columns:
            if any(x in col.lower() for x in ["sma", "ema"]):
                category = "Moving Averages"
            elif any(
                x in col.lower()
                for x in ["rsi", "stoch", "cci", "williams", "momentum", "roc"]
            ):
                category = "Oscillators"
            elif any(x in col.lower() for x in ["bb_", "atr"]):
                category = "Volatility"
            elif any(
                x in col.lower()
                for x in ["macd", "adx", "parabolic", "tenkan", "kijun"]
            ):
                category = "Trend"
            elif any(x in col.lower() for x in ["obv", "vwap"]):
                category = "Volume"
            elif any(x in col.lower() for x in ["fib_", "pivot", "supply", "demand"]):
                category = "Support/Resistance"
            else:
                category = "Other"

            if category not in summary["categories"]:
                summary["categories"][category] = []
            summary["categories"][category].append(col)

        return summary


if __name__ == "__main__":
    # Test the indicator library
    print("TrimurtiFX Indicator Library")
    print("=" * 40)

    # Create sample data
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    sample_data = pd.DataFrame(
        {
            "open": np.random.randn(100).cumsum() + 100,
            "high": np.random.randn(100).cumsum() + 102,
            "low": np.random.randn(100).cumsum() + 98,
            "close": np.random.randn(100).cumsum() + 100,
            "volume": np.random.randint(1000, 10000, 100),
        },
        index=dates,
    )

    # Test indicators
    print("Testing indicators...")

    # SMA
    df_with_sma = IndicatorLibrary.calculate_sma(sample_data, 20)
    print(f"SMA 20: {df_with_sma['sma_20'].iloc[-1]:.2f}")

    # RSI
    df_with_rsi = IndicatorLibrary.calculate_rsi(sample_data, 14)
    print(f"RSI 14: {df_with_rsi['rsi_14'].iloc[-1]:.2f}")

    # Bollinger Bands
    df_with_bb = IndicatorLibrary.calculate_bollinger_bands(sample_data, 20, 2.0)
    print(f"BB Upper: {df_with_bb['bb_upper_20_2.0'].iloc[-1]:.2f}")

    print("\nIndicator Library ready for use!")
