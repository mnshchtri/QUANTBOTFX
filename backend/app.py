#!/usr/bin/env python3
"""
QuantBotForex Backend Application
=================================

Main FastAPI application with proper modular structure.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Import routers
from routers import health, data, indicators, replay, strategies, workflows, backtrader

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="QuantBotForex API",
    description="Professional trading platform with AI-driven strategies",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(data.router, prefix="/api", tags=["Data"])
app.include_router(indicators.router, prefix="/api", tags=["Indicators"])
app.include_router(replay.router, prefix="/replay", tags=["Replay"])
app.include_router(strategies.router, prefix="/api/strategies", tags=["Strategies"])
app.include_router(workflows.router, prefix="/api/workflows", tags=["Workflows"])
app.include_router(backtrader.router, prefix="/api/backtrader", tags=["backtrader"])

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 QuantBotForex Backend starting up...")
    logger.info("✅ All services initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 QuantBotForex Backend shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 