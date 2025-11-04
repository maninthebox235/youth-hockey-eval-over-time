"""API routes for the trading system."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from app.models.trading import (
    TradeExecution,
    AccountState,
    TradingDecision,
    MarketDataInput,
)
from app.services.llm_trader import LLMTrader
from app.services.market_data import MarketDataService
from app.services.trading_engine import TradingEngine

router = APIRouter()

# Global instances (in production, use dependency injection)
market_data_service = MarketDataService()
trading_engine = TradingEngine(initial_capital=10000.0)
llm_trader = LLMTrader()


@router.get("/account", response_model=AccountState)
async def get_account_state():
    """Get current account state."""
    return trading_engine.get_account_state()


@router.get("/market-data")
async def get_market_data():
    """Get current market data for all coins."""
    return market_data_service.get_all_market_data()


@router.post("/trade/decision", response_model=TradingDecision)
async def get_trading_decision():
    """Get a trading decision from the LLM."""
    # Get market data
    market_data_dict = market_data_service.get_all_market_data()
    account_state = trading_engine.get_account_state()

    # Build input
    market_input = MarketDataInput(
        data_3min=market_data_dict["data_3min"],
        data_4h=market_data_dict["data_4h"],
        perpetual_metrics=market_data_dict["perpetual_metrics"],
        account_state=account_state
    )

    # Get decision from LLM
    try:
        decision = await llm_trader.get_trading_decision(market_input)
        return decision
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get decision: {str(e)}")


@router.post("/trade/execute", response_model=TradeExecution)
async def execute_trade(decision: TradingDecision):
    """Execute a trading decision."""
    try:
        execution = trading_engine.execute_decision(decision)
        return execution
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute trade: {str(e)}")


@router.post("/trade/auto-execute", response_model=dict)
async def auto_execute_trade():
    """Get decision from LLM and execute it automatically."""
    # Get decision
    market_data_dict = market_data_service.get_all_market_data()
    account_state = trading_engine.get_account_state()

    market_input = MarketDataInput(
        data_3min=market_data_dict["data_3min"],
        data_4h=market_data_dict["data_4h"],
        perpetual_metrics=market_data_dict["perpetual_metrics"],
        account_state=account_state
    )

    try:
        decision = await llm_trader.get_trading_decision(market_input)
        execution = trading_engine.execute_decision(decision)

        # Check for auto-closes
        auto_closes = trading_engine.check_and_close_positions()

        return {
            "decision": decision,
            "execution": execution,
            "auto_closes": auto_closes,
            "account_state": trading_engine.get_account_state()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to auto-execute: {str(e)}")


@router.get("/trades", response_model=List[TradeExecution])
async def get_trade_history(limit: int = 50):
    """Get trade history."""
    return trading_engine.get_trade_history(limit)


@router.post("/positions/check")
async def check_positions():
    """Check all positions for stop loss or profit target hits."""
    executions = trading_engine.check_and_close_positions()
    return {
        "closed_positions": executions,
        "account_state": trading_engine.get_account_state()
    }


@router.post("/reset")
async def reset_trading_engine():
    """Reset the trading engine (for testing)."""
    global trading_engine
    trading_engine = TradingEngine(initial_capital=10000.0)
    return {"message": "Trading engine reset successfully"}
