"""
Data router for QuantBotForex API
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime, timedelta
from models.trading import TradingDataResponse, MarketInfo
from data_loader import DataLoader
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import os
import logging
import yaml

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter()


def _load_oanda_settings():
    """Load OANDA settings from config.yaml with env fallback."""
    try:
        config_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")
        )
        with open(config_path, "r") as f:
            cfg = yaml.safe_load(f) or {}
        oanda_cfg = cfg.get("trading", {}).get("oanda", {})
        api_key = oanda_cfg.get("api_key") or os.getenv("OANDA_API_KEY")
        account_id = oanda_cfg.get("account_id") or os.getenv("OANDA_ACCOUNT_ID")
        base_url = (
            oanda_cfg.get("base_url")
            or os.getenv("OANDA_BASE_URL")
            or "https://api-fxpractice.oanda.com"
        )
        return api_key, account_id, base_url
    except Exception:
        # Fallback to env only
        return (
            os.getenv("OANDA_API_KEY"),
            os.getenv("OANDA_ACCOUNT_ID"),
            os.getenv("OANDA_BASE_URL") or "https://api-fxpractice.oanda.com",
        )


# Initialize data loader
data_loader = DataLoader()

# Load OANDA settings (hardcoded via config.yaml if present)
OANDA_API_KEY, OANDA_ACCOUNT_ID, OANDA_BASE_URL = _load_oanda_settings()


def fetch_oanda_data(
    instrument: str, granularity: str, count: int = 500
) -> pd.DataFrame:
    """Fetch data directly from OANDA API - NO FALLBACK DATA"""
    if not OANDA_API_KEY:
        logger.error("OANDA API key not configured. Cannot fetch data.")
        raise ValueError(
            "OANDA API key not configured. Please set OANDA_API_KEY environment variable."
        )

    headers = {
        "Authorization": f"Bearer {OANDA_API_KEY}",
        "Content-Type": "application/json",
    }

    url = f"{OANDA_BASE_URL}/v3/instruments/{instrument}/candles"
    params = {
        "count": min(count, 5000),
        "granularity": granularity,
        "price": "M",  # Mid prices
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)

        if response.status_code == 200:
            data = response.json()
            candles = data.get("candles", [])

            if not candles:
                raise HTTPException(
                    status_code=404, detail=f"No data available for {instrument}"
                )

            # Convert to DataFrame
            rows = []
            for candle in candles:
                if candle.get("complete"):
                    mid = candle["mid"]
                    rows.append(
                        {
                            "time": pd.to_datetime(candle["time"]),
                            "open": float(mid["o"]),
                            "high": float(mid["h"]),
                            "low": float(mid["l"]),
                            "close": float(mid["c"]),
                            "volume": int(candle.get("volume", 0)),
                        }
                    )

            if not rows:
                raise HTTPException(
                    status_code=404,
                    detail=f"No complete candles available for {instrument}",
                )

            df = pd.DataFrame(rows)
            df.set_index("time", inplace=True)
            # Handle timezone conversion safely
            # Ensure datetime index is timezone-aware in UTC
            if isinstance(df.index, pd.DatetimeIndex):
                try:
                    if df.index.tz is None:
                        df.index = df.index.tz_localize("UTC")
                    else:
                        df.index = df.index.tz_convert("UTC")
                except Exception:
                    # Best-effort fallback
                    try:
                        df.index = pd.to_datetime(df.index, utc=True)
                    except Exception:
                        pass

            return df
        else:
            # OANDA API error - no fallback
            error_msg = f"OANDA API error ({response.status_code}): {response.text}"
            logger.error(error_msg)
            raise HTTPException(status_code=response.status_code, detail=error_msg)

    except HTTPException:
        # Re-raise HTTPException as-is
        raise
    except Exception as e:
        # Any other error - no fallback
        error_msg = f"Error fetching from OANDA API: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/trading-data/{instrument}/{timeframe}")
def get_trading_data(instrument: str, timeframe: str):
    """Get trading data for a specific instrument and timeframe (NO LIMITS)"""
    try:
        # Check if OANDA API key is configured
        if not OANDA_API_KEY or OANDA_API_KEY == "practice-API-KEY-HERE":
            raise HTTPException(
                status_code=401,
                detail="OANDA API key not configured. Please set OANDA_API_KEY in config.yaml",
            )

        logger.info(f"📊 Fetching trading data for {instrument} {timeframe}")
        logger.info(f"📊 Fetching ALL available data (no limits)")

        # Fetch data from OANDA with NO LIMITS
        df = fetch_oanda_data(instrument, timeframe, count=10000)  # Maximum possible

        if df is None or df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No data available for {instrument} {timeframe}",
            )

        logger.info(
            f"✅ Successfully fetched {len(df)} candles for {instrument} {timeframe}"
        )
        logger.info(f"📊 Data range: {df.index[0]} to {df.index[-1]}")

        # Return success response with metadata only (avoid DataFrame serialization)
        return {
            "success": True,
            "message": f"Data retrieved successfully for {instrument} {timeframe}",
            "metadata": {
                "instrument": instrument,
                "timeframe": timeframe,
                "total_candles": int(len(df)),
                "start_date": str(df.index[0]) if not df.empty else None,
                "end_date": str(df.index[-1]) if not df.empty else None,
                "data_source": "OANDA",
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error processing trading data: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/market-info")
async def get_market_info(symbol: str = Query("GBP_JPY")):
    """Get market information for symbol"""
    try:
        # Get recent data to calculate market info
        df = fetch_oanda_data(symbol, "M15", 200)  # Get ~2 days of M15 data

        # Get current and previous data
        current = df.iloc[-1]
        previous = df.iloc[-2] if len(df) > 1 else current

        # Calculate change
        current_price = float(current["close"])
        previous_price = float(previous["close"])
        change = current_price - previous_price
        change_percent = (change / previous_price) * 100 if previous_price != 0 else 0

        # Get daily high/low from recent data
        recent_data = df.tail(96)  # Last 24 hours of M15 data
        daily_high = float(recent_data["high"].max())
        daily_low = float(recent_data["low"].min())

        market_info = {
            "symbol": symbol,
            "current_price": current_price,
            "change": round(change, 5),
            "change_percent": round(change_percent, 2),
            "high": daily_high,
            "low": daily_low,
            "volume": float(recent_data["volume"].sum()),
            "spread": 0.0005,  # Default spread for now
        }

        return market_info

    except HTTPException:
        # Re-raise HTTPException as-is to preserve status code and detail
        raise
    except Exception as e:
        # Handle other exceptions
        error_msg = f"Error processing market info: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/candlestick-data")
async def get_candlestick_data(
    symbol: str = Query("GBP_JPY"),
    timeframe: str = Query("M15"),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get candlestick data"""
    try:
        # Get real market data directly from OANDA API
        df = fetch_oanda_data(symbol, timeframe, limit)

        # Convert DataFrame to list format
        data = []
        df_limited = df.tail(limit)  # Get the most recent data

        for index, row in df_limited.iterrows():
            # Normalize timestamp safely
            try:
                ts_ms = int(pd.Timestamp(index).to_pydatetime().timestamp() * 1000)
            except Exception:
                ts_ms = int(datetime.now().timestamp() * 1000)

            volume_val = 0
            try:
                vol = row["volume"] if "volume" in row else 0
                if pd.notna(vol):
                    volume_val = int(vol)
            except Exception:
                volume_val = 0

            candle = {
                "timestamp": ts_ms,
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": volume_val,
            }
            data.append(candle)

        return {
            "success": True,
            "data": data,
            "symbol": symbol,
            "timeframe": timeframe,
            "source": "OANDA API Direct",
            "count": len(data),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/candles/{instrument}/{timeframe}")
def get_candles_data(
    instrument: str, timeframe: str, limit: int = Query(1000, ge=1, le=5000)
):
    """Get candlestick data for trading dashboard (returns actual candle data)"""
    try:
        # Check if OANDA API key is configured
        if not OANDA_API_KEY or OANDA_API_KEY == "practice-API-KEY-HERE":
            raise HTTPException(
                status_code=401,
                detail="OANDA API key not configured. Please set OANDA_API_KEY in config.yaml",
            )

        logger.info(f"📊 Fetching candles for {instrument} {timeframe} (limit: {limit})")

        # Fetch data from OANDA
        df = fetch_oanda_data(instrument, timeframe, count=limit)

        if df is None or df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No data available for {instrument} {timeframe}",
            )

        # Convert DataFrame to list format for frontend
        data = []
        for index, row in df.iterrows():
            # Convert timestamp to milliseconds for frontend
            ts_ms = int(pd.Timestamp(index).timestamp() * 1000)

            candle = {
                "timestamp": ts_ms,
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": int(row["volume"]),
            }
            data.append(candle)

        logger.info(
            f"✅ Successfully returned {len(data)} candles for {instrument} {timeframe}"
        )

        return {
            "success": True,
            "data": data,
            "metadata": {
                "instrument": instrument,
                "timeframe": timeframe,
                "total_candles": len(data),
                "start_date": str(df.index[0]) if not df.empty else None,
                "end_date": str(df.index[-1]) if not df.empty else None,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error processing candles data: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
