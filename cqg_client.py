"""
CQG WebAPI Real-Time WebSocket Client
Connects to CQG WebAPI via Secure WebSockets (WSS) and Google Protocol Buffers (Protobuf).
Parses real-time streaming market data for Futures, Options, and Cash instruments.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional, Any

import websockets
from google.protobuf.timestamp_pb2 import Timestamp

from WebAPI.webapi_2_pb2 import ClientMsg, ServerMsg
from WebAPI.user_session_2_pb2 import LogonResult
from WebAPI.market_data_2_pb2 import MarketDataSubscription, Quote, RealTimeMarketData
from WebAPI.metadata_2_pb2 import SymbolResolutionRequest, ContractMetadata
from common.decimal_pb2 import Decimal as ProtoDecimal

logger = logging.getLogger("CQGClient")
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")


def decode_proto_decimal(d: ProtoDecimal) -> Optional[float]:
    """Decodes a cqg.Decimal protobuf message into a Python float."""
    if d is None:
        return None
    try:
        return float(d.significand * (10 ** d.exponent))
    except Exception:
        return None


class CQGContractInfo:
    """Stores metadata for a resolved contract."""
    def __init__(self, metadata: ContractMetadata):
        self.contract_id: int = metadata.contract_id
        self.symbol: str = metadata.contract_symbol or metadata.cqg_contract_symbol
        self.cqg_symbol: str = metadata.cqg_contract_symbol or metadata.contract_symbol
        self.title: str = metadata.title or metadata.description
        self.description: str = metadata.description
        self.price_scale: float = metadata.correct_price_scale if metadata.correct_price_scale != 0 else 1.0
        self.tick_size: float = metadata.tick_size
        self.tick_value: float = metadata.tick_value
        self.currency: str = metadata.currency
        self.underlying_symbol: str = metadata.underlying_contract_symbol
        self.strike_price: float = metadata.strike_price if metadata.strike_price != 0 else None
        self.last_trading_date: int = metadata.last_trading_date

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "symbol": self.symbol,
            "cqg_symbol": self.cqg_symbol,
            "title": self.title,
            "description": self.description,
            "price_scale": self.price_scale,
            "tick_size": self.tick_size,
            "tick_value": self.tick_value,
            "currency": self.currency,
            "underlying_symbol": self.underlying_symbol,
            "strike_price": self.strike_price,
        }


class CQGWebsocketClient:
    """
    Asynchronous CQG WebAPI WebSocket Client.
    Handles authentication, heartbeat pings, symbol resolution, and real-time data streaming.
    """

    def __init__(
        self,
        username: str,
        password: str,
        host: str = "wss://demoapi.cqg.com:443",
        client_app_id: str = "CQGDesktop",
        client_version: str = "python-client-v1.0",
        on_data_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        self.username = username
        self.password = password
        self.host = host
        self.client_app_id = client_app_id
        self.client_version = client_version
        self.on_data_callback = on_data_callback

        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.is_connected = False
        self.is_logged_on = False
        self.session_token: Optional[str] = None
        self._msg_id = 0

        # Mapping: symbol string -> CQGContractInfo & contract_id -> CQGContractInfo
        self.contracts_by_id: Dict[int, CQGContractInfo] = {}
        self.contracts_by_symbol: Dict[str, CQGContractInfo] = {}
        self.subscribed_contract_ids: set = set()
        self._resolution_futures: Dict[int, asyncio.Future] = {}
        self._running_tasks: List[asyncio.Task] = []

    def _next_msg_id(self) -> int:
        self._msg_id += 1
        return self._msg_id

    async def connect(self):
        """Connects to the CQG WebSocket endpoint and initiates logon."""
        logger.info(f"Connecting to CQG WebAPI at {self.host}...")
        self.ws = await websockets.connect(self.host, max_size=10 * 1024 * 1024, ping_interval=None)
        self.is_connected = True
        logger.info("Connected to WebSocket transport.")

        # Start receiver loop
        receiver_task = asyncio.create_task(self._receive_loop())
        self._running_tasks.append(receiver_task)

        # Send Logon request
        await self._send_logon()

        # Wait for logon confirmation
        for _ in range(50):
            if self.is_logged_on:
                break
            await asyncio.sleep(0.1)

        if not self.is_logged_on:
            raise TimeoutError("CQG Logon timed out or failed.")

        # Start heartbeat ping loop
        ping_task = asyncio.create_task(self._ping_loop())
        self._running_tasks.append(ping_task)
        logger.info("CQG Client is ready and authenticated.")

    async def _send_logon(self):
        """Builds and sends the initial Logon message."""
        client_msg = ClientMsg()
        logon = client_msg.logon
        logon.user_name = self.username
        logon.password = self.password
        logon.client_app_id = self.client_app_id
        logon.client_version = self.client_version
        logon.protocol_version_major = 2
        logon.protocol_version_minor = 230
        
        await self._send_message(client_msg)
        logger.info(f"Logon request sent for user '{self.username}' (App: {self.client_app_id}).")

    async def _send_message(self, client_msg: ClientMsg):
        """Serializes and sends a ClientMsg protobuf over WebSocket."""
        if not self.ws:
            raise ConnectionError("WebSocket is not connected.")
        payload = client_msg.SerializeToString()
        await self.ws.send(payload)

    async def _ping_loop(self):
        """Sends periodic ping messages to keep the session alive."""
        try:
            while self.is_connected and self.is_logged_on:
                await asyncio.sleep(30)
                client_msg = ClientMsg()
                ping = client_msg.ping
                ping.ping_utc_timestamp.GetCurrentTime()
                await self._send_message(client_msg)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.warning(f"Ping loop encountered error: {e}")

    async def _receive_loop(self):
        """Asynchronously receives and parses incoming ServerMsg protobuf messages."""
        try:
            async for raw_data in self.ws:
                server_msg = ServerMsg()
                server_msg.ParseFromString(raw_data)
                await self._handle_server_message(server_msg)
        except websockets.ConnectionClosed as e:
            logger.warning(f"WebSocket connection closed: {e}")
        except Exception as e:
            logger.error(f"Error in receive loop: {e}", exc_info=True)
        finally:
            self.is_connected = False
            self.is_logged_on = False

    async def _handle_server_message(self, msg: ServerMsg):
        """Routes different sub-messages contained in ServerMsg."""
        # 1. Logon result
        if msg.HasField("logon_result"):
            result = msg.logon_result
            if result.result_code == LogonResult.ResultCode.RESULT_CODE_SUCCESS:
                self.is_logged_on = True
                self.session_token = result.session_token
                logger.info(f"Logon SUCCESS! Base Time: {result.base_time}")
                self._dispatch_event({
                    "type": "logon",
                    "status": "success",
                    "server_time": result.base_time,
                })
            else:
                self.is_logged_on = False
                err_msg = result.text_message or f"Error Code {result.result_code}"
                logger.error(f"Logon FAILED: {err_msg}")
                self._dispatch_event({
                    "type": "logon",
                    "status": "failed",
                    "error": err_msg,
                    "result_code": result.result_code
                })

        # 2. Information reports (Symbol resolution)
        for info_report in msg.information_reports:
            req_id = info_report.id
            if info_report.HasField("symbol_resolution_report"):
                res_report = info_report.symbol_resolution_report
                meta = res_report.contract_metadata
                contract_info = CQGContractInfo(meta)
                self.contracts_by_id[contract_info.contract_id] = contract_info
                self.contracts_by_symbol[contract_info.symbol] = contract_info
                self.contracts_by_symbol[contract_info.cqg_symbol] = contract_info

                logger.info(
                    f"Symbol Resolved: '{contract_info.symbol}' -> ID={contract_info.contract_id}, "
                    f"Scale={contract_info.price_scale}, Tick={contract_info.tick_size}, Title='{contract_info.title}'"
                )

                if req_id in self._resolution_futures and not self._resolution_futures[req_id].done():
                    self._resolution_futures[req_id].set_result(contract_info)

                self._dispatch_event({
                    "type": "symbol_resolved",
                    "contract": contract_info.to_dict(),
                })

        # 3. Market Data Subscription Status
        for status in msg.market_data_subscription_statuses:
            status_code = status.status_code
            contract_id = status.contract_id
            sym = self.contracts_by_id.get(contract_id)
            sym_name = sym.symbol if sym else str(contract_id)
            logger.info(f"Subscription status for '{sym_name}' (ID={contract_id}): code={status_code}, level={status.level}")
            self._dispatch_event({
                "type": "subscription_status",
                "contract_id": contract_id,
                "symbol": sym_name,
                "status_code": status_code,
                "level": status.level,
            })

        # 4. Real-Time Market Data updates (Quotes, Trades, DOM, Market Values)
        for rt_data in msg.real_time_market_data:
            self._process_real_time_market_data(rt_data)

        # 5. Logged off / kicked
        if msg.HasField("logged_off"):
            logger.warning(f"Logged off by server. Reason: {msg.logged_off.text_message or msg.logged_off.logoff_reason}")
            self.is_logged_on = False
            self._dispatch_event({
                "type": "logged_off",
                "reason": msg.logged_off.text_message or msg.logged_off.logoff_reason
            })

    def _process_real_time_market_data(self, rt: RealTimeMarketData):
        """Decodes real-time market data quotes and market values into clean events."""
        contract_id = rt.contract_id
        contract = self.contracts_by_id.get(contract_id)
        symbol_name = contract.symbol if contract else f"ID_{contract_id}"
        price_scale = rt.correct_price_scale if rt.correct_price_scale != 0 else (contract.price_scale if contract else 1.0)

        # Process individual quotes (Trades, Best Bid, Best Ask, Settlement, etc.)
        for q in rt.quotes:
            quote_type = q.type
            scaled_p = q.scaled_price
            price = round(scaled_p * price_scale, 8)
            vol = decode_proto_decimal(q.volume) if q.HasField("volume") else None

            # Convert quote timestamp
            ts_str = datetime.now(timezone.utc).isoformat()
            if q.quote_utc_time:
                try:
                    ts_str = datetime.fromtimestamp(q.quote_utc_time / 1000.0, tz=timezone.utc).isoformat()
                except Exception:
                    pass

            event_type = "quote"
            if quote_type == Quote.Type.TYPE_TRADE:
                event_type = "trade"
            elif quote_type == Quote.Type.TYPE_BESTBID:
                event_type = "best_bid"
            elif quote_type == Quote.Type.TYPE_BESTASK:
                event_type = "best_ask"
            elif quote_type == Quote.Type.TYPE_BID:
                event_type = "bid_depth"
            elif quote_type == Quote.Type.TYPE_ASK:
                event_type = "ask_depth"
            elif quote_type == Quote.Type.TYPE_SETTLEMENT:
                event_type = "settlement"

            quote_event = {
                "type": event_type,
                "symbol": symbol_name,
                "contract_id": contract_id,
                "price": price,
                "volume": vol,
                "timestamp": ts_str,
                "is_snapshot": rt.is_snapshot,
            }
            self._dispatch_event(quote_event)

        # Process Market Values (OHLC, Settlement, Volume, Open Interest)
        for mv in rt.market_values:
            mv_event = {
                "type": "market_values",
                "symbol": symbol_name,
                "contract_id": contract_id,
                "day_index": mv.day_index,
                "open": round(mv.scaled_open_price * price_scale, 8) if mv.scaled_open_price else None,
                "high": round(mv.scaled_high_price * price_scale, 8) if mv.scaled_high_price else None,
                "low": round(mv.scaled_low_price * price_scale, 8) if mv.scaled_low_price else None,
                "close": round(mv.scaled_close_price * price_scale, 8) if mv.scaled_close_price else None,
                "last_price": round(mv.scaled_last_price_no_settlement * price_scale, 8) if mv.scaled_last_price_no_settlement else None,
                "settlement": round(mv.scaled_settlement * price_scale, 8) if mv.scaled_settlement else None,
                "total_volume": decode_proto_decimal(mv.total_volume) if mv.HasField("total_volume") else None,
                "open_interest": decode_proto_decimal(mv.open_interest) if mv.HasField("open_interest") else None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            self._dispatch_event(mv_event)

    def _dispatch_event(self, event: Dict[str, Any]):
        """Dispatches decoded events to the registered callback."""
        if self.on_data_callback:
            try:
                self.on_data_callback(event)
            except Exception as e:
                logger.error(f"Error in data callback: {e}")

    async def resolve_symbol(self, symbol: str, timeout: float = 10.0) -> CQGContractInfo:
        """
        Resolves a CQG symbol (e.g. 'SIEU26', 'EP', 'C.SIEU26 2800') to get its ContractMetadata.
        """
        if symbol in self.contracts_by_symbol:
            return self.contracts_by_symbol[symbol]

        msg_id = self._next_msg_id()
        client_msg = ClientMsg()
        info_req = client_msg.information_requests.add()
        info_req.id = msg_id
        info_req.symbol_resolution_request.symbol = symbol

        fut = asyncio.get_event_loop().create_future()
        self._resolution_futures[msg_id] = fut

        await self._send_message(client_msg)
        logger.info(f"Sent Symbol Resolution Request for '{symbol}' (MsgID={msg_id})...")

        try:
            contract_info = await asyncio.wait_for(fut, timeout=timeout)
            return contract_info
        finally:
            self._resolution_futures.pop(msg_id, None)

    async def subscribe_market_data(
        self,
        symbol_or_contract_id: Any,
        level: int = MarketDataSubscription.Level.LEVEL_TRADES_BBA_VOLUMES,
    ) -> int:
        """
        Subscribes to real-time market data for a symbol or contract ID.
        Levels:
          1: LEVEL_TRADES (Trades and settlements)
          2: LEVEL_TRADES_BBA (Trades + Best Bid/Ask prices)
          3: LEVEL_TRADES_BBA_VOLUMES (Trades + BBO with Volumes)
          4: LEVEL_TRADES_BBA_DOM (Full Depth of Market L2)
        """
        if isinstance(symbol_or_contract_id, str):
            contract_info = await self.resolve_symbol(symbol_or_contract_id)
            contract_id = contract_info.contract_id
        else:
            contract_id = int(symbol_or_contract_id)

        msg_id = self._next_msg_id()
        client_msg = ClientMsg()
        sub = client_msg.market_data_subscriptions.add()
        sub.contract_id = contract_id
        sub.request_id = msg_id
        sub.level = level
        sub.include_past_quotes = True

        await self._send_message(client_msg)
        self.subscribed_contract_ids.add(contract_id)
        logger.info(f"Sent Market Data Subscription for Contract ID {contract_id} (Level={level}).")
        return contract_id

    async def unsubscribe_market_data(self, contract_id: int):
        """Unsubscribes from real-time market data for a contract."""
        msg_id = self._next_msg_id()
        client_msg = ClientMsg()
        sub = client_msg.market_data_subscriptions.add()
        sub.contract_id = contract_id
        sub.request_id = msg_id
        sub.level = MarketDataSubscription.Level.LEVEL_NONE

        await self._send_message(client_msg)
        self.subscribed_contract_ids.discard(contract_id)
        logger.info(f"Unsubscribed from Contract ID {contract_id}.")

    async def disconnect(self):
        """Closes the WebSocket connection and cleans up background tasks."""
        logger.info("Disconnecting from CQG WebAPI...")
        self.is_connected = False
        self.is_logged_on = False

        for task in self._running_tasks:
            task.cancel()
        self._running_tasks.clear()

        if self.ws:
            try:
                await self.ws.close()
            except Exception:
                pass
        logger.info("Disconnected.")
