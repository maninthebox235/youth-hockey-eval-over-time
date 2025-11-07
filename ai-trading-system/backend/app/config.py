"""Configuration management for production trading system."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    # API Keys
    anthropic_api_key: str
    exchange_api_key: Optional[str] = None
    exchange_api_secret: Optional[str] = None

    # Exchange Settings
    exchange_type: str = "binance"  # binance, hyperliquid, etc.
    exchange_testnet: bool = True  # Use testnet by default

    # Trading Parameters
    initial_capital: float = 10000.0
    max_position_size_pct: float = 20.0  # Max % of capital per position
    max_total_risk_pct: float = 50.0  # Max % of capital at risk total
    max_leverage: int = 10
    max_drawdown_pct: float = 15.0  # Circuit breaker

    # LLM Settings
    llm_model: str = "claude-3-opus-20240229"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2000

    # Decision Parameters
    decision_interval_seconds: int = 180  # 3 minutes
    min_confidence_threshold: float = 0.6  # Don't trade below this confidence

    # Safety Settings
    enable_trading: bool = False  # Kill switch - must be explicitly enabled
    max_trades_per_day: int = 50
    max_consecutive_losses: int = 5  # Pause after this many losses
    require_manual_approval: bool = True  # Require approval for each trade

    # Database
    database_url: str = "sqlite:///./trading.db"  # PostgreSQL in production

    # Logging
    log_level: str = "INFO"
    log_file: str = "trading.log"

    # Monitoring
    enable_telegram_alerts: bool = False
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
