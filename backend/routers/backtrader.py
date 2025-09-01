"""
Backtrader Router for QuantBotForex API

This router provides endpoints for running backtests using backtrader,
managing backtest results, and integrating with the replay system.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from services.backtrader_service import get_backtrader_service

router = APIRouter()

# Request/Response Models
class BacktestRequest(BaseModel):
    strategy_name: str
    instrument: str
    timeframe: str
    start_date: str
    end_date: str
    parameters: Dict[str, Any] = {}
    indicators: List[str] = []

class BacktestResultResponse(BaseModel):
    strategy_name: str
    instrument: str
    timeframe: str
    total_return: float
    max_drawdown: float
    sharpe_ratio: float
    total_trades: int
    win_rate: float

# Backtest Management Endpoints
@router.post("/run")
async def run_backtest(request: BacktestRequest):
    """Run a new backtest"""
    try:
        backtrader_service = get_backtrader_service()
        
        # Convert string dates to datetime
        from datetime import datetime
        start_date = datetime.fromisoformat(request.start_date)
        end_date = datetime.fromisoformat(request.end_date)
        
        # Prepare strategy configuration
        strategy_config = {
            "strategy_name": request.strategy_name,
            "instrument": request.instrument,
            "timeframe": request.timeframe,
            "start_date": start_date,
            "end_date": end_date,
            "parameters": request.parameters,
            "indicators": request.indicators
        }
        
        # Run backtest
        result = backtrader_service.run_backtest(strategy_config)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results")
async def get_backtest_results(strategy_name: Optional[str] = None):
    """Get backtest results, optionally filtered by strategy name"""
    try:
        backtrader_service = get_backtrader_service()
        results = backtrader_service.get_backtest_results(strategy_name)
        
        return {
            "success": True,
            "message": f"Retrieved {len(results)} backtest results",
            "data": {
                "results": results,
                "total_count": len(results)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{strategy_name}")
async def get_strategy_backtest_results(strategy_name: str):
    """Get backtest results for a specific strategy"""
    try:
        backtrader_service = get_backtrader_service()
        results = backtrader_service.get_backtest_results(strategy_name)
        
        return {
            "success": True,
            "message": f"Retrieved {len(results)} backtest results for {strategy_name}",
            "data": {
                "strategy_name": strategy_name,
                "results": results,
                "total_count": len(results)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/results/{result_id}")
async def delete_backtest_result(result_id: str):
    """Delete a backtest result"""
    try:
        backtrader_service = get_backtrader_service()
        result = backtrader_service.delete_backtest_result(result_id)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_backtest_status():
    """Get backtest service status"""
    try:
        backtrader_service = get_backtrader_service()
        result = backtrader_service.get_backtest_status()
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Strategy Development Endpoints
@router.post("/strategies/develop")
async def develop_strategy(request: Dict[str, Any]):
    """AI-assisted strategy development (placeholder for future implementation)"""
    try:
        # TODO: Implement AI agent for strategy development
        # This will integrate with the frontend AI bot
        
        return {
            "success": True,
            "message": "Strategy development endpoint (AI integration coming soon)",
            "data": {
                "strategy_name": request.get("strategy_name", "NewStrategy"),
                "status": "development_requested",
                "ai_agent": "enabled"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies/templates")
async def get_strategy_templates():
    """Get available strategy templates for development"""
    try:
        # TODO: Implement strategy template system
        templates = [
            {
                "name": "Moving Average Crossover",
                "description": "Simple moving average crossover strategy",
                "indicators": ["SMA", "EMA"],
                "parameters": ["fast_period", "slow_period"]
            },
            {
                "name": "RSI Strategy",
                "description": "RSI-based mean reversion strategy",
                "indicators": ["RSI"],
                "parameters": ["rsi_period", "oversold", "overbought"]
            },
            {
                "name": "Bollinger Bands",
                "description": "Bollinger Bands mean reversion strategy",
                "indicators": ["BB"],
                "parameters": ["bb_period", "bb_std"]
            }
        ]
        
        return {
            "success": True,
            "message": "Strategy templates retrieved",
            "data": {
                "templates": templates,
                "total_templates": len(templates)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Integration Endpoints
@router.get("/replay/signals/{strategy_name}")
async def get_strategy_signals_for_replay(
    strategy_name: str, 
    instrument: str, 
    timeframe: str,
    start_date: str,
    end_date: str
):
    """Get strategy signals for replay mode (used by replay system)"""
    try:
        backtrader_service = get_backtrader_service()
        
        # Convert string dates to datetime
        from datetime import datetime
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        # Get signals for replay
        signals = backtrader_service.get_strategy_signals(
            strategy_name, instrument, timeframe, start_dt, end_dt
        )
        
        return {
            "success": True,
            "message": f"Retrieved {len(signals)} signals for replay",
            "data": {
                "strategy_name": strategy_name,
                "instrument": instrument,
                "timeframe": timeframe,
                "signals": signals,
                "signal_count": len(signals)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/validate-alignment")
async def validate_data_alignment(
    instrument: str,
    timeframe: str,
    start_date: str,
    end_date: str
):
    """Validate that backtest data aligns with replay data timeframe"""
    try:
        backtrader_service = get_backtrader_service()
        
        # Convert string dates to datetime
        from datetime import datetime
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        # Validate alignment
        result = backtrader_service.validate_data_alignment(
            instrument, timeframe, start_dt, end_dt
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-aligned-backtest")
async def create_aligned_backtest(request: BacktestRequest):
    """Create a backtest that aligns with the replay data timeframe"""
    try:
        backtrader_service = get_backtrader_service()
        
        # Convert string dates to datetime
        from datetime import datetime
        start_date = datetime.fromisoformat(request.start_date)
        end_date = datetime.fromisoformat(request.end_date)
        
        # Create aligned backtest
        result = backtrader_service.create_aligned_backtest(
            request.strategy_name,
            request.instrument,
            request.timeframe,
            start_date,
            end_date,
            request.parameters
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
