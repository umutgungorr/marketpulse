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
    # Check trigger
    assert alerts[0]["is_triggered"] is True


def test_dividend_and_health_score(tmp_path: Path):
    db_file = tmp_path / "test_div.db"
    market_data = MarketDataService()
    pm = PortfolioManager(db_file, market_data)

    # EREGL has 8.4% dividend yield, TUPRS has 9.8%
    pm.add_position("EREGL", quantity=500, buy_price=45.0)
    pm.add_position("TUPRS", quantity=100, buy_price=160.0)

    summary = pm.get_portfolio_summary()
    assert summary["total_annual_dividend_try"] > 0
    assert summary["average_dividend_yield"] > 0
    assert summary["health_score"] >= 50
    assert summary["risk_level"] in ("DÜŞÜK / DENGELİ", "ORTA DÜZEY", "YÜKSEK RİSK")


def test_portfolio_csv_export(tmp_path: Path):
    db_file = tmp_path / "test_csv.db"
    market_data = MarketDataService()
    pm = PortfolioManager(db_file, market_data)

    pm.add_position("ASELS", quantity=100, buy_price=60.0, notes="Defensive hold")
    csv_text = pm.export_portfolio_csv()
    assert "Sembol,Varlık Türü,Miktar" in csv_text
    assert "ASELS" in csv_text
    assert "\ufeff" in csv_text  # UTF-8 BOM


def test_simulate_exit(tmp_path: Path):
    db_file = tmp_path / "test_sim.db"
    market_data = MarketDataService()
    pm = PortfolioManager(db_file, market_data)

    pm.add_position("THYAO", quantity=100, buy_price=300.0)

    # Simulate selling 30 shares at 350.0
    sim = pm.simulate_exit("THYAO", sell_qty=30, sell_price=350.0)
    assert sim["symbol"] == "THYAO"
    assert sim["sell_quantity"] == 30
    assert sim["sold_cost_basis"] == 30 * 300.0  # 9000
    assert sim["gross_proceeds"] == 30 * 350.0   # 10500
    assert sim["net_realized_profit"] == 1500.0
    assert sim["profit_percentage"] == round((50.0 / 300.0) * 100, 2)
    assert sim["remaining_quantity"] == 70.0

