# AI Trading System - Frontend

React + TypeScript frontend dashboard for the AI trading system.

## Features

- **Real-time Account Overview**: View total equity, PnL, Sharpe ratio, and win rate
- **Position Management**: Monitor all open positions with live PnL updates
- **LLM Decision Display**: See the latest trading decision from the AI with full reasoning
- **Trade History**: Complete history of all executed trades
- **Manual Trading**: Execute individual trades on demand
- **Auto-Trading**: Enable automatic trading every 3 minutes
- **Position Monitoring**: Automatic stop loss and profit target checks

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
cd ai-trading-system/frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Edit .env if your backend is not on localhost:8000
nano .env
```

### Development

```bash
# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Environment Variables

- `VITE_API_URL`: Backend API URL (default: `http://localhost:8000`)

## Dashboard Components

### Account Overview
- Total equity and available cash
- Realized and unrealized PnL
- Sharpe ratio with color coding
- Win rate and trade statistics
- Number of open positions

### Latest LLM Decision
- Trading signal (buy/sell/hold/close)
- Coin selection
- Position size and leverage
- Confidence score
- Profit target and stop loss
- Reward-to-risk ratio
- Full justification from the LLM
- Invalidation condition

### Open Positions
- Coin and side (long/short)
- Entry price and current PnL
- Leverage used
- Profit target and stop loss levels
- Time opened
- Invalidation condition

### Trade History
- All executed trades with timestamps
- Execution prices and signals
- PnL for closed positions
- Confidence scores
- Justifications and close reasons

## Auto-Trading Mode

When enabled, auto-trading will:
1. Request a trading decision from the LLM every 3 minutes
2. Automatically execute the decision
3. Check all positions for stop loss or profit target hits
4. Update the dashboard with results

**Note**: Auto-trading uses real (simulated) capital. Monitor carefully!

## Color Coding

### Sharpe Ratio
- 🟢 Green (>2): Excellent performance
- 🟡 Yellow (1-2): Good performance
- 🟠 Orange (0-1): Positive but volatile
- 🔴 Red (<0): Losing money

### PnL
- 🟢 Green: Positive
- 🔴 Red: Negative

### Positions
- 🟢 Green border: Long position
- 🔴 Red border: Short position

## Tech Stack

- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool and dev server
- **Tailwind CSS**: Styling
- **Fetch API**: HTTP requests

## Development Notes

### State Management
- Uses React hooks (useState, useEffect)
- No external state management library needed
- Polling for updates when auto-trading is enabled

### API Integration
- All API calls centralized in `src/services/api.ts`
- Type-safe with TypeScript interfaces
- Error handling with user-friendly messages

### Responsive Design
- Mobile-friendly layout
- Grid system adapts to screen size
- Touch-optimized buttons

## Future Enhancements

- Real-time WebSocket updates
- Charts for performance visualization
- Multiple model comparison
- Trade analytics dashboard
- Export trade history
- Backtesting interface

## License

MIT
