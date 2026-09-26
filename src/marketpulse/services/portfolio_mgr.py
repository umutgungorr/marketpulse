"""Portfolio, Watchlist, and Price Alerts management service."""

from datetime import datetime
from pathlib import Path
from typing import Any
from marketpulse.database import get_connection, init_db
from marketpulse.models import PortfolioPosition, PriceAlert
from marketpulse.services.asset_registry import AssetRegistry
from marketpulse.services.market_data import MarketDataService

USD_TRY_RATE = 34.18  # Baseline conversion rate


class PortfolioManager:
    def __init__(self, db_path: Path, market_data: MarketDataService, registry: AssetRegistry | None = None):
        self.db_path = db_path
        self.market_data = market_data
        self.registry = registry or AssetRegistry()
        init_db(self.db_path)

    # --- PORTFOLIO OPERATIONS ---
    def add_position(self, symbol: str, quantity: float, buy_price: float, notes: str = "") -> dict[str, Any]:
        sym = symbol.strip().upper()
        asset = self.registry.get_by_symbol(sym)
        if not asset:
            raise ValueError(f"Unknown symbol: {symbol}")
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        if buy_price <= 0:
            raise ValueError("Buy price must be greater than zero.")

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with get_connection(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO portfolio_items (symbol, asset_type, quantity, buy_price, buy_currency, added_at, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (sym, asset.asset_type.value, quantity, buy_price, asset.currency, now_str, notes),
            )
            conn.commit()
            pos_id = cursor.lastrowid

        return {
            "id": pos_id,
            "symbol": sym,
            "asset_type": asset.asset_type.value,
            "quantity": quantity,
            "buy_price": buy_price,
            "buy_currency": asset.currency,
            "added_at": now_str,
            "notes": notes,
        }

    def remove_position(self, position_id: int) -> bool:
        with get_connection(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM portfolio_items WHERE id = ?", (position_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_portfolio_summary(self) -> dict[str, Any]:
        with get_connection(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM portfolio_items ORDER BY id DESC").fetchall()

        positions = []
        total_cost_try = 0.0
        total_current_try = 0.0
        total_annual_dividend_try = 0.0

        allocation_by_type = {"bist": 0.0, "crypto": 0.0, "global": 0.0}

        for row in rows:
            sym = row["symbol"]
            qty = row["quantity"]
            buy_p = row["buy_price"]
            curr = row["buy_currency"]
            asset_type = row["asset_type"]

            quote = self.market_data.get_quote(sym)
            current_p = quote.current_price if quote else buy_p
            asset = self.registry.get_by_symbol(sym)
            div_yield = asset.dividend_yield if asset else 0.0

            cost = qty * buy_p
            curr_val = qty * current_p
            pnl_amount = curr_val - cost
            pnl_pct = ((current_p - buy_p) / buy_p) * 100 if buy_p > 0 else 0.0

            # Convert to TRY for global aggregate
            multiplier = USD_TRY_RATE if curr == "USD" else 1.0
            cost_try = cost * multiplier
            curr_val_try = curr_val * multiplier

            # Dividend calculation
            annual_div = curr_val * (div_yield / 100.0)
            annual_div_try = annual_div * multiplier
            total_annual_dividend_try += annual_div_try

            total_cost_try += cost_try
            total_current_try += curr_val_try

            if asset_type in allocation_by_type:
                allocation_by_type[asset_type] += curr_val_try

            positions.append({
                "id": row["id"],
                "symbol": sym,
                "asset_type": asset_type,
                "quantity": qty,
                "buy_price": buy_p,
                "current_price": current_p,
                "currency": curr,
                "cost_basis": round(cost, 2),
                "current_value": round(curr_val, 2),
                "pnl_amount": round(pnl_amount, 2),
                "pnl_pct": round(pnl_pct, 2),
                "dividend_yield": div_yield,
                "annual_dividend": round(annual_div, 2),
                "added_at": row["added_at"],
                "notes": row["notes"],
            })

        total_pnl_try = total_current_try - total_cost_try
        total_pnl_pct = (total_pnl_try / total_cost_try * 100) if total_cost_try > 0 else 0.0

        # Allocation percentages
        allocation_pct = {}
        for k, v in allocation_by_type.items():
            allocation_pct[k] = round((v / total_current_try * 100), 1) if total_current_try > 0 else 0.0

        # --- PORTFOLIO HEALTH & RISK SCORE (0-100) ---
        base_score = 100
        warnings = []

        if len(positions) == 0:
            health_score = 0
            risk_level = "NEUTRAL"
        else:
            # 1. Single asset concentration penalty
            for p in positions:
                val_try = p["current_value"] * (USD_TRY_RATE if p["currency"] == "USD" else 1.0)
                pct_of_total = (val_try / total_current_try * 100) if total_current_try > 0 else 0
                if pct_of_total > 45:
                    base_score -= 20
                    warnings.append(f"Yüksek Yoğunlaşma: {p['symbol']} portföyün %{round(pct_of_total, 1)}'ini oluşturuyor.")
                    break

            # 2. Crypto volatility risk
            crypto_pct = allocation_pct.get("crypto", 0)
            if crypto_pct > 60:
                base_score -= 20
                warnings.append(f"Yüksek Volatilite: Portföyün %{crypto_pct}'si kripto varlıklarda.")

            # 3. Diversification breadth
            if len(positions) == 1:
                base_score -= 20
                warnings.append("Tek Varlık Riski: Portföyde sadece 1 adet pozisyon var.")
            elif len(positions) >= 4:
                base_score = min(100, base_score + 5)

            health_score = max(20, min(100, base_score))
            if health_score >= 80:
                risk_level = "DÜŞÜK / DENGELİ"
            elif health_score >= 55:
                risk_level = "ORTA DÜZEY"
            else:
                risk_level = "YÜKSEK RİSK"

        avg_dividend_yield = (total_annual_dividend_try / total_current_try * 100) if total_current_try > 0 else 0.0

        return {
            "total_value_try": round(total_current_try, 2),
            "total_value_usd": round(total_current_try / USD_TRY_RATE, 2),
            "total_cost_try": round(total_cost_try, 2),
            "total_pnl_try": round(total_pnl_try, 2),
            "total_pnl_pct": round(total_pnl_pct, 2),
            "total_annual_dividend_try": round(total_annual_dividend_try, 2),
            "average_dividend_yield": round(avg_dividend_yield, 2),
            "health_score": health_score,
            "risk_level": risk_level,
            "risk_warnings": warnings,
            "positions_count": len(positions),
            "allocation_pct": allocation_pct,
            "positions": positions,
        }

    def export_portfolio_csv(self) -> str:
        """Generates UTF-8 encoded CSV string of open portfolio positions."""
        summary = self.get_portfolio_summary()
        lines = [
            "Sembol,Varlık Türü,Miktar,Alış Fiyatı,Güncel Fiyat,Para Birimi,Maliyet,Güncel Değer,Kâr/Zarar (Tutar),Kâr/Zarar (%),Temettü Verimi (%),Yıllık Temettü,Kayıt Tarihi,Notlar"
        ]
        for p in summary["positions"]:
            line = (
                f"{p['symbol']},{p['asset_type']},{p['quantity']},{p['buy_price']},"
                f"{p['current_price']},{p['currency']},{p['cost_basis']},{p['current_value']},"
                f"{p['pnl_amount']},{p['pnl_pct']}%,%{p.get('dividend_yield', 0)},"
                f"{p.get('annual_dividend', 0)},{p['added_at']},\"{p.get('notes', '')}\""
            )
            lines.append(line)
        return "\ufeff" + "\n".join(lines)  # Prepend BOM for Excel compatibility

    def simulate_exit(self, symbol: str, sell_qty: float, sell_price: float) -> dict[str, Any]:
        """Calculates realized profit and tax/net return for a planned partial or full exit."""
        sym = symbol.strip().upper()
        summary = self.get_portfolio_summary()
        matching = [p for p in summary["positions"] if p["symbol"] == sym]
        if not matching:
            raise ValueError(f"Portföyünüzde {sym} bulunmuyor.")

        total_held = sum(p["quantity"] for p in matching)
        if sell_qty > total_held:
            raise ValueError(f"Yetersiz bakiye! Elinizde {total_held} adet var, {sell_qty} satamazsınız.")

        # Weighted average buy price
        total_cost = sum(p["quantity"] * p["buy_price"] for p in matching)
        avg_buy_price = total_cost / total_held if total_held > 0 else 0.0

        sold_cost_basis = sell_qty * avg_buy_price
        gross_proceeds = sell_qty * sell_price
        net_profit = gross_proceeds - sold_cost_basis
        profit_pct = (net_profit / sold_cost_basis * 100) if sold_cost_basis > 0 else 0.0

        currency = matching[0]["currency"]

        return {
            "symbol": sym,
            "sell_quantity": sell_qty,
            "sell_price": sell_price,
            "average_buy_price": round(avg_buy_price, 2),
            "sold_cost_basis": round(sold_cost_basis, 2),
            "gross_proceeds": round(gross_proceeds, 2),
            "net_realized_profit": round(net_profit, 2),
            "profit_percentage": round(profit_pct, 2),
            "remaining_quantity": round(total_held - sell_qty, 4),
            "currency": currency,
        }

    # --- WATCHLIST OPERATIONS ---
    def toggle_watchlist(self, symbol: str) -> bool:
        sym = symbol.strip().upper()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with get_connection(self.db_path) as conn:
            exists = conn.execute("SELECT 1 FROM watchlist WHERE symbol = ?", (sym,)).fetchone()
            if exists:
                conn.execute("DELETE FROM watchlist WHERE symbol = ?", (sym,))
                conn.commit()
                return False  # Removed
            else:
                conn.execute("INSERT INTO watchlist (symbol, added_at) VALUES (?, ?)", (sym, now_str))
                conn.commit()
                return True  # Added

    def get_watchlist(self) -> list[str]:
        with get_connection(self.db_path) as conn:
            rows = conn.execute("SELECT symbol FROM watchlist ORDER BY added_at DESC").fetchall()
            return [r["symbol"] for r in rows]

    # --- ALERTS OPERATIONS ---
    def create_alert(self, symbol: str, target_price: float, condition: str) -> dict[str, Any]:
        sym = symbol.strip().upper()
        cond = condition.strip().upper()
        if cond not in ("ABOVE", "BELOW"):
            raise ValueError("Condition must be 'ABOVE' or 'BELOW'.")
        if target_price <= 0:
            raise ValueError("Target price must be positive.")

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with get_connection(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO price_alerts (symbol, target_price, condition, is_triggered, created_at)
                VALUES (?, ?, ?, 0, ?)
                """,
                (sym, target_price, cond, now_str),
            )
            conn.commit()
            alert_id = cursor.lastrowid

        return {
            "id": alert_id,
            "symbol": sym,
            "target_price": target_price,
            "condition": cond,
            "is_triggered": False,
            "created_at": now_str,
        }

    def list_alerts(self) -> list[dict[str, Any]]:
        self.check_alerts()
        with get_connection(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM price_alerts ORDER BY id DESC").fetchall()
            return [
                {
                    "id": r["id"],
                    "symbol": r["symbol"],
                    "target_price": r["target_price"],
                    "condition": r["condition"],
                    "is_triggered": bool(r["is_triggered"]),
                    "created_at": r["created_at"],
                    "triggered_at": r["triggered_at"],
                }
                for r in rows
            ]

    def delete_alert(self, alert_id: int) -> bool:
        with get_connection(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM price_alerts WHERE id = ?", (alert_id,))
            conn.commit()
            return cursor.rowcount > 0

    def check_alerts(self) -> list[dict[str, Any]]:
        """Evaluates active alerts against current market prices."""
        triggered = []
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with get_connection(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM price_alerts WHERE is_triggered = 0").fetchall()
            for r in rows:
                sym = r["symbol"]
                target = r["target_price"]
                cond = r["condition"]
                quote = self.market_data.get_quote(sym)
                if not quote:
                    continue

                curr = quote.current_price
                is_hit = (cond == "ABOVE" and curr >= target) or (cond == "BELOW" and curr <= target)

                if is_hit:
                    conn.execute(
                        "UPDATE price_alerts SET is_triggered = 1, triggered_at = ? WHERE id = ?",
                        (now_str, r["id"]),
                    )
                    triggered.append({
                        "id": r["id"],
                        "symbol": sym,
                        "target_price": target,
                        "current_price": curr,
                        "condition": cond,
                    })
            if triggered:
                conn.commit()

        return triggered
