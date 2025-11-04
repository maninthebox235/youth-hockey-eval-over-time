# AI Trading System - Backend

LLM-powered autonomous trading system based on the nof1.ai Alpha Arena approach.

## Overview

This backend implements an AI trading system that uses Large Language Models (LLMs) to make autonomous trading decisions through prompt engineering. The system:

- Uses prompt engineering to turn unmodified LLMs into trading agents
- Simulates trading on perpetual futures (BTC, ETH, SOL, BNB, DOGE, XRP)
- Implements risk management with stop losses, profit targets, and position sizing
- Tracks performance with Sharpe ratio and PnL metrics
- Provides a RESTful API for interaction

## Architecture

### Core Components

1. **LLM Trader Service** (`app/services/llm_trader.py`)
   - Prompt engineering framework
   - System and user prompt construction
   - JSON-based decision parsing

2. **Market Data Service** (`app/services/market_data.py`)
   - Technical indicator calculation (EMA, MACD, RSI, ATR)
   - Mock market data generation
   - Real-time price simulation

3. **Trading Engine** (`app/services/trading_engine.py`)
   - Trade execution
   - Position management
   - Risk management (stop loss/profit target monitoring)
   - Performance tracking (Sharpe ratio, PnL)

4. **Data Models** (`app/models/trading.py`)
   - Pydantic models for type safety
   - Trading signals, positions, account state
   - Market data structures

## Setup

### Prerequisites

- Python 3.10+
- Poetry (for dependency management)
- Anthropic API key

### Installation

```bash
cd ai-trading-system/backend

# Install dependencies
poetry install

# Copy environment template
cp .env.example .env

# Edit .env and add your ANTHROPIC_API_KEY
nano .env
```

### Running the Server

```bash
# Development mode with auto-reload
poetry run fastapi dev app/main.py

# Production mode
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Account Management

- `GET /api/account` - Get current account state
- `POST /api/reset` - Reset trading engine (testing)

### Market Data

- `GET /api/market-data` - Get current market data for all coins

### Trading Operations

- `POST /api/trade/decision` - Get trading decision from LLM
- `POST /api/trade/execute` - Execute a specific trading decision
- `POST /api/trade/auto-execute` - Get decision and execute automatically
- `GET /api/trades?limit=50` - Get trade history
- `POST /api/positions/check` - Check positions for stop loss/profit target hits

### API Documentation

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Prompt Engineering

The system implements the nof1.ai prompt engineering approach:

### System Prompt Features

- Role establishment as autonomous trading agent
- Clear operational constraints
- Risk management rules
- Meta-cognitive requirements (confidence, invalidation conditions)

### Data Input Structure

- **3-minute intervals**: EMA20, MACD, RSI7, RSI14, volume
- **4-hour context**: EMA20/50, ATR, MACD, volume comparison
- **Perpetual metrics**: Open Interest, funding rates
- **Account state**: Positions, PnL, Sharpe Ratio

### Critical Design Elements

1. **Temporal Ordering Emphasis**: Repeated reminders that data is ordered OLDEST → NEWEST
2. **JSON Output**: Structured format reduces hallucinations
3. **Meta-Cognitive Fields**: Confidence and invalidation conditions prevent overconfidence
4. **Multi-Timeframe**: Separates entry timing (3-min) from trend context (4-hour)

## Trading Rules

### Position Management

- Starting capital: $10,000
- Max leverage: 20x
- Max risk per trade: 3% of account
- One position per coin maximum
- No pyramiding, no hedging, no partial exits

### Required Decision Parameters

Every trading decision must include:
- Profit target (minimum 2:1 reward-to-risk ratio)
- Stop loss
- Invalidation condition
- Confidence score (0-1)
- Risk exposure in USD

### Available Actions

- `buy_to_enter` - Open long position
- `sell_to_enter` - Open short position
- `hold` - No action
- `close` - Close existing position

## Performance Tracking

### Sharpe Ratio

The system calculates Sharpe ratio for risk-adjusted performance:
- <0: Losing money
- 0-1: Positive but volatile
- 1-2: Good performance
- >2: Excellent performance

### Metrics Tracked

- Realized PnL
- Unrealized PnL
- Total equity
- Win rate
- Total trades
- Sharpe ratio

## Testing

```bash
# Run tests
poetry run pytest

# With coverage
poetry run pytest --cov=app
```

## Development Notes

### Current Implementation

- **Stateless**: No conversation history between decisions
- **Mock Data**: Uses simulated market data
- **In-Memory**: No persistent database

### Future Enhancements

- Real exchange integration (Hyperliquid, Binance)
- Persistent storage (PostgreSQL)
- Short-term memory for LLM
- Multiple model support (GPT-4, Gemini, etc.)
- Backtesting framework
- Paper trading mode

## License

MIT
