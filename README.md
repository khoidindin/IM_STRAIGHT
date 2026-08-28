# CQG Real-Time Multi-Contract Market Data Pipeline & Terminal Pro

An institutional-grade, ultra-low-latency real-time market data aggregator and trading terminal for 26 commodity futures contracts (CBOT, COMEX, NYMEX, ICE US, ICE EU, SGX, TOCOM) powered by CQG Desktop / WebAPI.

---

## 🌟 Key Features

* **Multi-Contract Delivery Month Architecture**: Tracks active prompt delivery months and forward spreads for all 26 international commodities (e.g. `ZSEX26`, `CCEZ26`, `LRCX26`, `SIEZ26`, `FEFU26`).
* **Real-Time OHLCV Candle Aggregator**: Automatic candle closure and continuous bar formation across all timeframes (`1s`, `5s`, `1m`, `5m`, `15m`, `1h`, `1D`).
* **Server-Side Persistent History**: Seamless REST API `/api/history` prevents chart hopping, resets, or repeating timestamps.
* **Level 2 Depth of Market (DOM)**: 10-level Bid/Ask orderbook ladder with dynamic relative volume depth visualization.
* **Modern Black & Orange Institutional UI**: TradingView Lightweight Charts with smooth panning, dragging, mouse wheel zoom, and responsive crosshairs.
* **Clean Architecture & Design Patterns**:
  * **Singleton Pattern**: Centralized configuration management via `.env`.
  * **Adapter / Relay Pattern**: Headless Chrome DevTools Protocol (`CDP`) Protobuf frame interceptor.
  * **Pub/Sub Broadcaster**: Non-blocking asynchronous WebSocket hub.

---

## 📁 Repository Structure

```
├── core/
│   ├── __init__.py
│   └── config.py               # Singleton AppConfig loaded from .env
├── web/
│   ├── server.py               # AsyncIO WebSocket & REST Streaming Engine (Port 8080)
│   └── public/
│       ├── index.html          # Modern Clean Trading Interface
│       ├── style.css           # Institutional Cyber Obsidian & Electric Orange Theme
│       └── app.js              # Lightweight Charts Engine & WebSocket Client
├── WebAPI/
│   ├── webapi_2_pb2.py         # Google Protobuf Binary Decoders
│   └── webapi_2.proto          # CQG WebAPI Protocol Schema
├── cqg_browser_relay.py        # Automated Headless CDP Interceptor
├── stream_live_data.py         # Standalone Python Real-Time Console Streamer
├── verify_data_pipeline.py     # Automated 5-Step Verification Test Suite
├── ARCHITECTURE_REPORT.md      # Comprehensive Architecture & Technical Report
├── .env.example                # Environment Variable Template (Safe for GitHub)
├── .gitignore                  # Git Ignore rules (protects credentials & logs)
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/your-username/cqg-market-data-terminal.git
cd cqg-market-data-terminal

# Install dependencies
pip install aiohttp websockets selenium python-dotenv protobuf
```

### 2. Environment Configuration
Copy the template `.env.example` to `.env` and configure your credentials:
```bash
cp .env.example .env
```

Edit `.env`:
```ini
CQG_USERNAME=your_username
CQG_PASSWORD=your_password
CQG_GATEWAY_URL=wss://api-hongkong.cqg.com
SERVER_HOST=0.0.0.0
SERVER_PORT=8080
```

### 3. Launch the Server
```bash
python web/server.py
```
Open **[http://localhost:8080](http://localhost:8080)** in your browser.

### 4. Run Python Real-Time Streamer
```bash
# Stream default benchmark prompt contracts
python stream_live_data.py

# Or specify custom contracts
python stream_live_data.py ZSEX26 CCEZ26 LRCX26 SIEZ26 FEFU26
```

### 5. Run Verification Suite
```bash
python verify_data_pipeline.py
```

---

## 🛡️ Security & GitHub Safety
* Real credentials and secret keys must **ONLY** reside in `.env`.
* `.env` and `config.json` are strictly excluded in `.gitignore`.
* Never push confidential passwords or auth tokens to public repositories.

---

## 📄 License
MIT License. Commercial use permitted.
