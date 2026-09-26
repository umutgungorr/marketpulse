# 📊 MarketPulse (PiyasaRadarı)

> **Bilingual (TR/EN) Financial & Asset Intelligence Web Platform**  
> *Strict parsing, sentiment analysis, and personal portfolio tracking for Borsa Istanbul (BIST), Cryptocurrencies, and Global Stocks.*

---

## 🌟 Highlighted Features (v0.2.0)

1. **🎯 Strict & Smart Symbol Search (Zero-Junk Search):**
   - Filters out random or meaningless searches; does not produce garbage results.
   - Provides popular asset recommendations when verified symbols are not found.
2. **🇹🇷 / 🇬🇧 Live Bilingual Support (TR / EN):**
   - Instantly translates the entire interface, charts, metrics, and news sentiment cards between Turkish and English with a single click.
3. **🗂️ Strict Asset Segregation (Stocks vs Crypto):**
   - **BIST 100:** THYAO, ASELS, EREGL, GARAN, SASA, TUPRS, KCHOL etc. (P/E, P/B, Dividend Yield %, Volume).
   - **Cryptocurrencies:** BTC, ETH, SOL, AVAX, XRP, BNB etc. (Market Cap, 24h Volume, L1/DeFi categories).
   - **Global (US):** AAPL, NVDA, MSFT, TSLA, AMZN (Nasdaq/NYSE leaders).
4. **💰 Dividend & Annual Passive Income Radar:**
   - Annual dividend yields (%) and payment months for BIST stocks.
   - Calculates the estimated total annual dividend cash return across the entire portfolio.
5. **🛡️ Portfolio Health & Risk Diversification Score (0-100):**
   - Analyzes single-asset concentration and high crypto volatility risks to generate scores and warnings.
6. **📥 1-Click Excel / CSV Export:**
   - Download all open positions in UTF-8 BOM format, fully compatible with Excel and Google Sheets.
7. **🧮 Profit Realization & Exit Simulator:**
   - Pre-calculates the net profit and remaining lot amount if an exit is made at a specific target price.
8. **📰 News & KAP Disclosures Sentiment Radar:**
   - Scans BIST KAP (Public Disclosure Platform) announcements and global financial news to calculate a **Positive (Bullish) / Neutral / Negative (Bearish)** sentiment score. Features a dedicated KAP sub-filter.
9. **⏰ Price Alert System:**
   - Local alert mechanism that produces visual notifications when a specified target price is breached.
10. **⚡ Zero External Dependencies:**
    - Built with pure Python standard library (`http.server`, `sqlite3`, `json`). Zero installation hassle.

---

## 🚀 Quickstart

```bash
# Clone the repository and enter the directory:
git clone https://github.com/umutgungorr/marketpulse.git
cd marketpulse

# Start the web application (No setup required!):
python run.py
```

Open the following address in your browser:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🧪 Running Tests

```bash
uv run pytest tests -v
```

---

## 📡 REST API Endpoints

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/api/health` | Service health status |
| `GET` | `/api/indices` | Headline market indices (BIST 100, BTC.D, SPX, USD/TRY) |
| `GET` | `/api/assets?type=bist\|crypto\|global` | List assets and current prices |
| `GET` | `/api/search?q={query}&type={category}` | Strict symbol and company search |
| `GET` | `/api/chart/{symbol}?timeframe=1D\|1W\|1M\|1Y` | Historical candlestick/line chart series |
| `GET` | `/api/news?symbol={symbol}` | News feed with sentiment scores and KAP announcements |
| `GET` | `/api/portfolio` | Portfolio summary, total value, and PnL |
| `POST` | `/api/portfolio` | Add a new position (`symbol`, `quantity`, `buy_price`) |
| `DELETE` | `/api/portfolio/{id}` | Delete a position |
| `GET` | `/api/alerts` | List price alerts |
| `POST` | `/api/alerts` | Create a price alert (`symbol`, `target_price`, `condition`) |

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
