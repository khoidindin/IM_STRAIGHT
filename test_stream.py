"""
Standalone Interactive Test Streamer for CQG
Usage:
    python test_stream.py [symbols...]

Examples:
    python test_stream.py SIEU26
    python test_stream.py SIEU26 "C.US.SIEU26 2800" "P.US.SIEU26 2700"
    python test_stream.py EP CLE
"""

import asyncio
import json
import os
import sys
from cqg_client import CQGWebsocketClient

# ANSI colors for terminal display
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"


def handle_event(event):
    etype = event.get("type")
    sym = event.get("symbol", "")
    ts = event.get("timestamp", "")[11:19]  # HH:MM:SS

    if etype == "trade":
        price = event.get("price")
        vol = event.get("volume")
        vol_str = f"x {vol}" if vol is not None else ""
        print(f"[{ts}] {BOLD}{CYAN}[TRADE]{RESET} {BOLD}{sym:<12}{RESET} Price: {GREEN}{price:>10.4f}{RESET} {vol_str}")

    elif etype == "best_bid":
        price = event.get("price")
        vol = event.get("volume")
        vol_str = f"({vol})" if vol is not None else ""
        print(f"[{ts}] {GREEN}[BID  ]{RESET} {sym:<12} {price:>10.4f} {vol_str}")

    elif etype == "best_ask":
        price = event.get("price")
        vol = event.get("volume")
        vol_str = f"({vol})" if vol is not None else ""
        print(f"[{ts}] {RED}[ASK  ]{RESET} {sym:<12} {price:>10.4f} {vol_str}")

    elif etype == "market_values":
        last = event.get("last_price")
        high = event.get("high")
        low = event.get("low")
        settle = event.get("settlement")
        tot_vol = event.get("total_volume")
        print(f"[{ts}] {YELLOW}[MV   ]{RESET} {sym:<12} Last: {last} | High: {high} | Low: {low} | Settle: {settle} | Vol: {tot_vol}")

    elif etype == "symbol_resolved":
        contract = event.get("contract", {})
        print(f"{BOLD}{GREEN}✓ Symbol Resolved:{RESET} {contract.get('symbol')} (ID={contract.get('contract_id')}) - {contract.get('title')}")

    elif etype == "logon":
        if event.get("status") == "success":
            print(f"{BOLD}{GREEN}✓ Logged on to CQG WebAPI successfully!{RESET}")
        else:
            print(f"{BOLD}{RED}✗ Logon Failed: {event.get('error')}{RESET}")


async def main():
    config_path = "config.json"
    if not os.path.exists(config_path):
        print(f"Error: {config_path} not found.")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    cqg_cfg = config.get("cqg", {})
    username = cqg_cfg.get("username")
    password = cqg_cfg.get("password")
    host = cqg_cfg.get("host", "wss://api.cqg.com:443")
    client_app_id = cqg_cfg.get("client_app_id", "CQGDesktop")

    if not username or username == "YOUR_CQG_USERNAME":
        print(f"\n{BOLD}{YELLOW}[Action Required]{RESET} Please update your CQG credentials in {BOLD}config.json{RESET} first!")
        print("Set username, password, and host (wss://api.cqg.com:443 for Live or wss://demoapi.cqg.com:443 for Demo).\n")
        return

    # Symbols from command line arguments or config
    symbols = sys.argv[1:] if len(sys.argv) > 1 else cqg_cfg.get("initial_symbols", ["SIEU26"])

    print(f"\n{BOLD}=== CQG Real-Time WebSocket Streamer ==={RESET}")
    print(f"Target Host:    {host}")
    print(f"User:           {username}")
    print(f"Target Symbols: {', '.join(symbols)}\n")
    print("Connecting... (Make sure to log out of the CQG Desktop browser tab to avoid session kick)\n")

    client = CQGWebsocketClient(
        username=username,
        password=password,
        host=host,
        client_app_id=client_app_id,
        on_data_callback=handle_event,
    )

    try:
        await client.connect()
        for sym in symbols:
            await client.subscribe_market_data(sym)

        print(f"\n{BOLD}{GREEN}Streaming real-time data... Press Ctrl+C to stop.{RESET}\n")
        await asyncio.Future()  # run indefinitely
    except KeyboardInterrupt:
        print("\nStopping streamer...")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
