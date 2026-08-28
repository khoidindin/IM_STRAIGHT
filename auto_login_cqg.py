import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def perform_auto_login():
    print("Launching Chrome for automated login to m.cqg.com...")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    driver = webdriver.Chrome(options=options)
    driver.get("https://m.cqg.com/cqg/desktop/main")
    
    wait = WebDriverWait(driver, 15)
    print("Waiting for login inputs...")
    user_input = wait.until(EC.presence_of_element_located((By.NAME, "userName")))
    pass_input = driver.find_element(By.NAME, "password")
    
    print("Filling credentials for '080C4171295'...")
    user_input.clear()
    user_input.send_keys("080C4171295")
    pass_input.clear()
    pass_input.send_keys("BillTun@1111")
    
    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    print("Clicking 'Log on'...")
    submit_btn.click()
    
    print("Waiting 10 seconds for authentication & workspace initialization...")
    time.sleep(10)
    
    print("Current URL:", driver.current_url)
    print("Page Title:", driver.title)
    
    # Extract Local Storage keys
    storage_keys = driver.execute_script("return Object.keys(localStorage);")
    print("\nLocal Storage Keys found:", storage_keys)
    
    captured_cwas_token = driver.execute_script("return localStorage.getItem('cwasToken') || sessionStorage.getItem('cwasToken');")
    print(f"Captured cwasToken: {captured_cwas_token}")
    
    # Extract performance logs for WebSocket frames
    logs = driver.get_log("performance")
    ws_created = []
    ws_frames = 0
    for entry in logs:
        msg = json.loads(entry["message"])["message"]
        method = msg.get("method", "")
        if "Network.webSocketCreated" in method:
            ws_created.append(msg["params"].get("url"))
        elif "Network.webSocketFrameReceived" in method:
            ws_frames += 1

    print(f"WebSockets Created: {ws_created}")
    print(f"Total WebSocket Frames received: {ws_frames}")
    
    driver.quit()

if __name__ == "__main__":
    perform_auto_login()
