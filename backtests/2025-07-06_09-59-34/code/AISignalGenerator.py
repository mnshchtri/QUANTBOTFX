from AlgorithmImports import *
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os


class AISignalGenerator:
    def __init__(self, algorithm, symbol, lookback_period=50):
        """
        AI-powered signal generator that enhances existing technical indicators
        """
        self.algorithm = algorithm
        self.symbol = symbol
        self.lookback_period = lookback_period

        # Feature storage
        self.price_history = []
        self.volume_history = []
        self.feature_history = []
        self.signal_history = []

        # ML model components
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False

        # Technical indicators for features
        self.ema_short = algorithm.ema(symbol, 12)
        self.ema_long = algorithm.ema(symbol, 26)
        self.rsi = algorithm.rsi(symbol, 14)
        self.macd = algorithm.macd(symbol, 12, 26, 9)

    def extract_features(self, current_price, current_volume):
        """
        Extract comprehensive features for ML model
        """
        features = []

        # Price-based features
        if len(self.price_history) > 0:
            returns = (current_price - self.price_history[-1]) / self.price_history[-1]
            features.append(returns)

            # Volatility (rolling standard deviation)
            if len(self.price_history) >= 20:
                recent_prices = self.price_history[-20:]
                volatility = np.std(recent_prices) / np.mean(recent_prices)
                features.append(volatility)
            else:
                features.append(0)
        else:
            features.extend([0, 0])

        # Technical indicator features
        if self.ema_short.IsReady:
            ema_ratio = current_price / self.ema_short.Current.Value
            features.append(ema_ratio)
        else:
            features.append(1)

        if self.ema_long.IsReady:
            ema_trend = self.ema_short.Current.Value / self.ema_long.Current.Value
            features.append(ema_trend)
        else:
            features.append(1)

        if self.rsi.IsReady:
            features.append(self.rsi.Current.Value / 100)  # Normalize to 0-1
        else:
            features.append(0.5)

        if self.macd.IsReady:
            features.append(self.macd.Current.Value)
            features.append(self.macd.Signal.Current.Value)
        else:
            features.extend([0, 0])

        # Volume features
        if len(self.volume_history) > 0:
            volume_ratio = (
                current_volume / np.mean(self.volume_history[-20:])
                if len(self.volume_history) >= 20
                else 1
            )
            features.append(volume_ratio)
        else:
            features.append(1)

        # Time-based features
        current_time = self.algorithm.Time
        hour = current_time.hour
        minute = current_time.minute

        # Market session features
        features.append(1 if 9 <= hour <= 16 else 0)  # Regular market hours
        features.append(1 if hour in [9, 10, 15, 16] else 0)  # High activity hours

        return np.array(features)

    def update(self, time, price, volume=0):
        """
        Update indicators and store data
        """
        self.ema_short.Update(time, price)
        self.ema_long.Update(time, price)
        self.rsi.Update(time, price)
        self.macd.Update(time, price)

        # Store historical data
        self.price_history.append(price)
        self.volume_history.append(volume)

        # Keep only recent history
        if len(self.price_history) > self.lookback_period:
            self.price_history.pop(0)
            self.volume_history.pop(0)

    def generate_signal(self, current_price, current_volume=0):
        """
        Generate AI-enhanced trading signal
        """
        try:
            if not self.is_trained or len(self.price_history) < 20:
                return "NEUTRAL", 0.5

            # Extract features
            features = self.extract_features(current_price, current_volume)

            if len(features) == 0:
                return "NEUTRAL", 0.5

            features_scaled = self.scaler.transform(features.reshape(1, -1))

            # Get model prediction
            prediction = self.model.predict(features_scaled)[0]
            probability = self.model.predict_proba(features_scaled)[0]

            # Convert to signal
            if prediction == 1:
                signal = "BUY"
                confidence = probability[1]
            else:
                signal = "SELL"
                confidence = probability[0]

            return signal, confidence

        except Exception as e:
            self.algorithm.Debug(f"AI signal generation error: {str(e)}")
            return "NEUTRAL", 0.5

    def train_model(self, historical_data):
        """
        Train the ML model with historical data
        """
        X = []  # Features
        y = []  # Labels (1 for profitable trade, 0 for loss)

        for i in range(20, len(historical_data) - 1):
            # Extract features for this point
            features = self.extract_features(
                historical_data[i]["price"], historical_data[i].get("volume", 0)
            )

            # Create label based on future price movement
            future_return = (
                historical_data[i + 1]["price"] - historical_data[i]["price"]
            ) / historical_data[i]["price"]
            label = 1 if future_return > 0.001 else 0  # 0.1% threshold

            X.append(features)
            y.append(label)

        if len(X) > 10:  # Need minimum data
            X = np.array(X)
            y = np.array(y)

            # Scale features
            X_scaled = self.scaler.fit_transform(X)

            # Train model
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_scaled, y)
            self.is_trained = True

            self.algorithm.Debug(f"AI Model trained with {len(X)} samples")

    def save_model(self, filepath):
        """
        Save trained model to file
        """
        if self.is_trained:
            model_data = {
                "model": self.model,
                "scaler": self.scaler,
                "feature_names": [
                    "returns",
                    "volatility",
                    "ema_ratio",
                    "ema_trend",
                    "rsi",
                    "macd",
                    "macd_signal",
                    "volume_ratio",
                    "market_hours",
                    "high_activity_hours",
                ],
            }
            joblib.dump(model_data, filepath)
            self.algorithm.Debug(f"Model saved to {filepath}")

    def load_model(self, filepath):
        """
        Load trained model from file
        """
        if os.path.exists(filepath):
            model_data = joblib.load(filepath)
            self.model = model_data["model"]
            self.scaler = model_data["scaler"]
            self.is_trained = True
            self.algorithm.Debug(f"Model loaded from {filepath}")
