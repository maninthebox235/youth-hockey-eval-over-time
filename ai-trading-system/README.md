# AI Trading System

An LLM-powered autonomous cryptocurrency trading system based on the [nof1.ai Alpha Arena](https://nof1.ai/blog/TechPost1) approach.

## Overview

This project implements an AI trading system that uses Large Language Models (LLMs) to make autonomous trading decisions through prompt engineering alone - no fine-tuning required. The system demonstrates how unmodified LLMs can be turned into trading agents using structured prompts, technical indicators, and risk management rules.

### Key Features

- **LLM-Powered Trading**: Uses Claude (or other LLMs) to make trading decisions
- **Prompt Engineering**: Sophisticated system prompts with meta-cognitive features
- **Risk Management**: Automatic stop losses, profit targets, and position sizing
- **Technical Analysis**: Real-time market data with multiple indicators (EMA, MACD, RSI, ATR)
- **Performance Tracking**: Sharpe ratio, PnL, win rate, and trade analytics
- **Web Dashboard**: Beautiful React-based UI for monitoring and control
- **Auto-Trading**: Fully autonomous mode with 3-minute decision intervals
- **Mock Exchange**: Realistic market simulation for testing

## Architecture

```
ai-trading-system/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # Pydantic data models
│   │   ├── services/       # Core business logic
│   │   │   ├── llm_trader.py       # LLM prompt engineering
│   │   │   ├── market_data.py      # Technical indicators
│   │   │   └── trading_engine.py   # Trade execution
│   │   ├── api/            # REST API endpoints
│   │   └── main.py         # FastAPI application
│   └── pyproject.toml      # Python dependencies
│
└── frontend/               # React + TypeScript frontend
    ├── src/
    │   ├── components/     # UI components
    │   ├── services/       # API integration
    │   ├── types/          # TypeScript types
    │   └── App.tsx         # Main application
    └── package.json        # Node dependencies
```

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Anthropic API key (for Claude)
- Poetry (for Python dependency management)

### Backend Setup

```bash
cd ai-trading-system/backend

# Install dependencies
poetry install

# Set up environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Run the server
poetry run fastapi dev app/main.py
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd ai-trading-system/frontend

# Install dependencies
npm install

# Set up environment (optional - defaults to localhost:8000)
cp .env.example .env

# Run the dev server
npm run dev
```

Frontend will be available at `http://localhost:5173`

## How It Works

### 1. Prompt Engineering Framework

The system uses a sophisticated prompt engineering approach inspired by nof1.ai:

**System Prompt Features:**
- Role establishment as autonomous trading agent
- Clear operational constraints (no external data, stateless decisions)
- Risk management rules (2:1 reward-risk ratio, max 3% risk per trade)
- Meta-cognitive requirements (confidence scores, invalidation conditions)

**Data Input Structure:**
- **3-minute intervals**: Recent price action with EMA20, MACD, RSI7, RSI14, volume
- **4-hour context**: Trend indicators with EMA20/50, ATR, MACD
- **Perpetual metrics**: Open interest and funding rates
- **Account state**: Current positions, PnL, Sharpe ratio

**Critical Design Elements:**
- **Temporal ordering emphasis**: Repeated reminders that data is OLDEST → NEWEST
- **JSON output**: Structured format reduces hallucinations
- **Meta-cognitive fields**: Confidence and invalidation conditions prevent overconfidence
- **Multi-timeframe framing**: Separates entry timing from trend context

### 2. Trading Engine

The trading engine manages:
- Position entry and exit
- Stop loss and profit target monitoring
- Account state tracking
- Performance calculation (Sharpe ratio)
- Trade history

### 3. Market Data Service

Provides:
- Technical indicator calculation (EMA, MACD, RSI, ATR)
- Mock market data generation with realistic volatility
- Price simulation for 6 cryptocurrencies (BTC, ETH, SOL, BNB, DOGE, XRP)

### 4. Web Dashboard

Interactive dashboard with:
- Real-time account overview
- Position monitoring
- LLM decision display with full reasoning
- Trade history
- Manual and auto-trading controls

## Trading Rules

### Position Management
- Starting capital: $10,000
- Supported coins: BTC, ETH, SOL, BNB, DOGE, XRP
- Max leverage: 20x (adjustable based on conviction)
- Max risk per trade: 3% of account
- One position per coin maximum
- No pyramiding, no hedging, no partial exits

### Decision Actions
- `buy_to_enter` - Open long position
- `sell_to_enter` - Open short position
- `hold` - No action
- `close` - Close existing position

### Required Parameters
Every decision must include:
- Profit target (minimum 2:1 reward-to-risk ratio)
- Stop loss
- Invalidation condition (objective thesis-breaking signal)
- Confidence score (0-1)
- Risk exposure in USD
- Justification

## API Endpoints

### Account
- `GET /api/account` - Get account state
- `POST /api/reset` - Reset trading engine

### Trading
- `POST /api/trade/decision` - Get LLM trading decision
- `POST /api/trade/execute` - Execute a specific decision
- `POST /api/trade/auto-execute` - Get decision and execute automatically
- `GET /api/trades?limit=50` - Get trade history
- `POST /api/positions/check` - Check positions for stop loss/profit target hits

### Market Data
- `GET /api/market-data` - Get current market data for all coins

## Performance Metrics

### Sharpe Ratio
The system calculates annualized Sharpe ratio:
- **>2**: Excellent performance
- **1-2**: Good risk-adjusted performance
- **0-1**: Positive but volatile
- **<0**: Losing money

### Other Metrics
- Total equity
- Realized and unrealized PnL
- Win rate
- Total trades
- Open positions

## Prompt Engineering Insights

Based on the nof1.ai approach, this system implements several key prompt engineering techniques:

1. **Structural Enforcement**: JSON output format ensures programmatic executability and reduces hallucinations

2. **Meta-Cognitive Design**: Confidence fields and invalidation conditions create self-doubt mechanisms to prevent overconfidence bias

3. **Redundant Ordering Emphasis**: Data ordering is mentioned multiple times because transformer attention doesn't reliably preserve temporal sequence

4. **Multi-Timeframe Framing**: Separating 3-minute (entry timing) from 4-hour (trend context) reduces cognitive load while preventing conflicting signals

5. **Operational Constraints**: Explicitly stating "No pyramiding, no hedging, no external data access" prevents unintended behaviors

6. **Stateless Design**: Each decision is independent, testing the LLM's zero-shot decision capability

## Model Support

Currently supports:
- **Claude 3.5 Sonnet** (default, via Anthropic API)

Easy to extend to:
- GPT-4 (via OpenAI API)
- Gemini (via Google AI API)
- Qwen/DeepSeek (via various APIs)

Each model may require prompt tuning:
- **GPT-4**: Add "Inaction has opportunity cost" to counter conservatism
- **Claude**: Balance against over-cautious capital preservation
- **Gemini**: Emphasize indicators are tools, not rules
- **Qwen/DeepSeek**: Frame as research experiment to bypass regulation concerns

## Current Limitations

- **Mock Data**: Uses simulated market data instead of real exchange integration
- **In-Memory Storage**: No persistent database (data resets on server restart)
- **Stateless LLM**: No conversation history or learning between decisions
- **Single Model**: Currently only supports Claude

## Future Enhancements

- [ ] Real exchange integration (Hyperliquid, Binance)
- [ ] Persistent database (PostgreSQL)
- [ ] Multi-model support (GPT-4, Gemini, etc.)
- [ ] Short-term memory for LLM
- [ ] Cross-session learning mechanisms
- [ ] Backtesting framework
- [ ] Paper trading mode
- [ ] Real-time WebSocket updates
- [ ] Performance charts and analytics
- [ ] Trade export functionality

## Development

### Running Tests

```bash
cd backend
poetry run pytest

cd ../frontend
npm run test
```

### Code Structure

The codebase follows clean architecture principles:
- **Models**: Pure data structures with validation
- **Services**: Business logic and external integrations
- **API**: HTTP endpoints and request/response handling
- **Components**: Reusable UI elements

## Credits

Inspired by [nof1.ai Alpha Arena](https://nof1.ai/blog/TechPost1) - an experiment where six leading LLMs traded with $10k each in real markets using only prompt engineering.

## License

MIT

## Disclaimer

This is a demonstration project for educational purposes. The system uses simulated market data and should not be used for actual trading without extensive testing and risk management. Cryptocurrency trading carries significant risk.

## Contributing

Contributions welcome! Please open an issue or PR.

## Support

For questions or issues:
1. Check the documentation in `/backend/README.md` and `/frontend/README.md`
2. Review the API documentation at `http://localhost:8000/docs`
3. Open an issue on GitHub
