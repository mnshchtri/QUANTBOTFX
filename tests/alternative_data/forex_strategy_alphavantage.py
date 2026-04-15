#!/usr/bin/env python3
"""
Forex Strategy with Alpha Vantage Data Source
Multi-timeframe Stochastic RSI Strategy
"""

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import json
import os


class AlphaVantageDataProvider:
    """Data provider using Alpha Vantage API"""

    def __init__(self, api_key=None):
        self.api_key = api_key or "demo"  # Use demo key if none provided
        self.base_url = "https://www.alphavantage.co/query"

    def get_forex_data(
        self, from_currency, to_currency, interval="daily", outputsize="compact"
    ):
        """Get forex data from Alpha Vantage"""

        params = {
            "function": "FX_DAILY" if interval == "daily" else "FX_INTRADAY",
            "from_symbol": from_currency,
            "to_symbol": to_currency,
            "outputsize": outputsize,
            "apikey": self.api_key,
        }

        if interval != "daily":
            params["interval"] = interval

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if "Error Message" in data:
                raise Exception(f"Alpha Vantage Error: {data['Error Message']}")

            if "Note" in data:
                print(f"⚠️  Alpha Vantage Note: {data['Note']}")
                return None

            # Parse the data
            time_series_key = (
                "Time Series FX (Daily)"
                if interval == "daily"
                else f"Time Series FX ({interval.upper()})"
            )

            if time_series_key not in data:
                print(f"❌ No data found for {from_currency}/{to_currency}")
                return None

            df = pd.DataFrame.from_dict(data[time_series_key], orient="index")
            df.index = pd.to_datetime(df.index)

            # Rename columns
            df.columns = ["open", "high", "low", "close", "volume"]

            # Convert to numeric
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            return df.sort_index()

        except Exception as e:
            print(f"❌ Error fetching data: {str(e)}")
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

    def calculate_stochastic(self, prices, period=14):
        """Calculate Stochastic Oscillator"""
        lowest_low = prices.rolling(window=period).min()
        highest_high = prices.rolling(window=period).max()
        k_percent = 100 * ((prices - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=3).mean()
        return k_percent, d_percent

    def calculate_stochastic_rsi(self, prices, rsi_period=14, stoch_period=14):
        """Calculate Stochastic RSI"""
        rsi = self.calculate_rsi(prices, rsi_period)
        k_percent, d_percent = self.calculate_stochastic(rsi, stoch_period)
        return k_percent, d_percent

    def generate_signals(self, df, rsi_period=14, stoch_period=14):
        """Generate trading signals"""
        close_prices = df["close"]

        # Calculate Stochastic RSI
        k_percent, d_percent = self.calculate_stochastic_rsi(
            close_prices, rsi_period, stoch_period
        )

        # Calculate regular RSI
        rsi = self.calculate_rsi(close_prices, rsi_period)

        # Generate signals
        signals = pd.DataFrame(index=df.index)
        signals["close"] = close_prices
        signals["rsi"] = rsi
        signals["stoch_k"] = k_percent
        signals["stoch_d"] = d_percent

        # Signal conditions
        signals["buy_signal"] = (k_percent < 20) & (d_percent < 20) & (rsi < 30)

        signals["sell_signal"] = (k_percent > 80) & (d_percent > 80) & (rsi > 70)

        return signals

    def analyze_timeframe(self, from_currency, to_currency, interval="daily"):
        """Analyze a specific timeframe"""
        print(f"\n📊 Analyzing {from_currency}/{to_currency} - {interval} timeframe")

        # Get data
        df = self.data_provider.get_forex_data(from_currency, to_currency, interval)

        if df is None or df.empty:
            print(f"❌ No data available for {from_currency}/{to_currency}")
            return None

        # Generate signals
        signals = self.generate_signals(df)

        # Count signals
        buy_signals = signals["buy_signal"].sum()
        sell_signals = signals["sell_signal"].sum()

        print(f"   📈 Buy signals: {buy_signals}")
        print(f"   📉 Sell signals: {sell_signals}")
        print(f"   📊 Total data points: {len(signals)}")

        return signals

    def create_chart(self, signals, title, save_path=None):
        """Create TradingView-style chart"""

        fig, (ax1, ax2, ax3) = plt.subplots(
            3, 1, figsize=(15, 12), gridspec_kw={"height_ratios": [3, 1, 1]}
        )

        # Price chart
        ax1.plot(signals.index, signals["close"], color="#1f77b4", linewidth=1)
        ax1.set_title(f"{title} - Price Action", fontsize=14, fontweight="bold")
        ax1.set_ylabel("Price")
        ax1.grid(True, alpha=0.3)

        # Highlight signals
        buy_points = signals[signals["buy_signal"]]
        sell_points = signals[signals["sell_signal"]]

        if not buy_points.empty:
            ax1.scatter(
                buy_points.index,
                buy_points["close"],
                color="green",
                s=100,
                marker="^",
                label="Buy Signal",
            )
        if not sell_points.empty:
            ax1.scatter(
                sell_points.index,
                sell_points["close"],
                color="red",
                s=100,
                marker="v",
                label="Sell Signal",
            )

        ax1.legend()

        # RSI
        ax2.plot(signals.index, signals["rsi"], color="#ff7f0e", linewidth=1)
        ax2.axhline(y=70, color="red", linestyle="--", alpha=0.7, label="Overbought")
        ax2.axhline(y=30, color="green", linestyle="--", alpha=0.7, label="Oversold")
        ax2.set_title("RSI", fontsize=12)
        ax2.set_ylabel("RSI")
        ax2.set_ylim(0, 100)
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        # Stochastic RSI
        ax3.plot(
            signals.index, signals["stoch_k"], color="#2ca02c", linewidth=1, label="%K"
        )
        ax3.plot(
            signals.index, signals["stoch_d"], color="#d62728", linewidth=1, label="%D"
        )
        ax3.axhline(y=80, color="red", linestyle="--", alpha=0.7, label="Overbought")
        ax3.axhline(y=20, color="green", linestyle="--", alpha=0.7, label="Oversold")
        ax3.set_title("Stochastic RSI", fontsize=12)
        ax3.set_ylabel("Stoch RSI")
        ax3.set_ylim(0, 100)
        ax3.grid(True, alpha=0.3)
        ax3.legend()

        # Format x-axis
        for ax in [ax1, ax2, ax3]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"📊 Chart saved to: {save_path}")

        plt.show()


def main():
    """Main function"""
    print("🚀 Forex Strategy with Alpha Vantage Data")
    print("=" * 50)

    # Initialize data provider
    data_provider = AlphaVantageDataProvider()
    strategy = StochasticRSIStrategy(data_provider)

    # Test with EUR/USD
    currency_pair = "EUR/USD"
    from_currency, to_currency = currency_pair.split("/")

    # Analyze daily timeframe
    signals = strategy.analyze_timeframe(from_currency, to_currency, "daily")

    if signals is not None:
        # Create chart
        chart_path = f"forex_strategy_{from_currency}{to_currency}_daily.png"
        strategy.create_chart(signals, f"{currency_pair} Daily Analysis", chart_path)

        # Show recent signals
        recent_signals = signals.tail(10)
        print(f"\n📋 Recent signals for {currency_pair}:")
        print(
            recent_signals[
                ["close", "rsi", "stoch_k", "stoch_d", "buy_signal", "sell_signal"]
            ].round(2)
        )


if __name__ == "__main__":
    main()
