"""Production trading engine with real exchange integration."""

import logging
from datetime import datetime
from typing import Dict, List, Optional
import asyncio
from app.models.trading import (
    TradingDecision,
    Position,
    AccountState,
    TradeExecution,
    Coin,
    TradingSignal,
)
from app.services.exchange_interface import ExchangeInterface
from app.services.binance_exchange import BinanceExchange
from app.services.safety_manager import SafetyManager
from app.config import settings

logger = logging.getLogger(__name__)


class ProductionTradingEngine:
    """Production trading engine with real exchange integration."""

    def __init__(
        self,
        exchange: Optional[ExchangeInterface] = None,
        safety_manager: Optional[SafetyManager] = None
    ):
        """Initialize production trading engine."""
        self.exchange = exchange or BinanceExchange(testnet=settings.exchange_testnet)
        self.safety_manager = safety_manager or SafetyManager()
        self.trade_history: List[TradeExecution] = []
        self.positions: Dict[Coin, Position] = {}

    async def get_account_state(self) -> AccountState:
        """Get current account state from exchange."""
        try:
            # Get balance from exchange
            balance = await self.exchange.get_account_balance()

            # Get positions from exchange
            exchange_positions = await self.exchange.get_positions()

            # Convert to our Position model
            positions = []
            total_unrealized_pnl = 0.0

            for pos in exchange_positions:
                coin = self._symbol_to_coin(pos['symbol'])
                if not coin:
                    continue

                unrealized_pnl = float(pos.get('unrealizedPnl', 0))
                total_unrealized_pnl += unrealized_pnl

                position = Position(
                    coin=coin,
                    entry_price=float(pos['entryPrice']),
                    quantity=abs(float(pos['contracts'])),
                    leverage=int(pos.get('leverage', 1)),
                    side='long' if float(pos['contracts']) > 0 else 'short',
                    unrealized_pnl=unrealized_pnl,
                    profit_target=0.0,  # Would be stored separately
                    stop_loss=0.0,  # Would be stored separately
                    invalidation_condition="",
                    opened_at=datetime.now()  # Would be stored separately
                )
                positions.append(position)
                self.positions[coin] = position

            # Calculate realized PnL from closed trades
            realized_pnl = sum(
                trade.pnl for trade in self.trade_history
                if trade.pnl is not None
            )

            # Calculate win/loss stats
            closed_trades = [t for t in self.trade_history if t.pnl is not None]
            winning_trades = sum(1 for t in closed_trades if t.pnl > 0)
            losing_trades = sum(1 for t in closed_trades if t.pnl < 0)

            return AccountState(
                available_cash=balance['free'],
                total_equity=balance['total'],
                positions=positions,
                unrealized_pnl=total_unrealized_pnl,
                realized_pnl=realized_pnl,
                sharpe_ratio=0.0,  # Would be calculated from returns
                total_trades=len(self.trade_history),
                winning_trades=winning_trades,
                losing_trades=losing_trades
            )
        except Exception as e:
            logger.error(f"Error getting account state: {e}")
            raise

    async def execute_decision(
        self,
        decision: TradingDecision,
        require_approval: bool = None
    ) -> TradeExecution:
        """Execute a trading decision on the real exchange."""
        if require_approval is None:
            require_approval = settings.require_manual_approval

        trade_id = f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        timestamp = datetime.now()

        try:
            # Get current account state
            account_state = await self.get_account_state()

            # Safety check: Can we trade?
            can_trade, reason = self.safety_manager.check_can_trade(account_state)
            if not can_trade:
                logger.warning(f"Trading blocked: {reason}")
                return TradeExecution(
                    id=trade_id,
                    timestamp=timestamp,
                    decision=decision,
                    execution_price=0.0,
                    status="blocked",
                    pnl=None,
                    close_reason=reason
                )

            # Validate decision
            is_valid, reason = self.safety_manager.validate_decision(decision, account_state)
            if not is_valid:
                logger.warning(f"Decision validation failed: {reason}")
                return TradeExecution(
                    id=trade_id,
                    timestamp=timestamp,
                    decision=decision,
                    execution_price=0.0,
                    status="rejected",
                    pnl=None,
                    close_reason=reason
                )

            # Manual approval check
            if require_approval:
                logger.info(f"Trade requires manual approval: {decision.signal} {decision.coin}")
                return TradeExecution(
                    id=trade_id,
                    timestamp=timestamp,
                    decision=decision,
                    execution_price=0.0,
                    status="pending_approval",
                    pnl=None,
                    close_reason="Awaiting manual approval"
                )

            # Get current price
            current_price = await self.exchange.get_current_price(decision.coin)

            # Execute based on signal
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
                order = await self.exchange.close_position(decision.coin)

                # Calculate PnL (would get from exchange)
                pnl = 0.0  # Simplified
                if decision.coin in self.positions:
                    pos = self.positions[decision.coin]
                    pnl = pos.unrealized_pnl
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

            else:  # BUY_TO_ENTER or SELL_TO_ENTER
                # Check if position already exists
                if decision.coin in self.positions:
                    return TradeExecution(
                        id=trade_id,
                        timestamp=timestamp,
                        decision=decision,
                        execution_price=current_price,
                        status="rejected",
                        pnl=None,
                        close_reason="position_already_exists"
                    )

                # Calculate quantity
                quantity = self.exchange.calculate_quantity(
                    current_price,
                    decision.risk_usd,
                    decision.leverage
                )

                # Determine order side
                side = 'buy' if decision.signal == TradingSignal.BUY_TO_ENTER else 'sell'

                # Place market order
                order = await self.exchange.place_market_order(
                    decision.coin,
                    side,
                    quantity,
                    decision.leverage
                )

                # Place stop loss
                stop_side = 'sell' if side == 'buy' else 'buy'
                await self.exchange.place_stop_loss(
                    decision.coin,
                    stop_side,
                    quantity,
                    decision.stop_loss
                )

                # Place take profit
                await self.exchange.place_take_profit(
                    decision.coin,
                    stop_side,
                    quantity,
                    decision.profit_target
                )

                logger.info(f"Position opened: {side} {quantity} {decision.coin} @ ${current_price}")

                execution = TradeExecution(
                    id=trade_id,
                    timestamp=timestamp,
                    decision=decision,
                    execution_price=current_price,
                    status="executed",
                    pnl=None,
                    close_reason=None
                )

            # Record trade
            self.trade_history.append(execution)
            self.safety_manager.record_trade(execution)

            return execution

        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return TradeExecution(
                id=trade_id,
                timestamp=timestamp,
                decision=decision,
                execution_price=0.0,
                status="error",
                pnl=None,
                close_reason=str(e)
            )

    async def check_and_close_positions(self) -> List[TradeExecution]:
        """Check positions - stops/targets handled by exchange."""
        # In production, stops and targets are managed by the exchange
        # This method would check for invalidation conditions from LLM
        return []

    def get_trade_history(self, limit: int = 50) -> List[TradeExecution]:
        """Get recent trade history."""
        return self.trade_history[-limit:]

    def _symbol_to_coin(self, symbol: str) -> Optional[Coin]:
        """Convert exchange symbol to Coin enum."""
        symbol_map = {
            'BTC/USDT': Coin.BTC,
            'ETH/USDT': Coin.ETH,
            'SOL/USDT': Coin.SOL,
            'BNB/USDT': Coin.BNB,
            'DOGE/USDT': Coin.DOGE,
            'XRP/USDT': Coin.XRP,
        }
        return symbol_map.get(symbol)
