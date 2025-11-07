"""Database models and setup."""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.config import settings
import enum

Base = declarative_base()


class SignalType(str, enum.Enum):
    """Trading signal types."""
    BUY_TO_ENTER = "buy_to_enter"
    SELL_TO_ENTER = "sell_to_enter"
    HOLD = "hold"
    CLOSE = "close"


class TradeDB(Base):
    """Trade execution record in database."""
    __tablename__ = "trades"

    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)

    # Decision details
    signal = Column(Enum(SignalType), nullable=False)
    coin = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    leverage = Column(Integer, nullable=False)
    profit_target = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    invalidation_condition = Column(Text)
    confidence = Column(Float, nullable=False)
    risk_usd = Column(Float, nullable=False)
    justification = Column(Text)

    # Execution details
    execution_price = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    pnl = Column(Float, nullable=True)
    close_reason = Column(String, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    # Exchange details
    exchange_order_id = Column(String, nullable=True)
    exchange_name = Column(String, default="binance")


class PositionDB(Base):
    """Open position record in database."""
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    coin = Column(String, unique=True, nullable=False)
    entry_price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    leverage = Column(Integer, nullable=False)
    side = Column(String, nullable=False)  # long or short
    unrealized_pnl = Column(Float, default=0.0)

    # Risk management
    profit_target = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    invalidation_condition = Column(Text)

    # Timestamps
    opened_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Exchange details
    exchange_order_id = Column(String, nullable=True)
    stop_loss_order_id = Column(String, nullable=True)
    take_profit_order_id = Column(String, nullable=True)


class PerformanceMetricDB(Base):
    """Daily performance metrics."""
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, default=datetime.now, nullable=False, unique=True)

    # Account metrics
    total_equity = Column(Float, nullable=False)
    available_cash = Column(Float, nullable=False)
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)

    # Performance metrics
    sharpe_ratio = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)

    # Risk metrics
    max_drawdown_pct = Column(Float, default=0.0)
    largest_win = Column(Float, default=0.0)
    largest_loss = Column(Float, default=0.0)


class SystemEventDB(Base):
    """System events and alerts."""
    __tablename__ = "system_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    event_type = Column(String, nullable=False)  # error, warning, info, critical
    category = Column(String, nullable=False)  # safety, execution, market_data, etc.
    message = Column(Text, nullable=False)
    details = Column(Text, nullable=True)


# Create database engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
