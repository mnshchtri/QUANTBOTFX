"""
Data Loading Module for TrimurtiFX Charting Platform
===================================================

Handles loading and processing of financial data from various sources.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional
import pytz
import sys
import os

# Add parent directory to path
from strategies.momentum_following_strategy import RangeOfTheDayStrategy


class DataLoader:
    """Handles loading and processing of financial data"""

    def __init__(self):
        self.strategy = RangeOfTheDayStrategy()
        self.est = pytz.timezone("US/Eastern")

    def load_historical_data(
        self, instrument: str, timeframe: str, start_date: datetime, end_date: datetime
    ) -> Optional[pd.DataFrame]:
        """
        Load historical data for a specific instrument and timeframe

        Args:
            instrument: Trading instrument (e.g., 'GBP_JPY')
            timeframe: Timeframe (e.g., 'M15', 'H1', 'D1')
            start_date: Start date for data
            end_date: End date for data

        Returns:
            DataFrame with OHLCV data or None if no data available
        """
        try:
            # Get extended historical data
            days_back = (end_date - start_date).days + 30
            df = self.strategy.get_extended_historical_data(
                instrument, granularity=timeframe, days_back=days_back
            )

            if df is None or len(df) == 0:
                return None

            # Filter data for selected date range
            start_dt = self.est.localize(start_date)
            end_dt = self.est.localize(end_date + timedelta(days=1))
            df = df[(df.index >= start_dt) & (df.index < end_dt)]

            if len(df) == 0:
                return None

            # Ensure data quality
            df = self._clean_data(df)

            return df

        except Exception as e:
            print(f"Error loading data: {e}")
            return None

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate the data

        Args:
            df: Raw DataFrame

        Returns:
            Cleaned DataFrame
        """
        # Remove any rows with NaN values
        df = df.dropna()

        # Ensure all price columns are numeric
        price_columns = ["open", "high", "low", "close"]
        for col in price_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Remove rows with invalid prices
        df = df[df["open"] > 0].copy()
        df = df[df["high"] > 0].copy()
        df = df[df["low"] > 0].copy()
        df = df[df["close"] > 0].copy()

        # Ensure high >= low
        df = df[df["high"] >= df["low"]].copy()

        # Sort by timestamp
        df = df.sort_index()

        return df

    def get_available_instruments(self) -> list:
        """Get list of available instruments"""
        return ["GBP_JPY", "EUR_USD", "USD_JPY", "GBP_USD", "EUR_JPY"]

    def get_available_timeframes(self) -> dict:
        """Get available timeframes"""
        return {
            "1 Minute": "M1",
            "5 Minutes": "M5",
            "15 Minutes": "M15",
            "30 Minutes": "M30",
            "1 Hour": "H1",
            "4 Hours": "H4",
            "Daily": "D1",
        }

    def validate_data_quality(self, df: pd.DataFrame) -> dict:
        """
        Validate data quality and return statistics

        Args:
            df: DataFrame to validate

        Returns:
            Dictionary with validation results
        """
        if df is None or len(df) == 0:
            return {"valid": False, "message": "No data available"}

        stats = {
            "valid": True,
            "total_candles": len(df),
            "date_range": {"start": df.index.min(), "end": df.index.max()},
            "gaps": [],
            "weekend_candles": 0,
            "quality_score": 100,
        }

        # Check for data gaps
        expected_interval = self._get_expected_interval(df)
        if expected_interval:
            gaps = self._find_data_gaps(df, expected_interval)
            stats["gaps"] = gaps
            if gaps:
                stats["quality_score"] -= len(gaps) * 5

        # Count weekend candles (expected for forex)
        weekend_candles = len(df[df.index.to_series().dt.weekday >= 5])
        stats["weekend_candles"] = weekend_candles

        # Check for price anomalies
        price_anomalies = self._check_price_anomalies(df)
        if price_anomalies:
            stats["quality_score"] -= len(price_anomalies) * 10

        stats["quality_score"] = max(0, stats["quality_score"])

        return stats

    def _get_expected_interval(self, df: pd.DataFrame) -> timedelta:
        """Get expected time interval between candles"""
        if len(df) < 2:
            return None

        intervals = df.index.to_series().diff().dropna()
        if len(intervals) == 0:
            return None

        # Get the most common interval
        mode_interval = (
            intervals.mode().iloc[0]
            if len(intervals.mode()) > 0
            else intervals.median()
        )
        return mode_interval

    def _find_data_gaps(self, df: pd.DataFrame, expected_interval: timedelta) -> list:
        """Find gaps in the data"""
        gaps = []

        for i in range(1, len(df)):
            actual_interval = df.index[i] - df.index[i - 1]
            if actual_interval > expected_interval * 2:  # Allow for some tolerance
                gaps.append(
                    {
                        "start": df.index[i - 1],
                        "end": df.index[i],
                        "duration": actual_interval,
                    }
                )

        return gaps

    def _check_price_anomalies(self, df: pd.DataFrame) -> list:
        """Check for price anomalies"""
        anomalies = []

        # Check for extreme price movements
        price_changes = df["close"].pct_change().abs()
        extreme_moves = price_changes > 0.1  # 10% moves

        for idx in df[extreme_moves].index:
            anomalies.append(
                {
                    "timestamp": idx,
                    "type": "extreme_price_move",
                    "value": price_changes[idx],
                }
            )

        return anomalies
