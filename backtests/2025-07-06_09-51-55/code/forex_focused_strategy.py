"""
Forex-Focused Trading Strategy
Uses only OANDA forex data for trading
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ForexSignal:
    """Forex trading signal structure"""
    timestamp: datetime
    symbol: str
    signal: str  # BUY, SELL, HOLD
    confidence: float
    strategy: str
    features: Dict[str, float]
    risk_score: float
    price: float
    pip_value: float

class ForexFeatureEngine:
    """Forex-specific feature engineering"""
    
    def __init__(self):
        self.major_pairs = [
            'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 
            'AUDUSD', 'USDCAD', 'NZDUSD'
        ]
        self.minor_pairs = [
            'EURGBP', 'EURJPY', 'GBPJPY', 'CHFJPY',
            'EURCHF', 'AUDCAD', 'CADCHF'
        ]
        self.exotic_pairs = [
            'USDZAR', 'USDSGD', 'USDHKD', 'USDDKK'
        ]
    
    def extract_forex_features(self, data: pd.DataFrame) -> Dict[str, float]:
        """Extract forex-specific features"""
        if len(data) < 50:
            return {}
        
        close_prices = data['close'].values
        high_prices = data['high'].values
        low_prices = data['low'].values
        volumes = data['volume'].values if 'volume' in data.columns else np.ones(len(data))
        
        features = {}
        
        # Forex-specific price features
        features['returns_1d'] = (close_prices[-1] - close_prices[-2]) / close_prices[-2]
        features['returns_5d'] = (close_prices[-1] - close_prices[-5]) / close_prices[-5]
        features['returns_20d'] = (close_prices[-1] - close_prices[-20]) / close_prices[-20]
        
        # Volatility features
        features['volatility_20d'] = np.std(close_prices[-20:]) / np.mean(close_prices[-20:])
        features['atr_14'] = self._calculate_atr(high_prices, low_prices, close_prices, 14)
        
        # Technical indicators
        features['ema_12_ratio'] = close_prices[-1] / self._calculate_ema(close_prices, 12)
        features['ema_26_ratio'] = close_prices[-1] / self._calculate_ema(close_prices, 26)
        features['rsi_14'] = self._calculate_rsi(close_prices, 14)
        features['macd'] = self._calculate_macd(close_prices)
        
        # Forex-specific breakout features
        features.update(self._extract_forex_breakout_features(high_prices, low_prices, close_prices))
        
        # Currency strength features
        features.update(self._extract_currency_strength_features(close_prices))
        
        # Volume features (if available)
        if len(volumes) > 20:
            features['volume_ratio'] = volumes[-1] / np.mean(volumes[-20:])
            features['volume_momentum'] = (volumes[-1] - volumes[-2]) / volumes[-2]
        
        return features
    
    def _extract_forex_breakout_features(self, high_prices: np.ndarray, 
                                       low_prices: np.ndarray, 
                                       close_prices: np.ndarray) -> Dict[str, float]:
        """Extract forex-specific breakout features"""
        features = {}
        
        # Support and resistance levels
        resistance_20 = np.max(high_prices[-20:])
        support_20 = np.min(low_prices[-20:])
        
        # Breakout detection
        features['breakout_up'] = 1.0 if close_prices[-1] > resistance_20 else 0.0
        features['breakout_down'] = 1.0 if close_prices[-1] < support_20 else 0.0
        
        # Distance to levels
        features['resistance_distance'] = (resistance_20 - close_prices[-1]) / close_prices[-1]
        features['support_distance'] = (close_prices[-1] - support_20) / close_prices[-1]
        
        # Range analysis
        features['range_20d'] = (resistance_20 - support_20) / close_prices[-1]
        features['position_in_range'] = (close_prices[-1] - support_20) / (resistance_20 - support_20)
        
        # Pin bar detection
        features['pin_bar_up'] = self._detect_pin_bar_up(high_prices, low_prices, close_prices)
        features['pin_bar_down'] = self._detect_pin_bar_down(high_prices, low_prices, close_prices)
        
        return features
    
    def _extract_currency_strength_features(self, close_prices: np.ndarray) -> Dict[str, float]:
        """Extract currency strength features"""
        features = {}
        
        # Momentum indicators
        features['momentum_5d'] = (close_prices[-1] - close_prices[-5]) / close_prices[-5]
        features['momentum_10d'] = (close_prices[-1] - close_prices[-10]) / close_prices[-10]
        
        # Rate of change
        features['roc_5d'] = (close_prices[-1] / close_prices[-5] - 1) * 100
        features['roc_10d'] = (close_prices[-1] / close_prices[-10] - 1) * 100
        
        # Trend strength
        features['trend_strength'] = self._calculate_trend_strength(close_prices)
        
        return features
    
    def _calculate_atr(self, high_prices: np.ndarray, low_prices: np.ndarray, 
                      close_prices: np.ndarray, period: int) -> float:
        """Calculate Average True Range"""
        if len(high_prices) < period + 1:
            return 0.0
        
        true_ranges = []
        for i in range(1, len(high_prices)):
            high_low = high_prices[i] - low_prices[i]
            high_close = abs(high_prices[i] - close_prices[i-1])
            low_close = abs(low_prices[i] - close_prices[i-1])
            true_range = max(high_low, high_close, low_close)
            true_ranges.append(true_range)
        
        return np.mean(true_ranges[-period:])
    
    def _calculate_ema(self, prices: np.ndarray, period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return prices[-1]
        
        alpha = 2 / (period + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = alpha * price + (1 - alpha) * ema
        return ema
    
    def _calculate_rsi(self, prices: np.ndarray, period: int) -> float:
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
    
    def _calculate_macd(self, prices: np.ndarray) -> float:
        """Calculate MACD"""
        ema_12 = self._calculate_ema(prices, 12)
        ema_26 = self._calculate_ema(prices, 26)
        return ema_12 - ema_26
    
    def _detect_pin_bar_up(self, high_prices: np.ndarray, low_prices: np.ndarray, 
                          close_prices: np.ndarray) -> float:
        """Detect bullish pin bar pattern"""
        if len(high_prices) < 3:
            return 0.0
        
        # Check if current candle is a pin bar
        body_size = abs(close_prices[-1] - close_prices[-2])
        upper_shadow = high_prices[-1] - max(close_prices[-1], close_prices[-2])
        lower_shadow = min(close_prices[-1], close_prices[-2]) - low_prices[-1]
        
        # Pin bar criteria: small body, long lower shadow, short upper shadow
        if (body_size < (upper_shadow + lower_shadow) * 0.3 and 
            lower_shadow > body_size * 2 and 
            upper_shadow < body_size * 0.5):
            return 1.0
        
        return 0.0
    
    def _detect_pin_bar_down(self, high_prices: np.ndarray, low_prices: np.ndarray, 
                            close_prices: np.ndarray) -> float:
        """Detect bearish pin bar pattern"""
        if len(high_prices) < 3:
            return 0.0
        
        # Check if current candle is a pin bar
        body_size = abs(close_prices[-1] - close_prices[-2])
        upper_shadow = high_prices[-1] - max(close_prices[-1], close_prices[-2])
        lower_shadow = min(close_prices[-1], close_prices[-2]) - low_prices[-1]
        
        # Pin bar criteria: small body, long upper shadow, short lower shadow
        if (body_size < (upper_shadow + lower_shadow) * 0.3 and 
            upper_shadow > body_size * 2 and 
            lower_shadow < body_size * 0.5):
            return 1.0
        
        return 0.0
    
    def _calculate_trend_strength(self, prices: np.ndarray) -> float:
        """Calculate trend strength using linear regression"""
        if len(prices) < 20:
            return 0.0
        
        x = np.arange(len(prices[-20:]))
        y = prices[-20:]
        
        # Linear regression
        slope, intercept = np.polyfit(x, y, 1)
        
        # Calculate R-squared
        y_pred = slope * x + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        return r_squared

class ForexAISignalGenerator:
    """Forex-specific AI signal generator"""
    
    def __init__(self):
        self.feature_engine = ForexFeatureEngine()
        self.is_trained = True
    
    def generate_forex_signal(self, data: pd.DataFrame, symbol: str) -> ForexSignal:
        """Generate forex trading signal"""
        features = self.feature_engine.extract_forex_features(data)
        
        if not features:
            return ForexSignal(
                timestamp=datetime.now(),
                symbol=symbol,
                signal="HOLD",
                confidence=0.0,
                strategy="FOREX_AI",
                features=features,
                risk_score=0.5,
                price=data['close'].iloc[-1] if len(data) > 0 else 1.0,
                pip_value=self._calculate_pip_value(symbol, data['close'].iloc[-1] if len(data) > 0 else 1.0)
            )
        
        # Forex-specific signal generation
        score = self._calculate_forex_score(features, symbol)
        
        # Convert score to signal
        if score > 0.4:
            signal = "BUY"
            confidence = min(abs(score), 0.9)
        elif score < -0.4:
            signal = "SELL"
            confidence = min(abs(score), 0.9)
        else:
            signal = "HOLD"
            confidence = 0.0
        
        risk_score = self._calculate_forex_risk_score(features)
        
        return ForexSignal(
            timestamp=datetime.now(),
            symbol=symbol,
            signal=signal,
            confidence=confidence,
            strategy="FOREX_AI_BREAKOUT",
            features=features,
            risk_score=risk_score,
            price=data['close'].iloc[-1] if len(data) > 0 else 1.0,
            pip_value=self._calculate_pip_value(symbol, data['close'].iloc[-1] if len(data) > 0 else 1.0)
        )
    
    def _calculate_forex_score(self, features: Dict[str, float], symbol: str) -> float:
        """Calculate forex-specific signal score"""
        score = 0.0
        
        # Breakout rules
        if features.get('breakout_up', 0) > 0:
            score += 0.3
        if features.get('breakout_down', 0) > 0:
            score -= 0.3
        
        # Pin bar patterns
        if features.get('pin_bar_up', 0) > 0:
            score += 0.2
        if features.get('pin_bar_down', 0) > 0:
            score -= 0.2
        
        # RSI rules
        rsi = features.get('rsi_14', 50)
        if rsi < 30:
            score += 0.2
        elif rsi > 70:
            score -= 0.2
        
        # Trend strength
        trend_strength = features.get('trend_strength', 0)
        if trend_strength > 0.7:
            momentum = features.get('momentum_5d', 0)
            if momentum > 0:
                score += 0.1
            else:
                score -= 0.1
        
        # Currency-specific adjustments
        if 'JPY' in symbol:
            # JPY pairs are more volatile
            score *= 0.8
        elif 'GBP' in symbol:
            # GBP pairs have higher spreads
            score *= 0.9
        
        return score
    
    def _calculate_forex_risk_score(self, features: Dict[str, float]) -> float:
        """Calculate forex-specific risk score"""
        risk_factors = [
            features.get('volatility_20d', 0),
            features.get('atr_14', 0),
            features.get('range_20d', 0)
        ]
        
        risk_score = np.mean([abs(factor) for factor in risk_factors])
        return min(risk_score, 1.0)
    
    def _calculate_pip_value(self, symbol: str, price: float) -> float:
        """Calculate pip value for the currency pair"""
        # Standard pip values (simplified)
        pip_values = {
            'EURUSD': 0.0001,
            'GBPUSD': 0.0001,
            'USDJPY': 0.01,
            'USDCHF': 0.0001,
            'AUDUSD': 0.0001,
            'USDCAD': 0.0001,
            'NZDUSD': 0.0001,
            'EURGBP': 0.0001,
            'EURJPY': 0.01,
            'GBPJPY': 0.01
        }
        
        return pip_values.get(symbol, 0.0001)

class ForexRiskManager:
    """Forex-specific risk management"""
    
    def __init__(self, max_risk_per_trade: float = 0.02, max_daily_loss: float = 0.05):
        self.max_risk_per_trade = max_risk_per_trade
        self.max_daily_loss = max_daily_loss
        self.daily_pnl = 0.0
        self.last_reset_date = datetime.now().date()
    
    def calculate_forex_position_size(self, signal: ForexSignal, 
                                    account_balance: float, 
                                    stop_loss_pips: int = 50) -> int:
        """Calculate forex position size based on risk management"""
        
        # Reset daily P&L if it's a new day
        current_date = datetime.now().date()
        if current_date != self.last_reset_date:
            self.daily_pnl = 0.0
            self.last_reset_date = current_date
        
        # Check daily loss limit
        if self.daily_pnl < -account_balance * self.max_daily_loss:
            logger.warning("Daily loss limit reached")
            return 0
        
        # Calculate risk amount
        risk_amount = account_balance * self.max_risk_per_trade
        
        # Calculate pip value for stop loss
        stop_loss_amount = signal.pip_value * stop_loss_pips
        
        if stop_loss_amount == 0:
            return 0
        
        # Calculate position size
        position_size = risk_amount / stop_loss_amount
        
        # Apply confidence and risk adjustments
        confidence_multiplier = signal.confidence
        risk_multiplier = 1 - signal.risk_score
        
        final_position_size = position_size * confidence_multiplier * risk_multiplier
        
        # Convert to standard lot sizes (1000 units = 0.01 lot)
        units = int(final_position_size * 1000)
        
        # Ensure minimum position size
        if units < 1000:  # Minimum 0.01 lot
            units = 0
        
        return units
    
    def update_daily_pnl(self, pnl: float):
        """Update daily P&L"""
        self.daily_pnl += pnl

def main():
    """Demo forex strategy"""
    print("💱 Forex-Focused Trading Strategy")
    print("=" * 40)
    
    # Create components
    feature_engine = ForexFeatureEngine()
    ai_generator = ForexAISignalGenerator()
    risk_manager = ForexRiskManager()
    
    # Demo with sample data
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1min')
    sample_data = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.normal(1.1000, 0.0020, 100),
        'high': np.random.normal(1.1005, 0.0020, 100),
        'low': np.random.normal(1.0995, 0.0020, 100),
        'close': np.random.normal(1.1000, 0.0020, 100),
        'volume': np.random.randint(1000, 10000, 100)
    })
    
    # Generate signal
    signal = ai_generator.generate_forex_signal(sample_data, "EURUSD")
    
    print(f"Symbol: {signal.symbol}")
    print(f"Signal: {signal.signal}")
    print(f"Confidence: {signal.confidence:.2f}")
    print(f"Risk Score: {signal.risk_score:.2f}")
    print(f"Price: {signal.price:.4f}")
    print(f"Pip Value: {signal.pip_value:.5f}")
    
    # Calculate position size
    account_balance = 10000.0
    units = risk_manager.calculate_forex_position_size(signal, account_balance)
    
    print(f"Position Size: {units} units")
    print(f"Risk Amount: ${account_balance * 0.02:.2f}")

if __name__ == "__main__":
    main() 