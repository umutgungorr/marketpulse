"""Configuration settings for MarketPulse server."""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = Path.home() / ".marketpulse"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "marketpulse.db"

HOST = os.environ.get("MARKETPULSE_HOST", "127.0.0.1")
PORT = int(os.environ.get("MARKETPULSE_PORT", "8000"))
DEBUG = os.environ.get("MARKETPULSE_DEBUG", "0") == "1"
