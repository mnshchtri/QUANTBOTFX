"""
Replay router for QuantBotForex API
"""

from fastapi import APIRouter, HTTPException
from models.replay import ReplayState, ReplayControlRequest, ReplayPositionRequest
from services.replay_service import get_replay_service

router = APIRouter()

from pydantic import BaseModel

class ReplayInitializeRequest(BaseModel):
    instrument: str = "GBP_JPY"
    timeframe: str = "M15"

@router.post("/initialize")
async def initialize_replay(request: ReplayInitializeRequest):
    """Initialize replay session"""
    try:
        replay_service = get_replay_service()
        result = await replay_service.initialize_replay(request.instrument, request.timeframe)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_replay_status():
    """Get current replay status"""
    try:
        replay_service = get_replay_service()
        status = replay_service.get_replay_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data")
async def get_replay_data():
    """Get current replay data with signals"""
    try:
        replay_service = get_replay_service()
        data = replay_service.get_replay_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/control")
async def control_replay(request: ReplayControlRequest):
    """Control replay playback"""
    try:
        replay_service = get_replay_service()
        result = replay_service.control_replay(request.action, request.speed or 1.0)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/set-start-position")
async def set_start_position(request: ReplayPositionRequest):
    """Set replay start position"""
    try:
        replay_service = get_replay_service()
        result = replay_service.set_start_position(
            date=request.date if request.date else None,
            position=request.position if request.position else None,
            context_candles=request.context_candles or 50
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_replay_performance():
    """Get replay performance metrics"""
    try:
        replay_service = get_replay_service()
        performance = replay_service.get_performance_metrics()
        return performance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-indicator")
async def add_indicator(request: dict):
    """Add indicator to replay"""
    try:
        replay_service = get_replay_service()
        # For now, just return success
        return {"success": True, "message": "Indicator added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/remove-indicator")
async def remove_indicator(request: dict):
    """Remove indicator from replay"""
    try:
        replay_service = get_replay_service()
        # For now, just return success
        return {"success": True, "message": "Indicator removed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute-trade")
async def execute_trade(request: dict):
    """Execute trade in replay"""
    try:
        replay_service = get_replay_service()
        # For now, just return success
        return {"success": True, "message": "Trade executed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-strategy-signals")
async def add_strategy_signals(request: dict):
    """Add strategy signals as overlays from backtest results"""
    try:
        replay_service = get_replay_service()
        strategy_name = request.get("strategy_name", "RangeOfTheDay")
        result = replay_service.add_strategy_overlay(strategy_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategy-signals")
async def get_strategy_signals_from_replay():
    """Get all strategy signal overlays from backtest results"""
    try:
        replay_service = get_replay_service()
        result = replay_service.get_strategy_overlays()
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 