"""Safety manager for production trading."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from app.config import settings
from app.models.trading import TradingDecision, AccountState, TradeExecution

logger = logging.getLogger(__name__)


class SafetyManager:
    """Manages trading safety and risk controls."""

    def __init__(self):
        """Initialize safety manager."""
        self.consecutive_losses = 0
        self.trades_today = 0
        self.last_trade_date = datetime.now().date()
        self.is_paused = False
        self.pause_reason = None
        self.initial_capital = settings.initial_capital

    def check_can_trade(self, account_state: AccountState) -> tuple[bool, Optional[str]]:
        """Check if trading is allowed based on safety parameters.

        Returns: (can_trade: bool, reason: Optional[str])
        """
        # Check kill switch
        if not settings.enable_trading:
            return False, "Trading is disabled (kill switch)"

        # Check if paused
        if self.is_paused:
            return False, f"Trading paused: {self.pause_reason}"

        # Reset daily trade count if new day
        today = datetime.now().date()
        if today != self.last_trade_date:
            self.trades_today = 0
            self.last_trade_date = today

        # Check daily trade limit
        if self.trades_today >= settings.max_trades_per_day:
            self.pause_trading("Daily trade limit reached")
            return False, "Daily trade limit reached"

        # Check consecutive losses
        if self.consecutive_losses >= settings.max_consecutive_losses:
            self.pause_trading(f"Max consecutive losses ({settings.max_consecutive_losses}) reached")
            return False, f"Too many consecutive losses ({self.consecutive_losses})"

        # Check drawdown
        current_equity = account_state.total_equity
        drawdown_pct = ((self.initial_capital - current_equity) / self.initial_capital) * 100

        if drawdown_pct >= settings.max_drawdown_pct:
            self.pause_trading(f"Max drawdown ({settings.max_drawdown_pct}%) reached")
            return False, f"Max drawdown exceeded: {drawdown_pct:.2f}%"

        # Check total risk exposure
        total_risk = sum(abs(pos.unrealized_pnl) for pos in account_state.positions)
        risk_pct = (total_risk / account_state.total_equity) * 100

        if risk_pct >= settings.max_total_risk_pct:
            return False, f"Total risk exposure too high: {risk_pct:.2f}%"

        return True, None

    def validate_decision(
        self,
        decision: TradingDecision,
        account_state: AccountState
    ) -> tuple[bool, Optional[str]]:
        """Validate a trading decision against safety parameters.

        Returns: (is_valid: bool, reason: Optional[str])
        """
        # Check confidence threshold
        if decision.confidence < settings.min_confidence_threshold:
            return False, f"Confidence too low: {decision.confidence:.2%} < {settings.min_confidence_threshold:.2%}"

        # Check leverage limits
        if decision.leverage > settings.max_leverage:
            logger.warning(f"Leverage {decision.leverage}x exceeds max {settings.max_leverage}x, reducing")
            decision.leverage = settings.max_leverage

        # Check position size
        position_size_pct = (decision.risk_usd / account_state.total_equity) * 100
        if position_size_pct > settings.max_position_size_pct:
            return False, f"Position size too large: {position_size_pct:.2f}% > {settings.max_position_size_pct}%"

        # Check reward-to-risk ratio (should be at least 2:1)
        if decision.signal in ['buy_to_enter', 'sell_to_enter']:
            entry_price = decision.profit_target  # This should be calculated differently
            risk = abs(entry_price - decision.stop_loss)
            reward = abs(decision.profit_target - entry_price)

            if risk > 0:
                reward_risk_ratio = reward / risk
                if reward_risk_ratio < 2.0:
                    return False, f"Reward-to-risk ratio too low: {reward_risk_ratio:.2f}:1 (min 2:1)"

        # Check available cash
        if decision.risk_usd > account_state.available_cash:
            return False, f"Insufficient cash: ${decision.risk_usd:.2f} required, ${account_state.available_cash:.2f} available"

        return True, None

    def record_trade(self, execution: TradeExecution):
        """Record a trade and update safety counters."""
        self.trades_today += 1

        # Update consecutive losses counter
        if execution.pnl is not None:
            if execution.pnl < 0:
                self.consecutive_losses += 1
                logger.warning(f"Consecutive losses: {self.consecutive_losses}")
            else:
                self.consecutive_losses = 0

        logger.info(f"Trade recorded: {execution.status} | Trades today: {self.trades_today}")

    def pause_trading(self, reason: str):
        """Pause trading with reason."""
        self.is_paused = True
        self.pause_reason = reason
        logger.critical(f"TRADING PAUSED: {reason}")

    def resume_trading(self):
        """Resume trading (manual override)."""
        self.is_paused = False
        self.pause_reason = None
        self.consecutive_losses = 0
        logger.info("Trading resumed manually")

    def reset_daily_counters(self):
        """Reset daily counters (for testing or new day)."""
        self.trades_today = 0
        self.last_trade_date = datetime.now().date()
        logger.info("Daily counters reset")

    def get_status(self) -> dict:
        """Get current safety status."""
        return {
            "trading_enabled": settings.enable_trading,
            "is_paused": self.is_paused,
            "pause_reason": self.pause_reason,
            "consecutive_losses": self.consecutive_losses,
            "trades_today": self.trades_today,
            "max_trades_per_day": settings.max_trades_per_day,
            "max_consecutive_losses": settings.max_consecutive_losses,
            "max_drawdown_pct": settings.max_drawdown_pct,
        }


# Global instance
safety_manager = SafetyManager()
