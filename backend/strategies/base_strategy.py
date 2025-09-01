"""
Base Strategy Class for TrimurtiFX

This module provides the base class that all trading strategies should inherit from.
It defines the common interface and structure for all strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass
from enum import Enum


class SignalType(Enum):
    """Signal types for trading decisions"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class StrategyStatus(Enum):
    """Strategy status enumeration"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PAUSED = "PAUSED"


@dataclass
class TradeSignal:
    """Data class for trade signals"""
    signal_type: SignalType
    strength: float  # 0.0 to 1.0
    reason: str
    entry_price: float
    timestamp: pd.Timestamp
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class StrategyResult:
    """Data class for strategy analysis results"""
    signals: List[TradeSignal]
    analysis: Dict[str, Any]
    status: StrategyStatus
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseStrategy(ABC):
    """
    Base class for all trading strategies
    
    This class provides the common interface and structure that all strategies
    must implement. It includes basic functionality for data validation,
    signal generation, and strategy management.
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize the base strategy
        
        Args:
            name: Strategy name
            description: Strategy description
        """
        self.name = name
        self.description = description
        self.status = StrategyStatus.INACTIVE
        self.parameters = {}
        self.metadata = {}
        
    @abstractmethod
    def analyze(self, data: pd.DataFrame) -> StrategyResult:
        """
        Analyze market data and generate trading signals
        
        Args:
            data: Market data DataFrame with OHLCV columns
            
        Returns:
            StrategyResult containing signals and analysis
        """
        pass
    
    @abstractmethod
    def get_required_indicators(self) -> List[str]:
        """
        Get list of required indicators for this strategy
        
        Returns:
            List of indicator names required by this strategy
        """
        pass
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate that the data meets the strategy's requirements
        
        Args:
            data: Market data DataFrame
            
        Returns:
            True if data is valid, False otherwise
        """
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        
        if data is None or data.empty:
            return False
            
        # Check for required columns
        for col in required_columns:
            if col not in data.columns:
                return False
                
        # Check for sufficient data points
        if len(data) < 50:  # Minimum data points
            return False
            
        return True
    
    def set_parameters(self, parameters: Dict[str, Any]) -> None:
        """
        Set strategy parameters
        
        Args:
            parameters: Dictionary of parameter names and values
        """
        self.parameters.update(parameters)
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get current strategy parameters
        
        Returns:
            Dictionary of current parameters
        """
        return self.parameters.copy()
    
    def activate(self) -> None:
        """Activate the strategy"""
        self.status = StrategyStatus.ACTIVE
    
    def deactivate(self) -> None:
        """Deactivate the strategy"""
        self.status = StrategyStatus.INACTIVE
    
    def pause(self) -> None:
        """Pause the strategy"""
        self.status = StrategyStatus.PAUSED
    
    def is_active(self) -> bool:
        """
        Check if strategy is active
        
        Returns:
            True if strategy is active
        """
        return self.status == StrategyStatus.ACTIVE
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get strategy information
        
        Returns:
            Dictionary with strategy information
        """
        return {
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'parameters': self.parameters,
            'metadata': self.metadata
        }
    
    def __str__(self) -> str:
        return f"{self.name}: {self.description}"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}')>" 