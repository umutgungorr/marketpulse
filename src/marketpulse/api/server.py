"""Zero-dependency HTTP REST API and static web app server."""

from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import logging
from pathlib import Path
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
from urllib.parse import parse_qs, unquote, urlparse
from marketpulse.config import DB_PATH, HOST, PORT, STATIC_DIR
from marketpulse.services.asset_registry import AssetRegistry
from marketpulse.services.market_data import MarketDataService
from marketpulse.services.portfolio_mgr import PortfolioManager
from marketpulse.services.search_engine import SearchEngine
from marketpulse.services.sentiment import SentimentEngine

logger = logging.getLogger("marketpulse")


class MarketPulseHandler(SimpleHTTPRequestHandler):
    registry: AssetRegistry
    market_data: MarketDataService
    search_engine: SearchEngine
    sentiment_engine: SentimentEngine
    portfolio_mgr: PortfolioManager

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def _send_json(self, data: any, status: int = HTTPStatus.OK):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict:
        content_len = int(self.headers.get("Content-Length", 0))
        if content_len == 0:
            return {}
        raw = self.rfile.read(content_len).decode("utf-8")
        return json.loads(raw)

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # Static routing
        if not path.startswith("/api/"):
            if path in ("", "/"):
                self.path = "/index.html"
            return super().do_GET()

        try:
            # --- API ROUTES ---
            if path == "/api/health":
                self._send_json({"status": "ok", "app": "MarketPulse", "version": "0.1.0"})

            elif path == "/api/indices":
                indices = self.market_data.get_market_indices()
                self._send_json(indices)

            elif path == "/api/assets":
                type_filter = query.get("type", ["all"])[0]
                quotes = self.market_data.list_quotes(type_filter)
                self._send_json(quotes)

            elif path.startswith("/api/assets/"):
                symbol = unquote(path.split("/api/assets/")[1]).strip().upper()
                quote = self.market_data.get_quote(symbol)
                asset = self.registry.get_by_symbol(symbol)
                if not asset or not quote:
                    self._send_json({"error": "Asset not found"}, status=HTTPStatus.NOT_FOUND)
                else:
                    self._send_json({**asset.to_dict(), **quote.to_dict()})

            elif path == "/api/search":
                q = query.get("q", [""])[0]
                type_filter = query.get("type", ["all"])[0]
                res = self.search_engine.search(q, asset_type=type_filter)
                self._send_json(res.to_dict())

            elif path.startswith("/api/chart/"):
                symbol = unquote(path.split("/api/chart/")[1]).strip().upper()
                timeframe = query.get("timeframe", ["1M"])[0]
                series = self.market_data.get_chart_series(symbol, timeframe)
                self._send_json({"symbol": symbol, "timeframe": timeframe, "points": series})

            elif path == "/api/news":
                symbol = query.get("symbol", [None])[0]
                category = query.get("category", [None])[0]
                news = self.sentiment_engine.get_news(symbol, category)
                self._send_json(news)

            elif path == "/api/portfolio/export":
                csv_data = self.portfolio_mgr.export_portfolio_csv().encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Disposition", "attachment; filename=marketpulse_portfolio.csv")
                self.send_header("Content-Length", str(len(csv_data)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(csv_data)

            elif path == "/api/portfolio":
                summary = self.portfolio_mgr.get_portfolio_summary()
                self._send_json(summary)

            elif path == "/api/watchlist":
                items = self.portfolio_mgr.get_watchlist()
                self._send_json(items)

            elif path == "/api/alerts":
                alerts = self.portfolio_mgr.list_alerts()
                self._send_json(alerts)

            else:
                self._send_json({"error": "Endpoint not found"}, status=HTTPStatus.NOT_FOUND)

        except Exception as e:
            logger.exception("Error handling GET %s", path)
            self._send_json({"error": str(e)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        try:
            body = self._read_json_body()

            if path == "/api/portfolio":
                symbol = body.get("symbol")
                quantity = float(body.get("quantity", 0))
                buy_price = float(body.get("buy_price", 0))
                notes = body.get("notes", "")

                pos = self.portfolio_mgr.add_position(symbol, quantity, buy_price, notes)
                self._send_json(pos, status=HTTPStatus.CREATED)

            elif path == "/api/portfolio/simulate":
                symbol = body.get("symbol")
                sell_qty = float(body.get("sell_quantity", 0))
                sell_price = float(body.get("sell_price", 0))
                res = self.portfolio_mgr.simulate_exit(symbol, sell_qty, sell_price)
                self._send_json(res)

            elif path == "/api/watchlist/toggle":
                symbol = body.get("symbol", "")
                is_added = self.portfolio_mgr.toggle_watchlist(symbol)
                self._send_json({"symbol": symbol.upper(), "is_in_watchlist": is_added})

            elif path == "/api/alerts":
                symbol = body.get("symbol")
                target_price = float(body.get("target_price", 0))
                condition = body.get("condition", "ABOVE")

                alert = self.portfolio_mgr.create_alert(symbol, target_price, condition)
                self._send_json(alert, status=HTTPStatus.CREATED)

            else:
                self._send_json({"error": "Endpoint not found"}, status=HTTPStatus.NOT_FOUND)

        except ValueError as ve:
            self._send_json({"error": str(ve)}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.exception("Error handling POST %s", path)
            self._send_json({"error": str(e)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path

        try:
            if path.startswith("/api/portfolio/"):
                pos_id = int(path.split("/api/portfolio/")[1])
                success = self.portfolio_mgr.remove_position(pos_id)
                self._send_json({"success": success})

            elif path.startswith("/api/alerts/"):
                alert_id = int(path.split("/api/alerts/")[1])
                success = self.portfolio_mgr.delete_alert(alert_id)
                self._send_json({"success": success})

            else:
                self._send_json({"error": "Endpoint not found"}, status=HTTPStatus.NOT_FOUND)

        except Exception as e:
            logger.exception("Error handling DELETE %s", path)
            self._send_json({"error": str(e)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)


def create_server(host: str = HOST, port: int = PORT, db_path: Path = DB_PATH) -> ThreadingHTTPServer:
    registry = AssetRegistry()
    market_data = MarketDataService(registry)
    search_engine = SearchEngine(registry)
    sentiment_engine = SentimentEngine()
    portfolio_mgr = PortfolioManager(db_path, market_data, registry)

    class CustomHandler(MarketPulseHandler):
        pass

    CustomHandler.registry = registry
    CustomHandler.market_data = market_data
    CustomHandler.search_engine = search_engine
    CustomHandler.sentiment_engine = sentiment_engine
    CustomHandler.portfolio_mgr = portfolio_mgr

    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((host, port), CustomHandler)
    return server


def main():
    server = create_server()
    print(f"🚀 MarketPulse server running at: http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down MarketPulse server...")
        server.server_close()


if __name__ == "__main__":
    main()
