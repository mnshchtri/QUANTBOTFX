"""
TradingView-like Replay Engine
Simulates real-time trading with historical data and strategy signals
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
from datetime import datetime, timedelta
import time
from typing import Dict, List, Tuple, Optional, Any
import threading
import requests
from strategies.momentum_following_strategy import RangeOfTheDayStrategy

# Set up logging
logger = logging.getLogger(__name__)

class ReplayEngine:
    def __init__(self):
        self.strategy = RangeOfTheDayStrategy()
        self.is_playing = False
        self.current_index = 0  # Start at 0 to show all candles initially
        self.start_play_index = 0  # Index where actual playback should start
        self.speed_multiplier = 1.0
        self.data = None
        self.trades = []
        self.signals = []
        self.performance_history = []
        self.real_time_mode = False
        self.auto_trade = False
        self.risk_management = True
        
        # Enhanced features
        self.position_size = 10000  # Default position size
        self.max_risk_per_trade = 0.02  # 2% risk per trade
        self.max_drawdown_limit = 0.10  # 10% max drawdown
        self.take_profit_pips = 50
        self.stop_loss_pips = 30
        
        # Performance tracking
        self.initial_balance = 100000
        self.current_balance = self.initial_balance
        self.peak_balance = self.initial_balance
        self.max_drawdown = 0
        
        # Fade-out settings
        self.signal_fade_days = 2
        
        # Colors
        self.colors = {
            'background': '#1e222d',
            'grid': '#2a2e39',
            'text': '#d1d4dc',
            'candle_green': '#26a69a',
            'candle_red': '#ef5350',
            'buy_signal': '#4caf50',
            'sell_signal': '#f44336',
            'position_long': '#4caf50',
            'position_short': '#f44336'
        }
    
    def load_data(self, instrument: str, start_date: str, end_date: str, timeframe: str = 'M15'):
        """Load historical data for replay - DEPRECATED: Use load_backtest_data instead"""
        logger.warning("load_data() is deprecated. Use load_backtest_data() with proper data structure instead.")
        return False

    def load_backtest_data(self, replay_export: Dict):
        """
        🎬 Load market data for TradingView-style replay
        
        Handles both backtest data and live market data for replay visualization.
        """
        try:
            if not replay_export or 'data' not in replay_export:
                logger.error("Invalid replay export data")
                return False
                
            logger.info(f"🎬 Loading market data for replay...")
            
            # Clear existing data first
            self.data = None
            self.trades = []
            self.signals = []
            self.performance_history = []
            self.current_index = 0
            self.start_play_index = 0
            
            # Load the primary data
            data = replay_export['data']
            logger.info(f"Loading data type: {type(data)}, length: {len(data) if hasattr(data, '__len__') else 'unknown'}")
            
            # Debug: Log the replay export structure
            logger.info(f"🎬 Replay export keys: {list(replay_export.keys())}")
            logger.info(f"🎬 Instrument: {replay_export.get('instrument', 'Unknown')}")
            logger.info(f"🎬 Timeframe: {replay_export.get('timeframe', 'Unknown')}")
            
            if isinstance(data, pd.DataFrame):  # It's a DataFrame
                self.data = data.copy()
                logger.info("Loaded as DataFrame copy")
            elif isinstance(data, list):  # It's a list of records
                logger.info("Converting list to DataFrame...")
                self.data = pd.DataFrame(data)
                logger.info(f"DataFrame created with shape: {self.data.shape}")
                # Convert datetime strings back to datetime if needed
                if 'time' in self.data.columns:
                    self.data['time'] = pd.to_datetime(self.data['time'])
                    self.data = self.data.set_index('time')
                    logger.info("Set time column as index")
                elif len(self.data) > 0:
                    # Create a simple integer index if no time column
                    self.data.reset_index(drop=True, inplace=True)
                    logger.info("Set integer index")
            else:
                logger.info("Converting to DataFrame (fallback)...")
                self.data = pd.DataFrame(data)
                if len(self.data) > 0:
                    self.data.reset_index(drop=True, inplace=True)
            
            logger.info(f"Final data type: {type(self.data)}, shape: {getattr(self.data, 'shape', 'N/A')}")
            
            # Handle both backtest and live data
            if 'trades' in replay_export and 'signals' in replay_export:
                # This is backtest data
                self.trades = replay_export.get('trades', [])
                self.signals = replay_export.get('signals', [])
                self.performance_history = replay_export.get('performance_history', [])
                
                # Update metadata for backtest
                metadata = replay_export.get('metadata', {})
                self.backtest_metadata = {
                    'strategy_name': metadata.get('strategy_name', 'Unknown Strategy'),
                    'symbol': replay_export.get('symbol', 'Unknown'),
                    'timeframe': replay_export.get('timeframe', '15M'),
                    'total_signals': metadata.get('total_signals', len(self.signals)),
                    'total_trades': metadata.get('total_trades', len(self.trades)),
                    'backtest_return': metadata.get('total_return', 0),
                    'data_range': metadata.get('data_range', {})
                }
            else:
                # This is live market data - generate signals using strategy
                self.trades = []
                self.performance_history = []
                
                # Generate signals for live market data using strategy
                if hasattr(self.strategy, 'generate_signals') and not self.data.empty:
                    logger.info(f"🎯 Generating signals using strategy...")
                    try:
                        generated_signals = self.strategy.generate_signals(self.data)
                        self.signals = generated_signals
                        logger.info(f"✅ Generated {len(self.signals)} signals")
                    except Exception as e:
                        logger.error(f"Error generating signals: {e}")
                        self.signals = []
                else:
                    self.signals = []
                
                # Update metadata for live data
                self.backtest_metadata = {
                    'strategy_name': getattr(self.strategy, 'name', 'Range of the Day Strategy'),
                    'symbol': replay_export.get('instrument', 'Unknown'),
                    'timeframe': replay_export.get('timeframe', '15M'),
                    'total_signals': len(self.signals),
                    'total_trades': 0,
                    'backtest_return': 0,
                    'data_range': {}
                }
            
            # Setup replay state
            self.current_index = len(self.data) - 1 if len(self.data) > 0 else 0  # Show all candles initially
            self.is_playing = False
            self.auto_trade = False  # Disable auto-trade for live data
            self.real_time_mode = False
            
            # Reset performance tracking for replay
            self.initial_balance = 100000
            self.current_balance = self.initial_balance
            self.peak_balance = self.initial_balance
            self.max_drawdown = 0
            
            # Create index mappings for fast lookups during replay
            self._create_signal_index_map()
            self._create_trade_index_map()
            
            # Set start position to show all candles initially
            self.current_index = len(self.data) - 1 if len(self.data) > 0 else 0
            self.start_play_index = 0
            
            logger.info(f"✅ Market data loaded successfully!")
            logger.info(f"   📊 {len(self.data)} candles ({self.backtest_metadata['timeframe']})")
            logger.info(f"   🎯 {len(self.signals)} signals from {self.backtest_metadata['strategy_name']}")
            logger.info(f"   💰 {len(self.trades)} trades")
            logger.info(f"   📅 Symbol: {self.backtest_metadata['symbol']}")
            
            # Log first few candles to verify data
            if not self.data.empty:
                logger.info(f"   📈 First candle: {self.data.iloc[0]}")
                logger.info(f"   📈 Last candle: {self.data.iloc[-1]}")
                logger.info(f"   📈 Data range: {self.data.index[0]} to {self.data.index[-1]}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading market data: {e}")
            return False
    
    def _create_signal_index_map(self):
        """Create fast lookup map for signals by candle index"""
        self.signal_index_map = {}
        for signal in self.signals:
            index = signal.get('index', 0)
            if index not in self.signal_index_map:
                self.signal_index_map[index] = []
            self.signal_index_map[index].append(signal)
    
    def _create_trade_index_map(self):
        """Create fast lookup maps for trade entries and exits by candle index"""
        self.trade_entry_map = {}
        self.trade_exit_map = {}
        
        for trade in self.trades:
            # Map trade entries
            entry_index = trade.get('entry_index', 0)
            if entry_index not in self.trade_entry_map:
                self.trade_entry_map[entry_index] = []
            self.trade_entry_map[entry_index].append(trade)
            
            # Map trade exits
            exit_index = trade.get('exit_index', 0)
            if exit_index not in self.trade_exit_map:
                self.trade_exit_map[exit_index] = []
            self.trade_exit_map[exit_index].append(trade)
    
    def get_current_replay_state(self):
        """Get detailed state for current replay position"""
        if self.data is None or self.current_index >= len(self.data):
            return None
        
        # Handle different index types safely
        try:
            current_timestamp = self.data.index[self.current_index]
        except (IndexError, TypeError):
            current_timestamp = self.current_index  # Fallback to integer index
            
        current_candle = self.data.iloc[self.current_index]
        
        # Get signals at current position
        current_signals = self.signal_index_map.get(self.current_index, [])
        
        # Get trades at current position  
        trade_entries = self.trade_entry_map.get(self.current_index, [])
        trade_exits = self.trade_exit_map.get(self.current_index, [])
        
        # Get performance at current position
        current_performance = None
        for perf in self.performance_history:
            if perf['index'] == self.current_index:
                current_performance = perf
                break
        
        # Calculate open positions at current time
        open_positions = []
        for trade in self.trades:
            if (trade['entry_index'] <= self.current_index and 
                trade['exit_index'] > self.current_index):
                open_positions.append(trade)
        
        return {
            'timestamp': current_timestamp,
            'candle_index': self.current_index,
            'candle_data': {
                'open': current_candle['open'],
                'high': current_candle['high'], 
                'low': current_candle['low'],
                'close': current_candle['close'],
                'volume': current_candle['volume']
            },
            'signals': current_signals,
            'trade_entries': trade_entries,
            'trade_exits': trade_exits,
            'open_positions': open_positions,
            'performance': current_performance,
            'metadata': self.backtest_metadata,
            'replay_progress': {
                'current_index': self.current_index,
                'total_candles': len(self.data),
                'progress_percent': (self.current_index / len(self.data)) * 100 if len(self.data) > 0 else 0,
                'is_playing': self.is_playing,
                'speed': self.speed_multiplier
            }
        }
    
    def _reset_performance(self):
        """Reset performance tracking"""
        self.current_balance = self.initial_balance
        self.peak_balance = self.initial_balance
        self.max_drawdown = 0
        self.performance_history = []
    
    def simulate_strategy(self):
        """Simulate strategy execution at current position"""
        if self.data is None or self.current_index >= len(self.data):
            return
        
        if not isinstance(self.data, pd.DataFrame):
            return
        
        current_data = self.data.iloc[:self.current_index + 1]
        if len(current_data) < 20:  # Need minimum data for indicators
            return
        
        try:
            # Get strategy signals
            if hasattr(self.strategy, 'generate_signals'):
                signals = self.strategy.generate_signals(current_data)
            else:
                signals = []
            
            # Process signals and execute trades
            for signal in signals:
                if signal['type'] == 'BUY' and self.auto_trade:
                    self._execute_buy_trade(signal)
                elif signal['type'] == 'SELL' and self.auto_trade:
                    self._execute_sell_trade(signal)
            
            # Update performance metrics
            self._update_performance()
            
        except Exception as e:
            logger.error(f"Error simulating strategy: {e}")
    
    def _execute_buy_trade(self, signal: Dict):
        """Execute a buy trade with risk management"""
        if not self._check_risk_limits():
            return
        
        current_price = signal['price']
        position_size = self._calculate_position_size(current_price)
        
        trade = {
            'id': len(self.trades) + 1,
            'type': 'BUY',
            'entry_price': current_price,
            'entry_time': signal['timestamp'],
            'position_size': position_size,
            'status': 'open',
            'signal_strength': signal.get('strength', 0.5),
            'stop_loss': current_price - (self.stop_loss_pips / 10000),
            'take_profit': current_price + (self.take_profit_pips / 10000)
        }
        
        self.trades.append(trade)
        logger.info(f"Executed BUY trade at {current_price}")
    
    def _execute_sell_trade(self, signal: Dict):
        """Execute a sell trade with risk management"""
        if not self._check_risk_limits():
            return
        
        current_price = signal['price']
        
        # Close existing long positions
        for trade in self.trades:
            if trade['status'] == 'open' and trade['type'] == 'BUY':
                trade['exit_price'] = current_price
                trade['exit_time'] = signal['timestamp']
                trade['status'] = 'closed'
                trade['profit_loss_pips'] = (current_price - trade['entry_price']) * 10000
                trade['profit_loss_percent'] = ((current_price - trade['entry_price']) / trade['entry_price']) * 100
        
        # Open new short position if auto_trade is enabled
        if self.auto_trade:
            position_size = self._calculate_position_size(current_price)
            trade = {
                'id': len(self.trades) + 1,
                'type': 'SELL',
                'entry_price': current_price,
                'entry_time': signal['timestamp'],
                'position_size': position_size,
                'status': 'open',
                'signal_strength': signal.get('strength', 0.5),
                'stop_loss': current_price + (self.stop_loss_pips / 10000),
                'take_profit': current_price - (self.take_profit_pips / 10000)
            }
            self.trades.append(trade)
            logger.info(f"Executed SELL trade at {current_price}")
    
    def _check_risk_limits(self) -> bool:
        """Check if we can take another trade based on risk limits"""
        if not self.risk_management:
            return True
        
        # Check drawdown limit
        current_drawdown = (self.peak_balance - self.current_balance) / self.peak_balance
        if current_drawdown > self.max_drawdown_limit:
            logger.warning(f"Max drawdown limit reached: {current_drawdown:.2%}")
            return False
        
        # Check open positions
        open_positions = [t for t in self.trades if t['status'] == 'open']
        if len(open_positions) >= 3:  # Max 3 open positions
            logger.warning("Maximum open positions reached")
            return False
        
        return True
    
    def _calculate_position_size(self, price: float) -> float:
        """Calculate position size based on risk management"""
        if not self.risk_management:
            return self.position_size
        
        risk_amount = self.current_balance * self.max_risk_per_trade
        position_size = risk_amount / (self.stop_loss_pips / 10000)
        return min(position_size, self.position_size)
    
    def _update_performance(self):
        """Update performance metrics"""
        if self.data is None or self.current_index >= len(self.data):
            return
        
        if not isinstance(self.data, pd.DataFrame):
            return
        
        # Calculate current balance
        total_pnl = 0
        for trade in self.trades:
            if trade['status'] == 'closed':
                total_pnl += trade.get('profit_loss_pips', 0) * trade['position_size'] / 10000
        
        self.current_balance = self.initial_balance + total_pnl
        
        # Update peak balance and drawdown
        if self.current_balance > self.peak_balance:
            self.peak_balance = self.current_balance
        
        current_drawdown = (self.peak_balance - self.current_balance) / self.peak_balance
        if current_drawdown > self.max_drawdown:
            self.max_drawdown = current_drawdown
        
        # Add to performance history
        timestamp = None
        if self.current_index < len(self.data) and hasattr(self.data, 'index'):
            timestamp = self.data.index[self.current_index]
        
        self.performance_history.append({
            'index': self.current_index,
            'balance': self.current_balance,
            'drawdown': current_drawdown,
            'timestamp': timestamp
        })
    
    def get_current_data(self) -> Tuple[pd.DataFrame, List, List]:
        """Get data up to current replay position with fade-out effects"""
        logger.info(f"get_current_data called - is_playing: {self.is_playing}, current_index: {self.current_index}")
        
        if self.data is None:
            logger.warning("No data available in get_current_data")
            return pd.DataFrame(), [], []
        
        if not isinstance(self.data, pd.DataFrame):
            logger.warning("Data is not a DataFrame in get_current_data")
            return pd.DataFrame(), [], []
        
        # Create a DataFrame for display with proper replay logic
        display_df = self._create_display_dataframe()
        logger.info(f"Display DataFrame created with {len(display_df)} rows")
        
        # Apply fade-out effect for signals
        faded_signals = []
        for signal in self.signals:
            try:
                signal_time = pd.to_datetime(signal['timestamp'])
                if hasattr(self.data, 'index') and self.current_index < len(self.data):
                    days_old = (self.data.index[self.current_index] - signal_time).days
                    
                    if days_old <= self.signal_fade_days:
                        opacity = 1.0 - (days_old / self.signal_fade_days) * 0.5
                        faded_signal = signal.copy()
                        faded_signal['opacity'] = opacity
                        faded_signals.append(faded_signal)
            except Exception:
                continue
        
        return display_df, self.trades, faded_signals
    
    def _create_display_dataframe(self) -> pd.DataFrame:
        """Create DataFrame for display based on replay state"""
        if self.data is None or len(self.data) == 0:
            logger.warning("No data available for display")
            return pd.DataFrame()
        
        logger.info(f"Creating display DataFrame - is_playing: {self.is_playing}, current_index: {self.current_index}")
        
        # Progressive replay: show candles up to current position (whether playing or paused)
        if self.current_index < len(self.data) - 1:
            # Show candles from beginning up to current_index + 1
            display_data = self.data.iloc[:self.current_index + 1].copy()
            logger.info(f"Replay position {self.current_index}: showing {len(display_data)} candles (playing: {self.is_playing})")
            return display_data
        else:
            # If we're at or past the end, show all data
            logger.info(f"Replay at end: showing all {len(self.data)} candles")
            return self.data.copy()
    
    def get_current_position(self) -> Optional[Dict]:
        """Get current trading position"""
        open_positions = [t for t in self.trades if t['status'] == 'open']
        if not open_positions:
            return None
        
        # Return the most recent open position
        return open_positions[-1]
    
    def get_performance_metrics(self) -> Dict:
        """Get comprehensive performance metrics"""
        if not self.trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'total_profit_loss': 0.0,
                'max_drawdown': 0.0,
                'sharpe_ratio': 0.0,
                'current_balance': self.current_balance,
                'peak_balance': self.peak_balance
            }
        
        closed_trades = [t for t in self.trades if t['status'] == 'closed']
        winning_trades = [t for t in closed_trades if t.get('profit_loss_pips', 0) > 0]
        losing_trades = [t for t in closed_trades if t.get('profit_loss_pips', 0) < 0]
        
        total_trades = len(closed_trades)
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0.0
        
        total_profit_loss = sum(t.get('profit_loss_pips', 0) for t in closed_trades)
        
        # Calculate Sharpe ratio (simplified)
        if len(self.performance_history) > 1:
            returns = [p['balance'] - self.performance_history[i-1]['balance'] 
                      for i, p in enumerate(self.performance_history[1:], 1)]
            if returns:
                avg_return = np.mean(returns)
                std_return = np.std(returns)
                sharpe_ratio = avg_return / std_return if std_return > 0 else 0.0
            else:
                sharpe_ratio = 0.0
        else:
            sharpe_ratio = 0.0
        
        return {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'total_profit_loss': total_profit_loss,
            'max_drawdown': self.max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'current_balance': self.current_balance,
            'peak_balance': self.peak_balance,
            'open_positions': len([t for t in self.trades if t['status'] == 'open'])
        }
    
    def step_forward(self):
        """Move replay forward by one candle"""
        if self.data is None or self.current_index >= len(self.data) - 1:
            return False
        
        self.current_index += 1
        
        # Simulate strategy if auto-trade is enabled
        if self.auto_trade:
            self.simulate_strategy()
        
        return True
    
    def step_backward(self):
        """Move replay backward by one candle"""
        if self.current_index > 0:
            self.current_index -= 1
            return True
        return False
    
    def jump_to_date(self, target_date: str) -> bool:
        """Jump to a specific date in the replay"""
        if self.data is None:
            logger.error("No data available for jump")
            return False
        
        try:
            target_dt = pd.to_datetime(target_date)
            logger.info(f"Target date: {target_dt}")
            
            # Ensure both datetime objects are timezone-aware
            if target_dt.tz is None:
                target_dt = target_dt.tz_localize('UTC')
            
            # Make sure data index is timezone-aware
            if self.data.index.tz is None:
                data_index = self.data.index.tz_localize('UTC')
            else:
                data_index = self.data.index
            
            logger.info(f"Data index range: {data_index.min()} to {data_index.max()}")
            
            # Find the closest index
            time_diff = abs(data_index - target_dt)
            closest_index = time_diff.argmin()
            
            logger.info(f"Closest index: {closest_index}, time difference: {time_diff[closest_index]}")
            
            if 0 <= closest_index < len(self.data):
                self.current_index = closest_index
                logger.info(f"Jumped to index {closest_index}, date: {data_index[closest_index]}")
                return True
            else:
                logger.error(f"Closest index {closest_index} is out of range [0, {len(self.data)})")
                return False
        except Exception as e:
            logger.error(f"Error jumping to date {target_date}: {e}")
            return False

    def set_start_position_with_context(self, target_date: str, context_candles: int = 14) -> bool:
        """Set the start position with historical context candles before it"""
        if self.data is None:
            logger.error("No data available for setting start position")
            return False
        
        try:
            target_dt = pd.to_datetime(target_date)
            logger.info(f"Setting start position for date: {target_dt}")
            
            # Ensure both datetime objects are timezone-aware
            if target_dt.tz is None:
                target_dt = target_dt.tz_localize('UTC')
            
            # Make sure data index is timezone-aware
            if self.data.index.tz is None:
                data_index = self.data.index.tz_localize('UTC')
            else:
                data_index = self.data.index
            
            # Find the closest index to target date
            time_diff = abs(data_index - target_dt)
            target_index = time_diff.argmin()
            
            logger.info(f"Target index: {target_index}, date: {data_index[target_index]}")
            
            if 0 <= target_index < len(self.data):
                # Store where actual playback should start
                self.start_play_index = target_index
                
                # Set current_index to show context_candles before the target
                start_index = max(0, target_index - context_candles)
                self.current_index = start_index
                
                # Ensure replay is not playing when setting position
                self.is_playing = False
                
                logger.info(f"Set start position: context from index {start_index}, play will start at index {target_index}")
                return True
            else:
                logger.error(f"Target index {target_index} is out of range [0, {len(self.data)})")
                return False
        except Exception as e:
            logger.error(f"Error setting start position for date {target_date}: {e}")
            return False
    
    def play(self):
        """Start replay from the designated start position"""
        self.is_playing = True
        # If we have a start_play_index set, move to that position
        if hasattr(self, 'start_play_index') and self.start_play_index > 0:
            if self.current_index < self.start_play_index:
                self.current_index = self.start_play_index
                logger.info(f"Starting replay from position {self.start_play_index}")
        else:
            # Default behavior: start from current position
            logger.info(f"Starting replay from current position {self.current_index}")
    
    def pause(self):
        """Pause replay"""
        self.is_playing = False
    
    def stop(self):
        """Stop replay and pause at current position"""
        self.is_playing = False
        # Don't reset current_index - just pause
    
    def reset(self):
        """Reset replay to beginning"""
        self.is_playing = False
        self.current_index = 0
        if hasattr(self, 'start_play_index'):
            self.start_play_index = 0
    
    def set_speed(self, speed: float):
        """Set replay speed multiplier"""
        self.speed_multiplier = max(0.1, min(10.0, speed))
    
    def toggle_auto_trade(self):
        """Toggle automatic trading simulation"""
        self.auto_trade = not self.auto_trade
    
    def toggle_risk_management(self):
        """Toggle risk management features"""
        self.risk_management = not self.risk_management
    
    def get_replay_state(self) -> Dict[str, Any]:
        """Get current replay state for API"""
        return {
            'is_playing': self.is_playing,
            'current_index': int(self.current_index),
            'speed_multiplier': float(self.speed_multiplier),
            'auto_trade': self.auto_trade,
            'risk_management': self.risk_management,
            'data_loaded': self.data is not None and len(self.data) > 0,
            'total_candles': int(len(self.data)) if self.data is not None else 0,
            'current_date': str(self.data.index[self.current_index]) if self.data is not None and self.current_index < len(self.data) else None
        }
    
    def get_replay_data(self) -> Dict[str, Any]:
        """Get current replay data for API"""
        current_data, trades, signals = self.get_current_data()
        
        return {
            'data': current_data.to_dict('records') if not current_data.empty else [],
            'trades': trades,
            'signals': signals,
            'replay_state': self.get_replay_state(),
            'performance': self.get_performance_metrics()
        } 

    def get_data_range(self) -> Dict[str, str]:
        """Get the available data range for date/time constraints"""
        if self.data is None or len(self.data) == 0:
            return {"start_date": "", "end_date": ""}
        
        try:
            start_date = self.data.index[0].strftime('%Y-%m-%d')
            end_date = self.data.index[-1].strftime('%Y-%m-%d')
            start_time = self.data.index[0].strftime('%H:%M')
            end_time = self.data.index[-1].strftime('%H:%M')
            
            return {
                "start_date": start_date,
                "end_date": end_date,
                "start_time": start_time,
                "end_time": end_time,
                "total_candles": len(self.data)
            }
        except Exception as e:
            logger.error(f"Error getting data range: {e}")
            return {"start_date": "", "end_date": ""} 