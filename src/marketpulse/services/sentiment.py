"""Bilingual (TR/EN) news & KAP announcement sentiment analysis engine."""

from datetime import datetime, timedelta
import re
from typing import Any
from marketpulse.models import NewsItem, SentimentLabel

# Bilingual financial lexicon for polarity scoring
POSITIVE_KEYWORDS_TR = [
    "rekor", "büyüme", "kâr", "artış", "ihale", "anlaşma", "yükseliş", "sözleşme", 
    "temettü", "onay", "genişleme", "yatırım", "zirve", "güçlü", "kazanç", "ortaklık"
]
NEGATIVE_KEYWORDS_TR = [
    "düşüş", "zarar", "soruşturma", "ceza", "iptal", "kriz", "enflasyon", "kayıp",
    "risk", "dava", "iflas", "gerileme", "satış baskısı", "savaş", "yaptırım"
]

POSITIVE_KEYWORDS_EN = [
    "record", "surge", "growth", "profit", "bullish", "approval", "rally", "partnership",
    "expansion", "dividend", "breakthrough", "outperform", "upgrade", "all-time high"
]
NEGATIVE_KEYWORDS_EN = [
    "drop", "plunge", "loss", "bearish", "investigation", "penalty", "inflation",
    "recession", "lawsuit", "slump", "downside", "crash", "downgrade", "sanction"
]


CURATED_NEWS_FEED: list[dict[str, Any]] = [
    {
        "id": "news-1",
        "title_tr": "THY 2026 İlk Yarı Yolcu Sayısında Tarihi Rekor Kırdı",
        "title_en": "Turkish Airlines Breaks All-Time Passenger Record in H1 2026",
        "summary_tr": "Türk Hava Yolları, uluslararası transit yolcu ve kargo gelirlerindeki %18 büyüme ile yılın ilk yarısında tüm zamanların en yüksek operasyonel kârına ulaştı.",
        "summary_en": "Turkish Airlines achieved historic operational profits in H1 driven by an 18% surge in international transit passenger and cargo revenues.",
        "source": "KAP / Finans Bülteni",
        "published_minutes_ago": 25,
        "related_symbols": ["THYAO"],
        "category": "KAP / Havacılık",
    },
    {
        "id": "news-2",
        "title_tr": "Bitcoin 66,000$ Seviyesini Savunuyor: Kurumsal ETF Girişleri Sürüyor",
        "title_en": "Bitcoin Defends $66,000 Support as Institutional ETF Inflows Accelerate",
        "summary_tr": "Spot Bitcoin ETF'lerine son 48 saatte 420 milyon dolarlık net sermaye girişi gerçekleşti. Analistler zincir üstü verilerin güçlü birikime işaret ettiğini belirtiyor.",
        "summary_en": "Spot Bitcoin ETFs recorded $420M in net inflows over 48 hours. On-chain metrics confirm robust accumulation among long-term institutional holders.",
        "source": "CoinDesk / Bloomberg Crypto",
        "published_minutes_ago": 60,
        "related_symbols": ["BTC", "ETH"],
        "category": "Kripto / Global",
    },
    {
        "id": "news-3",
        "title_tr": "Aselsan Yeni Nesil Radar ve Elektro-Optik Sistemleri İçin 140 Milyon Dolarlık İhracat Sözleşmesi İmzaladı",
        "title_en": "Aselsan Secures $140M Defense Export Contract for Next-Gen Radar Systems",
        "summary_tr": "Aselsan, NATO üyesi iki ülke ile hava savunma radarları ve elektro-optik hedefleme sistemleri teslimatı için dev bir anlaşmaya imza attı.",
        "summary_en": "Aselsan signed a massive $140M contract with two NATO nations for the delivery of tactical air defense radar and electro-optical targeting packages.",
        "source": "KAP Resmi Bildirim",
        "published_minutes_ago": 115,
        "related_symbols": ["ASELS"],
        "category": "KAP / Savunma",
    },
    {
        "id": "news-4",
        "title_tr": "NVIDIA Yeni B200 Yapay Zeka Çiplerinin Sevkiyatına Başladı, Tedarik Talebi Karşılayamıyor",
        "title_en": "NVIDIA Commences Blackwell B200 AI Chip Shipments Amid Insatiable Demand",
        "summary_tr": "Bulut devlerinin yapay zeka altyapı siparişleri nedeniyle NVIDIA'nın yeni mimari çipleri 12 ay boyunca tamamen tükendi.",
        "summary_en": "Heavy data center investments from hyperscalers leave NVIDIA's Blackwell architecture pre-orders fully booked for the next 12 months.",
        "source": "Reuters Tech",
        "published_minutes_ago": 180,
        "related_symbols": ["NVDA", "MSFT"],
        "category": "Global / Yapay Zeka",
    },
    {
        "id": "news-5",
        "title_tr": "Ereğli Demir Çelik Küresel Çelik Fiyatlarındaki Durgunluk Nedeniyle Marj Baskısı Yaşıyor",
        "title_en": "Erdemir Faces Margin Headwinds from Chinese Steel Export Pressures",
        "summary_tr": "Asya kaynaklı ucuz çelik arzı ve küresel inşaat sektöründeki durgunluk, demir-çelik sektöründe kâr marjlarını sınırlamaya devam ediyor.",
        "summary_en": "Excess Asian steel supply and muted European manufacturing demand continue to pressure operational gross margins across the sector.",
        "source": "BIST Sanayi Raporu",
        "published_minutes_ago": 260,
        "related_symbols": ["EREGL"],
        "category": "Sanayi / BIST",
    },
    {
        "id": "news-6",
        "title_tr": "Solana Ağında Günlük Aktif Cüzdan Sayısı 4.2 Milyona Ulaşarak Yeni Bir Rekor Kırdı",
        "title_en": "Solana Hits Record 4.2M Daily Active Wallets Propelled by High-Frequency DeFi",
        "summary_tr": "Merkeziyetsiz borsalardaki hacim artışı ve mikro-ödeme transferleri Solana blokzincirini aktif kullanıcı sayısında zirveye taşıdı.",
        "summary_en": "DEX volume surges and micro-payment transfers propelled Solana to new heights in on-chain user engagement and fee generation.",
        "source": "DefiLlama / CryptoSlate",
        "published_minutes_ago": 340,
        "related_symbols": ["SOL"],
        "category": "Kripto / DeFi",
    },
]


class SentimentEngine:
    @staticmethod
    def calculate_sentiment(text_tr: str, text_en: str) -> tuple[float, SentimentLabel]:
        """Calculates a normalized polarity score (-1.0 to 1.0) and categorical label."""
        text_tr_l = text_tr.lower()
        text_en_l = text_en.lower()

        pos_count = sum(1 for kw in POSITIVE_KEYWORDS_TR if kw in text_tr_l) + \
                    sum(1 for kw in POSITIVE_KEYWORDS_EN if kw in text_en_l)
        neg_count = sum(1 for kw in NEGATIVE_KEYWORDS_TR if kw in text_tr_l) + \
                    sum(1 for kw in NEGATIVE_KEYWORDS_EN if kw in text_en_l)

        total = pos_count + neg_count
        if total == 0:
            return 0.0, SentimentLabel.NEUTRAL

        score = (pos_count - neg_count) / max(total, 1)
        # Cap between -1.0 and 1.0
        score = max(-1.0, min(1.0, score))

        if score >= 0.25:
            label = SentimentLabel.BULLISH
        elif score <= -0.25:
            label = SentimentLabel.BEARISH
        else:
            label = SentimentLabel.NEUTRAL

        return score, label

    def get_news(self, symbol: str | None = None, category: str | None = None) -> list[dict[str, Any]]:
        """Returns news feed items with sentiment scores."""
        now = datetime.now()
        items: list[NewsItem] = []

        sym_filter = symbol.strip().upper() if symbol else None

        for raw in CURATED_NEWS_FEED:
            if sym_filter and sym_filter not in raw["related_symbols"]:
                continue

            pub_time = now - timedelta(minutes=raw["published_minutes_ago"])
            time_str = pub_time.strftime("%H:%M - %d.%m.%Y")

            score, label = self.calculate_sentiment(
                raw["title_tr"] + " " + raw["summary_tr"],
                raw["title_en"] + " " + raw["summary_en"]
            )

            news = NewsItem(
                id=raw["id"],
                title_tr=raw["title_tr"],
                title_en=raw["title_en"],
                summary_tr=raw["summary_tr"],
                summary_en=raw["summary_en"],
                source=raw["source"],
                published_at=time_str,
                sentiment_score=score,
                sentiment_label=label,
                related_symbols=raw["related_symbols"],
                category=raw["category"],
            )
            items.append(news)

        return [n.to_dict() for n in items]
