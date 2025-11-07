"""Main FastAPI application for AI trading system."""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as simulation_router
from app.api.production_routes import router as production_router
from app.database import init_db
from app.config import settings

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / '.env'
load_dotenv(dotenv_path=env_path)
logger.info(f"Loading .env from: {env_path}")
logger.info(f"API KEY loaded: {os.getenv('ANTHROPIC_API_KEY')[:20]}..." if os.getenv('ANTHROPIC_API_KEY') else "NO API KEY")
logger.info(f"Trading Mode: {'TESTNET' if settings.exchange_testnet else 'PRODUCTION'}")
logger.info(f"Trading Enabled: {settings.enable_trading}")
logger.info(f"Manual Approval: {settings.require_manual_approval}")

# Initialize database
try:
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")

app = FastAPI(
    title="AI Trading System - Production Ready",
    description="LLM-powered autonomous trading system with real exchange integration",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(simulation_router, prefix="/api/sim", tags=["simulation"])
app.include_router(production_router, prefix="/api", tags=["production"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Trading System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
