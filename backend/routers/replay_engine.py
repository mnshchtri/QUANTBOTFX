"""
Replay Engine Router for QuantBotForex API
Matches frontend expectations in replayService.ts
"""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, List, Any, Optional
from services.replay_service import get_replay_service
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

@router.get("/replay-state/{symbol}/{timeframe}")
async def get_replay_state_by_symbol(
    symbol: str,
    timeframe: str,
    current_index: int = Query(0),
    is_playing: bool = Query(False),
    speed: float = Query(1.0)
):
    """Get replay state for specific symbol and timeframe"""
    try:
        replay_service = get_replay_service()
        status = replay_service.get_replay_status()
        if status.get("success"):
            data = status.get("data", {})
            return {
                "current_index": data.get("current_index", 0),
                "total_candles": data.get("total_candles", 0),
                "current_time": str(datetime.now()),
                "is_playing": data.get("is_playing", False),
                "speed": data.get("replay_speed", 1.0)
            }
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class LoadDataRequest(BaseModel):
    instrument: str
    start_date: str
    end_date: str
    timeframe: str = "M15"

class SetSpeedRequest(BaseModel):
    speed: float

@router.post("/replay-engine/load-data")
async def load_data(request: LoadDataRequest):
    """Load data for replay engine"""
    try:
        replay_service = get_replay_service()
        result = await replay_service.initialize_replay(request.instrument, request.timeframe)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/replay-engine/state")
async def get_state():
    """Get replay engine state"""
    try:
        replay_service = get_replay_service()
        status = replay_service.get_replay_status()
        if status.get("success"):
            data = status.get("data", {})
            return {
                "is_playing": data.get("is_playing", False),
                "current_index": data.get("current_index", 0),
                "speed_multiplier": data.get("replay_speed", 1.0),
                "auto_trade": data.get("auto_trade_enabled", False),
                "risk_management": True,
                "data_loaded": data.get("total_candles", 0) > 0
            }
        return {"success": False, "message": "Failed to get state"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/replay-engine/play")
async def play():
    """Start replay"""
    try:
        replay_service = get_replay_service()
        success = replay_service.play_replay()
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/replay-engine/pause")
async def pause():
    """Pause replay"""
    try:
        replay_service = get_replay_service()
        success = replay_service.pause_replay()
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/replay-engine/stop")
async def stop():
    """Stop replay"""
    try:
        replay_service = get_replay_service()
        success = replay_service.stop_replay()
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/replay-engine/step-forward")
async def step_forward():
    """Step forward one candle"""
    try:
        replay_service = get_replay_service()
        success = replay_service.step_forward()
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/replay-engine/step-backward")
async def step_backward():
    """Step backward one candle"""
    try:
        replay_service = get_replay_service()
        success = replay_service.step_backward()
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/replay-engine/set-speed")
async def set_speed(request: SetSpeedRequest):
    """Set replay speed"""
    try:
        replay_service = get_replay_service()
        success = replay_service.set_speed(request.speed)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/replay-engine/toggle-auto-trade")
async def toggle_auto_trade():
    """Toggle auto trade"""
    try:
        replay_service = get_replay_service()
        return replay_service.toggle_auto_trade()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/replay-engine/toggle-risk-management")
async def toggle_risk_management():
    """Toggle risk management"""
    try:
        replay_service = get_replay_service()
        return replay_service.toggle_risk_management()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/replay-engine/performance")
async def get_performance():
    """Get replay performance"""
    try:
        replay_service = get_replay_service()
        perf = replay_service.get_performance_metrics()
        if perf.get("success"):
            data = perf.get("data", {})
            return {
                "total_trades": data.get("total_trades", 0),
                "winning_trades": data.get("winning_trades", 0),
                "losing_trades": data.get("losing_trades", 0),
                "win_rate": data.get("win_rate", 0.0),
                "total_profit_loss": data.get("total_profit_loss", 0.0),
                "max_drawdown": data.get("max_drawdown", 0.0),
                "sharpe_ratio": 0.0,
                "trade_history": data.get("trade_history", []),
                "performance_history": data.get("performance_history", [])
            }
        return {"success": False, "message": "Failed to get performance"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/replay-engine/simulate-strategy")
async def simulate_strategy():
    """Simulate strategy"""
    try:
        replay_service = get_replay_service()
        success = replay_service.simulate_strategy()
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/replay-engine/status")
async def get_status():
    """Get comprehensive status"""
    try:
        replay_service = get_replay_service()
        return replay_service.get_replay_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
