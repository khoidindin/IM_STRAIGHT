import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_cdp():
    print("Initializing Chrome with Performance/CDP logging...")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    driver = webdriver.Chrome(options=options)
    print("Navigating to https://m.cqg.com/cqg/desktop/main...")
    driver.get("https://m.cqg.com/cqg/desktop/main")
    
    time.sleep(5)
    print("Page title:", driver.title)
    
    # Check captured performance logs
    logs = driver.get_log("performance")
    ws_events = 0
    for entry in logs:
        msg = json.loads(entry["message"])["message"]
        if "webSocket" in msg.get("method", ""):
            ws_events += 1
            print(f"CDP Event: {msg['method']}")
            
    print(f"Total WebSocket CDP events captured: {ws_events}")
    driver.quit()

if __name__ == "__main__":
    test_cdp()
