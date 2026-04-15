#!/usr/bin/env python3
"""
Working Forex Strategy with Alpha Vantage
Handles API limitations and tests multiple pairs
"""

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import json
import time


class AlphaVantageDataProvider:
    """Data provider using Alpha Vantage API with better error handling"""

    def __init__(self, api_key="demo"):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"

    def get_forex_data(self, from_currency, to_currency, interval="daily"):
        """Get forex data from Alpha Vantage"""

        params = {
            "function": "FX_DAILY",
            "from_symbol": from_currency,
            "to_symbol": to_currency,
            "outputsize": "compact",
            "apikey": self.api_key,
        }

        try:
            print(f"  📡 Fetching {from_currency}/{to_currency} data...")
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()

            # Check for API limit messages
            if "Note" in data:
                print(f"  ⚠️  API Limit: {data['Note']}")
                return None

            if "Error Message" in data:
                print(f"  ❌ API Error: {data['Error Message']}")
                return None

            # Check if we have data
            time_series_key = "Time Series FX (Daily)"
            if time_series_key not in data:
                print(f"  ❌ No data available for {from_currency}/{to_currency}")
                return None

            # Parse the data
            df = pd.DataFrame.from_dict(data[time_series_key], orient="index")
            df.index = pd.to_datetime(df.index)

            # Rename columns
            df.columns = ["open", "high", "low", "close", "volume"]

            # Convert to numeric
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            print(f"  ✅ Retrieved {len(df)} data points")
            return df.sort_index()

        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return None


class StochasticRSIStrategy:
    """Stochastic RSI Strategy Implementation"""

    def __init__(self, data_provider):
        self.data_provider = data_provider

    def calculate_rsi(self, prices, period=14):
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_stochastic_rsi(self, prices, rsi_period=14, stoch_period=14):
        """Calculate Stochastic RSI"""
        rsi = self.calculate_rsi(prices, rsi_period)
        lowest_low = rsi.rolling(window=stoch_period).min()
        highest_high = rsi.rolling(window=stoch_period).max()
        k_percent = 100 * ((rsi - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=3).mean()
        return k_percent, d_percent

    def generate_signals(self, df, rsi_period=14, stoch_period=14):
        """Generate trading signals"""
        close_prices = df["close"]

        # Calculate indicators
        rsi = self.calculate_rsi(close_prices, rsi_period)
        k_percent, d_percent = self.calculate_stochastic_rsi(
            close_prices, rsi_period, stoch_period
        )

        # Generate signals
        signals = pd.DataFrame(index=df.index)
        signals["close"] = close_prices
        signals["rsi"] = rsi
        signals["stoch_k"] = k_percent
        signals["stoch_d"] = d_percent

        # Relaxed signal conditions for demo
        signals["buy_signal"] = (k_percent < 25) & (d_percent < 25) & (rsi < 35)

        signals["sell_signal"] = (k_percent > 75) & (d_percent > 75) & (rsi > 65)

        return signals

    def analyze_currency_pair(self, from_currency, to_currency):
        """Analyze a currency pair"""
        print(f"\n📊 Analyzing {from_currency}/{to_currency}")
        print("-" * 40)

        # Get data
        df = self.data_provider.get_forex_data(from_currency, to_currency)

        if df is None or df.empty:
            return None

        # Generate signals
        signals = self.generate_signals(df)

        # Count signals
        buy_signals = signals["buy_signal"].sum()
        sell_signals = signals["sell_signal"].sum()

        print(f"   📈 Buy signals: {buy_signals}")
        print(f"   📉 Sell signals: {sell_signals}")
        print(f"   📊 Total data points: {len(signals)}")

        # Show recent data
        recent = signals.tail(5)
        print(f"\n   📋 Recent data:")
        print(f"   Latest close: {recent['close'].iloc[-1]:.4f}")
        print(f"   Latest RSI: {recent['rsi'].iloc[-1]:.1f}")
        print(f"   Latest Stoch K: {recent['stoch_k'].iloc[-1]:.1f}")
        print(f"   Latest Stoch D: {recent['stoch_d'].iloc[-1]:.1f}")

        return signals


def test_multiple_pairs():
    """Test multiple currency pairs"""
    print("🚀 Testing Multiple Currency Pairs")
    print("=" * 50)

    # Initialize
    data_provider = AlphaVantageDataProvider()
    strategy = StochasticRSIStrategy(data_provider)

    # Test different currency pairs
    pairs_to_test = [
        ("EUR", "USD"),
        ("GBP", "USD"),
        ("USD", "JPY"),
        ("USD", "CAD"),
        ("AUD", "USD"),
    ]

    results = {}

    for from_curr, to_curr in pairs_to_test:
        signals = strategy.analyze_currency_pair(from_curr, to_curr)
        if signals is not None:
            results[f"{from_curr}/{to_curr}"] = signals

        # Wait between API calls to respect rate limits
        time.sleep(2)

    return results


def main():
    """Main function"""
    print("🎯 Forex Strategy Testing")
    print("=" * 50)
    print("Testing with Alpha Vantage demo key...")
    print("(Get free API key at: https://www.alphavantage.co/support/#api-key)")

    results = test_multiple_pairs()

    if results:
        print(f"\n✅ Successfully analyzed {len(results)} currency pairs")
        print("\n📊 Summary:")
        for pair, signals in results.items():
            buy_count = signals["buy_signal"].sum()
            sell_count = signals["sell_signal"].sum()
            print(f"   {pair}: {buy_count} buy, {sell_count} sell signals")
    else:
        print("\n❌ No data retrieved. Consider:")
        print("   1. Getting a free Alpha Vantage API key")
        print("   2. Waiting a few minutes (rate limits)")
        print("   3. Trying different currency pairs")


if __name__ == "__main__":
    main()
