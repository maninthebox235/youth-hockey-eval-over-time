"""Market data service for fetching and calculating technical indicators."""

import random
from datetime import datetime, timedelta
from typing import List, Dict
import numpy as np
from app.models.trading import (
    MarketDataPoint,
    MarketData4H,
    PerpetualMetrics,
    Coin,
)


class MarketDataService:
    """Service for fetching and processing market data.

    This is a mock implementation. In production, this would connect
    to a real exchange API (e.g., Hyperliquid, Binance).
    """

    def __init__(self):
        """Initialize market data service with base prices."""
        # Base prices for each coin (as of recent market data)
        self.base_prices = {
            Coin.BTC: 43000.0,
            Coin.ETH: 2300.0,
            Coin.SOL: 110.0,
            Coin.BNB: 320.0,
            Coin.DOGE: 0.08,
            Coin.XRP: 0.55,
        }

        # Track price history for more realistic data
        self.price_history: Dict[Coin, List[float]] = {
            coin: [price] for coin, price in self.base_prices.items()
        }

    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average."""
        if len(prices) < period:
            return sum(prices) / len(prices)

        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period

        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema

        return ema

    def _calculate_macd(self, prices: List[float]) -> float:
        """Calculate MACD (12, 26, 9)."""
        if len(prices) < 26:
            return 0.0

        ema_12 = self._calculate_ema(prices, 12)
        ema_26 = self._calculate_ema(prices, 26)
        macd = ema_12 - ema_26

        return macd

    def _calculate_rsi(self, prices: List[float], period: int) -> float:
        """Calculate Relative Strength Index."""
        if len(prices) < period + 1:
            return 50.0

        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def _calculate_atr(self, prices: List[float], period: int = 14) -> float:
        """Calculate Average True Range."""
        if len(prices) < 2:
            return prices[0] * 0.02  # 2% of price as default

        true_ranges = []
        for i in range(1, len(prices)):
            high = prices[i]
            low = prices[i] * 0.98  # Simulate low as 2% below
            prev_close = prices[i-1]

            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)

        atr = sum(true_ranges[-period:]) / min(len(true_ranges), period)
        return atr

    def _generate_next_price(self, coin: Coin, current_price: float) -> float:
        """Generate next price with realistic volatility."""
        # Different volatility for different coins
        volatility = {
            Coin.BTC: 0.005,
            Coin.ETH: 0.008,
            Coin.SOL: 0.015,
            Coin.BNB: 0.010,
            Coin.DOGE: 0.025,
            Coin.XRP: 0.020,
        }

        vol = volatility.get(coin, 0.01)

        # Random walk with slight upward bias
        change = random.gauss(0.0001, vol)
        new_price = current_price * (1 + change)

        return new_price

    def get_3min_data(
        self,
        coin: Coin,
        num_points: int = 10
    ) -> List[MarketDataPoint]:
        """Get 3-minute interval data for a coin."""
        data_points = []
        now = datetime.now()

        # Get or generate price history
        if len(self.price_history[coin]) < num_points + 50:
            # Generate more history
            current_price = self.price_history[coin][-1]
            for _ in range(num_points + 50):
                current_price = self._generate_next_price(coin, current_price)
                self.price_history[coin].append(current_price)

        # Get recent prices
        recent_prices = self.price_history[coin][-num_points-50:]

        # Create data points
        for i in range(num_points):
            timestamp = now - timedelta(minutes=3 * (num_points - i - 1))
            prices_up_to_point = recent_prices[:50 + i]
            current_price = recent_prices[50 + i]

            ema20 = self._calculate_ema(prices_up_to_point, 20)
            macd = self._calculate_macd(prices_up_to_point)
            rsi7 = self._calculate_rsi(prices_up_to_point, 7)
            rsi14 = self._calculate_rsi(prices_up_to_point, 14)
            volume = current_price * random.uniform(1000, 10000)

            data_points.append(MarketDataPoint(
                timestamp=timestamp,
                coin=coin,
                price=current_price,
                ema20=ema20,
                macd=macd,
                rsi7=rsi7,
                rsi14=rsi14,
                volume=volume
            ))

        return data_points

    def get_4h_data(self, coin: Coin) -> MarketData4H:
        """Get 4-hour context data for a coin."""
        prices = self.price_history[coin][-100:]

        ema20 = self._calculate_ema(prices, 20)
        ema50 = self._calculate_ema(prices, 50)
        atr = self._calculate_atr(prices)
        macd = self._calculate_macd(prices)

        # Volume comparison (mock)
        volume_comparison = random.uniform(-0.3, 0.3)

        return MarketData4H(
            coin=coin,
            ema20=ema20,
            ema50=ema50,
            atr=atr,
            macd=macd,
            volume_comparison=volume_comparison
        )

    def get_perpetual_metrics(self, coin: Coin) -> PerpetualMetrics:
        """Get perpetual futures metrics for a coin."""
        current_price = self.price_history[coin][-1]

        # Mock open interest and funding rate
        open_interest = current_price * random.uniform(100000, 1000000)
        funding_rate = random.uniform(-0.001, 0.001)

        return PerpetualMetrics(
            coin=coin,
            open_interest=open_interest,
            funding_rate=funding_rate
        )

    def get_all_market_data(self) -> Dict[str, List]:
        """Get complete market data for all coins."""
        all_3min_data = []
        all_4h_data = []
        all_perpetual_metrics = []

        for coin in Coin:
            all_3min_data.extend(self.get_3min_data(coin, num_points=5))
            all_4h_data.append(self.get_4h_data(coin))
            all_perpetual_metrics.append(self.get_perpetual_metrics(coin))

        return {
            "data_3min": all_3min_data,
            "data_4h": all_4h_data,
            "perpetual_metrics": all_perpetual_metrics
        }

    def get_current_price(self, coin: Coin) -> float:
        """Get current price for a coin."""
        return self.price_history[coin][-1]
