"""
Strategies Router for QuantBotForex API

This router provides endpoints for managing trading strategies,
their execution during replay, and strategy performance analysis.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from services.strategy_manager import get_strategy_manager

router = APIRouter()

# Request/Response Models
class StrategyConfigRequest(BaseModel):
    strategy_name: str
    parameters: Dict[str, Any] = {}
    description: str = ""

class StrategyActivationRequest(BaseModel):
    strategy_name: str

class StrategyParameterUpdateRequest(BaseModel):
    parameters: Dict[str, Any]

class StrategyExecutionRequest(BaseModel):
    strategy_name: str
    data_index: int

# Strategy Management Endpoints
@router.get("/")
async def list_strategies():
    """List all available strategies"""
    try:
        strategy_manager = get_strategy_manager()
        result = strategy_manager.get_all_strategies_info()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{strategy_name}")
async def get_strategy_info(strategy_name: str):
    """Get information about a specific strategy"""
    try:
        strategy_manager = get_strategy_manager()
        result = strategy_manager.get_strategy_info(strategy_name)
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/register")
async def register_strategy(request: StrategyConfigRequest):
    """Register a new strategy"""
    try:
        strategy_manager = get_strategy_manager()
        result = strategy_manager.register_strategy(
            request.strategy_name,
            {
                "parameters": request.parameters,
                "description": request.description
            }
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/activate")
async def activate_strategy(request: StrategyActivationRequest):
    """Activate a strategy"""
    try:
        strategy_manager = get_strategy_manager()
        result = strategy_manager.activate_strategy(request.strategy_name)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/deactivate")
async def deactivate_strategy(request: StrategyActivationRequest):
    """Deactivate a strategy"""
    try:
        strategy_manager = get_strategy_manager()
        result = strategy_manager.deactivate_strategy(request.strategy_name)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{strategy_name}/parameters")
async def update_strategy_parameters(strategy_name: str, request: StrategyParameterUpdateRequest):
    """Update strategy parameters"""
    try:
        strategy_manager = get_strategy_manager()
        result = strategy_manager.update_strategy_parameters(strategy_name, request.parameters)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Strategy Execution Endpoints
@router.post("/execute")
async def execute_strategy(request: StrategyExecutionRequest):
    """Execute a strategy on current replay data"""
    try:
        from services.replay_service import get_replay_service
        
        replay_service = get_replay_service()
        strategy_manager = get_strategy_manager()
        
        # Get current replay data
        replay_data = replay_service.get_replay_data()
        
        if not replay_data.get("success", False):
            raise HTTPException(status_code=400, detail="No replay data available")
        
        # Extract data from replay
        data_df = replay_data.get("data", {})
        if not data_df:
            raise HTTPException(status_code=400, detail="No data available for strategy execution")
        
        # Execute strategy
        results = strategy_manager.execute_strategies_on_data(data_df, request.data_index)
        
        return {
            "success": True,
            "message": f"Strategy {request.strategy_name} executed",
            "data": {
                "strategy_name": request.strategy_name,
                "execution_results": [
                    {
                        "timestamp": r.timestamp.isoformat(),
                        "signal": {
                            "type": r.signal.signal_type.value if r.signal and hasattr(r.signal.signal_type, 'value') else str(r.signal.signal_type) if r.signal else None,
                            "price": getattr(r.signal, 'price', getattr(r.signal, 'entry_price', 0)) if r.signal else None,
                            "strength": r.signal.strength if r.signal else None,
                            "reason": r.signal.reason if r.signal else None
                        } if r.signal else None,
                        "execution_time_ms": r.execution_time_ms
                    } for r in results
                ]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{strategy_name}/signals")
async def get_strategy_signals(strategy_name: str):
    """Get signals from a specific strategy for current replay data"""
    try:
        from services.replay_service import get_replay_service
        
        replay_service = get_replay_service()
        strategy_manager = get_strategy_manager()
        
        # Get current replay data
        replay_data = replay_service.get_replay_data()
        
        if not replay_data.get("success", False):
            raise HTTPException(status_code=400, detail="No replay data available")
        
        # Extract data from replay
        data_df = replay_data.get("data", {})
        if not data_df:
            raise HTTPException(status_code=400, detail="No data available for signal generation")
        
        # Get strategy signals
        signals = strategy_manager.get_strategy_signals(strategy_name, data_df)
        
        return {
            "success": True,
            "message": f"Signals retrieved for strategy {strategy_name}",
            "data": {
                "strategy_name": strategy_name,
                "signals": signals,
                "total_signals": len(signals)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/signals/all")
async def get_all_strategy_signals():
    """Get signals from all active strategies"""
    try:
        from services.replay_service import get_replay_service
        
        replay_service = get_replay_service()
        strategy_manager = get_strategy_manager()
        
        # Get current replay data
        replay_data = replay_service.get_replay_data()
        
        if not replay_data.get("success", False):
            raise HTTPException(status_code=400, detail="No replay data available")
        
        # Extract data from replay
        data_df = replay_data.get("data", {})
        if not data_df:
            raise HTTPException(status_code=400, detail="No data available for signal generation")
        
        # Get all strategy signals
        all_signals = strategy_manager.get_all_strategy_signals(data_df)
        
        return {
            "success": True,
            "message": "Signals retrieved for all active strategies",
            "data": {
                "signals": all_signals,
                "total_strategies": len(all_signals),
                "active_strategies": list(all_signals.keys())
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Performance and Analytics Endpoints
@router.get("/performance/{strategy_name}")
async def get_strategy_performance(strategy_name: str):
    """Get performance metrics for a specific strategy"""
    try:
        strategy_manager = get_strategy_manager()
        
        # For now, return basic info - this could be enhanced with actual performance calculation
        strategy_info = strategy_manager.get_strategy_info(strategy_name)
        
        if not strategy_info["success"]:
            raise HTTPException(status_code=404, detail=strategy_info["message"])
        
        return {
            "success": True,
            "message": f"Performance metrics for strategy {strategy_name}",
            "data": {
                "strategy_name": strategy_name,
                "is_active": strategy_info["data"].get("is_active", False),
                "execution_stats": strategy_manager.get_execution_stats()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/execution/stats")
async def get_execution_statistics():
    """Get overall strategy execution statistics"""
    try:
        strategy_manager = get_strategy_manager()
        stats = strategy_manager.get_execution_stats()
        
        return {
            "success": True,
            "message": "Execution statistics retrieved",
            "data": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/execution/history")
async def clear_execution_history():
    """Clear strategy execution history"""
    try:
        strategy_manager = get_strategy_manager()
        strategy_manager.clear_execution_history()
        
        return {
            "success": True,
            "message": "Execution history cleared",
            "data": {}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Strategy Testing Endpoints
@router.post("/test/{strategy_name}")
async def test_strategy(strategy_name: str, test_data: Dict[str, Any]):
    """Test a strategy with provided data"""
    try:
        strategy_manager = get_strategy_manager()
        
        if strategy_name not in strategy_manager.registered_strategies:
            raise HTTPException(status_code=404, detail=f"Strategy {strategy_name} not found")
        
        # Convert test data to DataFrame
        import pandas as pd
        data_df = pd.DataFrame(test_data.get("data", []))
        
        if data_df.empty:
            raise HTTPException(status_code=400, detail="No test data provided")
        
        # Execute strategy on test data
        results = strategy_manager.execute_strategies_on_data(data_df, len(data_df) - 1)
        
        return {
            "success": True,
            "message": f"Strategy {strategy_name} tested successfully",
            "data": {
                "strategy_name": strategy_name,
                "test_results": results,
                "data_points": len(data_df)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 