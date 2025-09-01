"""
Backtrader Service for QuantBotForex

This service integrates with backtrader to run backtests on user-developed strategies
and stores results for use as overlays in replay mode.
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class BacktestResult:
    """Container for backtest results"""
    
    def __init__(self, strategy_name: str, instrument: str, timeframe: str):
        self.strategy_name = strategy_name
        self.instrument = instrument
        self.timeframe = timeframe
        self.start_date = None
        self.end_date = None
        self.total_return = 0.0
        self.max_drawdown = 0.0
        self.sharpe_ratio = 0.0
        self.total_trades = 0
        self.win_rate = 0.0
        self.signals = []
        self.trades = []
        self.equity_curve = []
        self.parameters = {}
        self.backtest_date = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "strategy_name": self.strategy_name,
            "instrument": self.instrument,
            "timeframe": self.timeframe,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "total_return": self.total_return,
            "max_drawdown": self.max_drawdown,
            "sharpe_ratio": self.sharpe_ratio,
            "total_trades": self.total_trades,
            "win_rate": self.win_rate,
            "signals": self.signals,
            "trades": self.trades,
            "equity_curve": self.equity_curve,
            "parameters": self.parameters,
            "backtest_date": self.backtest_date.isoformat()
        }

class BacktraderService:
    """
    Service for running backtests using backtrader and managing results
    """
    
    def __init__(self):
        self.backtest_results_dir = Path("storage/backtests")
        self.backtest_results_dir.mkdir(parents=True, exist_ok=True)
        
        # Active backtests
        self.active_backtests: Dict[str, Dict[str, Any]] = {}
        
        # Load existing results
        self._load_existing_results()
    
    def _load_existing_results(self):
        """Load existing backtest results from storage"""
        try:
            for result_file in self.backtest_results_dir.glob("*.json"):
                try:
                    with open(result_file, 'r') as f:
                        data = json.load(f)
                        logger.info(f"📊 Loaded backtest result: {data.get('strategy_name', 'Unknown')}")
                except Exception as e:
                    logger.error(f"Error loading backtest result {result_file}: {e}")
        except Exception as e:
            logger.error(f"Error loading existing backtest results: {e}")
    
    def run_backtest(self, strategy_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a backtest using backtrader
        
        Args:
            strategy_config: Strategy configuration including:
                - strategy_name: Name of the strategy
                - instrument: Trading instrument
                - timeframe: Timeframe for backtest
                - start_date: Start date for backtest
                - end_date: End date for backtest
                - parameters: Strategy parameters
                - indicators: List of indicators to use
        
        Returns:
            Backtest result with performance metrics and signals
        """
        try:
            strategy_name = strategy_config.get("strategy_name")
            instrument = strategy_config.get("instrument")
            timeframe = strategy_config.get("timeframe")
            
            logger.info(f"🚀 Starting backtest for strategy: {strategy_name}")
            logger.info(f"📊 Instrument: {instrument}, Timeframe: {timeframe}")
            
            # TODO: Implement actual backtrader integration
            # For now, create a mock result
            
            result = self._create_mock_backtest_result(strategy_config)
            
            # Store the result
            self._store_backtest_result(result)
            
            logger.info(f"✅ Backtest completed for {strategy_name}")
            
            return {
                "success": True,
                "message": f"Backtest completed for {strategy_name}",
                "data": result.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            return {
                "success": False,
                "message": f"Error running backtest: {str(e)}",
                "data": {}
            }
    
    def _create_mock_backtest_result(self, strategy_config: Dict[str, Any]) -> BacktestResult:
        """Create a mock backtest result for testing (will be replaced with actual backtrader)"""
        strategy_name = strategy_config.get("strategy_name")
        instrument = strategy_config.get("instrument")
        timeframe = strategy_config.get("timeframe")
        
        result = BacktestResult(strategy_name, instrument, timeframe)
        
        # Mock data
        result.start_date = datetime.now() - timedelta(days=30)
        result.end_date = datetime.now()
        result.total_return = 0.085  # 8.5%
        result.max_drawdown = 0.023  # 2.3%
        result.sharpe_ratio = 1.45
        result.total_trades = 24
        result.win_rate = 0.625  # 62.5%
        
        # Mock signals (these would come from actual backtest)
        result.signals = [
            {
                "timestamp": (result.start_date + timedelta(days=i)).isoformat(),
                "type": "buy" if i % 3 == 0 else "sell",
                "price": 100.0 + i * 0.1,
                "strength": 0.7 + (i % 3) * 0.1,
                "reason": f"Signal {i+1} from {strategy_name}"
            }
            for i in range(10)
        ]
        
        # Mock trades
        result.trades = [
            {
                "entry_time": (result.start_date + timedelta(days=i)).isoformat(),
                "exit_time": (result.start_date + timedelta(days=i+1)).isoformat(),
                "entry_price": 100.0 + i * 0.1,
                "exit_price": 100.0 + (i+1) * 0.1,
                "type": "long" if i % 2 == 0 else "short",
                "pnl": 0.1 if i % 2 == 0 else -0.1,
                "size": 1000
            }
            for i in range(5)
        ]
        
        result.parameters = strategy_config.get("parameters", {})
        
        return result
    
    def _store_backtest_result(self, result: BacktestResult):
        """Store backtest result to file"""
        try:
            filename = f"{result.strategy_name}_{result.instrument}_{result.timeframe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.backtest_results_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(result.to_dict(), f, indent=2)
            
            logger.info(f"💾 Stored backtest result: {filepath}")
            
        except Exception as e:
            logger.error(f"Error storing backtest result: {e}")
    
    def get_backtest_results(self, strategy_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get backtest results, optionally filtered by strategy name"""
        try:
            results = []
            
            for result_file in self.backtest_results_dir.glob("*.json"):
                try:
                    with open(result_file, 'r') as f:
                        data = json.load(f)
                        
                        if strategy_name is None or data.get("strategy_name") == strategy_name:
                            results.append(data)
                            
                except Exception as e:
                    logger.error(f"Error reading backtest result {result_file}: {e}")
                    continue
            
            # Sort by backtest date (newest first)
            results.sort(key=lambda x: x.get("backtest_date", ""), reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting backtest results: {e}")
            return []
    
    def get_strategy_signals(self, strategy_name: str, instrument: str, timeframe: str, 
                           start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get strategy signals for a specific period (used by replay system)"""
        try:
            # Get backtest results for this strategy
            results = self.get_backtest_results(strategy_name)
            
            if not results:
                logger.warning(f"No backtest results found for strategy: {strategy_name}")
                return []
            
            # Find the most recent result for this instrument/timeframe
            matching_results = [
                r for r in results 
                if r.get("instrument") == instrument and r.get("timeframe") == timeframe
            ]
            
            if not matching_results:
                logger.warning(f"No backtest results found for {strategy_name} on {instrument} {timeframe}")
                return []
            
            # Use the most recent result
            latest_result = max(matching_results, key=lambda x: x.get("backtest_date", ""))
            
            # Filter signals by date range
            filtered_signals = []
            for signal in latest_result.get("signals", []):
                try:
                    signal_time = datetime.fromisoformat(signal["timestamp"])
                    
                    # Make both dates timezone-aware for comparison
                    if signal_time.tzinfo is None:
                        signal_time = signal_time.replace(tzinfo=start_date.tzinfo)
                    
                    if start_date <= signal_time <= end_date:
                        filtered_signals.append(signal)
                except Exception as e:
                    logger.warning(f"Error parsing signal timestamp: {e}")
                    continue
            
            logger.info(f"📊 Found {len(filtered_signals)} signals for {strategy_name} in date range")
            
            return filtered_signals
            
        except Exception as e:
            logger.error(f"Error getting strategy signals: {e}")
            return []
    
    def delete_backtest_result(self, result_id: str) -> Dict[str, Any]:
        """Delete a backtest result"""
        try:
            # Find and delete the result file
            for result_file in self.backtest_results_dir.glob("*.json"):
                if result_id in result_file.name:
                    result_file.unlink()
                    logger.info(f"🗑️ Deleted backtest result: {result_file}")
                    
                    return {
                        "success": True,
                        "message": "Backtest result deleted successfully",
                        "data": {}
                    }
            
            return {
                "success": False,
                "message": "Backtest result not found",
                "data": {}
            }
            
        except Exception as e:
            logger.error(f"Error deleting backtest result: {e}")
            return {
                "success": False,
                "message": f"Error deleting backtest result: {str(e)}",
                "data": {}
            }
    
    def get_backtest_status(self) -> Dict[str, Any]:
        """Get overall backtest service status"""
        try:
            total_results = len(list(self.backtest_results_dir.glob("*.json")))
            active_backtests = len(self.active_backtests)
            
            return {
                "success": True,
                "message": "Backtest service status retrieved",
                "data": {
                    "total_results": total_results,
                    "active_backtests": active_backtests,
                    "storage_directory": str(self.backtest_results_dir),
                    "status": "healthy"
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting backtest status: {e}")
            return {
                "success": False,
                "message": f"Error getting backtest status: {str(e)}",
                "data": {}
            }

    def validate_data_alignment(self, instrument: str, timeframe: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Validate that backtest data aligns with replay data"""
        try:
            # Check if we have backtest results for this exact timeframe
            matching_results = []
            
            for result_file in self.backtest_results_dir.glob("*.json"):
                try:
                    with open(result_file, 'r') as f:
                        data = json.load(f)
                        
                        if (data.get("instrument") == instrument and 
                            data.get("timeframe") == timeframe):
                            
                            # Check date range overlap
                            result_start = datetime.fromisoformat(data.get("start_date", ""))
                            result_end = datetime.fromisoformat(data.get("end_date", ""))
                            
                            # Check if there's significant overlap
                            overlap_start = max(start_date, result_start)
                            overlap_end = min(end_date, result_end)
                            
                            if overlap_start < overlap_end:
                                overlap_days = (overlap_end - overlap_start).days
                                total_days = (end_date - start_date).days
                                overlap_percentage = (overlap_days / total_days) * 100
                                
                                matching_results.append({
                                    "file": result_file.name,
                                    "strategy_name": data.get("strategy_name"),
                                    "overlap_percentage": overlap_percentage,
                                    "result_start": result_start,
                                    "result_end": result_end,
                                    "data": data
                                })
                                
                except Exception as e:
                    logger.warning(f"Error reading backtest result {result_file}: {e}")
                    continue
            
            # Sort by overlap percentage (highest first)
            matching_results.sort(key=lambda x: x["overlap_percentage"], reverse=True)
            
            return {
                "success": True,
                "message": f"Data alignment validation completed",
                "data": {
                    "requested_range": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "instrument": instrument,
                        "timeframe": timeframe
                    },
                    "matching_results": matching_results,
                    "best_match": matching_results[0] if matching_results else None,
                    "total_matches": len(matching_results)
                }
            }
            
        except Exception as e:
            logger.error(f"Error validating data alignment: {e}")
            return {
                "success": False,
                "message": f"Error validating data alignment: {str(e)}",
                "data": {}
            }
    
    def create_aligned_backtest(self, strategy_name: str, instrument: str, timeframe: str, 
                              start_date: datetime, end_date: datetime, 
                              parameters: Dict[str, Any] = {}) -> Dict[str, Any]:
        """Create a backtest that aligns with the replay data timeframe"""
        try:
            logger.info(f"🎯 Creating aligned backtest for {strategy_name}")
            logger.info(f"📊 Timeframe: {instrument} {timeframe}")
            logger.info(f"📅 Date range: {start_date} to {end_date}")
            
            # Create strategy configuration with exact replay timeframe
            strategy_config = {
                "strategy_name": strategy_name,
                "instrument": instrument,
                "timeframe": timeframe,
                "start_date": start_date,
                "end_date": end_date,
                "parameters": parameters,
                "indicators": ["RSI", "MACD", "SMA"]  # Default indicators
            }
            
            # Run backtest
            result = self.run_backtest(strategy_config)
            
            if result["success"]:
                logger.info(f"✅ Aligned backtest created successfully for {strategy_name}")
            else:
                logger.error(f"❌ Failed to create aligned backtest for {strategy_name}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating aligned backtest: {e}")
            return {
                "success": False,
                "message": f"Error creating aligned backtest: {str(e)}",
                "data": {}
            }

# Global instance
_backtrader_service = None

def get_backtrader_service() -> BacktraderService:
    """Get global backtrader service instance"""
    global _backtrader_service
    if _backtrader_service is None:
        _backtrader_service = BacktraderService()
    return _backtrader_service
