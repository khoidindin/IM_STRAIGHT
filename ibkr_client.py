"""
Interactive Brokers (IBKR) Real-Time WebSocket & Market Depth Client.
Uses ib_insync to stream real-time Trades, BBO, OHLCV, and Level 2 Orderbook (DOM).
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional, Any

from ib_insync import IB, Contract, Ticker, DOMLevel
from ibkr_symbols import IBKR_COMMODITY_MAP, create_ibkr_contract

logger = logging.getLogger("IBKRClient")
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")


class IBKRMarketDataClient:
    """
    Asynchronous client for Interactive Brokers (TWS / IB Gateway).
    Streams real-time Quotes, Trades, OHLCV, and Level 2 Market Depth (Orderbook).
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 7497,  # 7497 for TWS Paper, 7496 for TWS Live, 4002 for Gateway Paper, 4001 for Gateway Live
        client_id: int = 1,
        on_data_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.on_data_callback = on_data_callback

        self.ib = IB()
        self.is_connected = False

        # Track active subscriptions
        self.active_tickers: Dict[str, Ticker] = {}
        self.active_contracts: Dict[str, Contract] = {}
        self.depth_subscriptions: Dict[str, Any] = {}

    async def connect(self):
        """Connects to TWS or IB Gateway."""
        logger.info(f"Connecting to Interactive Brokers at {self.host}:{self.port} (ClientID={self.client_id})...")
        try:
            await self.ib.connectAsync(self.host, self.port, clientId=self.client_id, timeout=15)
            self.is_connected = True
            logger.info("[OK] Connected to Interactive Brokers API successfully!")

            # Set market data type (1: Real-time Live, 3: Delayed 15m, 4: Delayed-Frozen)
            self.ib.reqMarketDataType(1)

        except Exception as e:
            self.is_connected = False
            logger.error(f"[FAILED] Could not connect to IBKR at {self.host}:{self.port}: {e}")
            raise

    async def subscribe_symbol(self, symbol_key: str, expiry: Optional[str] = None, include_depth: bool = True, depth_rows: int = 5):
        """
        Subscribes to real-time market data and Level 2 Orderbook for a commodity symbol.
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to IBKR.")

        contract = create_ibkr_contract(symbol_key, expiry=expiry)
        qualified = await self.ib.qualifyContractsAsync(contract)
        if not qualified:
            logger.warning(f"Could not qualify contract for symbol '{symbol_key}'. Using raw contract.")
            target_contract = contract
        else:
            target_contract = qualified[0]

        sym = symbol_key.upper().strip()
        self.active_contracts[sym] = target_contract

        logger.info(f"Subscribing to real-time ticks for '{sym}' (IB: {target_contract.symbol} on {target_contract.exchange})...")

        # 1. Request real-time ticker stream (Trades, BBO, OHLCV)
        ticker = self.ib.reqMktData(target_contract, genericTickList="", snapshot=False, regulatorySnapshot=False)
        ticker.updateEvent += lambda t: self._on_ticker_update(sym, t)
        self.active_tickers[sym] = ticker

        # 2. Request Level 2 Orderbook / Market Depth
        if include_depth:
            logger.info(f"Subscribing to Level 2 Orderbook (DOM - {depth_rows} levels) for '{sym}'...")
            depth = self.ib.reqMktDepth(target_contract, numRows=depth_rows, isSmartDepth=False)
            depth.updateEvent += lambda d: self._on_depth_update(sym, d)
            self.depth_subscriptions[sym] = depth

        self._dispatch_event({
            "type": "symbol_subscribed",
            "symbol": sym,
            "ib_contract": {
                "conId": target_contract.conId,
                "symbol": target_contract.symbol,
                "exchange": target_contract.exchange,
                "currency": target_contract.currency,
                "localSymbol": getattr(target_contract, "localSymbol", ""),
            }
        })

    def _on_ticker_update(self, symbol: str, ticker: Ticker):
        """Processes real-time BBO, Trades, and OHLCV updates from IBKR."""
        ts_str = datetime.now(timezone.utc).isoformat()

        # 1. Best Bid / Best Ask (BBO)
        if ticker.bid is not None or ticker.ask is not None:
            self._dispatch_event({
                "type": "bbo",
                "symbol": symbol,
                "bid": ticker.bid if ticker.bid and ticker.bid > 0 else None,
                "bid_size": ticker.bidSize if ticker.bidSize and ticker.bidSize > 0 else None,
                "ask": ticker.ask if ticker.ask and ticker.ask > 0 else None,
                "ask_size": ticker.askSize if ticker.askSize and ticker.askSize > 0 else None,
                "timestamp": ts_str,
            })

        # 2. Last Trade Tick
        if ticker.last is not None and ticker.last > 0:
            self._dispatch_event({
                "type": "trade",
                "symbol": symbol,
                "price": ticker.last,
                "volume": ticker.lastSize,
                "timestamp": ts_str,
            })

        # 3. Market Values (OHLCV)
        if any([ticker.open, ticker.high, ticker.low, ticker.close, ticker.volume]):
            self._dispatch_event({
                "type": "market_values",
                "symbol": symbol,
                "open": ticker.open if ticker.open and ticker.open > 0 else None,
                "high": ticker.high if ticker.high and ticker.high > 0 else None,
                "low": ticker.low if ticker.low and ticker.low > 0 else None,
                "close": ticker.close if ticker.close and ticker.close > 0 else None,
                "last_price": ticker.last if ticker.last and ticker.last > 0 else None,
                "total_volume": ticker.volume if ticker.volume and ticker.volume > 0 else None,
                "timestamp": ts_str,
            })

    def _on_depth_update(self, symbol: str, depth_ticker: Ticker):
        """Processes Level 2 Orderbook (DOM) updates."""
        bids: List[Dict[str, Any]] = []
        asks: List[Dict[str, Any]] = []

        if depth_ticker.domBids:
            for item in depth_ticker.domBids:
                bids.append({"price": item.price, "size": item.size, "market_maker": item.marketMaker})

        if depth_ticker.domAsks:
            for item in depth_ticker.domAsks:
                asks.append({"price": item.price, "size": item.size, "market_maker": item.marketMaker})

        self._dispatch_event({
            "type": "orderbook",
            "symbol": symbol,
            "bids": bids,
            "asks": asks,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def _dispatch_event(self, event: Dict[str, Any]):
        if self.on_data_callback:
            try:
                self.on_data_callback(event)
            except Exception as e:
                logger.error(f"Error in data callback: {e}")

    async def disconnect(self):
        """Disconnects from IBKR."""
        logger.info("Disconnecting from Interactive Brokers...")
        if self.is_connected:
            self.ib.disconnect()
            self.is_connected = False
        logger.info("Disconnected from IBKR.")
