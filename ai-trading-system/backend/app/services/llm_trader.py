"""LLM-based trading decision service using prompt engineering."""

import json
import os
from typing import Dict, Any
from anthropic import Anthropic
from app.models.trading import (
    MarketDataInput,
    TradingDecision,
    Coin,
)


class LLMTrader:
    """Service for getting trading decisions from LLM."""

    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        """Initialize LLM trader with API key."""
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = model

    def _build_system_prompt(self) -> str:
        """Build the system prompt for the trading LLM."""
        return """You are an autonomous cryptocurrency trading agent operating on the Hyperliquid perpetual futures exchange.

**TRADING ENVIRONMENT**
- Exchange: Hyperliquid perpetual futures
- Asset Universe: BTC, ETH, SOL, BNB, DOGE, XRP
- Starting Capital: $10,000 USD
- Decision Frequency: Every 2-3 minutes

**AVAILABLE ACTIONS**
You can execute four discrete actions:
1. `buy_to_enter` - Open a long position
2. `sell_to_enter` - Open a short position
3. `hold` - Take no action
4. `close` - Close an existing position

**MANDATORY RISK PARAMETERS**
Every trading decision MUST specify:
- Profit target (minimum 2:1 reward-to-risk ratio)
- Stop loss (1-3% account risk per trade)
- Invalidation condition (objective thesis-breaking signal)
- Confidence score (0-1 scale)
- Risk exposure in USD

**POSITION SIZING**
Position Size (USD) = Available Cash × Leverage × Allocation %
- Leverage: 1-20x based on conviction
- Never risk more than 3% of account per trade
- No pyramiding, no hedging, no partial exits

**OPERATIONAL CONSTRAINTS**
- Only use provided data - no external information access
- One position per coin maximum
- Stateless decisions - each call is independent
- Must return valid JSON format

**PERFORMANCE FEEDBACK**
Your Sharpe Ratio indicates risk-adjusted performance:
- <0: Reduce sizes, tighten stops
- 0-1: Positive but volatile
- 1-2: Good risk-adjusted performance
- >2: Excellent execution

**META-COGNITIVE REQUIREMENTS**
- Use confidence field to express uncertainty
- Set clear invalidation conditions to prevent overconfidence
- Remember: Inaction has opportunity cost, but preservation of capital is paramount
- Balance aggression with prudent risk management"""

    def _format_market_data(self, data: MarketDataInput) -> str:
        """Format market data for LLM input.

        ⚠️ CRITICAL: Data is ordered OLDEST → NEWEST
        """
        output = []

        output.append("⚠️ **DATA ORDERING: ALL DATA BELOW IS ORDERED OLDEST → NEWEST** ⚠️\n")

        # 3-minute interval data
        output.append("## 3-MINUTE INTERVAL DATA (Recent)")
        output.append("⚠️ ORDERED: OLDEST → NEWEST\n")

        # Group by coin
        coin_data_3min: Dict[str, list] = {}
        for point in data.data_3min:
            if point.coin not in coin_data_3min:
                coin_data_3min[point.coin] = []
            coin_data_3min[point.coin].append(point)

        for coin, points in coin_data_3min.items():
            output.append(f"\n### {coin}")
            output.append("Timestamp | Price | EMA20 | MACD | RSI7 | RSI14 | Volume")
            output.append("-" * 80)
            for point in points:
                output.append(
                    f"{point.timestamp.strftime('%Y-%m-%d %H:%M')} | "
                    f"${point.price:,.2f} | ${point.ema20:,.2f} | "
                    f"{point.macd:.4f} | {point.rsi7:.1f} | {point.rsi14:.1f} | "
                    f"${point.volume:,.0f}"
                )

        # 4-hour context data
        output.append("\n\n## 4-HOUR CONTEXT DATA")
        output.append("⚠️ ORDERED: OLDEST → NEWEST\n")
        output.append("Coin | EMA20 | EMA50 | ATR | MACD | Volume Comp")
        output.append("-" * 70)
        for data_4h in data.data_4h:
            output.append(
                f"{data_4h.coin} | ${data_4h.ema20:,.2f} | ${data_4h.ema50:,.2f} | "
                f"${data_4h.atr:.2f} | {data_4h.macd:.4f} | {data_4h.volume_comparison:.2%}"
            )

        # Perpetual metrics
        output.append("\n\n## PERPETUAL FUTURES METRICS")
        output.append("Coin | Open Interest | Funding Rate")
        output.append("-" * 50)
        for metrics in data.perpetual_metrics:
            output.append(
                f"{metrics.coin} | ${metrics.open_interest:,.0f} | {metrics.funding_rate:.4%}"
            )

        # Account state
        output.append("\n\n## ACCOUNT STATE")
        output.append(f"Available Cash: ${data.account_state.available_cash:,.2f}")
        output.append(f"Total Equity: ${data.account_state.total_equity:,.2f}")
        output.append(f"Unrealized PnL: ${data.account_state.unrealized_pnl:,.2f}")
        output.append(f"Realized PnL: ${data.account_state.realized_pnl:,.2f}")
        output.append(f"**Sharpe Ratio: {data.account_state.sharpe_ratio:.2f}**")
        output.append(f"Total Trades: {data.account_state.total_trades}")
        output.append(f"Win Rate: {data.account_state.winning_trades}/{data.account_state.total_trades if data.account_state.total_trades > 0 else 1}")

        if data.account_state.positions:
            output.append("\n### Current Positions")
            for pos in data.account_state.positions:
                output.append(
                    f"- {pos.coin} {pos.side.upper()}: {pos.quantity:.4f} @ ${pos.entry_price:,.2f} "
                    f"(Leverage: {pos.leverage}x, PnL: ${pos.unrealized_pnl:,.2f})"
                )
                output.append(f"  Profit Target: ${pos.profit_target:,.2f}, Stop Loss: ${pos.stop_loss:,.2f}")
                output.append(f"  Invalidation: {pos.invalidation_condition}")

        output.append("\n⚠️ REMINDER: ALL DATA ABOVE IS ORDERED OLDEST → NEWEST ⚠️")

        return "\n".join(output)

    def _build_user_prompt(self, data: MarketDataInput) -> str:
        """Build the user prompt with market data."""
        market_data_str = self._format_market_data(data)

        return f"""{market_data_str}

**YOUR TASK**
Analyze the data above and make a trading decision. You must respond with valid JSON only, using this exact structure:

```json
{{
  "signal": "buy_to_enter|sell_to_enter|hold|close",
  "coin": "BTC|ETH|SOL|BNB|DOGE|XRP",
  "quantity": <float>,
  "leverage": <1-20>,
  "profit_target": <float>,
  "stop_loss": <float>,
  "invalidation_condition": "<string>",
  "confidence": <0-1>,
  "risk_usd": <float>,
  "justification": "<string>"
}}
```

**IMPORTANT REQUIREMENTS**
- Ensure minimum 2:1 reward-to-risk ratio
- Risk no more than 3% of account per trade
- Set objective invalidation conditions
- Provide honest confidence assessment
- If holding or closing, still fill all fields with reasonable values
- Remember: DATA IS ORDERED OLDEST → NEWEST

Respond with JSON only, no additional text."""

    async def get_trading_decision(
        self,
        market_data: MarketDataInput
    ) -> TradingDecision:
        """Get a trading decision from the LLM."""
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(market_data)

        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            temperature=0.7,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        # Extract JSON from response
        response_text = response.content[0].text

        # Try to parse JSON (handle markdown code blocks)
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        else:
            json_str = response_text.strip()

        # Parse and validate
        decision_dict = json.loads(json_str)
        decision = TradingDecision(**decision_dict)

        return decision
