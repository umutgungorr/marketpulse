"""Unit tests for PortfolioManager and alerts."""

from pathlib import Path
from marketpulse.services.market_data import MarketDataService
from marketpulse.services.portfolio_mgr import PortfolioManager


def test_portfolio_lifecycle(tmp_path: Path):
    db_file = tmp_path / "test_portfolio.db"
    market_data = MarketDataService()
    pm = PortfolioManager(db_file, market_data)

    # 1. Add positions
    p1 = pm.add_position("THYAO", quantity=100, buy_price=300.0, notes="BIST investment")
    assert p1["symbol"] == "THYAO"
    assert p1["id"] is not None

    p2 = pm.add_position("BTC", quantity=0.1, buy_price=60000.0, notes="Crypto hold")
    assert p2["symbol"] == "BTC"

    # 2. Get summary
    summary = pm.get_portfolio_summary()
    assert summary["positions_count"] == 2
    assert summary["total_value_try"] > 0
    assert "bist" in summary["allocation_pct"]
    assert "crypto" in summary["allocation_pct"]

    # 3. Remove position
    removed = pm.remove_position(p1["id"])
    assert removed is True
    summary2 = pm.get_portfolio_summary()
    assert summary2["positions_count"] == 1


def test_watchlist_toggle(tmp_path: Path):
    db_file = tmp_path / "test_watchlist.db"
    market_data = MarketDataService()
    pm = PortfolioManager(db_file, market_data)

    assert pm.toggle_watchlist("ASELS") is True
    assert "ASELS" in pm.get_watchlist()
    assert pm.toggle_watchlist("ASELS") is False
    assert "ASELS" not in pm.get_watchlist()


def test_alerts_lifecycle(tmp_path: Path):
    db_file = tmp_path / "test_alerts.db"
    market_data = MarketDataService()
    pm = PortfolioManager(db_file, market_data)

    # Set an alert that is already hit (BTC price is ~66k, condition BELOW 100k)
    alert = pm.create_alert("BTC", target_price=100000.0, condition="BELOW")
    assert alert["id"] is not None

    alerts = pm.list_alerts()
    assert len(alerts) == 1
    # Check trigger
    assert alerts[0]["is_triggered"] is True
