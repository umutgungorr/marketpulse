#!/usr/bin/env python3
"""Launcher script for MarketPulse Web Application."""

import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from marketpulse.api.server import main

if __name__ == "__main__":
    main()
