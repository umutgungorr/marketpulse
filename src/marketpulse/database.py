"""SQLite persistent database initialization and connection helper."""

from pathlib import Path
import sqlite3
from typing import Generator
from contextlib import contextmanager

def get_connection(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: Path):
    """Initializes tables for portfolio, alerts, and user watchlists."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with get_connection(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                asset_type TEXT NOT NULL,
                quantity REAL NOT NULL,
                buy_price REAL NOT NULL,
                buy_currency TEXT NOT NULL,
                added_at TEXT NOT NULL,
                notes TEXT DEFAULT ''
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS price_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                target_price REAL NOT NULL,
                condition TEXT NOT NULL, -- 'ABOVE' or 'BELOW'
                is_triggered INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                triggered_at TEXT
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                symbol TEXT PRIMARY KEY,
                added_at TEXT NOT NULL
            );
        """)
        conn.commit()
