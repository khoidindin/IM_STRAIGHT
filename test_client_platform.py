"""
Example Downstream Platform Client
Demonstrates how your platform (frontend, backend, bot) connects to the local CQG Bridge (ws://localhost:8765)
and receives real-time JSON market data ticks without needing to touch Protobuf.
"""

import asyncio
import json
import websockets

BRIDGE_URL = "ws://127.0.0.1:8765"


async def run_platform_client():
    print(f"Connecting to local CQG Bridge at {BRIDGE_URL}...")
    try:
        async with websockets.connect(BRIDGE_URL) as ws:
            print("Connected to CQG Bridge!")

            # 1. Subscribe to desired symbols (Contracts or Options)
            subscribe_cmd = {
                "action": "subscribe",
                "symbols": ["SIEU26"],
                "level": 3  # Level 3: Trades + BBO with Volumes
            }
            await ws.send(json.dumps(subscribe_cmd))
            print(f"Sent subscription command: {subscribe_cmd}")

            # 2. Listen for real-time streaming JSON ticks
            print("\nListening for real-time JSON events from CQG:")
            async for message in ws:
                data = json.loads(message)
                event_type = data.get("type")
                symbol = data.get("symbol")

                if event_type in ("trade", "best_bid", "best_ask"):
                    price = data.get("price")
                    vol = data.get("volume")
                    ts = data.get("timestamp")
                    print(f"[{event_type.upper():<8}] {symbol:<10} Price: {price} (Vol: {vol}) @ {ts}")

                elif event_type == "market_values":
                    print(f"[MARKET_VALUES] {symbol} => Last: {data.get('last_price')}, High: {data.get('high')}, Low: {data.get('low')}, Vol: {data.get('total_volume')}")

                elif event_type == "symbol_resolved":
                    c = data.get("contract", {})
                    print(f"[RESOLVED] {c.get('symbol')} => ID: {c.get('contract_id')}, Title: {c.get('title')}, TickSize: {c.get('tick_size')}")

                elif event_type == "connection_status":
                    print(f"[STATUS] CQG Connected: {data.get('cqg_connected')}, Logged On: {data.get('cqg_logged_on')}")

                else:
                    print(f"[EVENT] {data}")

    except ConnectionRefusedError:
        print(f"Could not connect to {BRIDGE_URL}. Make sure 'python cqg_ws_bridge.py' is running!")
    except KeyboardInterrupt:
        print("\nDisconnected.")


if __name__ == "__main__":
    asyncio.run(run_platform_client())
