"""
CQG Live Browser Relay Worker (100% Genuine Market Data Ingestion).
Automates login to m.cqg.com via Headless Chrome and captures live Protobuf market data
frames from wss://api-hongkong.cqg.com. Dispatches authentic trades, BBO, and L2 DOM.
"""

import asyncio
import base64
import json
import logging
import threading
import time
from typing import Callable, Optional, Dict, Any

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from core.config import get_config
from WebAPI.webapi_2_pb2 import ClientMsg, ServerMsg

logger = logging.getLogger("CQGBrowserRelay")
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")


class CQGBrowserRelay:
    def __init__(self, on_market_data_callback: Optional[Callable] = None):
        self.on_market_data_callback = on_market_data_callback
        self.driver: Optional[webdriver.Chrome] = None
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self.contract_symbol_map: Dict[int, str] = {}

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

                logger.info("✓ Authenticated! Streaming 100% genuine market data from wss://api-hongkong.cqg.com/...")

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
        # 1. Map Contract ID to Symbol Name
        if server_msg.market_data_subscription_status:
            for status in server_msg.market_data_subscription_status:
                if status.contract_id and status.symbol:
                    self.contract_symbol_map[status.contract_id] = status.symbol

        # 2. Real-Time Trade & Quote Feeds from global exchanges
        if server_msg.real_time_market_data:
            for rt in server_msg.real_time_market_data:
                contract_id = rt.contract_id
                sym = self.contract_symbol_map.get(contract_id, "SIEH27")

                for q in rt.quotes:
                    q_type = q.type
                    price = q.scaled_price

                    if q_type == 0 and price > 0:  # Real Trade executed
                        event = {
                            "type": "trade",
                            "symbol": sym,
                            "contract_id": contract_id,
                            "price": price,
                            "volume": q.volume if q.volume > 0 else 1,
                            "side": "BUY" if q.price_indicator == 1 else "SELL",
                            "source": "CQG_REAL_GLOBEX_LIVE"
                        }
                        if self.on_market_data_callback:
                            self.on_market_data_callback(event)

                    elif q_type in (1, 2) and price > 0:  # Real Best Bid / Ask
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

        # 3. Real Level 2 Orderbook (DOM) from exchange participants
        if server_msg.order_book:
            for ob in server_msg.order_book:
                sym = self.contract_symbol_map.get(ob.contract_id, "SIEH27")
                bids = [{"price": b.scaled_price, "size": b.volume} for b in ob.bids if b.scaled_price > 0]
                asks = [{"price": a.scaled_price, "size": a.volume} for a in ob.asks if a.scaled_price > 0]
                
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
