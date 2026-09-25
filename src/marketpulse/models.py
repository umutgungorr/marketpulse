"""Domain models and data definitions for MarketPulse."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class AssetType(str, Enum):
    BIST = "bist"
    CRYPTO = "crypto"
    GLOBAL = "global"


class SentimentLabel(str, Enum):
    BULLISH = "BULLISH"
    NEUTRAL = "NEUTRAL"
    BEARISH = "BEARISH"


@dataclass
class Asset:
    symbol: str
    name: str
    asset_type: AssetType
    sector: str
    currency: str
    description_tr: str
    description_en: str
    exchange: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "name": self.name,
            "asset_type": self.asset_type.value,
            "sector": self.sector,
            "currency": self.currency,
            "exchange": self.exchange,
            "description_tr": self.description_tr,
            "description_en": self.description_en,
        }


@dataclass
class PriceQuote:
    symbol: str
    current_price: float
    change_24h: float
    change_pct_24h: float
    high_24h: float
    low_24h: float
    volume_24h: float
    market_cap: float
    currency: str
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    rsi_14: float = 50.0
    trend: str = "NEUTRAL"
    last_updated: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "current_price": self.current_price,
            "change_24h": round(self.change_24h, 2),
            "change_pct_24h": round(self.change_pct_24h, 2),
            "high_24h": self.high_24h,
            "low_24h": self.low_24h,
            "volume_24h": self.volume_24h,
            "market_cap": self.market_cap,
            "currency": self.currency,
            "pe_ratio": self.pe_ratio,
            "pb_ratio": self.pb_ratio,
            "rsi_14": round(self.rsi_14, 1),
            "trend": self.trend,
            "last_updated": self.last_updated,
        }


@dataclass
class CandlePoint:
    time: str
    price: float
    volume: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "time": self.time,
            "price": self.price,
            "volume": self.volume,
        }


@dataclass
class NewsItem:
    id: str
    title_tr: str
    title_en: str
    summary_tr: str
    summary_en: str
    source: str
    published_at: str
    sentiment_score: float  # -1.0 to +1.0
    sentiment_label: SentimentLabel
    related_symbols: list[str] = field(default_factory=list)
    category: str = "Piyasa"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title_tr": self.title_tr,
            "title_en": self.title_en,
            "summary_tr": self.summary_tr,
            "summary_en": self.summary_en,
            "source": self.source,
            "published_at": self.published_at,
            "sentiment_score": round(self.sentiment_score, 2),
            "sentiment_label": self.sentiment_label.value,
            "related_symbols": self.related_symbols,
            "category": self.category,
        }


@dataclass
class PortfolioPosition:
    id: int
    symbol: str
    asset_type: str
    quantity: float
    buy_price: float
    buy_currency: str
    added_at: str
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "symbol": self.symbol,
            "asset_type": self.asset_type,
            "quantity": self.quantity,
            "buy_price": self.buy_price,
            "buy_currency": self.buy_currency,
            "added_at": self.added_at,
            "notes": self.notes,
        }


@dataclass
class PriceAlert:
    id: int
    symbol: str
    target_price: float
    condition: str  # "ABOVE", "BELOW"
    is_triggered: bool
    created_at: str
    triggered_at: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "symbol": self.symbol,
            "target_price": self.target_price,
            "condition": self.condition,
            "is_triggered": self.is_triggered,
            "created_at": self.created_at,
            "triggered_at": self.triggered_at,
        }
