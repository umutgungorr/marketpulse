"""Market data service providing quotes, metrics, and multi-timeframe chart series."""

from datetime import datetime, timedelta
import math
import random
from typing import Any
from marketpulse.models import Asset, AssetType, CandlePoint, PriceQuote
from marketpulse.services.asset_registry import AssetRegistry

# Baseline reference prices for realistic simulation
BASE_PRICES: dict[str, dict[str, Any]] = {
    # BIST (TRY)
    "THYAO": {"price": 312.50, "pe": 5.2, "pb": 0.95, "vol": 14_850_000, "mcap": 431_000_000_000},
    "ASELS": {"price": 64.20, "pe": 12.8, "pb": 3.4, "vol": 22_400_000, "mcap": 292_000_000_000},
    "EREGL": {"price": 49.80, "pe": 18.4, "pb": 1.1, "vol": 31_200_000, "mcap": 174_000_000_000},
    "GARAN": {"price": 124.60, "pe": 4.6, "pb": 1.3, "vol": 18_100_000, "mcap": 523_000_000_000},
    "SASA": {"price": 42.10, "pe": 26.1, "pb": 4.8, "vol": 28_000_000, "mcap": 222_000_000_000},
    "TUPRS": {"price": 168.30, "pe": 6.1, "pb": 1.8, "vol": 12_500_000, "mcap": 324_000_000_000},
    "KCHOL": {"price": 218.40, "pe": 5.8, "pb": 1.4, "vol": 9_800_000, "mcap": 554_000_000_000},
    "BIMAS": {"price": 542.00, "pe": 15.3, "pb": 5.2, "vol": 4_200_000, "mcap": 329_000_000_000},
    "AKBNK": {"price": 58.75, "pe": 4.1, "pb": 1.1, "vol": 25_000_000, "mcap": 305_000_000_000},
    "SISE": {"price": 48.90, "pe": 7.9, "pb": 1.2, "vol": 16_300_000, "mcap": 150_000_000_000},

    # Crypto (USD)
    "BTC": {"price": 66_450.00, "vol": 28_400_000_000, "mcap": 1_310_000_000_000},
    "ETH": {"price": 3_480.00, "vol": 14_900_000_000, "mcap": 418_000_000_000},
    "SOL": {"price": 152.40, "vol": 3_800_000_000, "mcap": 71_000_000_000},
    "AVAX": {"price": 28.90, "vol": 420_000_000, "mcap": 11_500_000_000},
    "XRP": {"price": 0.585, "vol": 1_250_000_000, "mcap": 33_000_000_000},
    "BNB": {"price": 588.00, "vol": 980_000_000, "mcap": 86_000_000_000},
    "LINK": {"price": 12.45, "vol": 240_000_000, "mcap": 7_500_000_000},
    "NEAR": {"price": 5.15, "vol": 310_000_000, "mcap": 5_800_000_000},

    # Global / US (USD)
    "AAPL": {"price": 227.40, "pe": 34.2, "pb": 48.0, "vol": 48_000_000, "mcap": 3_460_000_000_000},
    "NVDA": {"price": 126.80, "pe": 48.5, "pb": 36.0, "vol": 62_000_000, "mcap": 3_110_000_000_000},
    "MSFT": {"price": 432.50, "pe": 35.8, "pb": 12.5, "vol": 19_000_000, "mcap": 3_210_000_000_000},
    "TSLA": {"price": 254.20, "pe": 72.0, "pb": 11.2, "vol": 85_000_000, "mcap": 810_000_000_000},
    "AMZN": {"price": 192.10, "pe": 44.1, "pb": 8.6, "vol": 34_000_000, "mcap": 2_000_000_000_000},
}


class MarketDataService:
    def __init__(self, registry: AssetRegistry | None = None):
        self.registry = registry or AssetRegistry()
        self._price_cache: dict[str, PriceQuote] = {}
        self._seed_quotes()

    def _seed_quotes(self):
        """Generates realistic deterministic initial quotes with micro-variations."""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for asset in self.registry.list_all():
            base_info = BASE_PRICES.get(asset.symbol, {"price": 100.0, "vol": 1_000_000, "mcap": 10_000_000})
            base_price = base_info["price"]

            # Deterministic variation using symbol hash
            seed_val = sum(ord(c) for c in asset.symbol)
            rng = random.Random(seed_val + 42)
            pct_change = rng.uniform(-4.5, 5.8)
            current_price = base_price * (1 + pct_change / 100)
            change_24h = current_price - base_price

            high_24h = max(current_price, base_price) * rng.uniform(1.005, 1.025)
            low_24h = min(current_price, base_price) * rng.uniform(0.975, 0.995)
            rsi = rng.uniform(32.0, 78.0)

            trend = "BULLISH" if pct_change > 1.2 else ("BEARISH" if pct_change < -1.2 else "NEUTRAL")

            self._price_cache[asset.symbol] = PriceQuote(
                symbol=asset.symbol,
                current_price=round(current_price, 4 if current_price < 10 else 2),
                change_24h=round(change_24h, 4 if current_price < 10 else 2),
                change_pct_24h=round(pct_change, 2),
                high_24h=round(high_24h, 4 if current_price < 10 else 2),
                low_24h=round(low_24h, 4 if current_price < 10 else 2),
                volume_24h=base_info.get("vol", 1_000_000),
                market_cap=base_info.get("mcap", 10_000_000),
                currency=asset.currency,
                pe_ratio=base_info.get("pe"),
                pb_ratio=base_info.get("pb"),
                rsi_14=rsi,
                trend=trend,
                last_updated=now_str,
            )

    def get_quote(self, symbol: str) -> PriceQuote | None:
        return self._price_cache.get(symbol.strip().upper())

    def list_quotes(self, asset_type: str | None = None) -> list[dict[str, Any]]:
        assets = self.registry.list_all(asset_type)
        items = []
        for asset in assets:
            quote = self.get_quote(asset.symbol)
            if quote:
                item = {
                    **asset.to_dict(),
                    **quote.to_dict(),
                }
                items.append(item)
        return items

    def get_market_indices(self) -> list[dict[str, Any]]:
        """Returns benchmark headline indicators."""
        return [
            {"symbol": "XU100", "name": "BIST 100", "value": 9_895.40, "change_pct": 1.34, "currency": "TRY"},
            {"symbol": "BTC.D", "name": "Bitcoin Dominance", "value": 57.2, "change_pct": 0.45, "currency": "%"},
            {"symbol": "SPX", "name": "S&P 500", "value": 5_738.10, "change_pct": 0.28, "currency": "USD"},
            {"symbol": "USDTRY", "name": "Dolar / TL", "value": 34.18, "change_pct": 0.08, "currency": "TRY"},
            {"symbol": "GLD", "name": "Gram Altın", "value": 2_920.00, "change_pct": 0.85, "currency": "TRY"},
        ]

    def get_chart_series(self, symbol: str, timeframe: str = "1M") -> list[dict[str, Any]]:
        """
        Generates realistic chronological historical price points for Chart.js.
        Timeframes: 1D (24 points), 1W (7 points), 1M (30 points), 1Y (52 weekly points).
        """
        sym = symbol.strip().upper()
        quote = self.get_quote(sym)
        current_p = quote.current_price if quote else 100.0

        tf = timeframe.upper()
        if tf == "1D":
            count = 24
            delta = timedelta(hours=1)
            time_fmt = "%H:00"
            volatility = 0.008
        elif tf == "1W":
            count = 7
            delta = timedelta(days=1)
            time_fmt = "%a %d"
            volatility = 0.02
        elif tf == "1Y":
            count = 52
            delta = timedelta(weeks=1)
            time_fmt = "%b %y"
            volatility = 0.035
        else:  # Default: 1M
            count = 30
            delta = timedelta(days=1)
            time_fmt = "%d %b"
            volatility = 0.025

        now = datetime.now()
        points: list[CandlePoint] = []

        seed = sum(ord(c) for c in sym) + count
        rng = random.Random(seed)

        # Work backward from current price
        prices = [current_p]
        p = current_p
        for _ in range(count - 1):
            shock = rng.uniform(-volatility, volatility)
            p = p / (1 + shock)
            prices.insert(0, p)

        for i, price_val in enumerate(prices):
            point_time = now - (count - 1 - i) * delta
            points.append(
                CandlePoint(
                    time=point_time.strftime(time_fmt),
                    price=round(price_val, 4 if price_val < 10 else 2),
                    volume=round(rng.uniform(10_000, 500_000)),
                )
            )

        return [p.to_dict() for p in points]
