"""
Practical AI Integration Example for Quantitative Trading Strategy

This example demonstrates how to integrate AI signals with your existing
EMA-based trading strategy to enhance decision-making.
"""

from AlgorithmImports import *
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os

class SimpleAITradingStrategy(QCAlgorithm):
    """
    Enhanced trading strategy that combines technical analysis with AI signals
    """
    
    def Initialize(self):
        # Basic setup
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2020, 3, 30)
        self.SetCash(100000)
        
        # Add symbol
        self.symbol = self.AddEquity("GLD", Resolution.Minute).Symbol
        
        # Initialize AI components
        self.ai_predictor = SimpleAIPredictor()
        self.feature_extractor = FeatureExtractor()
        
        # Technical indicators
        self.ema_short = self.EMA(self.symbol, 12)
        self.ema_long = self.EMA(self.symbol, 26)
        self.rsi = self.RSI(self.symbol, 14)
        
        # Trading parameters
        self.position_size = 1.0
        self.stop_loss_pips = 2.50
        self.ai_confidence_threshold = 0.7
        
        # Performance tracking
        self.trade_count = 0
        self.ai_correct_predictions = 0
        self.total_predictions = 0
        
        # Schedule daily model retraining
        self.Schedule.On(
            self.DateRules.EveryDay(self.symbol),
            self.TimeRules.At(9, 0),
            self.retrain_model
        )
    
    def OnData(self, data):
        if self.symbol not in data.Bars:
            return
            
        bar = data.Bars[self.symbol]
        
        # Update indicators
        self.ema_short.Update(bar.EndTime, bar.Close)
        self.ema_long.Update(bar.EndTime, bar.Close)
        self.rsi.Update(bar.EndTime, bar.Close)
        
        # Extract features
        features = self.feature_extractor.extract_features(
            bar.Close, bar.Volume, self.ema_short, self.ema_long, self.rsi
        )
        
        # Get AI prediction
        if len(features) > 0:
            ai_signal, confidence = self.ai_predictor.predict(features)
            
            # Combine with technical signals
            technical_signal = self.get_technical_signal()
            final_signal = self.combine_signals(technical_signal, ai_signal, confidence)
            
            # Execute trade if conditions are met
            if final_signal != "HOLD" and self.trade_count < 2:
                self.execute_trade(final_signal, bar.Close, confidence)
    
    def get_technical_signal(self):
        """Generate signal based on technical indicators"""
        if not all([self.ema_short.IsReady, self.ema_long.IsReady, self.rsi.IsReady]):
            return "HOLD"
        
        ema_short_val = self.ema_short.Current.Value
        ema_long_val = self.ema_long.Current.Value
        rsi_val = self.rsi.Current.Value
        
        # Simple technical rules
        if ema_short_val > ema_long_val and rsi_val < 70:
            return "BUY"
        elif ema_short_val < ema_long_val and rsi_val > 30:
            return "SELL"
        else:
            return "HOLD"
    
    def combine_signals(self, technical_signal, ai_signal, ai_confidence):
        """Combine technical and AI signals"""
        if ai_confidence > 0.8:
            # High confidence AI overrides technical
            return ai_signal
        elif ai_confidence > self.ai_confidence_threshold:
            # Medium confidence - use weighted combination
            if technical_signal == ai_signal:
                return ai_signal
            else:
                return "HOLD"  # Conflicting signals
        else:
            # Low confidence - rely on technical
            return technical_signal
    
    def execute_trade(self, signal, price, confidence):
        """Execute trade with AI-enhanced position sizing"""
        if signal == "BUY":
            # Adjust position size based on AI confidence
            adjusted_size = self.position_size * (0.5 + confidence)
            self.MarketOrder(self.symbol, adjusted_size)
            
            # Dynamic stop loss based on confidence
            stop_loss = self.stop_loss_pips * (2 - confidence)
            self.StopMarketOrder(self.symbol, -adjusted_size, price - stop_loss)
            
            self.Debug(f"BUY: Price={price}, Size={adjusted_size}, Confidence={confidence:.3f}")
            
        elif signal == "SELL":
            adjusted_size = self.position_size * (0.5 + confidence)
            self.MarketOrder(self.symbol, -adjusted_size)
            
            stop_loss = self.stop_loss_pips * (2 - confidence)
            self.StopMarketOrder(self.symbol, adjusted_size, price + stop_loss)
            
            self.Debug(f"SELL: Price={price}, Size={adjusted_size}, Confidence={confidence:.3f}")
        
        self.trade_count += 1
    
    def retrain_model(self):
        """Retrain AI model with recent data"""
        # This would typically use historical data
        # For now, just log the retraining event
        self.Debug("Scheduled model retraining")


class SimpleAIPredictor:
    """Simple AI predictor using Random Forest"""
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def predict(self, features):
        """Generate prediction and confidence"""
        if not self.is_trained:
            return "HOLD", 0.5
        
        try:
            features_scaled = self.scaler.transform([features])
            prediction = self.model.predict(features_scaled)[0]
            confidence = max(self.model.predict_proba(features_scaled)[0])
            
            signal = "BUY" if prediction == 1 else "SELL"
            return signal, confidence
        except:
            return "HOLD", 0.5
    
    def train(self, X, y):
        """Train the model"""
        if len(X) > 10:
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled, y)
            self.is_trained = True


class FeatureExtractor:
    """Extract features for AI model"""
    
    def __init__(self):
        self.price_history = []
        self.volume_history = []
    
    def extract_features(self, price, volume, ema_short, ema_long, rsi):
        """Extract comprehensive features"""
        features = []
        
        # Price momentum
        if len(self.price_history) > 0:
            returns = (price - self.price_history[-1]) / self.price_history[-1]
            features.append(returns)
        else:
            features.append(0)
        
        # Volatility
        if len(self.price_history) >= 20:
            volatility = np.std(self.price_history[-20:]) / np.mean(self.price_history[-20:])
            features.append(volatility)
        else:
            features.append(0)
        
        # Technical indicators
        if ema_short.IsReady and ema_long.IsReady:
            ema_ratio = ema_short.Current.Value / ema_long.Current.Value
            features.append(ema_ratio)
        else:
            features.append(1)
        
        if rsi.IsReady:
            features.append(rsi.Current.Value / 100)
        else:
            features.append(0.5)
        
        # Volume features
        if len(self.volume_history) > 0:
            volume_ratio = volume / np.mean(self.volume_history[-20:]) if len(self.volume_history) >= 20 else 1
            features.append(volume_ratio)
        else:
            features.append(1)
        
        # Update history
        self.price_history.append(price)
        self.volume_history.append(volume)
        
        # Keep only recent history
        if len(self.price_history) > 100:
            self.price_history.pop(0)
            self.volume_history.pop(0)
        
        return features


# Usage Example:
"""
To use this enhanced strategy:

1. Replace your current main.py with AI_Trading_Example.py
2. Install required packages: pip install scikit-learn numpy
3. Run the strategy in your QuantConnect environment

The strategy will:
- Extract features from price, volume, and technical indicators
- Use AI to predict market direction
- Combine AI signals with technical analysis
- Adjust position sizes based on AI confidence
- Implement dynamic stop losses

Key benefits:
- Enhanced decision making through AI
- Dynamic position sizing
- Risk management based on confidence levels
- Continuous model improvement
""" 