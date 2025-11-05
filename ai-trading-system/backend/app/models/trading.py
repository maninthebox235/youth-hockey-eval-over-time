"""Trading data models for the AI trading system."""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class TradingSignal(str, Enum):
    """Available trading signals."""
    BUY_TO_ENTER = "buy_to_enter"
    SELL_TO_ENTER = "sell_to_enter"
    HOLD = "hold"
    CLOSE = "close"


class Coin(str, Enum):
    """Supported cryptocurrencies."""
    BTC = "BTC"
    ETH = "ETH"
    SOL = "SOL"
    BNB = "BNB"
    DOGE = "DOGE"
    XRP = "XRP"


class TradingDecision(BaseModel):
    """LLM trading decision output."""
    signal: TradingSignal
    coin: Coin
    quantity: float = Field(gt=0)
    leverage: int = Field(ge=1, le=20)
    profit_target: float = Field(gt=0)
    stop_loss: float = Field(gt=0)
    invalidation_condition: str
    confidence: float = Field(ge=0, le=1)
    risk_usd: float = Field(ge=0)  # 0 allowed for HOLD/CLOSE signals
    justification: str


class MarketDataPoint(BaseModel):
    """Single market data point for technical analysis."""
    timestamp: datetime
    coin: Coin
    price: float
    ema20: float
    macd: float
    rsi7: float
    rsi14: float
    volume: float


class MarketData4H(BaseModel):
    """4-hour context market data."""
    coin: Coin
    ema20: float
    ema50: float
    atr: float
    macd: float
    volume_comparison: float  # vs previous period


class PerpetualMetrics(BaseModel):
    """Perpetual futures specific metrics."""
    coin: Coin
    open_interest: float
    funding_rate: float


class Position(BaseModel):
    """Current trading position."""
    coin: Coin
    entry_price: float
    quantity: float
    leverage: int
    side: str  # "long" or "short"
    unrealized_pnl: float
    profit_target: float
    stop_loss: float
    invalidation_condition: str
    opened_at: datetime


class AccountState(BaseModel):
    """Current account state."""
    available_cash: float
    total_equity: float
    positions: List[Position] = []
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    sharpe_ratio: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0


class MarketDataInput(BaseModel):
    """Complete market data input for LLM."""
    data_3min: List[MarketDataPoint]  # Recent 3-min intervals
    data_4h: List[MarketData4H]  # 4-hour context
    perpetual_metrics: List[PerpetualMetrics]
    account_state: AccountState


class TradeExecution(BaseModel):
    """Record of executed trade."""
    id: str
    timestamp: datetime
    decision: TradingDecision
    execution_price: float
    status: str  # "executed", "failed", "closed"
    pnl: Optional[float] = None
    close_reason: Optional[str] = None
