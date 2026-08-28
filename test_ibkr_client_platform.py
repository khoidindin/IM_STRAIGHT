"""
Example Downstream Platform Client for IBKR WebSocket Bridge
Demonstrates how your platform (frontend, backend, bot) connects to the local IBKR Bridge (ws://localhost:8766)
and receives real-time JSON market data ticks & Level 2 Orderbook.
"""

import asyncio
import json
import websockets

BRIDGE_URL = "ws://127.0.0.1:8766"


async def run_platform_client():
    print(f"Connecting to local IBKR Bridge at {BRIDGE_URL}...")
    try:
        async with websockets.connect(BRIDGE_URL) as ws:
            print("✓ Connected to IBKR Bridge!")

            # 1. Subscribe to desired symbols (e.g. ZME, SIE, LRC, FEF)
            subscribe_cmd = {
                "action": "subscribe",
                "symbols": ["ZME", "SIE", "LRC", "FEF"],
                "include_depth": True
            }
            await ws.send(json.dumps(subscribe_cmd))
            print(f"Sent subscription command: {subscribe_cmd}")

            # 2. Listen for real-time streaming JSON ticks
            print("\nListening for real-time JSON events from IBKR:")
            async for message in ws:
                data = json.loads(message)
                event_type = data.get("type")
                symbol = data.get("symbol")

                if event_type == "trade":
                    print(f"[TRADE] {symbol:<6} Price: {data.get('price')} (Vol: {data.get('volume')}) @ {data.get('timestamp')}")

                elif event_type == "bbo":
                    print(f"[BBO  ] {symbol:<6} Bid: {data.get('bid')} ({data.get('bid_size')}) | Ask: {data.get('ask')} ({data.get('ask_size')})")

                elif event_type == "orderbook":
                    bids = data.get("bids", [])
                    asks = data.get("asks", [])
                    top_b = f"{bids[0]['price']} ({bids[0]['size']})" if bids else "N/A"
                    top_a = f"{asks[0]['price']} ({asks[0]['size']})" if asks else "N/A"
                    print(f"[ORDERBOOK L2] {symbol:<6} Top Bid: {top_b} | Top Ask: {top_a} | Depth Levels: Bids={len(bids)}, Asks={len(asks)}")

                elif event_type == "market_values":
                    print(f"[OHLCV] {symbol:<6} Last: {data.get('last_price')}, High: {data.get('high')}, Low: {data.get('low')}, Vol: {data.get('total_volume')}")

                elif event_type == "connection_status":
                    print(f"[STATUS] Provider: {data.get('provider')}, IB Connected: {data.get('ib_connected')}")

                else:
                    print(f"[EVENT] {data}")

    except ConnectionRefusedError:
        print(f"Could not connect to {BRIDGE_URL}. Make sure 'python ibkr_ws_bridge.py' is running!")
    except KeyboardInterrupt:
        print("\nDisconnected.")


if __name__ == "__main__":
    asyncio.run(run_platform_client())
