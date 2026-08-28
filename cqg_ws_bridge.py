"""
CQG Local WebSocket Bridge Server
Bridges CQG WebAPI to your own trading platform or UI over a standard JSON WebSocket.

Your platform connects to: ws://localhost:8765
Send JSON commands:
  - Subscribe:   {"action": "subscribe", "symbols": ["SIEU26", "EP", "C.SIEU26 2800"]}
  - Unsubscribe: {"action": "unsubscribe", "symbols": ["SIEU26"]}
  - Get Status:  {"action": "status"}

Receives real-time JSON events (Trades, BBO Quotes, Market Values, DOM).
"""

import asyncio
import json
import logging
import os
from typing import Set, Dict, Any

import websockets
from cqg_client import CQGWebsocketClient

logger = logging.getLogger("CQGBridge")
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")


class CQGBridgeServer:
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.host = self.config.get("bridge_host", "0.0.0.0")
        self.port = self.config.get("bridge_port", 8765)

        # Downstream connected client websockets (your platform / UI / bots)
        self.downstream_clients: Set[websockets.WebSocketServerProtocol] = set()

        # Upstream CQG client
        cqg_cfg = self.config.get("cqg", {})
        self.cqg_client = CQGWebsocketClient(
            username=cqg_cfg.get("username", ""),
            password=cqg_cfg.get("password", ""),
            host=cqg_cfg.get("host", "wss://demoapi.cqg.com:443"),
            client_app_id=cqg_cfg.get("client_app_id", "CQGDesktop"),
            on_data_callback=self._broadcast_to_clients,
        )

    def _load_config(self, path: str) -> Dict[str, Any]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "bridge_host": "0.0.0.0",
            "bridge_port": 8765,
            "cqg": {
                "username": "YOUR_USERNAME",
                "password": "YOUR_PASSWORD",
                "host": "wss://demoapi.cqg.com:443",
                "client_app_id": "CQGDesktop",
                "initial_symbols": ["SIEU26"]
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
            "cqg_connected": self.cqg_client.is_connected,
            "cqg_logged_on": self.cqg_client.is_logged_on,
            "subscribed_symbols": list(self.cqg_client.contracts_by_symbol.keys()),
        }))

        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    action = data.get("action", "").lower()

                    if action == "subscribe":
                        symbols = data.get("symbols", [])
                        level = data.get("level", 3)
                        for sym in symbols:
                            logger.info(f"Client requested subscription to '{sym}'")
                            await self.cqg_client.subscribe_market_data(sym, level=level)
                        await websocket.send(json.dumps({"type": "ack", "action": "subscribe", "symbols": symbols}))

                    elif action == "unsubscribe":
                        symbols = data.get("symbols", [])
                        for sym in symbols:
                            info = self.cqg_client.contracts_by_symbol.get(sym)
                            if info:
                                await self.cqg_client.unsubscribe_market_data(info.contract_id)
                        await websocket.send(json.dumps({"type": "ack", "action": "unsubscribe", "symbols": symbols}))

                    elif action == "status":
                        await websocket.send(json.dumps({
                            "type": "status",
                            "cqg_connected": self.cqg_client.is_connected,
                            "cqg_logged_on": self.cqg_client.is_logged_on,
                            "contracts": [c.to_dict() for c in self.cqg_client.contracts_by_id.values()],
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
        """Starts both the CQG WebAPI upstream connection and the local WebSocket server."""
        # 1. Connect to CQG WebAPI
        cqg_cfg = self.config.get("cqg", {})
        username = cqg_cfg.get("username")
        password = cqg_cfg.get("password")

        if not username or username == "YOUR_USERNAME":
            logger.warning("! No valid CQG credentials found in config.json. Bridge server starting in standalone mode.")
            logger.warning("! Update config.json with your CQG Desktop credentials to stream live data.")
        else:
            try:
                await self.cqg_client.connect()
                # Subscribe to initial configured symbols
                initial_symbols = cqg_cfg.get("initial_symbols", [])
                for sym in initial_symbols:
                    await self.cqg_client.subscribe_market_data(sym)
            except Exception as e:
                logger.error(f"Failed to connect to CQG WebAPI: {e}")
                logger.info("Local bridge will remain open for platform clients to retry or configure.")

        # 2. Start local WebSocket server
        logger.info(f"Starting Local Platform WebSocket Bridge on ws://{self.host}:{self.port} ...")
        async with websockets.serve(self._handle_downstream_client, self.host, self.port):
            logger.info(f"=== CQG WebSocket Bridge is RUNNING on ws://{self.host}:{self.port} ===")
            await asyncio.Future()  # run forever


if __name__ == "__main__":
    bridge = CQGBridgeServer("config.json")
    try:
        asyncio.run(bridge.start())
    except KeyboardInterrupt:
        logger.info("Bridge stopped by user.")
