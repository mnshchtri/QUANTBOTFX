"""
Strategy Manager Service for QuantBotForex

This service manages trading strategies, their execution during replay,
and provides a unified interface for strategy analysis and signal generation.
"""

import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import asyncio

# Import strategies from backend
from strategies import (
    get_strategy_class,
    get_available_strategies,
    create_strategy_instance,
    BaseStrategy,
    TradeSignal,
    StrategyResult,
)

logger = logging.getLogger(__name__)


@dataclass
class StrategyExecutionResult:
    """Result of strategy execution on a specific data point"""

    timestamp: datetime
    signal: Optional[TradeSignal]
    data_point: Dict[str, Any]
    strategy_name: str
    execution_time_ms: float


@dataclass
class StrategyPerformance:
    """Performance metrics for a strategy"""

    strategy_name: str
    total_signals: int
    buy_signals: int
    sell_signals: int
    success_rate: float
    total_pnl: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    avg_win: float
    avg_loss: float


class StrategyManager:
    """
    Manages trading strategies and their execution during replay sessions
    """

    def __init__(self):
        self.registered_strategies: Dict[str, BaseStrategy] = {}
        self.active_strategies: Dict[str, Dict[str, Any]] = {}
        self.execution_history: List[StrategyExecutionResult] = []
        self.performance_metrics: Dict[str, StrategyPerformance] = {}

        # Strategy parameters and configurations
        self.strategy_configs: Dict[str, Dict[str, Any]] = {}

        # Initialize with available strategies
        self._initialize_default_strategies()

    def _initialize_default_strategies(self):
        """Initialize default strategies"""
        try:
            available_strategies = get_available_strategies()
            logger.info(f"Available strategies: {available_strategies}")

            for strategy_name in available_strategies:
                try:
                    strategy_instance = create_strategy_instance(strategy_name)
                    self.registered_strategies[strategy_name] = strategy_instance
                    logger.info(f"✅ Registered strategy: {strategy_name}")
                except Exception as e:
                    logger.error(f"Failed to register strategy {strategy_name}: {e}")

        except Exception as e:
            logger.error(f"Error initializing default strategies: {e}")

    def register_strategy(
        self, strategy_name: str, strategy_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Register a new strategy with configuration"""
        try:
            if strategy_name in self.registered_strategies:
                return {
                    "success": False,
                    "message": f"Strategy {strategy_name} already registered",
                    "data": {},
                }

            # Create strategy instance
            strategy_instance = create_strategy_instance(
                strategy_name, **strategy_config.get("parameters", {})
            )

            # Store strategy and configuration
            self.registered_strategies[strategy_name] = strategy_instance
            self.strategy_configs[strategy_name] = strategy_config

            logger.info(f"🎯 Strategy registered: {strategy_name}")

            return {
                "success": True,
                "message": f"Strategy {strategy_name} registered successfully",
                "data": {"strategy_name": strategy_name, "config": strategy_config},
            }

        except Exception as e:
            logger.error(f"Error registering strategy: {e}")
            return {
                "success": False,
                "message": f"Error registering strategy: {str(e)}",
                "data": {},
            }

    def activate_strategy(self, strategy_name: str) -> Dict[str, Any]:
        """Activate a registered strategy"""
        try:
            if strategy_name not in self.registered_strategies:
                return {
                    "success": False,
                    "message": f"Strategy {strategy_name} not found",
                    "data": {},
                }

            # Activate strategy
            strategy = self.registered_strategies[strategy_name]
            strategy.activate()

            self.active_strategies[strategy_name] = {
                "activated_at": datetime.now().isoformat(),
                "config": self.strategy_configs.get(strategy_name, {}),
                "performance": {"trades": 0, "pnl": 0.0},
            }

            logger.info(f"🎯 Strategy activated: {strategy_name}")

            return {
                "success": True,
                "message": f"Strategy {strategy_name} activated",
                "data": {
                    "strategy_name": strategy_name,
                    "active_strategies": list(self.active_strategies.keys()),
                },
            }

        except Exception as e:
            logger.error(f"Error activating strategy: {e}")
            return {
                "success": False,
                "message": f"Error activating strategy: {str(e)}",
                "data": {},
            }

    def deactivate_strategy(self, strategy_name: str) -> Dict[str, Any]:
        """Deactivate an active strategy"""
        try:
            if strategy_name not in self.active_strategies:
                return {
                    "success": False,
                    "message": f"Strategy {strategy_name} not active",
                    "data": {},
                }

            # Deactivate strategy
            strategy = self.registered_strategies[strategy_name]
            strategy.deactivate()

            # Remove from active strategies
            del self.active_strategies[strategy_name]

            logger.info(f"🎯 Strategy deactivated: {strategy_name}")

            return {
                "success": True,
                "message": f"Strategy {strategy_name} deactivated",
                "data": {
                    "strategy_name": strategy_name,
                    "active_strategies": list(self.active_strategies.keys()),
                },
            }

        except Exception as e:
            logger.error(f"Error deactivating strategy: {e}")
            return {
                "success": False,
                "message": f"Error deactivating strategy: {str(e)}",
                "data": {},
            }

    def execute_strategies_on_data(
        self, data: pd.DataFrame, current_index: int
    ) -> List[StrategyExecutionResult]:
        """Execute all active strategies on current data point"""
        results = []

        if data is None or data.empty:
            logger.warning("No data provided for strategy execution")
            return results

        # Get current data point (up to current_index)
        current_data = (
            data.iloc[: current_index + 1] if current_index < len(data) else data
        )

        for strategy_name, strategy_info in self.active_strategies.items():
            try:
                start_time = datetime.now()

                strategy = self.registered_strategies[strategy_name]

                # Execute strategy analysis
                result = strategy.analyze(current_data)

                execution_time = (datetime.now() - start_time).total_seconds() * 1000

                # Get current data point
                current_point = (
                    data.iloc[current_index] if current_index < len(data) else {}
                )

                # Create execution result
                execution_result = StrategyExecutionResult(
                    timestamp=datetime.now(),
                    signal=result.signals[-1] if result.signals else None,
                    data_point=current_point.to_dict()
                    if hasattr(current_point, "to_dict")
                    else {},
                    strategy_name=strategy_name,
                    execution_time_ms=execution_time,
                )

                results.append(execution_result)

                # Store in execution history
                self.execution_history.append(execution_result)

                logger.debug(
                    f"Strategy {strategy_name} executed in {execution_time:.2f}ms"
                )

            except Exception as e:
                logger.error(f"Error executing strategy {strategy_name}: {e}")
                continue

        return results

    def get_strategy_signals(
        self, strategy_name: str, data: pd.DataFrame
    ) -> List[Dict[str, Any]]:
        """Get all signals from a specific strategy for the given data"""
        try:
            if strategy_name not in self.registered_strategies:
                return []

            strategy = self.registered_strategies[strategy_name]
            result = strategy.analyze(data)

            signals = []
            for i, signal in enumerate(result.signals):
                signals.append(
                    {
                        "index": i,
                        "timestamp": signal.timestamp.isoformat()
                        if hasattr(signal.timestamp, "isoformat")
                        else str(signal.timestamp),
                        "type": signal.signal_type.value.lower()
                        if hasattr(signal.signal_type, "value")
                        else str(signal.signal_type),
                        "price": getattr(
                            signal, "price", getattr(signal, "entry_price", 0)
                        ),
                        "strength": signal.strength,
                        "reason": signal.reason,
                    }
                )

            return signals

        except Exception as e:
            logger.error(f"Error getting signals from strategy {strategy_name}: {e}")
            return []

    def get_all_strategy_signals(
        self, data: pd.DataFrame
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get signals from all active strategies"""
        all_signals = {}

        for strategy_name in self.active_strategies.keys():
            signals = self.get_strategy_signals(strategy_name, data)
            if signals:
                all_signals[strategy_name] = signals

        return all_signals

    def update_strategy_parameters(
        self, strategy_name: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update strategy parameters"""
        try:
            if strategy_name not in self.registered_strategies:
                return {
                    "success": False,
                    "message": f"Strategy {strategy_name} not found",
                    "data": {},
                }

            strategy = self.registered_strategies[strategy_name]
            strategy.set_parameters(parameters)

            # Update stored configuration
            if strategy_name in self.strategy_configs:
                self.strategy_configs[strategy_name]["parameters"] = parameters

            logger.info(f"📊 Strategy parameters updated: {strategy_name}")

            return {
                "success": True,
                "message": f"Strategy parameters updated for {strategy_name}",
                "data": {"strategy_name": strategy_name, "parameters": parameters},
            }

        except Exception as e:
            logger.error(f"Error updating strategy parameters: {e}")
            return {
                "success": False,
                "message": f"Error updating strategy parameters: {str(e)}",
                "data": {},
            }

    def get_strategy_info(self, strategy_name: str) -> Dict[str, Any]:
        """Get information about a specific strategy"""
        try:
            if strategy_name not in self.registered_strategies:
                return {
                    "success": False,
                    "message": f"Strategy {strategy_name} not found",
                    "data": {},
                }

            strategy = self.registered_strategies[strategy_name]
            info = strategy.get_info()

            # Add activation status
            info["is_active"] = strategy_name in self.active_strategies
            info["config"] = self.strategy_configs.get(strategy_name, {})

            return {
                "success": True,
                "message": f"Strategy info retrieved for {strategy_name}",
                "data": info,
            }

        except Exception as e:
            logger.error(f"Error getting strategy info: {e}")
            return {
                "success": False,
                "message": f"Error getting strategy info: {str(e)}",
                "data": {},
            }

    def get_all_strategies_info(self) -> Dict[str, Any]:
        """Get information about all registered strategies"""
        strategies_info = {}

        for strategy_name in self.registered_strategies.keys():
            info = self.get_strategy_info(strategy_name)
            if info["success"]:
                strategies_info[strategy_name] = info["data"]

        return {
            "success": True,
            "message": "All strategies info retrieved",
            "data": {
                "strategies": strategies_info,
                "total_strategies": len(strategies_info),
                "active_strategies": list(self.active_strategies.keys()),
            },
        }

    def clear_execution_history(self):
        """Clear execution history"""
        self.execution_history.clear()
        logger.info("Execution history cleared")

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        if not self.execution_history:
            return {"total_executions": 0, "avg_execution_time": 0, "total_signals": 0}

        total_executions = len(self.execution_history)
        avg_execution_time = (
            sum(r.execution_time_ms for r in self.execution_history) / total_executions
        )
        total_signals = len([r for r in self.execution_history if r.signal])

        return {
            "total_executions": total_executions,
            "avg_execution_time": avg_execution_time,
            "total_signals": total_signals,
            "last_execution": self.execution_history[-1].timestamp.isoformat()
            if self.execution_history
            else None,
        }


# Global instance
_strategy_manager = None


def get_strategy_manager() -> StrategyManager:
    """Get global strategy manager instance"""
    global _strategy_manager
    if _strategy_manager is None:
        _strategy_manager = StrategyManager()
    return _strategy_manager
