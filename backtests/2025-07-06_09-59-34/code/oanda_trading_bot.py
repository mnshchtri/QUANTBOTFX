"""
Professional OANDA Trading Bot
Live trading implementation with AI-enhanced breakout strategy
"""

import os
import time
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import requests
from dataclasses import dataclass
import threading
from queue import Queue
import signal
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('oanda_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class OANDAConfig:
    """OANDA API configuration"""
    account_id: str
    api_key: str
    environment: str = "practice"  # "practice" or "live"
    base_url: str = "https://api-fxpractice.oanda.com"  # Change for live
    
    def __post_init__(self):
        if self.environment == "live":
            self.base_url = "https://api-fxtrade.oanda.com"

@dataclass
class TradingSignal:
    """Trading signal structure"""
    timestamp: datetime
    symbol: str
    signal: str  # BUY, SELL, HOLD
    confidence: float
    strategy: str
    features: Dict[str, float]
    risk_score: float
    price: float

class OANDAConnector:
    """Professional OANDA API connector"""
    
    def __init__(self, config: OANDAConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {config.api_key}',
            'Content-Type': 'application/json'
        })
        self.base_url = config.base_url
        
    def get_account_info(self) -> Dict:
        """Get account information"""
        url = f"{self.base_url}/v3/accounts/{self.config.account_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_account_summary(self) -> Dict:
        """Get account summary"""
        url = f"{self.base_url}/v3/accounts/{self.config.account_id}/summary"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_positions(self) -> List[Dict]:
        """Get current positions"""
        url = f"{self.base_url}/v3/accounts/{self.config.account_id}/positions"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()['positions']
    
    def get_candles(self, instrument: str, granularity: str = "M5", 
                    count: int = 500) -> pd.DataFrame:
        """Get historical candles"""
        url = f"{self.base_url}/v3/instruments/{instrument}/candles"
        params = {
            'granularity': granularity,
            'count': count
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()['candles']
        df = pd.DataFrame(data)
        
        # Process candle data
        processed_data = []
        for candle in data:
            processed_data.append({
                'timestamp': pd.to_datetime(candle['time']),
                'open': float(candle['mid']['o']),
                'high': float(candle['mid']['h']),
                'low': float(candle['mid']['l']),
                'close': float(candle['mid']['c']),
                'volume': int(candle['volume']) if 'volume' in candle else 0
            })
        
        return pd.DataFrame(processed_data)
    
    def place_market_order(self, instrument: str, units: int, side: str) -> Dict:
        """Place a market order"""
        url = f"{self.base_url}/v3/accounts/{self.config.account_id}/orders"
        
        data = {
            "order": {
                "type": "MARKET",
                "instrument": instrument,
                "units": str(units),
                "timeInForce": "FOK",
                "positionFill": "DEFAULT"
            }
        }
        
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()
    
    def close_position(self, instrument: str, units: int = None) -> Dict:
        """Close a position"""
        url = f"{self.base_url}/v3/accounts/{self.config.account_id}/positions/{instrument}/close"
        
        data = {}
        if units:
            data["longUnits"] = str(units) if units > 0 else str(abs(units))
        
        response = self.session.put(url, json=data)
        response.raise_for_status()
        return response.json()

class FeatureEngine:
    """Professional feature engineering for trading signals"""
    
    def __init__(self):
        self.feature_groups = {
            'technical': self._extract_technical_features,
            'breakout': self._extract_breakout_features,
            'momentum': self._extract_momentum_features
        }
    
    def extract_features(self, data: pd.DataFrame) -> Dict[str, float]:
        """Extract comprehensive features"""
        features = {}
        
        for group_name, extractor in self.feature_groups.items():
            try:
                group_features = extractor(data)
                features.update(group_features)
            except Exception as e:
                logger.warning(f"Failed to extract {group_name} features: {e}")
        
        return features
    
    def _extract_technical_features(self, data: pd.DataFrame) -> Dict[str, float]:
        """Extract technical indicators"""
        if len(data) < 50:
            return {}
        
        close_prices = data['close'].values
        high_prices = data['high'].values
        low_prices = data['low'].values
        volumes = data['volume'].values
        
        features = {}
        
        # Price-based features
        features['returns_1d'] = (close_prices[-1] - close_prices[-2]) / close_prices[-2]
        features['returns_5d'] = (close_prices[-1] - close_prices[-5]) / close_prices[-5]
        features['volatility_20d'] = np.std(close_prices[-20:]) / np.mean(close_prices[-20:])
        
        # Technical indicators
        features['ema_12_ratio'] = close_prices[-1] / self._calculate_ema(close_prices, 12)
        features['ema_26_ratio'] = close_prices[-1] / self._calculate_ema(close_prices, 26)
        features['rsi_14'] = self._calculate_rsi(close_prices, 14)
        features['macd'] = self._calculate_macd(close_prices)
        
        # Volume features
        if len(volumes) > 20:
            features['volume_ratio'] = volumes[-1] / np.mean(volumes[-20:])
            features['volume_momentum'] = (volumes[-1] - volumes[-2]) / volumes[-2]
        
        return features
    
    def _extract_breakout_features(self, data: pd.DataFrame) -> Dict[str, float]:
        """Extract breakout-specific features"""
        if len(data) < 20:
            return {}
        
        close_prices = data['close'].values
        high_prices = data['high'].values
        low_prices = data['low'].values
        
        features = {}
        
        # Breakout detection
        current_high = high_prices[-1]
        current_low = low_prices[-1]
        
        # Resistance and support levels
        resistance_20 = np.max(high_prices[-20:])
        support_20 = np.min(low_prices[-20:])
        
        features['breakout_up'] = 1.0 if current_high > resistance_20 else 0.0
        features['breakout_down'] = 1.0 if current_low < support_20 else 0.0
        features['resistance_distance'] = (resistance_20 - close_prices[-1]) / close_prices[-1]
        features['support_distance'] = (close_prices[-1] - support_20) / close_prices[-1]
        
        # Range analysis
        features['range_20d'] = (resistance_20 - support_20) / close_prices[-1]
        features['position_in_range'] = (close_prices[-1] - support_20) / (resistance_20 - support_20)
        
        return features
    
    def _extract_momentum_features(self, data: pd.DataFrame) -> Dict[str, float]:
        """Extract momentum features"""
        if len(data) < 10:
            return {}
        
        close_prices = data['close'].values
        
        features = {}
        
        # Momentum indicators
        features['momentum_5d'] = (close_prices[-1] - close_prices[-5]) / close_prices[-5]
        features['momentum_10d'] = (close_prices[-1] - close_prices[-10]) / close_prices[-10]
        
        # Rate of change
        features['roc_5d'] = (close_prices[-1] / close_prices[-5] - 1) * 100
        features['roc_10d'] = (close_prices[-1] / close_prices[-10] - 1) * 100
        
        return features
    
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

class AISignalGenerator:
    """AI-powered signal generation"""
    
    def __init__(self):
        self.feature_engine = FeatureEngine()
        self.models = {}
        self.is_trained = False
    
    def train_model(self, historical_data: pd.DataFrame):
        """Train the AI model with historical data"""
        try:
            # Extract features
            features_list = []
            signals_list = []
            
            for i in range(50, len(historical_data) - 1):
                data_window = historical_data.iloc[:i+1]
                features = self.feature_engine.extract_features(data_window)
                
                if features:
                    # Generate signal based on future price movement
                    current_price = data_window['close'].iloc[-1]
                    future_price = historical_data['close'].iloc[i+1]
                    
                    if future_price > current_price * 1.001:  # 0.1% threshold
                        signal = "BUY"
                    elif future_price < current_price * 0.999:
                        signal = "SELL"
                    else:
                        signal = "HOLD"
                    
                    features_list.append(features)
                    signals_list.append(signal)
            
            if len(features_list) > 100:
                # Simple rule-based model for now
                self.models['rule_based'] = self._create_rule_based_model()
                self.is_trained = True
                logger.info("AI model trained successfully")
            else:
                logger.warning("Insufficient data for training")
                
        except Exception as e:
            logger.error(f"Error training AI model: {e}")
    
    def _create_rule_based_model(self):
        """Create a rule-based model"""
        def predict(features):
            score = 0.0
            
            # Breakout rules
            if features.get('breakout_up', 0) > 0:
                score += 0.3
            if features.get('breakout_down', 0) > 0:
                score -= 0.3
            
            # Momentum rules
            if features.get('momentum_5d', 0) > 0.01:
                score += 0.2
            elif features.get('momentum_5d', 0) < -0.01:
                score -= 0.2
            
            # RSI rules
            rsi = features.get('rsi_14', 50)
            if rsi < 30:
                score += 0.2
            elif rsi > 70:
                score -= 0.2
            
            # Volume rules
            if features.get('volume_ratio', 1) > 1.5:
                score += 0.1
            
            return score
        
        return predict
    
    def generate_signal(self, data: pd.DataFrame) -> TradingSignal:
        """Generate trading signal"""
        if not self.is_trained:
            return TradingSignal(
                timestamp=datetime.now(),
                symbol=data['symbol'].iloc[-1] if 'symbol' in data.columns else "XAU_USD",
                signal="HOLD",
                confidence=0.0,
                strategy="AI",
                features={},
                risk_score=0.5,
                price=data['close'].iloc[-1]
            )
        
        features = self.feature_engine.extract_features(data)
        
        if not features:
            return TradingSignal(
                timestamp=datetime.now(),
                symbol=data['symbol'].iloc[-1] if 'symbol' in data.columns else "XAU_USD",
                signal="HOLD",
                confidence=0.0,
                strategy="AI",
                features=features,
                risk_score=0.5,
                price=data['close'].iloc[-1]
            )
        
        # Get prediction from rule-based model
        score = self.models['rule_based'](features)
        
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
        
        risk_score = self._calculate_risk_score(features)
        
        return TradingSignal(
            timestamp=datetime.now(),
            symbol=data['symbol'].iloc[-1] if 'symbol' in data.columns else "XAU_USD",
            signal=signal,
            confidence=confidence,
            strategy="AI_BREAKOUT",
            features=features,
            risk_score=risk_score,
            price=data['close'].iloc[-1]
        )
    
    def _calculate_risk_score(self, features: Dict[str, float]) -> float:
        """Calculate risk score"""
        risk_factors = [
            features.get('volatility_20d', 0),
            features.get('volume_ratio', 1),
            features.get('range_20d', 0)
        ]
        
        risk_score = np.mean([abs(factor) for factor in risk_factors])
        return min(risk_score, 1.0)

class RiskManager:
    """Professional risk management"""
    
    def __init__(self, max_position_size: float = 0.02, max_daily_loss: float = 0.05):
        self.max_position_size = max_position_size
        self.max_daily_loss = max_daily_loss
        self.daily_pnl = 0.0
        self.last_reset_date = datetime.now().date()
    
    def calculate_position_size(self, signal: TradingSignal, 
                              account_balance: float, 
                              current_price: float) -> int:
        """Calculate position size based on risk management rules"""
        
        # Reset daily P&L if it's a new day
        current_date = datetime.now().date()
        if current_date != self.last_reset_date:
            self.daily_pnl = 0.0
            self.last_reset_date = current_date
        
        # Check daily loss limit
        if self.daily_pnl < -account_balance * self.max_daily_loss:
            logger.warning("Daily loss limit reached")
            return 0
        
        # Calculate position size based on confidence and risk
        base_size = account_balance * self.max_position_size
        confidence_multiplier = signal.confidence
        risk_multiplier = 1 - signal.risk_score
        
        position_value = base_size * confidence_multiplier * risk_multiplier
        units = int(position_value / current_price)
        
        # Ensure minimum position size
        if units < 1000:  # Minimum 1000 units for OANDA
            units = 0
        
        return units
    
    def update_daily_pnl(self, pnl: float):
        """Update daily P&L"""
        self.daily_pnl += pnl

class OANDATradingBot:
    """Professional OANDA trading bot"""
    
    def __init__(self, config: OANDAConfig):
        self.config = config
        self.connector = OANDAConnector(config)
        self.ai_generator = AISignalGenerator()
        self.risk_manager = RiskManager()
        self.running = False
        self.data_queue = Queue()
        self.signal_queue = Queue()
        
        # Trading parameters
        self.instruments = ["XAU_USD"]  # Gold
        self.granularity = "M5"  # 5-minute candles
        self.update_interval = 300  # 5 minutes
        
        # State tracking
        self.last_signals = {}
        self.positions = {}
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Received shutdown signal, stopping bot...")
        self.stop()
        sys.exit(0)
    
    def initialize(self):
        """Initialize the trading bot"""
        try:
            # Test connection
            account_info = self.connector.get_account_info()
            logger.info(f"Connected to OANDA account: {account_info['account']['name']}")
            
            # Get account summary
            summary = self.connector.get_account_summary()
            balance = float(summary['account']['balance'])
            logger.info(f"Account balance: {balance}")
            
            # Train AI model with historical data
            self._train_ai_model()
            
            logger.info("Trading bot initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize trading bot: {e}")
            return False
    
    def _train_ai_model(self):
        """Train AI model with historical data"""
        try:
            for instrument in self.instruments:
                logger.info(f"Training AI model for {instrument}")
                
                # Get historical data
                historical_data = self.connector.get_candles(
                    instrument, self.granularity, count=1000
                )
                
                if len(historical_data) > 100:
                    self.ai_generator.train_model(historical_data)
                    logger.info(f"AI model trained for {instrument}")
                else:
                    logger.warning(f"Insufficient historical data for {instrument}")
                    
        except Exception as e:
            logger.error(f"Error training AI model: {e}")
    
    def start(self):
        """Start the trading bot"""
        if not self.initialize():
            return
        
        self.running = True
        logger.info("Starting OANDA trading bot...")
        
        # Start data collection thread
        data_thread = threading.Thread(target=self._data_collection_loop)
        data_thread.daemon = True
        data_thread.start()
        
        # Start signal processing thread
        signal_thread = threading.Thread(target=self._signal_processing_loop)
        signal_thread.daemon = True
        signal_thread.start()
        
        # Main trading loop
        try:
            while self.running:
                self._trading_loop()
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.stop()
    
    def _data_collection_loop(self):
        """Data collection loop"""
        while self.running:
            try:
                for instrument in self.instruments:
                    # Get latest candles
                    candles = self.connector.get_candles(
                        instrument, self.granularity, count=100
                    )
                    
                    if not candles.empty:
                        candles['symbol'] = instrument
                        self.data_queue.put(candles)
                
                time.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Error in data collection: {e}")
                time.sleep(60)
    
    def _signal_processing_loop(self):
        """Signal processing loop"""
        while self.running:
            try:
                if not self.data_queue.empty():
                    data = self.data_queue.get()
                    
                    # Generate AI signal
                    signal = self.ai_generator.generate_signal(data)
                    
                    if signal.signal != "HOLD":
                        self.signal_queue.put(signal)
                
                time.sleep(10)  # Process signals every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in signal processing: {e}")
                time.sleep(10)
    
    def _trading_loop(self):
        """Main trading loop"""
        try:
            # Get current positions
            positions = self.connector.get_positions()
            current_positions = {}
            
            for position in positions:
                instrument = position['instrument']
                units = int(position['long']['units']) if float(position['long']['units']) > 0 else int(position['short']['units'])
                current_positions[instrument] = units
            
            # Process signals
            while not self.signal_queue.empty():
                signal = self.signal_queue.get()
                
                if signal.signal != "HOLD":
                    self._execute_signal(signal, current_positions)
            
            # Update positions
            self.positions = current_positions
            
        except Exception as e:
            logger.error(f"Error in trading loop: {e}")
    
    def _execute_signal(self, signal: TradingSignal, current_positions: Dict):
        """Execute trading signal"""
        try:
            instrument = signal.symbol
            current_position = current_positions.get(instrument, 0)
            
            # Get account balance
            summary = self.connector.get_account_summary()
            balance = float(summary['account']['balance'])
            
            # Calculate position size
            units = self.risk_manager.calculate_position_size(
                signal, balance, signal.price
            )
            
            if units == 0:
                logger.info(f"No position taken for {instrument} (risk management)")
                return
            
            # Execute trade
            if signal.signal == "BUY" and current_position <= 0:
                if current_position < 0:
                    # Close short position first
                    self.connector.close_position(instrument, abs(current_position))
                    logger.info(f"Closed short position for {instrument}")
                
                # Open long position
                order = self.connector.place_market_order(instrument, units, "buy")
                logger.info(f"Opened long position for {instrument}: {units} units")
                
            elif signal.signal == "SELL" and current_position >= 0:
                if current_position > 0:
                    # Close long position first
                    self.connector.close_position(instrument, current_position)
                    logger.info(f"Closed long position for {instrument}")
                
                # Open short position
                order = self.connector.place_market_order(instrument, -units, "sell")
                logger.info(f"Opened short position for {instrument}: {-units} units")
            
            # Log signal details
            logger.info(f"Signal executed: {signal.signal} {instrument} "
                       f"(confidence: {signal.confidence:.2f}, "
                       f"risk: {signal.risk_score:.2f})")
            
        except Exception as e:
            logger.error(f"Error executing signal: {e}")
    
    def stop(self):
        """Stop the trading bot"""
        self.running = False
        logger.info("Trading bot stopped")

def main():
    """Main function"""
    # Load configuration
    config = OANDAConfig(
        account_id=os.getenv("OANDA_ACCOUNT_ID"),
        api_key=os.getenv("OANDA_API_KEY"),
        environment=os.getenv("OANDA_ENVIRONMENT", "practice")
    )
    
    if not config.account_id or not config.api_key:
        logger.error("Please set OANDA_ACCOUNT_ID and OANDA_API_KEY environment variables")
        return
    
    # Create and start trading bot
    bot = OANDATradingBot(config)
    bot.start()

if __name__ == "__main__":
    main() 