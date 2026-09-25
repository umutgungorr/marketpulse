"""Unit tests for MarketPulse strict search engine."""

from marketpulse.services.asset_registry import AssetRegistry
from marketpulse.services.search_engine import SearchEngine


def test_search_gibberish_returns_zero_and_suggestions():
    engine = SearchEngine()
    result = engine.search("asdfghjkl_random_junk_123")
    assert result.total_matches == 0
    assert len(result.results) == 0
    assert len(result.suggestions) > 0
    assert "bulunamadı" in result.message_tr.lower()
    assert "no verified" in result.message_en.lower()


def test_search_empty_query():
    engine = SearchEngine()
    result = engine.search("")
    assert result.total_matches == 0
    assert len(result.suggestions) > 0


def test_search_exact_symbol_match():
    engine = SearchEngine()
    result = engine.search("BTC")
    assert result.total_matches >= 1
    assert result.results[0]["symbol"] == "BTC"
    assert result.results[0]["asset_type"] == "crypto"


def test_search_prefix_symbol():
    engine = SearchEngine()
    result = engine.search("asel")
    assert result.total_matches >= 1
    assert any(r["symbol"] == "ASELS" for r in result.results)


def test_search_category_isolation():
    engine = SearchEngine()

    # Search ETH in BIST category -> Must be 0 matches!
    res_bist = engine.search("ETH", asset_type="bist")
    assert res_bist.total_matches == 0

    # Search ETH in Crypto category -> Must match!
    res_crypto = engine.search("ETH", asset_type="crypto")
    assert res_crypto.total_matches >= 1
    assert res_crypto.results[0]["symbol"] == "ETH"


def test_search_by_company_name():
    engine = SearchEngine()
    result = engine.search("havayolları")
    assert result.total_matches >= 1
    assert result.results[0]["symbol"] == "THYAO"
