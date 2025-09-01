"""
Health check router for QuantBotForex API
"""

from fastapi import APIRouter
from models.base import BaseResponse

router = APIRouter()

@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "QuantBotForex API",
        "version": "2.0.0",
        "status": "running"
    }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return BaseResponse(
        success=True,
        message="API is healthy",
        data={
            "status": "healthy",
            "version": "2.0.0"
        }
    ) 