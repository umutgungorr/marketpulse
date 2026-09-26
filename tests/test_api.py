"""Integration tests for MarketPulse HTTP REST API."""

import json
from pathlib import Path
import threading
import time
import urllib.request
import pytest
from marketpulse.api.server import create_server


@pytest.fixture(scope="module")
def running_server(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("marketpulse_api_test")
    db_file = tmp_dir / "api_test.db"
    port = 8995
    server = create_server(host="127.0.0.1", port=port, db_path=db_file)

    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    time.sleep(0.3)  # Allow server to bind

    base_url = f"http://127.0.0.1:{port}"
    yield base_url

    server.shutdown()
    server.server_close()


def test_api_health(running_server):
    with urllib.request.urlopen(f"{running_server}/api/health") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert data["status"] == "ok"
        assert data["app"] == "MarketPulse"


def test_api_indices(running_server):
    with urllib.request.urlopen(f"{running_server}/api/indices") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert len(data) >= 5


def test_api_assets_filtered(running_server):
    # Only BIST
    with urllib.request.urlopen(f"{running_server}/api/assets?type=bist") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert all(a["asset_type"] == "bist" for a in data)

    # Only Crypto
    with urllib.request.urlopen(f"{running_server}/api/assets?type=crypto") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert all(a["asset_type"] == "crypto" for a in data)


def test_api_strict_search(running_server):
    # Nonsense query returns 0 matches
    with urllib.request.urlopen(f"{running_server}/api/search?q=nonsense_xyz_99") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert data["total_matches"] == 0
        assert len(data["suggestions"]) > 0

    # Valid symbol
    with urllib.request.urlopen(f"{running_server}/api/search?q=THYAO") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert data["total_matches"] >= 1
        assert data["results"][0]["symbol"] == "THYAO"


def test_api_portfolio_post_and_get(running_server):
    # 1. Post new position
    req_data = json.dumps({
        "symbol": "ASELS",
        "quantity": 50,
        "buy_price": 60.0,
        "notes": "Test buy",
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{running_server}/api/portfolio",
        data=req_data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 201
        res = json.loads(resp.read().decode())
        assert res["symbol"] == "ASELS"

    # 2. Get portfolio summary
    with urllib.request.urlopen(f"{running_server}/api/portfolio") as resp:
        assert resp.status == 200
        summary = json.loads(resp.read().decode())
        assert summary["positions_count"] >= 1
        assert summary["total_value_try"] > 0
        assert "health_score" in summary
        assert "total_annual_dividend_try" in summary


def test_api_portfolio_export_csv(running_server):
    with urllib.request.urlopen(f"{running_server}/api/portfolio/export") as resp:
        assert resp.status == 200
        assert "text/csv" in resp.headers.get("Content-Type")
        content = resp.read().decode("utf-8")
        assert "Sembol" in content
        assert "ASELS" in content


def test_api_portfolio_simulate(running_server):
    req_data = json.dumps({
        "symbol": "ASELS",
        "sell_quantity": 20,
        "sell_price": 75.0,
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{running_server}/api/portfolio/simulate",
        data=req_data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        res = json.loads(resp.read().decode())
        assert res["symbol"] == "ASELS"
        assert res["net_realized_profit"] > 0


def test_api_news_category_filter(running_server):
    # KAP category
    with urllib.request.urlopen(f"{running_server}/api/news?category=kap") as resp:
        assert resp.status == 200
        news = json.loads(resp.read().decode())
        assert len(news) >= 1
        assert all("kap" in n["category"].lower() for n in news)

