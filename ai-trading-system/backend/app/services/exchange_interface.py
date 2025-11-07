"""Exchange interface for trading operations."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
from app.models.trading import Coin


class ExchangeInterface(ABC):
    """Abstract interface for exchange operations."""

    @abstractmethod
    async def get_current_price(self, coin: Coin) -> float:
        """Get current market price for a coin."""
        pass

    @abstractmethod
    async def get_account_balance(self) -> Dict[str, float]:
        """Get account balance."""
        pass

    @abstractmethod
    async def place_market_order(
        self,
        coin: Coin,
        side: str,  # 'buy' or 'sell'
        quantity: float,
        leverage: int = 1
    ) -> Dict:
        """Place a market order."""
        pass

    @abstractmethod
    async def place_limit_order(
        self,
        coin: Coin,
        side: str,
        quantity: float,
        price: float,
        leverage: int = 1
    ) -> Dict:
        """Place a limit order."""
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an open order."""
        pass

    @abstractmethod
    async def get_open_orders(self) -> List[Dict]:
        """Get all open orders."""
        pass

    @abstractmethod
    async def get_positions(self) -> List[Dict]:
        """Get all open positions."""
        pass

    @abstractmethod
    async def close_position(self, coin: Coin) -> Dict:
        """Close a position."""
        pass

    @abstractmethod
    async def set_leverage(self, coin: Coin, leverage: int) -> bool:
        """Set leverage for a trading pair."""
        pass

    @abstractmethod
    async def get_market_data(
        self,
        coin: Coin,
        interval: str = "3m",
        limit: int = 100
    ) -> List[Dict]:
        """Get historical market data (OHLCV)."""
        pass

    @abstractmethod
    async def get_order_book(self, coin: Coin) -> Dict:
        """Get order book."""
        pass

    @abstractmethod
    def calculate_quantity(
        self,
        price: float,
        position_size_usd: float,
        leverage: int = 1
    ) -> float:
        """Calculate quantity from position size."""
        pass
