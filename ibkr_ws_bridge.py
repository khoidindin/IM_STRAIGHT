"""
Interactive Brokers (IBKR) Local WebSocket Bridge Server.
Bridges IBKR API (TWS / IB Gateway) to your platform over a standard JSON WebSocket.

Your platform connects to: ws://localhost:8766
Send JSON commands:
  - Subscribe:   {"action": "subscribe", "symbols": ["ZME", "SIE", "LRC", "FEF"]}
  - Unsubscribe: {"action": "unsubscribe", "symbols": ["ZME"]}
  - Get Status:  {"action": "status"}

Streams real-time JSON events (Trades, BBO Quotes, OHLCV, Level 2 Orderbook).
"""

import asyncio
import json
import logging
import os
from typing import Set, Dict, Any

import websockets
from ibkr_client import IBKRMarketDataClient
from ibkr_symbols import IBKR_COMMODITY_MAP

logger = logging.getLogger("IBKRBridge")
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")


class IBKRBridgeServer:
    def __init__(self, config_path: str = "ibkr_config.json"):
        self.config = self._load_config(config_path)
        self.host = self.config.get("bridge_host", "0.0.0.0")
        self.port = self.config.get("bridge_port", 8766)

        self.downstream_clients: Set[websockets.WebSocketServerProtocol] = set()

        ib_cfg = self.config.get("ibkr", {})
        self.ib_client = IBKRMarketDataClient(
            host=ib_cfg.get("host", "127.0.0.1"),
            port=ib_cfg.get("port", 7497),  # 7497: TWS Paper, 7496: TWS Live, 4002: Gateway Paper, 4001: Gateway Live
            client_id=ib_cfg.get("client_id", 1),
            on_data_callback=self._broadcast_to_clients,
        )

    def _load_config(self, path: str) -> Dict[str, Any]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "bridge_host": "127.0.0.1",
            "bridge_port": 8766,
            "ibkr": {
                "host": "127.0.0.1",
                "port": 7497,
                "client_id": 1,
                "initial_symbols": ["ZME", "SIE", "LRC", "FEF"]
            }
        }

    def _broadcast_to_clients(self, event: Dict[str, Any]):
        """Broadcasts decoded market data JSON event to all connected platform clients."""
        if not self.downstream_clients:
            return
        msg_str = json.dumps(event)
        websockets.broadcast(self.downstream_clients, msg_str)

    async def _handle_downstream_client(self, websocket: websockets.WebSocketServerProtocol):
        """Handles incoming commands from your platform connected to the local bridge."""
        self.downstream_clients.add(websocket)
        client_addr = websocket.remote_address
        logger.info(f"Platform client connected from {client_addr}. Total clients: {len(self.downstream_clients)}")

        # Send welcome/status message
        await websocket.send(json.dumps({
            "type": "connection_status",
            "provider": "Interactive Brokers",
            "ib_connected": self.ib_client.is_connected,
            "active_symbols": list(self.ib_client.active_contracts.keys()),
            "available_commodities": list(IBKR_COMMODITY_MAP.keys()),
        }))

        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    action = data.get("action", "").lower()

                    if action == "subscribe":
                        symbols = data.get("symbols", [])
                        include_depth = data.get("include_depth", True)
                        for sym in symbols:
                            logger.info(f"Client requested subscription to '{sym}'")
                            await self.ib_client.subscribe_symbol(sym, include_depth=include_depth)
                        await websocket.send(json.dumps({"type": "ack", "action": "subscribe", "symbols": symbols}))

                    elif action == "status":
                        await websocket.send(json.dumps({
                            "type": "status",
                            "ib_connected": self.ib_client.is_connected,
                            "active_symbols": list(self.ib_client.active_contracts.keys()),
                        }))

                    elif action == "ping":
                        await websocket.send(json.dumps({"type": "pong"}))

                    else:
                        await websocket.send(json.dumps({"type": "error", "message": f"Unknown action: {action}"}))

                except Exception as e:
                    logger.error(f"Error handling message from client {client_addr}: {e}")
                    await websocket.send(json.dumps({"type": "error", "message": str(e)}))

        except websockets.ConnectionClosed:
            pass
        finally:
            self.downstream_clients.remove(websocket)
            logger.info(f"Platform client {client_addr} disconnected. Remaining: {len(self.downstream_clients)}")

    async def start(self):
        """Starts both the IBKR connection and the local WebSocket bridge server."""
        # 1. Connect to IBKR (TWS or IB Gateway)
        ib_cfg = self.config.get("ibkr", {})
        try:
            await self.ib_client.connect()
            initial_symbols = ib_cfg.get("initial_symbols", ["ZME", "SIE"])
            for sym in initial_symbols:
                await self.ib_client.subscribe_symbol(sym)
        except Exception as e:
            logger.warning(f"Could not connect to IBKR at startup: {e}")
            logger.warning("Make sure TWS or IB Gateway is running with API enabled.")
            logger.info("Local bridge will remain open for platform clients.")

        # 2. Start local WebSocket server
        logger.info(f"Starting Local Platform WebSocket Bridge on ws://{self.host}:{self.port} ...")
        async with websockets.serve(self._handle_downstream_client, self.host, self.port):
            logger.info(f"=== IBKR WebSocket Bridge is RUNNING on ws://{self.host}:{self.port} ===")
            await asyncio.Future()


if __name__ == "__main__":
    bridge = IBKRBridgeServer("ibkr_config.json")
    try:
        asyncio.run(bridge.start())
    except KeyboardInterrupt:
        logger.info("Bridge stopped by user.")
