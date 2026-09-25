"""Unit tests for market data and chart point generation."""

from marketpulse.services.market_data import MarketDataService


def test_market_data_quotes_exist():
    service = MarketDataService()
    thyao_quote = service.get_quote("THYAO")
    assert thyao_quote is not None
    assert thyao_quote.current_price > 0
    assert thyao_quote.currency == "TRY"
    assert thyao_quote.rsi_14 > 0

    btc_quote = service.get_quote("BTC")
    assert btc_quote is not None
    assert btc_quote.current_price > 1000
    assert btc_quote.currency == "USD"


def test_market_indices():
    service = MarketDataService()
    indices = service.get_market_indices()
    assert len(indices) >= 5
    symbols = {i["symbol"] for i in indices}
    assert "XU100" in symbols
    assert "BTC.D" in symbols
    assert "SPX" in symbols


def test_chart_series_generation():
    service = MarketDataService()
    series_1d = service.get_chart_series("BTC", "1D")
    assert len(series_1d) == 24
    assert series_1d[0]["price"] > 0

    series_1m = service.get_chart_series("THYAO", "1M")
    assert len(series_1m) == 30
    assert series_1m[-1]["price"] > 0
