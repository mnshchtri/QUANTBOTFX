#!/usr/bin/env python3
"""
Indicator Service
================

Integrated technical indicator calculation service that provides all indicator 
functionality without requiring a separate AI agent process.

Features:
- Comprehensive indicator calculations using the IndicatorLibrary
- Data fetching from Data Management AI
- Frontend-ready data format
- Caching and optimization
- Direct class integration (no HTTP overhead)

Usage:
    from services.indicator_service import IndicatorService
    indicator_service = IndicatorService()
    result = await indicator_service.calculate_indicators(symbol, timeframe, indicators)
"""

import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import pandas as pd
import numpy as np
import requests

# Import the indicators library
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from indicators import IndicatorLibrary

# Configure logging
logger = logging.getLogger(__name__)


class IndicatorService:
    """Service for technical indicator calculations"""

    def __init__(self, data_management_url: str = "http://localhost:8002"):
        self.indicator_lib = IndicatorLibrary()
        self.data_management_url = data_management_url
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
        logger.info("🔧 Indicator Service initialized")

    async def get_data_from_management_ai(
        self, symbol: str, timeframe: str, limit: int = 1000
    ) -> pd.DataFrame:
        """Fetch data from Data Management AI"""
        try:
            url = f"{self.data_management_url}/api/data/{symbol}/{timeframe}"
            params = {"limit": limit}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Handle different response formats from Data Management AI
            if "candles" in data:
                # Convert candles format to DataFrame
                df_data = []
                for candle in data["candles"]:
                    df_data.append(
                        {
                            "timestamp": pd.to_datetime(candle["time"]),
                            "open": float(candle["open"]),
                            "high": float(candle["high"]),
                            "low": float(candle["low"]),
                            "close": float(candle["close"]),
                            "volume": float(candle.get("volume", 0)),
                        }
                    )
                df = pd.DataFrame(df_data)
                df.set_index("timestamp", inplace=True)
                logger.info(f"Converted {len(df)} candles from Data Management AI")
            elif "data" in data and isinstance(data["data"], list):
                # Handle direct data format
                df_data = []
                for item in data["data"]:
                    df_data.append(
                        {
                            "timestamp": pd.to_datetime(item["time"]),
                            "open": float(item["open"]),
                            "high": float(item["high"]),
                            "low": float(item["low"]),
                            "close": float(item["close"]),
                            "volume": float(item.get("volume", 0)),
                        }
                    )
                df = pd.DataFrame(df_data)
                df.set_index("timestamp", inplace=True)
                logger.info(f"Converted {len(df)} data points from Data Management AI")
            else:
                logger.error(f"Unexpected data format from Data Management AI: {data}")
                raise ValueError("Unexpected data format from Data Management AI")

            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from Data Management AI: {e}")
            raise Exception(f"Could not fetch data: {e}")
        except Exception as e:
            logger.error(f"Error processing data from Data Management AI: {e}")
            raise Exception(f"Could not process data: {e}")

    def _get_cache_key(
        self,
        symbol: str,
        timeframe: str,
        indicators: List[str],
        parameters: Dict[str, Any],
    ) -> str:
        """Generate cache key for request"""
        param_str = str(sorted(parameters.items())) if parameters else ""
        indicator_str = ",".join(sorted(indicators))
        return f"{symbol}_{timeframe}_{indicator_str}_{param_str}"

    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cache entry is still valid"""
        cache_time = cache_entry.get("timestamp", datetime.min)
        return (datetime.now() - cache_time).total_seconds() < self.cache_timeout

    async def calculate_indicators(
        self,
        symbol: str,
        timeframe: str,
        indicators: List[str],
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Calculate technical indicators for given symbol and timeframe"""

        if parameters is None:
            parameters = {}

        # Check cache first
        cache_key = self._get_cache_key(symbol, timeframe, indicators, parameters)
        if cache_key in self.cache and self._is_cache_valid(self.cache[cache_key]):
            logger.info(f"📊 Returning cached indicators for {symbol} {timeframe}")
            return self.cache[cache_key]["data"]

        try:
            # Fetch data
            df = await self.get_data_from_management_ai(symbol, timeframe)

            if df.empty:
                raise ValueError(f"No data available for {symbol} {timeframe}")

            # Prepare indicators data
            result_indicators = {}

            # Calculate each requested indicator
            for indicator in indicators:
                try:
                    indicator_params = parameters.get(indicator, {})

                    if indicator.lower() in ["rsi"]:
                        period = indicator_params.get("period", 14)
                        df_with_indicator = self.indicator_lib.calculate_rsi(
                            df, period=period
                        )
                        col_name = f"rsi_{period}"

                        if col_name in df_with_indicator.columns:
                            indicator_data = []
                            for idx, value in df_with_indicator[col_name].items():
                                if not pd.isna(value):
                                    indicator_data.append(
                                        {
                                            "time": int(idx.timestamp()) * 1000,
                                            "value": float(value),
                                        }
                                    )
                            result_indicators[f"rsi_{period}"] = indicator_data

                    elif indicator.lower() in ["stochastic", "stoch"]:
                        k_period = indicator_params.get("k_period", 14)
                        d_period = indicator_params.get("d_period", 3)

                        df_with_indicator = self.indicator_lib.calculate_stochastic(
                            df, k_period=k_period, d_period=d_period
                        )

                        # Stochastic K
                        k_col = f"stoch_k_{k_period}"
                        if k_col in df_with_indicator.columns:
                            k_data = []
                            for idx, value in df_with_indicator[k_col].items():
                                if not pd.isna(value):
                                    k_data.append(
                                        {
                                            "time": int(idx.timestamp()) * 1000,
                                            "value": float(value),
                                        }
                                    )
                            result_indicators[f"stochastic_k_{k_period}"] = k_data

                        # Stochastic D
                        d_col = f"stoch_d_{d_period}"
                        if d_col in df_with_indicator.columns:
                            d_data = []
                            for idx, value in df_with_indicator[d_col].items():
                                if not pd.isna(value):
                                    d_data.append(
                                        {
                                            "time": int(idx.timestamp()) * 1000,
                                            "value": float(value),
                                        }
                                    )
                            result_indicators[f"stochastic_d_{d_period}"] = d_data

                    elif indicator.lower() in ["sma"]:
                        period = indicator_params.get("period", 20)
                        df_with_indicator = self.indicator_lib.calculate_sma(
                            df, period=period
                        )
                        col_name = f"sma_{period}"

                        if col_name in df_with_indicator.columns:
                            indicator_data = []
                            for idx, value in df_with_indicator[col_name].items():
                                if not pd.isna(value):
                                    indicator_data.append(
                                        {
                                            "time": int(idx.timestamp()) * 1000,
                                            "value": float(value),
                                        }
                                    )
                            result_indicators[f"sma_{period}"] = indicator_data

                    elif indicator.lower() in ["ema"]:
                        period = indicator_params.get("period", 20)
                        df_with_indicator = self.indicator_lib.calculate_ema(
                            df, period=period
                        )
                        col_name = f"ema_{period}"

                        if col_name in df_with_indicator.columns:
                            indicator_data = []
                            for idx, value in df_with_indicator[col_name].items():
                                if not pd.isna(value):
                                    indicator_data.append(
                                        {
                                            "time": int(idx.timestamp()) * 1000,
                                            "value": float(value),
                                        }
                                    )
                            result_indicators[f"ema_{period}"] = indicator_data

                    elif indicator.lower() in ["macd"]:
                        fast = indicator_params.get("fast", 12)
                        slow = indicator_params.get("slow", 26)
                        signal = indicator_params.get("signal", 9)

                        df_with_indicator = self.indicator_lib.calculate_macd(
                            df, fast=fast, slow=slow, signal=signal
                        )

                        # MACD line
                        macd_col = f"macd_{fast}_{slow}"
                        if macd_col in df_with_indicator.columns:
                            macd_data = []
                            for idx, value in df_with_indicator[macd_col].items():
                                if not pd.isna(value):
                                    macd_data.append(
                                        {
                                            "time": int(idx.timestamp()) * 1000,
                                            "value": float(value),
                                        }
                                    )
                            result_indicators[f"macd_{fast}_{slow}"] = macd_data

                        # Signal line
                        signal_col = f"macd_signal_{signal}"
                        if signal_col in df_with_indicator.columns:
                            signal_data = []
                            for idx, value in df_with_indicator[signal_col].items():
                                if not pd.isna(value):
                                    signal_data.append(
                                        {
                                            "time": int(idx.timestamp()) * 1000,
                                            "value": float(value),
                                        }
                                    )
                            result_indicators[f"macd_signal_{signal}"] = signal_data

                        # Histogram
                        hist_col = f"macd_histogram_{signal}"
                        if hist_col in df_with_indicator.columns:
                            hist_data = []
                            for idx, value in df_with_indicator[hist_col].items():
                                if not pd.isna(value):
                                    hist_data.append(
                                        {
                                            "time": int(idx.timestamp()) * 1000,
                                            "value": float(value),
                                        }
                                    )
                            result_indicators[f"macd_histogram_{signal}"] = hist_data

                    else:
                        logger.warning(f"Unknown indicator: {indicator}")

                except Exception as e:
                    logger.error(f"Error calculating indicator {indicator}: {e}")
                    continue

            # Prepare result
            result = {
                "success": True,
                "data": {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "indicators": result_indicators,
                    "data_points": len(df),
                    "last_update": datetime.now().isoformat(),
                },
                "message": f"Successfully calculated {len(result_indicators)} indicators",
                "timestamp": datetime.now().isoformat(),
            }

            # Cache the result
            self.cache[cache_key] = {"data": result, "timestamp": datetime.now()}

            logger.info(
                f"📊 Calculated {len(result_indicators)} indicators for {symbol} {timeframe}"
            )
            return result

        except Exception as e:
            logger.error(f"Error in calculate_indicators: {e}")
            return {
                "success": False,
                "data": {},
                "message": f"Error calculating indicators: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        return {
            "service": "indicator_service",
            "status": "healthy",
            "cache_size": len(self.cache),
            "timestamp": datetime.now().isoformat(),
        }

    def clear_cache(self):
        """Clear the indicator cache"""
        self.cache.clear()
        logger.info("🧹 Indicator cache cleared")


# Global instance
_indicator_service = None


def get_indicator_service() -> IndicatorService:
    """Get global indicator service instance"""
    global _indicator_service
    if _indicator_service is None:
        _indicator_service = IndicatorService()
    return _indicator_service
