"""Unit tests for bilingual sentiment engine."""

from marketpulse.models import SentimentLabel
from marketpulse.services.sentiment import SentimentEngine


def test_sentiment_positive():
    score, label = SentimentEngine.calculate_sentiment(
        "Şirket rekor kâr ve devasa büyüme açıkladı, temettü artışı onaylandı.",
        "Company reported record profit and surge in growth with approved dividend expansion."
    )
    assert score > 0.3
    assert label == SentimentLabel.BULLISH


def test_sentiment_negative():
    score, label = SentimentEngine.calculate_sentiment(
        "Şirket aleyhine ağır ceza ve soruşturma açıldı, büyük zarar bekleniyor.",
        "Company faces heavy penalty and investigation with severe loss and lawsuit risks."
    )
    assert score < -0.3
    assert label == SentimentLabel.BEARISH


def test_news_retrieval_and_filtering():
    engine = SentimentEngine()
    all_news = engine.get_news()
    assert len(all_news) > 0

    thy_news = engine.get_news(symbol="THYAO")
    assert len(thy_news) >= 1
    assert "THYAO" in thy_news[0]["related_symbols"]
