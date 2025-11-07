"""Binance exchange implementation."""

import ccxt
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import logging
from app.services.exchange_interface import ExchangeInterface
from app.models.trading import Coin
from app.config import settings

logger = logging.getLogger(__name__)


class BinanceExchange(ExchangeInterface):
    """Binance exchange implementation using CCXT."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        testnet: bool = True
    ):
        """Initialize Binance exchange."""
        self.api_key = api_key or settings.exchange_api_key
        self.api_secret = api_secret or settings.exchange_api_secret
        self.testnet = testnet

        # Initialize CCXT exchange
        exchange_class = ccxt.binanceusdm if not testnet else ccxt.binanceusdm

        self.exchange = exchange_class({
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',  # Use futures
                'testnet': testnet,
            }
        })

        # If testnet, set testnet URLs
        if testnet:
            self.exchange.set_sandbox_mode(True)

        # Symbol mapping
        self.symbol_map = {
            Coin.BTC: 'BTC/USDT',
            Coin.ETH: 'ETH/USDT',
            Coin.SOL: 'SOL/USDT',
            Coin.BNB: 'BNB/USDT',
            Coin.DOGE: 'DOGE/USDT',
            Coin.XRP: 'XRP/USDT',
        }

    def _get_symbol(self, coin: Coin) -> str:
        """Get trading symbol for coin."""
        return self.symbol_map.get(coin, f"{coin.value}/USDT")

    async def get_current_price(self, coin: Coin) -> float:
        """Get current market price for a coin."""
        try:
            symbol = self._get_symbol(coin)
            ticker = await asyncio.to_thread(self.exchange.fetch_ticker, symbol)
            return float(ticker['last'])
        except Exception as e:
            logger.error(f"Error fetching price for {coin}: {e}")
            raise

    async def get_account_balance(self) -> Dict[str, float]:
        """Get account balance."""
        try:
            balance = await asyncio.to_thread(self.exchange.fetch_balance)
            return {
                'total': float(balance['total'].get('USDT', 0)),
                'free': float(balance['free'].get('USDT', 0)),
                'used': float(balance['used'].get('USDT', 0))
            }
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            raise

    async def place_market_order(
        self,
        coin: Coin,
        side: str,
        quantity: float,
        leverage: int = 1
    ) -> Dict:
        """Place a market order."""
        try:
            symbol = self._get_symbol(coin)

            # Set leverage first
            await self.set_leverage(coin, leverage)

            # Place order
            order = await asyncio.to_thread(
                self.exchange.create_market_order,
                symbol,
                side,
                quantity
            )

            logger.info(f"Market order placed: {side} {quantity} {symbol} @ {leverage}x")
            return order
        except Exception as e:
            logger.error(f"Error placing market order: {e}")
            raise

    async def place_limit_order(
        self,
        coin: Coin,
        side: str,
        quantity: float,
        price: float,
        leverage: int = 1
    ) -> Dict:
        """Place a limit order."""
        try:
            symbol = self._get_symbol(coin)

            # Set leverage first
            await self.set_leverage(coin, leverage)

            # Place order
            order = await asyncio.to_thread(
                self.exchange.create_limit_order,
                symbol,
                side,
                quantity,
                price
            )

            logger.info(f"Limit order placed: {side} {quantity} {symbol} @ ${price} {leverage}x")
            return order
        except Exception as e:
            logger.error(f"Error placing limit order: {e}")
            raise

    async def cancel_order(self, order_id: str, symbol: str = None) -> bool:
        """Cancel an open order."""
        try:
            await asyncio.to_thread(self.exchange.cancel_order, order_id, symbol)
            logger.info(f"Order {order_id} cancelled")
            return True
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            return False

    async def get_open_orders(self) -> List[Dict]:
        """Get all open orders."""
        try:
            orders = await asyncio.to_thread(self.exchange.fetch_open_orders)
            return orders
        except Exception as e:
            logger.error(f"Error fetching open orders: {e}")
            return []

    async def get_positions(self) -> List[Dict]:
        """Get all open positions."""
        try:
            positions = await asyncio.to_thread(self.exchange.fetch_positions)
            # Filter out zero positions
            active_positions = [p for p in positions if float(p.get('contracts', 0)) != 0]
            return active_positions
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return []

    async def close_position(self, coin: Coin) -> Dict:
        """Close a position."""
        try:
            symbol = self._get_symbol(coin)

            # Get current position
            positions = await self.get_positions()
            position = next((p for p in positions if p['symbol'] == symbol), None)

            if not position:
                logger.warning(f"No position found for {coin}")
                return {}

            # Determine side to close (opposite of position)
            contracts = float(position['contracts'])
            side = 'sell' if contracts > 0 else 'buy'
            quantity = abs(contracts)

            # Close position with market order
            order = await self.place_market_order(coin, side, quantity)
            logger.info(f"Position closed for {coin}: {quantity} contracts")
            return order
        except Exception as e:
            logger.error(f"Error closing position for {coin}: {e}")
            raise

    async def set_leverage(self, coin: Coin, leverage: int) -> bool:
        """Set leverage for a trading pair."""
        try:
            symbol = self._get_symbol(coin)
            await asyncio.to_thread(
                self.exchange.set_leverage,
                leverage,
                symbol
            )
            logger.debug(f"Leverage set to {leverage}x for {symbol}")
            return True
        except Exception as e:
            logger.error(f"Error setting leverage for {coin}: {e}")
            return False

    async def get_market_data(
        self,
        coin: Coin,
        interval: str = "3m",
        limit: int = 100
    ) -> List[Dict]:
        """Get historical market data (OHLCV)."""
        try:
            symbol = self._get_symbol(coin)
            ohlcv = await asyncio.to_thread(
                self.exchange.fetch_ohlcv,
                symbol,
                interval,
                limit=limit
            )

            # Convert to dict format
            data = []
            for candle in ohlcv:
                data.append({
                    'timestamp': datetime.fromtimestamp(candle[0] / 1000),
                    'open': float(candle[1]),
                    'high': float(candle[2]),
                    'low': float(candle[3]),
                    'close': float(candle[4]),
                    'volume': float(candle[5])
                })

            return data
        except Exception as e:
            logger.error(f"Error fetching market data for {coin}: {e}")
            raise

    async def get_order_book(self, coin: Coin) -> Dict:
        """Get order book."""
        try:
            symbol = self._get_symbol(coin)
            order_book = await asyncio.to_thread(self.exchange.fetch_order_book, symbol)
            return order_book
        except Exception as e:
            logger.error(f"Error fetching order book for {coin}: {e}")
            raise

    def calculate_quantity(
        self,
        price: float,
        position_size_usd: float,
        leverage: int = 1
    ) -> float:
        """Calculate quantity from position size."""
        # For futures: quantity = (position_size_usd * leverage) / price
        quantity = (position_size_usd * leverage) / price
        return quantity

    async def place_stop_loss(
        self,
        coin: Coin,
        side: str,
        quantity: float,
        stop_price: float
    ) -> Dict:
        """Place a stop loss order."""
        try:
            symbol = self._get_symbol(coin)

            # Create stop market order
            order = await asyncio.to_thread(
                self.exchange.create_order,
                symbol,
                'STOP_MARKET',
                side,
                quantity,
                None,  # price (not needed for stop market)
                {'stopPrice': stop_price}
            )

            logger.info(f"Stop loss placed: {side} {quantity} {symbol} @ ${stop_price}")
            return order
        except Exception as e:
            logger.error(f"Error placing stop loss: {e}")
            raise

    async def place_take_profit(
        self,
        coin: Coin,
        side: str,
        quantity: float,
        target_price: float
    ) -> Dict:
        """Place a take profit order."""
        try:
            symbol = self._get_symbol(coin)

            # Create take profit market order
            order = await asyncio.to_thread(
                self.exchange.create_order,
                symbol,
                'TAKE_PROFIT_MARKET',
                side,
                quantity,
                None,
                {'stopPrice': target_price}
            )

            logger.info(f"Take profit placed: {side} {quantity} {symbol} @ ${target_price}")
            return order
        except Exception as e:
            logger.error(f"Error placing take profit: {e}")
            raise
