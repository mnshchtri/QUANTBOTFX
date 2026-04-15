#!/usr/bin/env python3
"""
Replay Service
=============

Integrated replay service that manages replay functionality without requiring 
a separate AI agent process.

Features:
- Replay engine management
- Chart rendering integration
- Strategy execution in replay mode
- Performance tracking
- Direct class integration (no HTTP overhead)

Usage:
    from services.replay_service import ReplayService
    replay_service = ReplayService()
    result = await replay_service.initialize_replay(symbol, timeframe)
"""

import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import requests
import threading
import json
import time

# Import replay components
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from replay_engine import ReplayEngine
from indicators import IndicatorLibrary

# Configure logging
logger = logging.getLogger(__name__)

class ReplayService:
    """Service for replay functionality management"""
    
    def __init__(self):
        # Core components
        self.replay_engine = ReplayEngine()
        self.indicator_library = IndicatorLibrary()
        
        # Service state
        self.is_healthy = True
        self.last_health_check = datetime.now()
        self.error_count = 0
        self.max_errors = 5
        
        # Data integration URLs
        self.backend_url = "http://127.0.0.1:8000"
        
        # Replay state
        self.current_instrument = None
        self.current_timeframe = "M15"
        self.active_indicators = {}
        self.replay_speed = 1.0
        self.auto_trade_enabled = False
        
        # Strategy storage
        self.registered_strategies = {}
        self.active_strategies = {}
        
        # Performance tracking
        self.performance_history = []
        self.trade_history = []
        
        # Backtest results storage
        self.backtest_results = {}
        
        # Background stepping mechanism
        self.stepping_thread = None
        self.stepping_active = False
        self.step_interval = 1.0  # seconds between steps
        
        logger.info("🎬 Replay Service initialized")
    
    def _start_stepping_thread(self):
        """Start background thread for automatic stepping"""
        if self.stepping_thread and self.stepping_thread.is_alive():
            return
        
        self.stepping_active = True
        self.stepping_thread = threading.Thread(target=self._stepping_worker, daemon=True)
        self.stepping_thread.start()
        logger.info("🎬 Background stepping thread started")
    
    def _stop_stepping_thread(self):
        """Stop background stepping thread"""
        self.stepping_active = False
        if self.stepping_thread and self.stepping_thread.is_alive():
            self.stepping_thread.join(timeout=1.0)
        logger.info("🎬 Background stepping thread stopped")
    
    def _stepping_worker(self):
        """Background worker that steps the replay forward"""
        while self.stepping_active:
            try:
                if self.replay_engine.is_playing:
                    # Step forward one candle
                    success = self.replay_engine.step_forward()
                    if not success:
                        # Reached the end, stop playing
                        self.replay_engine.pause()
                        self.stepping_active = False
                        logger.info("🎬 Replay reached end, stopping")
                        break
                    
                    # Sleep based on replay speed
                    sleep_time = self.step_interval / self.replay_speed
                    time.sleep(sleep_time)
                else:
                    # Not playing, sleep longer
                    time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error in stepping worker: {e}")
                time.sleep(0.1)
    
    async def get_data_from_backend_api(self, instrument: str, timeframe: str) -> pd.DataFrame:
        """Get market data from backend API (NO LIMITS - fetch all available data)"""
        try:
            # Fetch data directly from OANDA API since backend router has serialization issues
            import os
            import yaml
            import requests
            import pandas as pd
            from datetime import datetime, timedelta
            
            # Load OANDA settings from config.yaml with env fallback
            try:
                config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml"))
                with open(config_path, "r") as f:
                    cfg = yaml.safe_load(f) or {}
                oanda_cfg = cfg.get("trading", {}).get("oanda", {})
                OANDA_API_KEY = oanda_cfg.get("api_key") or os.getenv("OANDA_API_KEY")
                OANDA_BASE_URL = oanda_cfg.get("base_url") or os.getenv("OANDA_BASE_URL") or "https://api-fxpractice.oanda.com"
            except Exception:
                # Fallback to env only
                OANDA_API_KEY = os.getenv("OANDA_API_KEY")
                OANDA_BASE_URL = os.getenv("OANDA_BASE_URL") or "https://api-fxpractice.oanda.com"
            
            if not OANDA_API_KEY:
                logger.error("OANDA API key not configured. Cannot fetch data.")
                raise ValueError("OANDA API key not configured. Please set OANDA_API_KEY environment variable.")
            
            headers = {
                'Authorization': f'Bearer {OANDA_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            url = f"{OANDA_BASE_URL}/v3/instruments/{instrument}/candles"
            params = {
                'count': 5000,  # Maximum allowed by OANDA
                'granularity': timeframe,
                'price': 'M'  # Mid prices
            }
            
            logger.info(f"🌐 Fetching data directly from OANDA: {instrument} {timeframe}")
            logger.info(f"📊 Fetching ALL available data (no limits)")
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                candles = data.get('candles', [])
                
                if not candles:
                    raise ValueError(f"No data available for {instrument} {timeframe}")
                
                # Convert to DataFrame
                rows = []
                for candle in candles:
                    if candle.get('complete'):
                        mid = candle['mid']
                        rows.append({
                            'time': pd.to_datetime(candle['time']),
                            'open': float(mid['o']),
                            'high': float(mid['h']),
                            'low': float(mid['l']),
                            'close': float(mid['c']),
                            'volume': int(candle.get('volume', 0))
                        })
                
                if not rows:
                    raise ValueError(f"No complete candles available for {instrument} {timeframe}")
                
                df = pd.DataFrame(rows)
                df.set_index('time', inplace=True)
                
                # Handle timezone conversion safely
                if hasattr(df.index, 'tz_convert'):
                    df.index = df.index.tz_convert('UTC')
                
                logger.info(f"✅ Successfully fetched {len(df)} candles from OANDA")
                logger.info(f"📊 Data range: {df.index[0]} to {df.index[-1]}")
                
                return df
            else:
                error_msg = f"OANDA API error ({response.status_code}): {response.text}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
        except Exception as e:
            logger.error(f"Failed to fetch data from OANDA API: {e}")
            raise ValueError(f"Failed to fetch data from OANDA API: {e}")
    
    async def initialize_replay(
        self, 
        instrument: str = "GBP_JPY", 
        timeframe: str = "M15", 
        days_back: int = None
    ) -> Dict[str, Any]:
        """Initialize replay session with unlimited market data from OANDA"""
        try:
            logger.info(f"🎬 Initializing replay for {instrument} {timeframe}")
            
            # Clear any existing replay data
            self.clear_cache()
            
            # Store current instrument and timeframe
            self.current_instrument = instrument
            self.current_timeframe = timeframe
            
            # Fetch live market data for the specified instrument and timeframe (NO LIMITS)
            logger.info(f"📊 Fetching live market data for {instrument} {timeframe}...")
            logger.info(f"📊 Backend URL: {self.backend_url}/api/trading-data/{instrument}/{timeframe}")
            
            # Get ALL available data from OANDA (no day restrictions)
            market_data = await self.get_data_from_backend_api(instrument, timeframe)
            
            # Debug: Log the actual data we received
            logger.info(f"📊 Received data shape: {market_data.shape if hasattr(market_data, 'shape') else 'No shape'}")
            if not market_data.empty:
                logger.info(f"📊 First candle: {market_data.iloc[0]}")
                logger.info(f"📊 Last candle: {market_data.iloc[-1]}")
                logger.info(f"📊 Data range: {market_data.index[0]} to {market_data.index[-1]}")
                logger.info(f"📊 Total candles: {len(market_data)}")
            else:
                logger.warning(f"📊 No data received for {instrument} {timeframe}")
            
            if market_data.empty:
                raise ValueError(f"No market data available for {instrument} {timeframe}")
            
            # Create replay export structure with ALL available data
            replay_export = {
                'data': market_data,
                'instrument': instrument,
                'timeframe': timeframe
                # No signals/trades keys - this will trigger live data signal generation
            }
            
            logger.info(f"📊 Created replay export with {len(market_data)} candles for {instrument} {timeframe}")
            
            # Clear any existing data and initialize replay engine with live market data
            logger.info(f"🔄 Clearing existing replay data and loading new data...")
            success = self.replay_engine.load_backtest_data(replay_export)
            
            if success:
                logger.info(f"✅ Replay initialized successfully for {instrument} {timeframe}")
                return {
                    "success": True,
                    "message": f"Replay initialized successfully for {instrument} {timeframe}",
                    "total_candles": len(self.replay_engine.data) if self.replay_engine.data is not None and not self.replay_engine.data.empty else 0,
                    "signals": len(self.replay_engine.signals) if hasattr(self.replay_engine, 'signals') and self.replay_engine.signals is not None else 0
                }
            else:
                raise ValueError("Failed to load replay data into engine")
                
        except Exception as e:
            logger.error(f"❌ Error initializing replay: {e}")
            self.error_count += 1
            self.is_healthy = False
            return {
                "success": False,
                "message": f"Failed to initialize replay: {str(e)}"
            }
    
    def get_replay_status(self) -> Dict[str, Any]:
        """Get current replay status"""
        try:
            status = self.replay_engine.get_replay_state()
            
            return {
                "success": True,
                "data": {
                    "instrument": self.current_instrument,
                    "timeframe": self.current_timeframe,
                    "replay_speed": self.replay_speed,
                    "is_playing": status.get("is_playing", False),
                    "current_index": status.get("current_index", 0),
                    "total_candles": status.get("total_candles", 0),
                    "progress": status.get("progress", 0.0),
                    "auto_trade_enabled": self.auto_trade_enabled,
                    "active_strategies": list(self.active_strategies.keys()),
                    "health": "healthy" if self.is_healthy else "unhealthy"
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting replay status: {e}")
            return {
                "success": False,
                "message": f"Error getting status: {str(e)}",
                "data": {}
            }
    
    def get_replay_data(self) -> Dict[str, Any]:
        """Get current replay data with candles and signals"""
        try:
            # Get the full data up to current position
            display_df, trades, signals = self.replay_engine.get_current_data()
            
            # Convert DataFrame to list of candles
            candles = []
            if not display_df.empty:
                for index, row in display_df.iterrows():
                    candles.append({
                        'timestamp': index.timestamp() if hasattr(index, 'timestamp') else index,
                        'open': float(row['open']),
                        'high': float(row['high']),
                        'low': float(row['low']),
                        'close': float(row['close']),
                        'volume': float(row.get('volume', 0))
                    })
            
            # Get replay state
            replay_state = self.replay_engine.get_replay_state()
            
            return {
                "success": True,
                "data": {
                    "candles": candles,
                    "signals": signals,
                    "trades": trades,
                    "replay_state": replay_state
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting replay data: {e}")
            return {
                "success": False,
                "message": f"Error getting replay data: {str(e)}",
                "data": {}
            }
    
    def control_replay(self, action: str, speed: float = 1.0) -> Dict[str, Any]:
        """Control replay playback"""
        try:
            logger.info(f"🎮 Replay control: {action} (speed: {speed})")
            
            if action == "play":
                self.replay_engine.play()
                self.replay_speed = speed
                # Start background stepping
                self._start_stepping_thread()
            elif action == "pause":
                self.replay_engine.pause()
                # Stop background stepping
                self._stop_stepping_thread()
            elif action == "step" or action == "step_forward":
                self.replay_engine.step_forward()
            elif action == "step_backward":
                self.replay_engine.step_backward()
            elif action == "reset":
                self.replay_engine.reset()
                # Stop background stepping
                self._stop_stepping_thread()
            elif action == "seek":
                # Speed parameter used as seek position
                self.replay_engine.seek_to_position(int(speed))
            else:
                raise ValueError(f"Unknown action: {action}")
            
            return {
                "success": True,
                "message": f"Replay {action} executed",
                "data": {
                    "action": action,
                    "speed": self.replay_speed
                }
            }
            
        except Exception as e:
            logger.error(f"Error controlling replay: {e}")
            return {
                "success": False,
                "message": f"Error controlling replay: {str(e)}",
                "data": {}
            }

    def play_replay(self) -> bool:
        """Start replay"""
        try:
            self.control_replay("play")
            return True
        except Exception:
            return False

    def pause_replay(self) -> bool:
        """Pause replay"""
        try:
            self.control_replay("pause")
            return True
        except Exception:
            return False

    def stop_replay(self) -> bool:
        """Stop replay"""
        try:
            self.control_replay("stop")
            return True
        except Exception:
            return False

    def step_forward(self) -> bool:
        """Step forward"""
        try:
            self.control_replay("step_forward")
            return True
        except Exception:
            return False

    def step_backward(self) -> bool:
        """Step backward"""
        try:
            self.control_replay("step_backward")
            return True
        except Exception:
            return False

    def set_speed(self, speed: float) -> bool:
        """Set replay speed"""
        try:
            self.replay_speed = speed
            self.replay_engine.set_speed(speed)
            return True
        except Exception:
            return False

    def toggle_auto_trade(self) -> Dict[str, Any]:
        """Toggle auto trading"""
        try:
            self.auto_trade_enabled = not self.auto_trade_enabled
            self.replay_engine.auto_trade = self.auto_trade_enabled
            return {
                "success": True,
                "auto_trade": self.auto_trade_enabled,
                "message": f"Auto trade {'enabled' if self.auto_trade_enabled else 'disabled'}"
            }
        except Exception as e:
            return {"success": False, "message": str(e), "auto_trade": self.auto_trade_enabled}

    def toggle_risk_management(self) -> Dict[str, Any]:
        """Toggle risk management"""
        try:
            self.replay_engine.toggle_risk_management()
            return {
                "success": True,
                "risk_management": self.replay_engine.risk_management,
                "message": f"Risk management {'enabled' if self.replay_engine.risk_management else 'disabled'}"
            }
        except Exception as e:
            return {"success": False, "message": str(e), "risk_management": self.replay_engine.risk_management}

    def simulate_strategy(self) -> bool:
        """Simulate strategy"""
        try:
            self.replay_engine.simulate_strategy()
            return True
        except Exception:
            return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get replay performance metrics"""
        try:
            # Get performance from replay engine
            performance = self.replay_engine.get_performance_metrics()
            
            return {
                "success": True,
                "data": {
                    "current_balance": performance.get("current_balance", 0.0),
                    "peak_balance": performance.get("peak_balance", 0.0),
                    "max_drawdown": performance.get("max_drawdown", 0.0),
                    "total_trades": performance.get("total_trades", 0),
                    "win_rate": performance.get("win_rate", 0.0),
                    "total_profit_loss": performance.get("total_profit_loss", 0.0),
                    "performance_history": self.performance_history[-100:],  # Last 100 entries
                    "trade_history": self.trade_history[-50:]  # Last 50 trades
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {
                "success": False,
                "message": f"Error getting performance: {str(e)}",
                "data": {}
            }
    
    def get_data_range(self) -> Dict[str, Any]:
        """Get replay data range information"""
        try:
            data_range = self.replay_engine.get_data_range()
            
            return {
                "success": True,
                "data": data_range
            }
            
        except Exception as e:
            logger.error(f"Error getting data range: {e}")
            return {
                "success": False,
                "message": f"Error getting data range: {str(e)}",
                "data": {}
            }
    
    def register_strategy(self, strategy_name: str, strategy_config: Dict[str, Any]) -> Dict[str, Any]:
        """Register a strategy for replay"""
        try:
            self.registered_strategies[strategy_name] = {
                "config": strategy_config,
                "registered_at": datetime.now().isoformat()
            }
            
            logger.info(f"📋 Strategy registered: {strategy_name}")
            
            return {
                "success": True,
                "message": f"Strategy {strategy_name} registered successfully",
                "data": {
                    "strategy_name": strategy_name,
                    "total_strategies": len(self.registered_strategies)
                }
            }
            
        except Exception as e:
            logger.error(f"Error registering strategy: {e}")
            return {
                "success": False,
                "message": f"Error registering strategy: {str(e)}",
                "data": {}
            }
    
    def activate_strategy(self, strategy_name: str) -> Dict[str, Any]:
        """Activate a registered strategy"""
        try:
            if strategy_name not in self.registered_strategies:
                raise ValueError(f"Strategy {strategy_name} not found")
            
            self.active_strategies[strategy_name] = {
                "config": self.registered_strategies[strategy_name]["config"],
                "activated_at": datetime.now().isoformat(),
                "performance": {"trades": 0, "pnl": 0.0}
            }
            
            logger.info(f"🎯 Strategy activated: {strategy_name}")
            
            return {
                "success": True,
                "message": f"Strategy {strategy_name} activated",
                "data": {
                    "strategy_name": strategy_name,
                    "active_strategies": list(self.active_strategies.keys())
                }
            }
            
        except Exception as e:
            logger.error(f"Error activating strategy: {e}")
            return {
                "success": False,
                "message": f"Error activating strategy: {str(e)}",
                "data": {}
            }
    
    def add_strategy_overlay(self, strategy_name: str) -> Dict[str, Any]:
        """Add strategy signals as overlays from backtest results"""
        try:
            # Load strategy signals from backtest results
            signals = self._load_strategy_backtest_signals(strategy_name)
            
            if signals:
                # Add signals to replay engine as overlays
                self.replay_engine.signals = signals
                
                logger.info(f"🎯 Added {len(signals)} strategy signals as overlay for {strategy_name}")
                
                return {
                    "success": True,
                    "message": f"Added {len(signals)} strategy signals as overlay",
                    "data": {
                        "signals_count": len(signals),
                        "strategy_name": strategy_name,
                        "overlay_type": "backtest_signals"
                    }
                }
            else:
                return {
                    "success": False,
                    "message": f"No backtest signals found for strategy {strategy_name}",
                    "data": {}
                }
                
        except Exception as e:
            logger.error(f"Error adding strategy overlay: {e}")
            return {
                "success": False,
                "message": f"Error adding strategy overlay: {str(e)}",
                "data": {}
            }
    
    def get_strategy_overlays(self) -> Dict[str, Any]:
        """Get all active strategy overlays from backtest results"""
        try:
            # Get current active strategies
            active_strategies = self._get_active_strategies()
            
            all_overlays = {}
            total_signals = 0
            
            for strategy_name in active_strategies:
                signals = self._load_strategy_backtest_signals(strategy_name)
                if signals:
                    all_overlays[strategy_name] = {
                        "signals": signals,
                        "signal_count": len(signals),
                        "overlay_type": "backtest_signals"
                    }
                    total_signals += len(signals)
            
            return {
                "success": True,
                "message": f"Retrieved {len(all_overlays)} strategy overlays",
                "data": {
                    "overlays": all_overlays,
                    "total_strategies": len(all_overlays),
                    "total_signals": total_signals,
                    "active_strategies": list(all_overlays.keys())
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting strategy overlays: {e}")
            return {
                "success": False,
                "message": f"Error getting strategy overlays: {str(e)}",
                "data": {}
            }
    
    def _load_strategy_backtest_signals(self, strategy_name: str) -> List[Dict[str, Any]]:
        """Load strategy signals from backtest results"""
        try:
            from services.backtrader_service import get_backtrader_service
            
            backtrader_service = get_backtrader_service()
            
            # Get current replay data to determine date range
            if self.replay_engine.data is None or self.replay_engine.data.empty:
                logger.warning("No replay data available for signal loading")
                return []
            
            # Get date range from replay data
            start_date = self.replay_engine.data.index[0].to_pydatetime()
            end_date = self.replay_engine.data.index[-1].to_pydatetime()
            
            # Get instrument and timeframe from replay
            instrument = getattr(self.replay_engine, 'instrument', 'GBP_JPY')
            timeframe = getattr(self.replay_engine, 'timeframe', 'M15')
            
            logger.info(f"🔍 Loading backtest signals for {strategy_name} on {instrument} {timeframe}")
            logger.info(f"📅 Date range: {start_date} to {end_date}")
            
            # Load signals from backtrader service
            signals = backtrader_service.get_strategy_signals(
                strategy_name, instrument, timeframe, start_date, end_date
            )
            
            logger.info(f"📊 Loaded {len(signals)} backtest signals for {strategy_name}")
            
            return signals
            
        except Exception as e:
            logger.error(f"Error loading backtest signals for {strategy_name}: {e}")
            return []
    
    def _get_active_strategies(self) -> List[str]:
        """Get list of active strategies for overlay display"""
        try:
            # This will be replaced with actual strategy management
            # For now, return default strategy
            
            # TODO: Get from strategy registry
            # TODO: Check which strategies are active for current replay
            
            return ["RangeOfTheDay"]  # Placeholder
            
        except Exception as e:
            logger.error(f"Error getting active strategies: {e}")
            return []
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        return {
            "service": "replay_service",
            "status": "healthy" if self.is_healthy else "unhealthy",
            "current_instrument": self.current_instrument,
            "current_timeframe": self.current_timeframe,
            "error_count": self.error_count,
            "active_strategies": len(self.active_strategies),
            "registered_strategies": len(self.registered_strategies),
            "timestamp": datetime.now().isoformat()
        }
    
    def clear_cache(self):
        """Clear service cache and reset state"""
        self.performance_history.clear()
        self.trade_history.clear()
        self.backtest_results.clear()
        
        # Clear replay engine data
        if hasattr(self, 'replay_engine'):
            self.replay_engine.data = None
            self.replay_engine.trades = []
            self.replay_engine.signals = []
            # Don't reset current_index - let it be set by the replay engine initialization
            self.replay_engine.start_play_index = 0
        
        # Clear current instrument/timeframe
        self.current_instrument = None
        self.current_timeframe = None
        
        logger.info("🧹 Replay service cache cleared")

    def set_start_position(self, date: Optional[str] = None, position: Optional[int] = None, context_candles: int = 50) -> Dict[str, Any]:
        """Set replay start position by date or position index"""
        try:
            logger.info(f"🎯 Setting replay start position: date={date}, position={position}")
            
            if self.replay_engine.data is None or self.replay_engine.data.empty:
                return {
                    "success": False,
                    "message": "No replay data available"
                }
            
            target_index = 0
            
            if date:
                # Convert date string to datetime and find matching index
                try:
                    target_datetime = pd.to_datetime(date)
                    # Make timezone-aware if the replay data is timezone-aware
                    if hasattr(self.replay_engine.data.index, 'tz') and self.replay_engine.data.index.tz is not None:
                        if target_datetime.tz is None:
                            target_datetime = target_datetime.tz_localize('UTC')
                        else:
                            target_datetime = target_datetime.tz_convert('UTC')
                    
                    # Find the closest index to the target datetime
                    time_diff = abs(self.replay_engine.data.index - target_datetime)
                    target_index = time_diff.argmin()
                    logger.info(f"🎯 Found target index {target_index} for date {date}")
                except Exception as e:
                    logger.error(f"Error parsing date {date}: {e}")
                    return {
                        "success": False,
                        "message": f"Invalid date format: {date}"
                    }
            elif position is not None:
                # Use position index directly
                target_index = max(0, min(position, len(self.replay_engine.data) - 1))
                logger.info(f"🎯 Using position index {target_index}")
            else:
                return {
                    "success": False,
                    "message": "Either date or position must be provided"
                }
            
            # Set the replay engine to the target position
            self.replay_engine.current_index = target_index
            self.replay_engine.is_playing = False  # Pause replay initially
            
            # Get the target date for confirmation
            target_date = self.replay_engine.data.index[target_index]
            
            logger.info(f"✅ Replay position set to index {target_index} (date: {target_date})")
            
            return {
                "success": True,
                "message": f"Replay position set to {target_date}",
                "data": {
                    "position": int(target_index),  # Convert to native int
                    "date": str(target_date),
                    "total_candles": int(len(self.replay_engine.data)),  # Convert to native int
                    "context_candles": int(context_candles)  # Convert to native int
                }
            }
            
        except Exception as e:
            logger.error(f"Error setting replay start position: {e}")
            return {
                "success": False,
                "message": f"Error setting replay start position: {str(e)}"
            }

# Global instance
_replay_service = None

def get_replay_service() -> ReplayService:
    """Get global replay service instance"""
    global _replay_service
    if _replay_service is None:
        _replay_service = ReplayService()
    return _replay_service