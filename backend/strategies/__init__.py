"""
QuantBotForex Backend Strategies Module

This module contains all trading strategies that can be used with the replay system.
Strategies are loaded dynamically and can be activated/deactivated during replay sessions.
"""

from .base_strategy import BaseStrategy, SignalType, StrategyStatus, TradeSignal, StrategyResult
from .momentum_following_strategy import RangeOfTheDayStrategy

# Strategy registry - maps strategy names to their classes
STRATEGY_REGISTRY = {
    "RangeOfTheDay": RangeOfTheDayStrategy,
    "MomentumFollowing": RangeOfTheDayStrategy,  # Alias for backward compatibility
}

def get_strategy_class(strategy_name: str):
    """Get strategy class by name"""
    return STRATEGY_REGISTRY.get(strategy_name)

def get_available_strategies():
    """Get list of available strategy names"""
    return list(STRATEGY_REGISTRY.keys())

def create_strategy_instance(strategy_name: str, **kwargs):
    """Create a new instance of a strategy by name"""
    strategy_class = get_strategy_class(strategy_name)
    if strategy_class:
        return strategy_class(**kwargs)
    raise ValueError(f"Strategy '{strategy_name}' not found")

__all__ = [
    "BaseStrategy",
    "SignalType", 
    "StrategyStatus",
    "TradeSignal",
    "StrategyResult",
    "RangeOfTheDayStrategy",
    "get_strategy_class",
    "get_available_strategies",
    "create_strategy_instance",
    "STRATEGY_REGISTRY"
] 