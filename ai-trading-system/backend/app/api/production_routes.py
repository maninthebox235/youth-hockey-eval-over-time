"""Production trading API routes with safety controls."""

import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session

from app.models.trading import (
    TradeExecution,
    AccountState,
    TradingDecision,
    MarketDataInput,
)
from app.services.llm_trader import LLMTrader
from app.services.market_data import MarketDataService
from app.services.production_trading_engine import ProductionTradingEngine
from app.services.binance_exchange import BinanceExchange
from app.services.safety_manager import safety_manager
from app.database import get_db, TradeDB, SystemEventDB
from app.config import settings

# Load environment variables
backend_dir = Path(__file__).parent.parent.parent
env_path = backend_dir / '.env'
load_dotenv(dotenv_path=env_path)

router = APIRouter(prefix="/production", tags=["production"])

# Global instances
market_data_service = MarketDataService()
llm_trader = LLMTrader(model=settings.llm_model)

# Production trading engine (lazy initialization)
_trading_engine = None


def get_trading_engine() -> ProductionTradingEngine:
    """Get or create trading engine."""
    global _trading_engine
    if _trading_engine is None:
        exchange = BinanceExchange(testnet=settings.exchange_testnet)
        _trading_engine = ProductionTradingEngine(
            exchange=exchange,
            safety_manager=safety_manager
        )
    return _trading_engine


@router.get("/account", response_model=AccountState)
async def get_account_state():
    """Get current account state from exchange."""
    engine = get_trading_engine()
    return await engine.get_account_state()


@router.post("/trade/decision", response_model=TradingDecision)
async def get_trading_decision():
    """Get a trading decision from the LLM."""
    try:
        # Get market data from exchange
        engine = get_trading_engine()
        # For now use mock data, in production would get from exchange
        market_data_dict = market_data_service.get_all_market_data()
        account_state = await engine.get_account_state()

        # Build input
        market_input = MarketDataInput(
            data_3min=market_data_dict["data_3min"],
            data_4h=market_data_dict["data_4h"],
            perpetual_metrics=market_data_dict["perpetual_metrics"],
            account_state=account_state
        )

        # Get decision from LLM
        decision = await llm_trader.get_trading_decision(market_input)
        return decision
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get decision: {str(e)}")


@router.post("/trade/execute", response_model=TradeExecution)
async def execute_trade(
    decision: TradingDecision,
    require_approval: bool = None,
    db: Session = Depends(get_db)
):
    """Execute a trading decision on real exchange."""
    try:
        engine = get_trading_engine()

        # Execute with safety checks
        execution = await engine.execute_decision(
            decision,
            require_approval=require_approval
        )

        # Save to database
        trade_db = TradeDB(
            id=execution.id,
            timestamp=execution.timestamp,
            signal=execution.decision.signal.value,
            coin=execution.decision.coin.value,
            quantity=execution.decision.quantity,
            leverage=execution.decision.leverage,
            profit_target=execution.decision.profit_target,
            stop_loss=execution.decision.stop_loss,
            invalidation_condition=execution.decision.invalidation_condition,
            confidence=execution.decision.confidence,
            risk_usd=execution.decision.risk_usd,
            justification=execution.decision.justification,
            execution_price=execution.execution_price,
            status=execution.status,
            pnl=execution.pnl,
            close_reason=execution.close_reason
        )
        db.add(trade_db)
        db.commit()

        return execution
    except Exception as e:
        # Log error
        error_event = SystemEventDB(
            event_type="error",
            category="execution",
            message=f"Trade execution failed: {str(e)}",
            details=str(decision.dict())
        )
        db.add(error_event)
        db.commit()

        raise HTTPException(status_code=500, detail=f"Failed to execute trade: {str(e)}")


@router.post("/trade/auto-execute", response_model=dict)
async def auto_execute_trade(db: Session = Depends(get_db)):
    """Get decision from LLM and execute automatically (with safety checks)."""
    try:
        engine = get_trading_engine()

        # Get market data
        market_data_dict = market_data_service.get_all_market_data()
        account_state = await engine.get_account_state()

        market_input = MarketDataInput(
            data_3min=market_data_dict["data_3min"],
            data_4h=market_data_dict["data_4h"],
            perpetual_metrics=market_data_dict["perpetual_metrics"],
            account_state=account_state
        )

        # Get decision from LLM
        decision = await llm_trader.get_trading_decision(market_input)

        # Execute with safety checks
        execution = await engine.execute_decision(decision)

        # Save to database
        trade_db = TradeDB(
            id=execution.id,
            timestamp=execution.timestamp,
            signal=execution.decision.signal.value,
            coin=execution.decision.coin.value,
            quantity=execution.decision.quantity,
            leverage=execution.decision.leverage,
            profit_target=execution.decision.profit_target,
            stop_loss=execution.decision.stop_loss,
            invalidation_condition=execution.decision.invalidation_condition,
            confidence=execution.decision.confidence,
            risk_usd=execution.decision.risk_usd,
            justification=execution.decision.justification,
            execution_price=execution.execution_price,
            status=execution.status,
            pnl=execution.pnl,
            close_reason=execution.close_reason
        )
        db.add(trade_db)
        db.commit()

        return {
            "decision": decision,
            "execution": execution,
            "account_state": await engine.get_account_state()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to auto-execute: {str(e)}")


@router.get("/trades", response_model=List[TradeExecution])
async def get_trade_history(limit: int = 50):
    """Get trade history."""
    engine = get_trading_engine()
    return engine.get_trade_history(limit)


@router.post("/positions/close-all")
async def close_all_positions(db: Session = Depends(get_db)):
    """Emergency: Close all open positions."""
    try:
        engine = get_trading_engine()
        account_state = await engine.get_account_state()

        closed = []
        for position in account_state.positions:
            # Close each position
            from app.models.trading import TradingDecision, TradingSignal
            close_decision = TradingDecision(
                signal=TradingSignal.CLOSE,
                coin=position.coin,
                quantity=position.quantity,
                leverage=position.leverage,
                profit_target=0.0,
                stop_loss=0.0,
                invalidation_condition="Emergency close",
                confidence=1.0,
                risk_usd=0.0,
                justification="Emergency close all positions"
            )

            execution = await engine.execute_decision(close_decision, require_approval=False)
            closed.append(execution)

        # Log event
        event = SystemEventDB(
            event_type="critical",
            category="safety",
            message="All positions closed manually",
            details=f"Closed {len(closed)} positions"
        )
        db.add(event)
        db.commit()

        return {
            "closed_positions": closed,
            "count": len(closed)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to close positions: {str(e)}")


# Safety endpoints
@router.get("/safety/status")
async def get_safety_status():
    """Get current safety status."""
    return safety_manager.get_status()


@router.post("/safety/pause")
async def pause_trading(reason: str = "Manual pause", db: Session = Depends(get_db)):
    """Pause all trading."""
    safety_manager.pause_trading(reason)

    # Log event
    event = SystemEventDB(
        event_type="warning",
        category="safety",
        message="Trading paused",
        details=reason
    )
    db.add(event)
    db.commit()

    return {"status": "paused", "reason": reason}


@router.post("/safety/resume")
async def resume_trading(db: Session = Depends(get_db)):
    """Resume trading (manual override)."""
    safety_manager.resume_trading()

    # Log event
    event = SystemEventDB(
        event_type="info",
        category="safety",
        message="Trading resumed",
        details="Manual resume"
    )
    db.add(event)
    db.commit()

    return {"status": "resumed"}


@router.get("/config")
async def get_config():
    """Get current configuration (sanitized)."""
    return {
        "exchange_type": settings.exchange_type,
        "testnet": settings.exchange_testnet,
        "trading_enabled": settings.enable_trading,
        "require_approval": settings.require_manual_approval,
        "max_position_size_pct": settings.max_position_size_pct,
        "max_leverage": settings.max_leverage,
        "max_drawdown_pct": settings.max_drawdown_pct,
        "max_trades_per_day": settings.max_trades_per_day,
        "min_confidence": settings.min_confidence_threshold,
    }
