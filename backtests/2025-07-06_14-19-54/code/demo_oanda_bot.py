#!/usr/bin/env python3
"""
Demo OANDA Trading Bot
Shows the bot functionality without requiring real API credentials
"""

import os
import time
import json
import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DemoOANDAConnector:
    """Demo OANDA connector that simulates API responses"""

    def __init__(self):
        self.base_price = 2000.0  # Gold base price
        self.price_variance = 50.0
        self.current_price = self.base_price

    def get_account_info(self):
        """Simulate account info"""
        return {
            "account": {
                "id": "demo_account_123",
                "name": "Demo Trading Account",
                "currency": "USD",
            }
        }

    def get_account_summary(self):
        """Simulate account summary"""
        return {"account": {"balance": "10000.00", "pl": "0.00", "marginRate": "0.05"}}

    def get_positions(self):
        """Simulate positions"""
        return []

    def get_candles(self, instrument, granularity="M5", count=100):
        """Generate simulated candle data"""
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=count * 5)

        timestamps = pd.date_range(start=start_time, end=end_time, periods=count)

        # Generate realistic price movements
        prices = []
        current_price = self.base_price

        for i in range(count):
            # Random walk with trend
            change = np.random.normal(0, 2) + np.sin(i * 0.1) * 5
            current_price += change

            # Ensure price stays reasonable
            current_price = max(current_price, self.base_price - self.price_variance)
            current_price = min(current_price, self.base_price + self.price_variance)

            # Generate OHLC
            open_price = current_price
            high_price = open_price + abs(np.random.normal(0, 5))
            low_price = open_price - abs(np.random.normal(0, 5))
            close_price = open_price + np.random.normal(0, 3)

            prices.append(
                {
                    "timestamp": timestamps[i],
                    "open": round(open_price, 2),
                    "high": round(max(high_price, open_price, close_price), 2),
                    "low": round(min(low_price, open_price, close_price), 2),
                    "close": round(close_price, 2),
                    "volume": np.random.randint(1000, 10000),
                    "symbol": instrument,
                }
            )

        self.current_price = close_price
        return pd.DataFrame(prices)


class DemoFeatureEngine:
    """Demo feature engine"""

    def extract_features(self, data):
        """Extract features from data"""
        if len(data) < 50:
            return {}

        close_prices = data["close"].values
        high_prices = data["high"].values
        low_prices = data["low"].values
        volumes = data["volume"].values

        features = {}

        # Price-based features
        features["returns_1d"] = (close_prices[-1] - close_prices[-2]) / close_prices[
            -2
        ]
        features["returns_5d"] = (close_prices[-1] - close_prices[-5]) / close_prices[
            -5
        ]
        features["volatility_20d"] = np.std(close_prices[-20:]) / np.mean(
            close_prices[-20:]
        )

        # Technical indicators
        features["ema_12_ratio"] = close_prices[-1] / self._calculate_ema(
            close_prices, 12
        )
        features["ema_26_ratio"] = close_prices[-1] / self._calculate_ema(
            close_prices, 26
        )
        features["rsi_14"] = self._calculate_rsi(close_prices, 14)

        # Breakout features
        resistance_20 = np.max(high_prices[-20:])
        support_20 = np.min(low_prices[-20:])

        features["breakout_up"] = 1.0 if close_prices[-1] > resistance_20 else 0.0
        features["breakout_down"] = 1.0 if close_prices[-1] < support_20 else 0.0
        features["resistance_distance"] = (
            resistance_20 - close_prices[-1]
        ) / close_prices[-1]
        features["support_distance"] = (close_prices[-1] - support_20) / close_prices[
            -1
        ]

        # Volume features
        if len(volumes) > 20:
            features["volume_ratio"] = volumes[-1] / np.mean(volumes[-20:])

        return features

    def _calculate_ema(self, prices, period):
        """Calculate EMA"""
        if len(prices) < period:
            return prices[-1]

        alpha = 2 / (period + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = alpha * price + (1 - alpha) * ema
        return ema

    def _calculate_rsi(self, prices, period):
        """Calculate RSI"""
        if len(prices) < period + 1:
            return 50.0

        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi


class DemoAISignalGenerator:
    """Demo AI signal generator"""

    def __init__(self):
        self.feature_engine = DemoFeatureEngine()
        self.is_trained = True

    def generate_signal(self, data):
        """Generate trading signal"""
        features = self.feature_engine.extract_features(data)

        if not features:
            return {
                "signal": "HOLD",
                "confidence": 0.0,
                "strategy": "AI_BREAKOUT",
                "features": features,
                "risk_score": 0.5,
                "price": data["close"].iloc[-1] if len(data) > 0 else 2000.0,
            }

        # Simple rule-based signal generation
        score = 0.0

        # Breakout rules
        if features.get("breakout_up", 0) > 0:
            score += 0.3
        if features.get("breakout_down", 0) > 0:
            score -= 0.3

        # RSI rules
        rsi = features.get("rsi_14", 50)
        if rsi < 30:
            score += 0.2
        elif rsi > 70:
            score -= 0.2

        # Volume rules
        if features.get("volume_ratio", 1) > 1.5:
            score += 0.1

        # Convert score to signal
        if score > 0.3:
            signal = "BUY"
            confidence = min(abs(score), 0.9)
        elif score < -0.3:
            signal = "SELL"
            confidence = min(abs(score), 0.9)
        else:
            signal = "HOLD"
            confidence = 0.0

        risk_score = min(abs(features.get("volatility_20d", 0)), 1.0)

        return {
            "signal": signal,
            "confidence": confidence,
            "strategy": "AI_BREAKOUT",
            "features": features,
            "risk_score": risk_score,
            "price": data["close"].iloc[-1] if len(data) > 0 else 2000.0,
        }


class DemoRiskManager:
    """Demo risk manager"""

    def calculate_position_size(self, signal, account_balance, current_price):
        """Calculate position size"""
        if signal["confidence"] < 0.3:
            return 0

        base_size = account_balance * 0.02  # 2% of account
        confidence_multiplier = signal["confidence"]
        risk_multiplier = 1 - signal["risk_score"]

        position_value = base_size * confidence_multiplier * risk_multiplier
        units = int(position_value / current_price)

        # Ensure minimum position size
        if units < 1000:
            units = 0

        return units


class DemoOANDATradingBot:
    """Demo OANDA trading bot"""

    def __init__(self):
        self.connector = DemoOANDAConnector()
        self.ai_generator = DemoAISignalGenerator()
        self.risk_manager = DemoRiskManager()
        self.running = False

        # Trading parameters
        self.instruments = ["XAU_USD"]
        self.granularity = "M5"
        self.update_interval = 30  # 30 seconds for demo

        # State tracking
        self.positions = {}
        self.trades = []

    def initialize(self):
        """Initialize the demo bot"""
        try:
            # Test connection
            account_info = self.connector.get_account_info()
            logger.info(f"Connected to demo account: {account_info['account']['name']}")

            # Get account summary
            summary = self.connector.get_account_summary()
            balance = float(summary["account"]["balance"])
            logger.info(f"Account balance: {balance}")

            logger.info("Demo trading bot initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize demo bot: {e}")
            return False

    def start(self):
        """Start the demo bot"""
        if not self.initialize():
            return

        self.running = True
        logger.info("Starting Demo OANDA trading bot...")
        logger.info("Press Ctrl+C to stop")

        try:
            while self.running:
                self._trading_loop()
                time.sleep(self.update_interval)

        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.stop()

    def _trading_loop(self):
        """Main trading loop"""
        try:
            for instrument in self.instruments:
                # Get market data
                candles = self.connector.get_candles(
                    instrument, self.granularity, count=100
                )

                if not candles.empty:
                    # Generate AI signal
                    signal = self.ai_generator.generate_signal(candles)

                    if signal["signal"] != "HOLD":
                        self._execute_signal(signal, instrument)

                    # Log current status
                    current_price = candles["close"].iloc[-1]
                    logger.info(f"Current {instrument} price: {current_price:.2f}")
                    logger.info(
                        f"Signal: {signal['signal']} (confidence: {signal['confidence']:.2f})"
                    )

        except Exception as e:
            logger.error(f"Error in trading loop: {e}")

    def _execute_signal(self, signal, instrument):
        """Execute trading signal"""
        try:
            # Get account balance
            summary = self.connector.get_account_summary()
            balance = float(summary["account"]["balance"])

            # Calculate position size
            units = self.risk_manager.calculate_position_size(
                signal, balance, signal["price"]
            )

            if units == 0:
                logger.info(f"No position taken for {instrument} (risk management)")
                return

            # Simulate trade execution
            trade = {
                "timestamp": datetime.now(),
                "instrument": instrument,
                "signal": signal["signal"],
                "units": units,
                "price": signal["price"],
                "confidence": signal["confidence"],
                "risk_score": signal["risk_score"],
            }

            self.trades.append(trade)

            logger.info(f"DEMO TRADE: {signal['signal']} {instrument}")
            logger.info(f"  Units: {units}")
            logger.info(f"  Price: {signal['price']:.2f}")
            logger.info(f"  Confidence: {signal['confidence']:.2f}")
            logger.info(f"  Risk Score: {signal['risk_score']:.2f}")

        except Exception as e:
            logger.error(f"Error executing signal: {e}")

    def stop(self):
        """Stop the demo bot"""
        self.running = False
        logger.info("Demo trading bot stopped")

        # Print summary
        if self.trades:
            logger.info(f"\n📊 Demo Trading Summary:")
            logger.info(f"Total trades: {len(self.trades)}")

            buy_trades = [t for t in self.trades if t["signal"] == "BUY"]
            sell_trades = [t for t in self.trades if t["signal"] == "SELL"]

            logger.info(f"Buy signals: {len(buy_trades)}")
            logger.info(f"Sell signals: {len(sell_trades)}")

            if self.trades:
                avg_confidence = np.mean([t["confidence"] for t in self.trades])
                avg_risk = np.mean([t["risk_score"] for t in self.trades])
                logger.info(f"Average confidence: {avg_confidence:.2f}")
                logger.info(f"Average risk score: {avg_risk:.2f}")


def main():
    """Main function"""
    print("🎭 Demo OANDA Trading Bot")
    print("=" * 40)
    print("This demo shows the bot functionality without real API calls")
    print("All trades are simulated for demonstration purposes")
    print("=" * 40)

    # Create and start demo bot
    bot = DemoOANDATradingBot()
    bot.start()


if __name__ == "__main__":
    main()
