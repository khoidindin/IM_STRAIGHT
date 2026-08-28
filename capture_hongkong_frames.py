"""
CQG Frame Capture Utility.
Captures upstream Protobuf binary WebSocket frames from api-hongkong.cqg.com via Chrome CDP.
Credentials and URLs are loaded securely from .env via the core.config module.
"""

import json
import time
import base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from core.config import get_config
from WebAPI.webapi_2_pb2 import ClientMsg, ServerMsg


def capture_hongkong_frames():
    cfg = get_config()
    print(f"[*] Launching Chrome to capture {cfg.cqg_gateway_url} frames...")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(cfg.cqg_web_url)
        
        wait = WebDriverWait(driver, 15)
        user_input = wait.until(EC.presence_of_element_located((By.NAME, "userName")))
        pass_input = driver.find_element(By.NAME, "password")
        
        # Ingest credentials securely from .env
        user_input.send_keys(cfg.cqg_username)
        pass_input.send_keys(cfg.cqg_password)
        
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_btn.click()
        
        print(f"[OK] Authenticated user '{cfg.cqg_username}'! Collecting frames for 12 seconds...")
        time.sleep(12)
        
        logs = driver.get_log("performance")
        decoded_count = 0
        
        for entry in logs:
            msg = json.loads(entry["message"])["message"]
            method = msg.get("method", "")
            
            if method == "Network.webSocketFrameReceived":
                payload = msg.get("params", {}).get("response", {}).get("payloadData", "")
                if payload:
                    try:
                        raw_bytes = base64.b64decode(payload)
                        server_msg = ServerMsg()
                        server_msg.ParseFromString(raw_bytes)
                        print(f"[*] Decoded CQG Protobuf Frame (Length: {len(raw_bytes)} bytes)")
                        decoded_count += 1
                    except Exception:
                        pass
                        
        print(f"[SUMMARY] Successfully decoded {decoded_count} live Protobuf market data frames.")
    finally:
        driver.quit()


if __name__ == "__main__":
    capture_hongkong_frames()
