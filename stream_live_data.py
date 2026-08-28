"""
=============================================================================
CQG REAL-TIME MARKET DATA STREAM VIEWER (METHOD 4 CLIENT)
=============================================================================
Connects to the local/remote CQG WebSocket Stream Engine and prints formatted
real-time trade ticks, Level 2 orderbook depth, and OHLCV market values.

Run directly in terminal:
    python stream_live_data.py
=============================================================================
"""

import asyncio
import json
import sys
import websockets
from datetime import datetime

# ANSI Color codes for terminal beauty
CYAN = "\033[96m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


async def stream_cqg_market_data(host="127.0.0.1", port=8080, symbols=None):
    if symbols is None:
        symbols = ["ZSEX26", "SIEZ26", "LRCX26", "CCEZ26", "FEFU26", "KCEZ26"]

    ws_url = f"ws://{host}:{port}/ws"
    print(f"\n{BOLD}{CYAN}======================================================================{RESET}")
    print(f"{BOLD}{CYAN}[*] CONNECTING TO CQG REAL-TIME STREAM ENGINE: {ws_url}{RESET}")
    print(f"{BOLD}{CYAN}[*] SUBSCRIBING SYMBOLS: {', '.join(symbols)}{RESET}")
    print(f"{BOLD}{CYAN}======================================================================{RESET}\n")

    while True:
        try:
            async with websockets.connect(ws_url) as ws:
                # 1. Receive connection handshake
                welcome_msg = await ws.recv()
                welcome = json.loads(welcome_msg)
                print(f"{GREEN}[OK] Connected! Provider: {welcome.get('provider')} | Status: {welcome.get('status')}{RESET}\n")

                # 2. Send subscription request
                sub_request = {
                    "action": "subscribe",
                    "symbols": symbols,
                    "include_depth": True
                }
                await ws.send(json.dumps(sub_request))
                print(f"{YELLOW}>>> Subscription request sent for: {symbols}{RESET}\n")
                print(f"{DIM}{'-'*85}{RESET}")
                print(f"{BOLD}{'TIME (UTC)':<12} | {'TYPE':<10} | {'SYMBOL':<10} | {'DETAILS / MARKET DATA':<45}{RESET}")
                print(f"{DIM}{'-'*85}{RESET}")

                # 3. Process continuous streaming frames
                async for message in ws:
                    try:
                        packet = json.loads(message)
                        p_type = packet.get("type", "")
                        sym = packet.get("symbol", "")
                        ts = packet.get("timestamp", datetime.utcnow().isoformat())[11:19]

                        if p_type == "trade":
                            price = packet.get("price")
                            vol = packet.get("volume", 1)
                            side = packet.get("side", "BUY")
                            color = GREEN if side == "BUY" else RED
                            print(f"{ts:<12} | {color}{'TRADE':<10}{RESET} | {BOLD}{sym:<10}{RESET} | Price: {color}{BOLD}{price:<10}{RESET} Vol: {vol:<4} Side: {color}{side}{RESET}")

                        elif p_type == "orderbook":
                            bids = packet.get("bids", [])
                            asks = packet.get("asks", [])
                            best_bid = f"{bids[0]['price']} ({bids[0]['size']})" if bids else "N/A"
                            best_ask = f"{asks[0]['price']} ({asks[0]['size']})" if asks else "N/A"
                            depth_count = min(len(bids), len(asks))
                            print(f"{ts:<12} | {CYAN}{'BOOK L2':<10}{RESET} | {BOLD}{sym:<10}{RESET} | BestBid: {GREEN}{best_bid:<14}{RESET} BestAsk: {RED}{best_ask:<14}{RESET} Depth: {depth_count} levels")

                        elif p_type == "market_values":
                            last_p = packet.get("last_price")
                            high_p = packet.get("high")
                            low_p = packet.get("low")
                            tot_vol = packet.get("total_volume", 0)
                            print(f"{ts:<12} | {YELLOW}{'OHLCV':<10}{RESET} | {BOLD}{sym:<10}{RESET} | Last: {BOLD}{last_p:<8}{RESET} H: {high_p:<8} L: {low_p:<8} Vol: {tot_vol}")

                    except Exception as e:
                        print(f"Error parsing frame: {e}")

        except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError) as e:
            print(f"{RED}[!] Disconnected from server: {e}. Reconnecting in 2s...{RESET}")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"{RED}[!] Unexpected error: {e}. Retrying in 2s...{RESET}")
            await asyncio.sleep(2)


if __name__ == "__main__":
    # Custom symbols can be passed via command line: python stream_live_data.py ZSEU26 LRCU26
    sub_symbols = sys.argv[1:] if len(sys.argv) > 1 else ["ZSEU26", "ZSEX26", "SIEU26", "LRCU26", "KCEU26", "FEFQ26"]
    try:
        asyncio.run(stream_cqg_market_data(symbols=sub_symbols))
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Stream stopped by user.{RESET}")
