"""
Indicators router for QuantBotForex API
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from models.trading import IndicatorData
from services.indicator_service import get_indicator_service

router = APIRouter()

@router.get("/indicators/{symbol}/{timeframe}")
async def get_indicators(
    symbol: str,
    timeframe: str,
    indicators: str = Query(..., description="Comma-separated indicator names"),
    parameters: Optional[str] = Query(None, description="JSON string of parameters")
):
    """Get technical indicators for symbol and timeframe"""
    try:
        # Parse indicators list
        indicator_list = [ind.strip() for ind in indicators.split(",")]
        
        # Parse parameters if provided
        indicator_params = {}
        if parameters:
            import json
            indicator_params = json.loads(parameters)
        
        # Use the existing indicator service
        indicator_service = get_indicator_service()
        result = await indicator_service.calculate_indicators(
            symbol, timeframe, indicator_list, indicator_params
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 