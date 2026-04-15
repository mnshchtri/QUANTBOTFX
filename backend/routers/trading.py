from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import time

router = APIRouter()


class Order(BaseModel):
    symbol: str
    type: str  # 'buy' or 'sell'
    volume: float
    price: float
    timestamp: float


# Mock storage for positions
positions = []


@router.post("/execute")
async def execute_trade(order: Order):
    # In a real app, this would call OANDA API
    positions.append({"id": f"pos_{int(time.time() * 1000)}", **order.dict()})
    return {
        "success": True,
        "message": f"Order executed for {order.symbol}",
        "position_id": positions[-1]["id"],
    }


@router.get("/summary")
async def get_account_summary():
    # Mock account summary
    total_balance = 100000.0
    equity = total_balance + sum(
        [p["volume"] * 10 for p in positions]
    )  # Simple mock PnL
    return {
        "success": True,
        "data": {
            "balance": total_balance,
            "equity": equity,
            "margin_used": len(positions) * 500.0,
            "free_margin": equity - (len(positions) * 500.0),
            "pnl_today": sum([p["volume"] * 10 for p in positions]),
            "pnl_percent": (sum([p["volume"] * 10 for p in positions]) / total_balance)
            * 100,
        },
    }


@router.get("/positions")
async def get_positions():
    return {"success": True, "data": positions}
