"""Trading engine for executing and managing trades."""

import uuid
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np
from app.models.trading import (
    TradingDecision,
    Position,
    AccountState,
    TradeExecution,
    Coin,
    TradingSignal,
)
from app.services.market_data import MarketDataService


class TradingEngine:
    """Engine for executing trades and managing account state."""

    def __init__(self, initial_capital: float = 10000.0):
        """Initialize trading engine."""
        self.initial_capital = initial_capital
        self.available_cash = initial_capital
        self.positions: Dict[Coin, Position] = {}
        self.trade_history: List[TradeExecution] = []
        self.returns_history: List[float] = []
        self.realized_pnl = 0.0
        self.market_data_service = MarketDataService()

    def _calculate_sharpe_ratio(self) -> float:
        """Calculate Sharpe ratio from returns history."""
        if len(self.returns_history) < 2:
            return 0.0

        returns = np.array(self.returns_history)
        mean_return = np.mean(returns)
        std_return = np.std(returns)

        if std_return == 0:
            return 0.0

        # Annualized Sharpe (assuming ~480 trading periods per day)
        sharpe = (mean_return / std_return) * np.sqrt(480)
        return sharpe

    def _calculate_position_pnl(
        self,
        position: Position,
        current_price: float
    ) -> float:
        """Calculate unrealized PnL for a position."""
        if position.side == "long":
            pnl = (current_price - position.entry_price) * position.quantity * position.leverage
        else:  # short
            pnl = (position.entry_price - current_price) * position.quantity * position.leverage

        return pnl

    def _check_stop_loss_or_target(
        self,
        position: Position,
        current_price: float
    ) -> Optional[str]:
        """Check if position hit stop loss or profit target."""
        if position.side == "long":
            if current_price <= position.stop_loss:
                return "stop_loss"
            elif current_price >= position.profit_target:
                return "profit_target"
        else:  # short
            if current_price >= position.stop_loss:
                return "stop_loss"
            elif current_price <= position.profit_target:
                return "profit_target"

        return None

    def get_account_state(self) -> AccountState:
        """Get current account state with all positions."""
        # Update unrealized PnL for all positions
        total_unrealized_pnl = 0.0

        for coin, position in self.positions.items():
            current_price = self.market_data_service.get_current_price(coin)
            pnl = self._calculate_position_pnl(position, current_price)
            position.unrealized_pnl = pnl
            total_unrealized_pnl += pnl

        # Calculate total equity
        total_equity = self.available_cash + total_unrealized_pnl

        # Calculate win rate
        winning_trades = sum(
            1 for trade in self.trade_history
            if trade.pnl and trade.pnl > 0
        )
        losing_trades = sum(
            1 for trade in self.trade_history
            if trade.pnl and trade.pnl < 0
        )

        return AccountState(
            available_cash=self.available_cash,
            total_equity=total_equity,
            positions=list(self.positions.values()),
            unrealized_pnl=total_unrealized_pnl,
            realized_pnl=self.realized_pnl,
            sharpe_ratio=self._calculate_sharpe_ratio(),
            total_trades=len(self.trade_history),
            winning_trades=winning_trades,
            losing_trades=losing_trades
        )

    def execute_decision(
        self,
        decision: TradingDecision
    ) -> TradeExecution:
        """Execute a trading decision."""
        current_price = self.market_data_service.get_current_price(decision.coin)
        trade_id = str(uuid.uuid4())
        timestamp = datetime.now()

        # Handle different signals
        if decision.signal == TradingSignal.HOLD:
            return TradeExecution(
                id=trade_id,
                timestamp=timestamp,
                decision=decision,
                execution_price=current_price,
                status="held",
                pnl=None,
                close_reason="no_action"
            )

        elif decision.signal == TradingSignal.CLOSE:
            # Close existing position
            if decision.coin in self.positions:
                position = self.positions[decision.coin]
                pnl = self._calculate_position_pnl(position, current_price)

                # Update cash and PnL
                position_value = position.quantity * current_price
                self.available_cash += position_value + pnl
                self.realized_pnl += pnl

                # Record return
                return_pct = pnl / (position.quantity * position.entry_price)
                self.returns_history.append(return_pct)

                # Remove position
                del self.positions[decision.coin]

                execution = TradeExecution(
                    id=trade_id,
                    timestamp=timestamp,
                    decision=decision,
                    execution_price=current_price,
                    status="closed",
                    pnl=pnl,
                    close_reason="manual_close"
                )
                self.trade_history.append(execution)
                return execution
            else:
                return TradeExecution(
                    id=trade_id,
                    timestamp=timestamp,
                    decision=decision,
                    execution_price=current_price,
                    status="failed",
                    pnl=None,
                    close_reason="no_position"
                )

        else:  # BUY_TO_ENTER or SELL_TO_ENTER
            # Check if position already exists
            if decision.coin in self.positions:
                return TradeExecution(
                    id=trade_id,
                    timestamp=timestamp,
                    decision=decision,
                    execution_price=current_price,
                    status="failed",
                    pnl=None,
                    close_reason="position_exists"
                )

            # Calculate position size
            position_value = decision.risk_usd * decision.leverage

            # Check if enough cash
            if position_value > self.available_cash:
                return TradeExecution(
                    id=trade_id,
                    timestamp=timestamp,
                    decision=decision,
                    execution_price=current_price,
                    status="failed",
                    pnl=None,
                    close_reason="insufficient_cash"
                )

            # Deduct cash
            self.available_cash -= position_value

            # Create position
            side = "long" if decision.signal == TradingSignal.BUY_TO_ENTER else "short"

            position = Position(
                coin=decision.coin,
                entry_price=current_price,
                quantity=decision.quantity,
                leverage=decision.leverage,
                side=side,
                unrealized_pnl=0.0,
                profit_target=decision.profit_target,
                stop_loss=decision.stop_loss,
                invalidation_condition=decision.invalidation_condition,
                opened_at=timestamp
            )

            self.positions[decision.coin] = position

            execution = TradeExecution(
                id=trade_id,
                timestamp=timestamp,
                decision=decision,
                execution_price=current_price,
                status="executed",
                pnl=None,
                close_reason=None
            )
            self.trade_history.append(execution)
            return execution

    def check_and_close_positions(self) -> List[TradeExecution]:
        """Check all positions for stop loss or profit target hits."""
        executions = []

        for coin, position in list(self.positions.items()):
            current_price = self.market_data_service.get_current_price(coin)
            close_reason = self._check_stop_loss_or_target(position, current_price)

            if close_reason:
                # Create close decision
                from app.models.trading import TradingDecision, TradingSignal

                close_decision = TradingDecision(
                    signal=TradingSignal.CLOSE,
                    coin=coin,
                    quantity=position.quantity,
                    leverage=position.leverage,
                    profit_target=position.profit_target,
                    stop_loss=position.stop_loss,
                    invalidation_condition=position.invalidation_condition,
                    confidence=1.0,
                    risk_usd=0.0,
                    justification=f"Auto-close: {close_reason}"
                )

                # Execute close
                execution = self.execute_decision(close_decision)
                execution.close_reason = close_reason
                executions.append(execution)

        return executions

    def get_trade_history(self, limit: int = 50) -> List[TradeExecution]:
        """Get recent trade history."""
        return self.trade_history[-limit:]
