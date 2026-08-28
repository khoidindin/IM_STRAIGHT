"""
Interactive Command-Line Test Streamer for Interactive Brokers (IBKR).
Usage:
    python test_ibkr_stream.py [symbols...]

Examples:
    python test_ibkr_stream.py ZME SIE
    python test_ibkr_stream.py LRC FEF TRU
    python test_ibkr_stream.py ZSE ZCE ZWA KCE SBE
"""

import asyncio
import json
import os
import sys
from ibkr_client import IBKRMarketDataClient
from ibkr_symbols import IBKR_COMMODITY_MAP

GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"


def handle_event(event):
    etype = event.get("type")
    sym = event.get("symbol", "")
    ts = event.get("timestamp", "")[11:19]  # HH:MM:SS

    if etype == "trade":
        price = event.get("price")
        vol = event.get("volume")
        print(f"[{ts}] {BOLD}{CYAN}[IBKR TRADE]{RESET} {BOLD}{sym:<8}{RESET} Price: {GREEN}{price:>10.4f}{RESET} (Vol: {vol})")

    elif etype == "bbo":
        bid = event.get("bid")
        bid_sz = event.get("bid_size")
        ask = event.get("ask")
        ask_sz = event.get("ask_size")
        bid_str = f"{bid:>8.4f} ({bid_sz})" if bid else "     N/A     "
        ask_str = f"{ask:>8.4f} ({ask_sz})" if ask else "     N/A     "
        print(f"[{ts}] {GREEN}[BBO]{RESET} {sym:<8} Bid: {GREEN}{bid_str}{RESET} | Ask: {RED}{ask_str}{RESET}")

    elif etype == "market_values":
        last = event.get("last_price")
        high = event.get("high")
        low = event.get("low")
        tot_vol = event.get("total_volume")
        print(f"[{ts}] {YELLOW}[OHLCV]{RESET} {sym:<8} Last: {last} | High: {high} | Low: {low} | Vol: {tot_vol}")

    elif etype == "orderbook":
        bids = event.get("bids", [])
        asks = event.get("asks", [])
        print(f"\n[{ts}] {BOLD}{MAGENTA}=== [ORDERBOOK LEVEL 2] {sym} ==={RESET}")
        print(f"  {'BIDS (MUA)':<25} | {'ASKS (BÁN)':<25}")
        max_rows = max(len(bids), len(asks))
        for i in range(min(max_rows, 5)):
            bid_item = bids[i] if i < len(bids) else {}
            ask_item = asks[i] if i < len(asks) else {}
            b_str = f"{bid_item.get('price', ''):>8} (sz: {bid_item.get('size', '')})" if bid_item else ""
            a_str = f"{ask_item.get('price', ''):>8} (sz: {ask_item.get('size', '')})" if ask_item else ""
            print(f"  {GREEN}{b_str:<25}{RESET} | {RED}{a_str:<25}{RESET}")
        print(f"  {'-'*53}\n")

    elif etype == "symbol_subscribed":
        c = event.get("ib_contract", {})
        print(f"{BOLD}{GREEN}[OK] Subscribed:{RESET} {sym} -> ConID={c.get('conId')}, Symbol={c.get('symbol')} on {c.get('exchange')}")


async def main():
    config_path = "ibkr_config.json"
    config = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

    ib_cfg = config.get("ibkr", {})
    host = ib_cfg.get("host", "127.0.0.1")
    port = ib_cfg.get("port", 7497)
    client_id = ib_cfg.get("client_id", 1)

    symbols = sys.argv[1:] if len(sys.argv) > 1 else ib_cfg.get("initial_symbols", ["ZME", "SIE", "LRC", "FEF"])

    print(f"\n{BOLD}=== Interactive Brokers Real-Time Streamer (Method 5) ==={RESET}")
    print(f"Target Host:    {host}:{port}")
    print(f"Client ID:      {client_id}")
    print(f"Target Symbols: {', '.join(symbols)}\n")
    print(f"Connecting to TWS / IB Gateway...")

    client = IBKRMarketDataClient(
        host=host,
        port=port,
        client_id=client_id,
        on_data_callback=handle_event,
    )

    try:
        await client.connect()
        for sym in symbols:
            await client.subscribe_symbol(sym, include_depth=True, depth_rows=5)

        print(f"\n{BOLD}{GREEN}Streaming IBKR Real-Time Data & Orderbook... Press Ctrl+C to stop.{RESET}\n")
        await asyncio.Future()
    except (ConnectionRefusedError, OSError):
        print(f"\n{BOLD}{RED}[FAILED] Connection Refused!{RESET}")
        print(f"Could not connect to {host}:{port}.")
        print("Please make sure Trader Workstation (TWS) or IB Gateway is running and API connection is enabled:")
        print("1. Open TWS / IB Gateway")
        print("2. Go to File -> Global Configuration -> API -> Settings")
        print("3. Check 'Enable ActiveX and Socket Clients'")
        print(f"4. Set Socket port to {port} (7497 for Paper, 7496 for Live, 4002 for Gateway)\n")
    except KeyboardInterrupt:
        print("\nStopping streamer...")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
