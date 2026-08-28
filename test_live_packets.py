import asyncio
import json
import websockets

async def test_stream():
    uri = "ws://127.0.0.1:8080/ws"
    print(f"Connecting to WebSocket Stream at {uri}...")
    async with websockets.connect(uri) as ws:
        print(" Connected! Receiving live real-time continuous stream:\n")
        print(f" {'TYPE':<14} | {'SYMBOL':<8} | {'PRICE / DETAIL':<22} | {'TIMING'}")
        print("-" * 65)
        for i in range(12):
            raw = await ws.recv()
            data = json.loads(raw)
            p_type = data.get("type", "").upper()
            sym = data.get("symbol", "SYSTEM")
            ts = data.get("timestamp", "")[11:19]
            
            if p_type == "TRADE":
                detail = f"Price: {data.get('price'):>8} (Vol: {data.get('volume')})"
            elif p_type == "ORDERBOOK":
                bids = len(data.get("bids", []))
                asks = len(data.get("asks", []))
                top_b = data["bids"][0]["price"] if bids > 0 else ""
                top_a = data["asks"][0]["price"] if asks > 0 else ""
                detail = f"Depth {bids}B/{asks}A | {top_b} x {top_a}"
            elif p_type == "MARKET_VALUES":
                detail = f"High: {data.get('high')} Low: {data.get('low')}"
            else:
                detail = data.get("status", "OK")

            print(f" {p_type:<14} | {sym:<8} | {detail:<22} | {ts}")

if __name__ == "__main__":
    asyncio.run(test_stream())
