"""
LEAN Forex Strategy
Focused on OANDA forex data only
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

# LEAN imports
from AlgorithmImports import *

class LeanForexStrategy(QCAlgorithm):
    """
    Forex-focused strategy using OANDA data
    """
    
    def Initialize(self):
        """Initialize the strategy"""
        # Set start and end dates
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2024, 12, 31)
        
        # Set cash
        self.SetCash(10000)
        
        # Forex pairs to trade
        self.forex_pairs = [
            "EURUSD",
            "GBPUSD", 
            "USDJPY",
            "USDCHF",
            "AUDUSD",
            "USDCAD",
            "NZDUSD"
        ]
        
        # Add forex symbols
        self.symbols = {}
        for pair in self.forex_pairs:
            symbol = self.AddForex(pair, Resolution.Minute, Market.Oanda)
            self.symbols[pair] = symbol
        
        # Strategy parameters
        self.lookback_period = 20
        self.ema_fast = 12
        self.ema_slow = 26
        self.rsi_period = 14
        self.confidence_threshold = 0.4
        self.max_position_size = 0.02  # 2% of portfolio per trade
        self.stop_loss_pips = 50
        self.take_profit_pips = 100
        
        # Pip values for different pairs
        self.pip_values = {
            "EURUSD": 0.0001,
            "GBPUSD": 0.0001,
            "USDJPY": 0.01,
            "USDCHF": 0.0001,
            "AUDUSD": 0.0001,
            "USDCAD": 0.0001,
            "NZDUSD": 0.0001
        }
        
        # Track indicators for each symbol
        self.indicators = {}
        for pair in self.forex_pairs:
            self.indicators[pair] = {
                'ema_fast': ExponentialMovingAverage(self.ema_fast),
                'ema_slow': ExponentialMovingAverage(self.ema_slow),
                'rsi': RelativeStrengthIndex(self.rsi_period),
                'atr': AverageTrueRange(14)
            }
        
        # Set warmup
        self.SetWarmUp(50)
        
        # Logging
        self.Debug(f"Initialized Forex Strategy with {len(self.forex_pairs)} pairs")
    
    def OnData(self, data):
        """Process new data"""
        if self.IsWarmingUp:
            return
        
        # Process each forex pair
        for pair in self.forex_pairs:
            if pair in data and data[pair] is not None:
                self.ProcessForexPair(pair, data[pair])
    
    def ProcessForexPair(self, pair: str, bar: TradeBar):
        """Process individual forex pair"""
        try:
            # Update indicators
            self.UpdateIndicators(pair, bar)
            
            # Generate signal
            signal = self.GenerateSignal(pair, bar)
            
            # Execute trade if signal is strong enough
            if signal['signal'] != 'HOLD' and signal['confidence'] >= self.confidence_threshold:
                self.ExecuteTrade(pair, signal, bar)
                
        except Exception as e:
            self.Debug(f"Error processing {pair}: {e}")
    
    def UpdateIndicators(self, pair: str, bar: TradeBar):
        """Update technical indicators"""
        indicators = self.indicators[pair]
        
        # Update EMAs
        indicators['ema_fast'].Update(bar.EndTime, bar.Close)
        indicators['ema_slow'].Update(bar.EndTime, bar.Close)
        
        # Update RSI
        indicators['rsi'].Update(bar.EndTime, bar.Close)
        
        # Update ATR
        indicators['atr'].Update(bar.EndTime, bar.High, bar.Low, bar.Close)
    
    def GenerateSignal(self, pair: str, bar: TradeBar) -> Dict:
        """Generate trading signal for forex pair"""
        indicators = self.indicators[pair]
        
        # Check if indicators are ready
        if not (indicators['ema_fast'].IsReady and 
                indicators['ema_slow'].IsReady and 
                indicators['rsi'].IsReady and 
                indicators['atr'].IsReady):
            return {'signal': 'HOLD', 'confidence': 0.0}
        
        # Get indicator values
        ema_fast = indicators['ema_fast'].Current.Value
        ema_slow = indicators['ema_slow'].Current.Value
        rsi = indicators['rsi'].Current.Value
        atr = indicators['atr'].Current.Value
        
        # Calculate features
        features = self.CalculateForexFeatures(pair, bar, ema_fast, ema_slow, rsi, atr)
        
        # Generate signal score
        score = self.CalculateSignalScore(features, pair)
        
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
        
        return {
            'signal': signal,
            'confidence': confidence,
            'features': features,
            'price': bar.Close
        }
    
    def CalculateForexFeatures(self, pair: str, bar: TradeBar, 
                             ema_fast: float, ema_slow: float, 
                             rsi: float, atr: float) -> Dict[str, float]:
        """Calculate forex-specific features"""
        features = {}
        
        # Price-based features
        features['ema_ratio'] = bar.Close / ema_fast if ema_fast > 0 else 1.0
        features['ema_cross'] = 1.0 if ema_fast > ema_slow else -1.0
        features['rsi'] = rsi
        features['atr'] = atr
        
        # Breakout features
        features.update(self.CalculateBreakoutFeatures(pair, bar))
        
        # Currency strength features
        features.update(self.CalculateCurrencyStrengthFeatures(pair, bar))
        
        return features
    
    def CalculateBreakoutFeatures(self, pair: str, bar: TradeBar) -> Dict[str, float]:
        """Calculate breakout features"""
        features = {}
        
        # Get historical data for breakout detection
        history = self.History(pair, 20, Resolution.Minute)
        if len(history) < 20:
            return features
        
        high_prices = history['high'].values
        low_prices = history['low'].values
        close_prices = history['close'].values
        
        # Support and resistance levels
        resistance_20 = np.max(high_prices)
        support_20 = np.min(low_prices)
        
        # Breakout detection
        features['breakout_up'] = 1.0 if bar.Close > resistance_20 else 0.0
        features['breakout_down'] = 1.0 if bar.Close < support_20 else 0.0
        
        # Distance to levels
        features['resistance_distance'] = (resistance_20 - bar.Close) / bar.Close
        features['support_distance'] = (bar.Close - support_20) / bar.Close
        
        # Range analysis
        features['range_20d'] = (resistance_20 - support_20) / bar.Close
        features['position_in_range'] = (bar.Close - support_20) / (resistance_20 - support_20)
        
        return features
    
    def CalculateCurrencyStrengthFeatures(self, pair: str, bar: TradeBar) -> Dict[str, float]:
        """Calculate currency strength features"""
        features = {}
        
        # Get historical data for momentum
        history = self.History(pair, 10, Resolution.Minute)
        if len(history) < 10:
            return features
        
        close_prices = history['close'].values
        
        # Momentum indicators
        features['momentum_5d'] = (bar.Close - close_prices[-5]) / close_prices[-5]
        features['momentum_10d'] = (bar.Close - close_prices[-10]) / close_prices[-10]
        
        # Rate of change
        features['roc_5d'] = (bar.Close / close_prices[-5] - 1) * 100
        features['roc_10d'] = (bar.Close / close_prices[-10] - 1) * 100
        
        return features
    
    def CalculateSignalScore(self, features: Dict[str, float], pair: str) -> float:
        """Calculate signal score"""
        score = 0.0
        
        # Breakout rules
        if features.get('breakout_up', 0) > 0:
            score += 0.3
        if features.get('breakout_down', 0) > 0:
            score -= 0.3
        
        # EMA rules
        if features.get('ema_cross', 0) > 0:
            score += 0.2
        else:
            score -= 0.2
        
        # RSI rules
        rsi = features.get('rsi', 50)
        if rsi < 30:
            score += 0.2
        elif rsi > 70:
            score -= 0.2
        
        # Momentum rules
        momentum = features.get('momentum_5d', 0)
        if abs(momentum) > 0.01:  # 1% threshold
            if momentum > 0:
                score += 0.1
            else:
                score -= 0.1
        
        # Currency-specific adjustments
        if 'JPY' in pair:
            # JPY pairs are more volatile
            score *= 0.8
        elif 'GBP' in pair:
            # GBP pairs have higher spreads
            score *= 0.9
        
        return score
    
    def ExecuteTrade(self, pair: str, signal: Dict, bar: TradeBar):
        """Execute forex trade"""
        try:
            # Check current position
            position = self.Portfolio[pair]
            
            # Calculate position size
            position_size = self.CalculatePositionSize(pair, signal, bar)
            
            if position_size == 0:
                return
            
            # Execute trade
            if signal['signal'] == 'BUY' and position.Quantity <= 0:
                # Close short position if exists
                if position.Quantity < 0:
                    self.Liquidate(pair)
                
                # Open long position
                self.MarketOrder(pair, position_size)
                self.Debug(f"BUY {pair}: {position_size} units at {bar.Close}")
                
            elif signal['signal'] == 'SELL' and position.Quantity >= 0:
                # Close long position if exists
                if position.Quantity > 0:
                    self.Liquidate(pair)
                
                # Open short position
                self.MarketOrder(pair, -position_size)
                self.Debug(f"SELL {pair}: {-position_size} units at {bar.Close}")
            
        except Exception as e:
            self.Debug(f"Error executing trade for {pair}: {e}")
    
    def CalculatePositionSize(self, pair: str, signal: Dict, bar: TradeBar) -> int:
        """Calculate position size based on risk management"""
        # Get account balance
        balance = self.Portfolio.Cash
        
        # Calculate risk amount
        risk_amount = balance * self.max_position_size
        
        # Get pip value
        pip_value = self.pip_values.get(pair, 0.0001)
        
        # Calculate stop loss in pips
        stop_loss_pips = self.stop_loss_pips
        
        # Calculate position size
        stop_loss_amount = pip_value * stop_loss_pips
        
        if stop_loss_amount == 0:
            return 0
        
        # Base position size
        position_size = risk_amount / stop_loss_amount
        
        # Apply confidence adjustment
        confidence_multiplier = signal['confidence']
        final_position_size = position_size * confidence_multiplier
        
        # Convert to standard lot sizes (1000 units = 0.01 lot)
        units = int(final_position_size * 1000)
        
        # Ensure minimum position size
        if units < 1000:  # Minimum 0.01 lot
            units = 0
        
        return units
    
    def OnOrderEvent(self, orderEvent):
        """Handle order events"""
        if orderEvent.Status == OrderStatus.Filled:
            self.Debug(f"Order filled: {orderEvent.Symbol} {orderEvent.FillQuantity} @ {orderEvent.FillPrice}")
    
    def OnEndOfAlgorithm(self):
        """Called at the end of the algorithm"""
        self.Debug("Forex Strategy completed")
        
        # Print final statistics
        total_return = self.Portfolio.TotalPortfolioValue / 10000 - 1
        self.Debug(f"Total Return: {total_return:.2%}")
        
        # Print pair-specific performance
        for pair in self.forex_pairs:
            if pair in self.Portfolio:
                position = self.Portfolio[pair]
                if position.Quantity != 0:
                    self.Debug(f"{pair}: {position.Quantity} units, P&L: {position.UnrealizedProfit}") 