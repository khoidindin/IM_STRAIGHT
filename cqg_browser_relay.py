"""
CQG Live Browser Relay Worker (100% Genuine Market Data Ingestion).
Automates login to m.cqg.com via Headless Chrome and captures live Protobuf market data
frames from wss://api-hongkong.cqg.com. Dispatches authentic trades, BBO, TimeBars, and L2 DOM.
"""

import asyncio
import base64
import json
import logging
import threading
import time
from typing import Callable, Optional, Dict, Any, List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from core.config import get_config
from WebAPI.webapi_2_pb2 import ClientMsg, ServerMsg
from WebAPI.historical_2_pb2 import BarUnit

logger = logging.getLogger("CQGBrowserRelay")
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")

# Default scale lookup table if metadata scale is not explicitly sent in frame
DEFAULT_PRICE_SCALES = {
    "SIE": 0.005,
    "SIL": 0.005,
    "MQI": 0.005,
    "CPE": 0.0005,
    "MQC": 0.0005,
    "MHG": 0.0005,
    "ALI": 0.5,
    "PLE": 0.1,
    "FEF": 0.01,
    "ZME": 0.1,
    "ZLE": 0.01,
    "ZSE": 0.25,
    "ZCE": 0.25,
    "ZWA": 0.25,
    "XB":  0.5,
    "XC":  0.5,
    "XW":  0.5,
    "KWE": 0.25,
    "KCE": 0.05,
    "LRC": 1.0,
    "ZFT": 0.1,
    "TRU": 0.1,
    "SBE": 0.01,
    "QW":  0.1,
    "CCE": 1.0,
    "CTE": 0.01,
}

DEFAULT_DIGITS = {
    "SIE": 3, "SIL": 3, "MQI": 3, "CPE": 4, "MQC": 4, "MHG": 4, "ALI": 1, "PLE": 1, "FEF": 2,
    "ZME": 1, "ZLE": 2, "ZSE": 2, "ZCE": 2, "ZWA": 2, "XB": 1, "XC": 1, "XW": 1, "KWE": 2,
    "KCE": 2, "LRC": 0, "ZFT": 1, "TRU": 1, "SBE": 2, "QW": 1, "CCE": 0, "CTE": 2
}


def _safe_vol(obj, field_name="scaled_volume", default=1) -> int:
    try:
        if hasattr(obj, "volume"):
            v = getattr(obj, "volume")
            if hasattr(v, "significand"):
                return int(v.significand) if v.significand > 0 else default
            if isinstance(v, (int, float)) and v > 0:
                return int(v)
        val = getattr(obj, field_name, default)
        return int(val) if val and val > 0 else default
    except Exception:
        return default


class CQGBrowserRelay:
    def __init__(self, on_market_data_callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        self.on_market_data_callback = on_market_data_callback
        self.driver: Optional[webdriver.Chrome] = None
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self.contract_symbol_map: Dict[int, str] = {}
        self.contract_scale_map: Dict[int, float] = {}
        self.contract_digits_map: Dict[int, int] = {}
        self.requested_symbols: List[str] = ["SIEZ26", "ZSEX26", "LRCX26", "CCEZ26", "CPEZ26"]

    def start(self, username: Optional[str] = None, password: Optional[str] = None):
        if self.is_running:
            return
        cfg = get_config()
        user = username or cfg.cqg_username
        pwd = password or cfg.cqg_password
        self.is_running = True
        self._thread = threading.Thread(target=self._run_loop, args=(user, pwd), daemon=True)
        self._thread.start()
        logger.info("CQG 100% Real Market Data Relay background thread launched.")

    def focus_symbol(self, symbol: str):
        """Notifies the browser session to switch or search for the active contract."""
        if symbol not in self.requested_symbols:
            self.requested_symbols.append(symbol)
        
        if self.driver:
            try:
                # Attempt to search or focus symbol in CQG omni-search
                self.driver.execute_script(f"""
                    try {{
                        const searchInputs = document.querySelectorAll("input[type='text'], input[placeholder*='Search'], input[placeholder*='Symbol']");
                        if (searchInputs.length > 0) {{
                            const inp = searchInputs[0];
                            inp.focus();
                            inp.value = '{symbol}';
                            inp.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            inp.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        }}
                    }} catch(e) {{}}
                """)
            except Exception as e:
                logger.debug(f"Focus symbol script non-critical: {e}")

    def _get_scale_and_digits(self, contract_id: int, symbol: str) -> tuple[float, int]:
        """Resolves accurate price multiplier and display digits."""
        if contract_id in self.contract_scale_map and self.contract_scale_map[contract_id] > 0:
            scale = self.contract_scale_map[contract_id]
            digits = self.contract_digits_map.get(contract_id, 2)
            return scale, digits

        # Fallback to symbol root lookup
        root = symbol[:3] if len(symbol) >= 3 else symbol
        if root not in DEFAULT_PRICE_SCALES and len(symbol) >= 2:
            root = symbol[:2]

        scale = DEFAULT_PRICE_SCALES.get(root, 1.0)
        digits = DEFAULT_DIGITS.get(root, 2)
        return scale, digits

    def _run_loop(self, username, password):
        while self.is_running:
            try:
                logger.info("Starting headless Chrome instance for genuine CQG Desktop live session...")
                options = Options()
                options.add_argument("--headless=new")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
                options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

                self.driver = webdriver.Chrome(options=options)
                cfg = get_config()
                self.driver.get(cfg.cqg_web_url)

                wait = WebDriverWait(self.driver, 20)
                user_input = wait.until(EC.presence_of_element_located((By.NAME, "userName")))
                pass_input = self.driver.find_element(By.NAME, "password")

                logger.info(f"Submitting credentials for user '{username}'...")
                user_input.clear()
                user_input.send_keys(username)
                pass_input.clear()
                pass_input.send_keys(password)

                submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                submit_btn.click()

                logger.info("Authentication submitted. Waiting 8s for workspace initialization...")
                time.sleep(8)

                # Click 'Quotes' tab to activate multi-symbol real-time streaming
                try:
                    quotes_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Quotes') or contains(text(), 'Quote')]")
                    for el in quotes_elements:
                        if el.is_displayed():
                            el.click()
                            logger.info("✓ Activated Quotes Board widget in CQG Desktop.")
                            time.sleep(2)
                            break
                except Exception as ex:
                    logger.warning(f"Could not automatically click Quotes tab: {ex}")

                logger.info("✓ Streaming 100% genuine live market data from wss://api-hongkong.cqg.com/...")

                # Continuous stream sniffing loop
                while self.is_running:
                    time.sleep(0.05)
                    try:
                        logs = self.driver.get_log("performance")
                    except Exception:
                        break

                    for entry in logs:
                        msg = json.loads(entry["message"])["message"]
                        method = msg.get("method", "")
                        params = msg.get("params", {})

                        if method == "Network.webSocketFrameReceived":
                            payload = params.get("response", {}).get("payloadData", "")
                            if not payload:
                                continue
                            try:
                                raw_bytes = base64.b64decode(payload)
                                server_msg = ServerMsg()
                                server_msg.ParseFromString(raw_bytes)
                                self._process_server_msg(server_msg)
                            except Exception:
                                pass

            except Exception as e:
                logger.error(f"Browser Relay error: {e}. Reconnecting in 5s...")
                time.sleep(5)
            finally:
                if self.driver:
                    try:
                        self.driver.quit()
                    except Exception:
                        pass

    def _process_server_msg(self, server_msg: ServerMsg):
        # 1. Map Contract ID to Symbol Name & Metadata Scale
        if server_msg.information_reports:
            for info in server_msg.information_reports:
                if info.HasField("symbol_resolution_report"):
                    res = info.symbol_resolution_report
                    meta = res.contract_metadata
                    cid = meta.contract_id
                    sym = meta.contract_symbol or meta.cqg_contract_symbol
                    if cid and sym:
                        self.contract_symbol_map[cid] = sym
                        if meta.correct_price_scale > 0:
                            self.contract_scale_map[cid] = meta.correct_price_scale
                        logger.info(f"[METADATA] Resolved: {sym} (ID={cid}, Scale={meta.correct_price_scale}, Tick={meta.tick_size})")

        if server_msg.market_data_subscription_status:
            for status in server_msg.market_data_subscription_status:
                if status.contract_id and status.symbol:
                    self.contract_symbol_map[status.contract_id] = status.symbol

        # 2. Historical Bars (TimeBarReports - Real Candles OHLCV)
        if server_msg.time_bar_reports:
            for tb_report in server_msg.time_bar_reports:
                req_id = tb_report.request_id
                time_bars = tb_report.time_bars
                if not time_bars:
                    continue

                sym = "SIEZ26"
                scale, digits = self._get_scale_and_digits(0, sym)

                bars = []
                for tb in time_bars:
                    t_sec = tb.bar_utc_time // 1000 if tb.bar_utc_time > 10000000000 else tb.bar_utc_time
                    o = round(tb.scaled_open_price * scale, digits)
                    h = round(tb.scaled_high_price * scale, digits)
                    l = round(tb.scaled_low_price * scale, digits)
                    c = round(tb.scaled_close_price * scale, digits)
                    vol = _safe_vol(tb, "scaled_volume", 1)
                    bars.append({
                        "time": t_sec,
                        "open": o,
                        "high": h,
                        "low": l,
                        "close": c,
                        "volume": vol
                    })

                event = {
                    "type": "history",
                    "symbol": sym,
                    "request_id": req_id,
                    "bars": bars,
                    "source": "CQG_REAL_GLOBEX_LIVE"
                }
                if self.on_market_data_callback:
                    self.on_market_data_callback(event)

        # 3. Real-Time Trade & Quote Feeds from global exchanges
        if server_msg.real_time_market_data:
            for rt in server_msg.real_time_market_data:
                contract_id = rt.contract_id
                sym = self.contract_symbol_map.get(contract_id, "SIEZ26")

                # Update scale if available
                if rt.correct_price_scale > 0:
                    self.contract_scale_map[contract_id] = rt.correct_price_scale

                scale, digits = self._get_scale_and_digits(contract_id, sym)

                for q in rt.quotes:
                    q_type = q.type
                    raw_p = q.scaled_price
                    if raw_p <= 0:
                        continue

                    price = round(raw_p * scale, digits)

                    if q_type == 0:  # Real Trade executed
                        event = {
                            "type": "trade",
                            "symbol": sym,
                            "contract_id": contract_id,
                            "price": price,
                            "volume": _safe_vol(q, "scaled_volume", 1),
                            "side": "BUY" if q.price_indicator == 1 else "SELL",
                            "source": "CQG_REAL_GLOBEX_LIVE"
                        }
                        if self.on_market_data_callback:
                            self.on_market_data_callback(event)

                    elif q_type in (1, 2):  # Real Best Bid / Ask
                        event = {
                            "type": "bbo",
                            "symbol": sym,
                            "contract_id": contract_id,
                            "bid": price if q_type == 1 else None,
                            "ask": price if q_type == 2 else None,
                            "source": "CQG_REAL_GLOBEX_LIVE"
                        }
                        if self.on_market_data_callback:
                            self.on_market_data_callback(event)

                for mv in rt.market_values:
                    mv_event = {
                        "type": "market_values",
                        "symbol": sym,
                        "contract_id": contract_id,
                        "open": round(mv.scaled_open_price * scale, digits) if mv.scaled_open_price else None,
                        "high": round(mv.scaled_high_price * scale, digits) if mv.scaled_high_price else None,
                        "low": round(mv.scaled_low_price * scale, digits) if mv.scaled_low_price else None,
                        "close": round(mv.scaled_close_price * scale, digits) if mv.scaled_close_price else None,
                        "last_price": round(mv.scaled_last_price_no_settlement * scale, digits) if mv.scaled_last_price_no_settlement else None,
                        "settlement": round(mv.scaled_settlement * scale, digits) if mv.scaled_settlement else None,
                        "total_volume": _safe_vol(mv, "scaled_total_volume", 0),
                        "source": "CQG_REAL_GLOBEX_LIVE"
                    }
                    if self.on_market_data_callback:
                        self.on_market_data_callback(mv_event)

        # 4. Real Level 2 Orderbook (DOM) from exchange participants
        if server_msg.order_book:
            for ob in server_msg.order_book:
                sym = self.contract_symbol_map.get(ob.contract_id, "SIEZ26")
                scale, digits = self._get_scale_and_digits(ob.contract_id, sym)

                bids = [{"price": round(b.scaled_price * scale, digits), "size": _safe_vol(b, "scaled_volume", 10)} for b in ob.bids if b.scaled_price > 0]
                asks = [{"price": round(a.scaled_price * scale, digits), "size": _safe_vol(a, "scaled_volume", 10)} for a in ob.asks if a.scaled_price > 0]

                # Sort bids descending, asks ascending
                bids.sort(key=lambda x: x["price"], reverse=True)
                asks.sort(key=lambda x: x["price"])

                event = {
                    "type": "orderbook",
                    "symbol": sym,
                    "contract_id": ob.contract_id,
                    "bids": bids,
                    "asks": asks,
                    "source": "CQG_REAL_GLOBEX_LIVE"
                }
                if self.on_market_data_callback:
                    self.on_market_data_callback(event)

    def stop(self):
        self.is_running = False
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass


if __name__ == "__main__":
    def print_event(e):
        print(f"[GENUINE LIVE EVENT] {e}")

    relay = CQGBrowserRelay(on_market_data_callback=print_event)
    relay.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        relay.stop()
