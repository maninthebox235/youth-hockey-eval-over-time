# Production Trading System Setup

## ⚠️ CRITICAL WARNINGS

**This system trades with REAL MONEY. Read this entire document before proceeding.**

- Start with testnet/paper trading mode
- Test thoroughly before using real funds
- Never risk more than you can afford to lose
- Cryptocurrency trading is highly risky
- Past performance does not guarantee future results
- LLMs can make mistakes - always monitor the system
- Use proper risk management settings

## Prerequisites

### 1. Exchange Account

Create an account on a supported exchange:
- **Binance Futures** (Recommended): https://www.binance.com/
- **Hyperliquid** (Coming soon)

### 2. API Keys

Create API keys with these permissions:
- ✅ Read account information
- ✅ Place/cancel orders
- ✅ Read market data
- ❌ Withdraw funds (NEVER enable this)

**Security Best Practices:**
- Use IP whitelisting
- Store keys in secure password manager
- Never commit keys to git
- Rotate keys regularly
- Use separate keys for testing and production

### 3. System Requirements

- Python 3.10+
- PostgreSQL 14+ (for production)
- Redis (for caching and task queue)
- 2GB+ RAM
- Stable internet connection
- Linux/macOS recommended

## Installation

### 1. Install Dependencies

```bash
cd ai-trading-system/backend

# Install Python dependencies
poetry install

# Install PostgreSQL
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# macOS:
brew install postgresql

# Install Redis
# Ubuntu/Debian:
sudo apt-get install redis-server

# macOS:
brew install redis
```

### 2. Database Setup

```bash
# Create database
createdb trading_prod

# Run migrations
poetry run alembic upgrade head
```

### 3. Configuration

Copy and edit the environment file:

```bash
cp .env.example .env
nano .env
```

**Critical Settings:**

```bash
# API Keys
ANTHROPIC_API_KEY=your_anthropic_key_here
EXCHANGE_API_KEY=your_binance_key_here
EXCHANGE_API_SECRET=your_binance_secret_here

# Exchange Settings
EXCHANGE_TYPE=binance
EXCHANGE_TESTNET=true  # SET TO TRUE FOR TESTING!

# Safety Settings - CONFIGURE THESE CAREFULLY!
ENABLE_TRADING=false  # Must be explicitly enabled
MAX_POSITION_SIZE_PCT=10.0  # Max 10% of capital per position
MAX_TOTAL_RISK_PCT=30.0  # Max 30% total exposure
MAX_LEVERAGE=5  # Conservative leverage
MAX_DRAWDOWN_PCT=10.0  # Stop if 10% drawdown
MAX_TRADES_PER_DAY=20  # Limit trades per day
MAX_CONSECUTIVE_LOSSES=3  # Pause after 3 losses
MIN_CONFIDENCE_THRESHOLD=0.7  # Min 70% confidence

# Approval Settings
REQUIRE_MANUAL_APPROVAL=true  # Approve each trade manually

# Database
DATABASE_URL=postgresql://user:password@localhost/trading_prod

# LLM Settings
LLM_MODEL=claude-3-opus-20240229
LLM_TEMPERATURE=0.7

# Capital
INITIAL_CAPITAL=10000.0

# Monitoring (optional)
ENABLE_TELEGRAM_ALERTS=false
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

## Testing Mode (IMPORTANT)

**ALWAYS start with testnet/paper trading:**

```bash
# In .env file:
EXCHANGE_TESTNET=true
ENABLE_TRADING=false
REQUIRE_MANUAL_APPROVAL=true
```

### Binance Testnet

1. Go to https://testnet.binancefuture.com/
2. Create testnet account
3. Get testnet API keys
4. Fund account with test USDT (free)

## Running the System

### 1. Start Services

```bash
# Start PostgreSQL
sudo service postgresql start

# Start Redis
redis-server

# Start backend
cd ai-trading-system/backend
poetry run python -m app.main
```

### 2. Initialize Database

```bash
# Run database migrations
poetry run python -c "from app.database import init_db; init_db()"
```

### 3. Monitor Logs

```bash
# Follow logs
tail -f trading.log
```

## Safety Mechanisms

### 1. Kill Switch

```bash
# Disable all trading immediately
ENABLE_TRADING=false
```

The system checks this on every trade. Set to `false` to stop all trading instantly.

### 2. Circuit Breakers

The system automatically pauses trading if:
- Max drawdown exceeded (default: 10%)
- Too many consecutive losses (default: 3)
- Daily trade limit reached (default: 20)
- Total risk exposure too high (default: 30%)

Resume manually via API:
```bash
curl -X POST http://localhost:8000/api/safety/resume
```

### 3. Position Limits

- **Max Position Size**: Default 10% of capital
- **Max Leverage**: Default 5x
- **Max Total Risk**: Default 30% of capital

### 4. Confidence Threshold

Trades below 70% confidence are rejected by default.

### 5. Manual Approval

When `REQUIRE_MANUAL_APPROVAL=true`, every trade requires approval:

```bash
# View pending trades
curl http://localhost:8000/api/trades/pending

# Approve trade
curl -X POST http://localhost:8000/api/trades/approve/{trade_id}

# Reject trade
curl -X POST http://localhost:8000/api/trades/reject/{trade_id}
```

## Monitoring

### 1. Dashboard

Access at http://localhost:5173

Shows:
- Real-time P&L
- Open positions
- LLM decisions
- Trade history
- Safety status

### 2. API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Account state
curl http://localhost:8000/api/account

# Safety status
curl http://localhost:8000/api/safety/status

# Pause trading
curl -X POST http://localhost:8000/api/safety/pause

# Resume trading
curl -X POST http://localhost:8000/api/safety/resume
```

### 3. Telegram Alerts (Optional)

1. Create Telegram bot via @BotFather
2. Get bot token
3. Get your chat ID
4. Configure in .env:

```bash
ENABLE_TELEGRAM_ALERTS=true
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

Alerts sent for:
- Trades executed
- Positions closed
- Safety triggers
- Errors

## Risk Management Best Practices

### 1. Start Small

- Begin with minimum capital ($100-1000 in testnet)
- Use low leverage (1-3x)
- Set tight position limits (5-10% max)

### 2. Monitor Actively

- Check dashboard regularly
- Review all LLM decisions
- Verify trades executed correctly
- Monitor exchange balances

### 3. Conservative Settings

```bash
MAX_POSITION_SIZE_PCT=5.0  # Very conservative
MAX_LEVERAGE=3  # Low leverage
MAX_TOTAL_RISK_PCT=20.0  # Limited total exposure
MAX_DRAWDOWN_PCT=5.0  # Tight circuit breaker
REQUIRE_MANUAL_APPROVAL=true  # Always approve
```

### 4. Gradual Scaling

- Test 1 week on testnet
- Test 1 week with tiny real capital
- Gradually increase if successful
- Never rush to scale up

## Going Live (Production)

### ⚠️ ONLY AFTER EXTENSIVE TESTING

1. **Verify Testnet Success**
   - Run for at least 2 weeks
   - Profitable or breakeven
   - No safety triggers
   - All systems working

2. **Update Configuration**

```bash
# In .env:
EXCHANGE_TESTNET=false  # ⚠️ NOW USING REAL MONEY
ENABLE_TRADING=true
INITIAL_CAPITAL=1000.0  # Start small!
```

3. **Use Real API Keys**
   - Add production Binance keys
   - Double-check permissions
   - Test with tiny trade first

4. **Monitor Closely**
   - Watch first 10 trades carefully
   - Verify execution prices
   - Check position sizes
   - Monitor PnL

5. **Be Ready to Stop**
   - Keep dashboard open
   - Set phone alerts
   - Know how to pause (API or kill switch)

## Troubleshooting

### Trade Rejected

Check logs for reason:
- Insufficient balance?
- Safety limits exceeded?
- Confidence too low?
- Trading disabled?

### Position Not Opening

- Verify exchange API keys
- Check testnet vs. prod mode
- Verify minimum order sizes
- Check exchange status

### High Losses

**STOP TRADING IMMEDIATELY**

```bash
# Pause system
curl -X POST http://localhost:8000/api/safety/pause

# Close all positions
curl -X POST http://localhost:8000/api/positions/close-all
```

Review:
- LLM decisions (justification)
- Market conditions
- Position sizing
- Risk parameters

### Exchange Errors

- Check API key permissions
- Verify rate limits not exceeded
- Check exchange maintenance
- Verify internet connection

## Backup and Recovery

### Database Backups

```bash
# Daily backup
pg_dump trading_prod > backup_$(date +%Y%m%d).sql

# Restore
psql trading_prod < backup_20250105.sql
```

### Configuration Backups

- Keep `.env` backed up securely
- Document all parameter changes
- Track performance after changes

## Performance Optimization

### 1. LLM Prompt Tuning

- Adjust system prompt for market conditions
- Test different confidence thresholds
- Review invalidation conditions

### 2. Parameter Optimization

- Backtest different leverage levels
- Test position size variations
- Optimize stop loss distances

### 3. Market Selection

- Track which coins perform best
- Adjust coin universe seasonally
- Consider market volatility

## Legal and Compliance

- Check local regulations for algorithmic trading
- Understand tax implications
- Keep detailed records
- Consider regulatory registration if required
- Consult financial/legal advisor

## Support and Updates

- Monitor GitHub for updates
- Review commit logs before updating
- Test updates on testnet first
- Keep dependencies updated

## Emergency Procedures

### System Failure

1. Close all positions manually on exchange
2. Disable API keys
3. Review logs
4. Contact support if needed

### Large Loss

1. Pause trading immediately
2. Close positions
3. Review what happened
4. Adjust parameters
5. Resume only when confident

### Exchange Issues

1. Pause trading
2. Verify balances on exchange
3. Reconcile with system records
4. Report discrepancies to exchange

## Final Checklist Before Going Live

- [ ] Tested on testnet for 2+ weeks
- [ ] All safety parameters configured
- [ ] Manual approval enabled
- [ ] Kill switch understood
- [ ] Emergency procedures documented
- [ ] Monitoring setup and tested
- [ ] Backup procedures in place
- [ ] Risk capital only (can afford to lose)
- [ ] Legal compliance verified
- [ ] Support contacts documented
- [ ] Starting with minimum capital
- [ ] Dashboard accessible and tested
- [ ] All API keys secured
- [ ] Logs being captured
- [ ] Telegram alerts working (if enabled)

## Remember

**"The market can remain irrational longer than you can remain solvent."**

- This system is experimental
- LLMs are not infallible
- Markets are unpredictable
- Always use proper risk management
- Never risk more than you can afford to lose
- When in doubt, stay out

**Good luck and trade safely!**
