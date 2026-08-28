"""
Interactive Brokers (IBKR) Commodity Symbol Mapping for the 26 target contracts.
Maps Vietnamese/CQG symbols to standard IBKR Contract definitions.
"""

from typing import Dict, Any, Optional
from ib_insync import Future, ContFuture, Contract

# 26 Commodity Contracts definition for Interactive Brokers
IBKR_COMMODITY_MAP: Dict[str, Dict[str, Any]] = {
    # --- 1. CBOT (Nông sản / Grain & Oilseeds) ---
    "ZME": {"ib_symbol": "ZM", "exchange": "CBOT", "currency": "USD", "name": "Khô Đậu Tương (Soybean Meal)"},
    "ZLE": {"ib_symbol": "ZL", "exchange": "CBOT", "currency": "USD", "name": "Dầu Đậu Tương (Soybean Oil)"},
    "ZSE": {"ib_symbol": "ZS", "exchange": "CBOT", "currency": "USD", "name": "Đậu Tương (Soybeans)"},
    "ZCE": {"ib_symbol": "ZC", "exchange": "CBOT", "currency": "USD", "name": "Ngô (Corn)"},
    "ZWA": {"ib_symbol": "ZW", "exchange": "CBOT", "currency": "USD", "name": "Lúa Mỳ (Wheat)"},
    "XB":  {"ib_symbol": "XB", "exchange": "CBOT", "currency": "USD", "name": "Đậu Tương Mini"},
    "XC":  {"ib_symbol": "XC", "exchange": "CBOT", "currency": "USD", "name": "Ngô Mini"},
    "XW":  {"ib_symbol": "XW", "exchange": "CBOT", "currency": "USD", "name": "Lúa Mỳ Mini"},
    "KWE": {"ib_symbol": "KE", "exchange": "CBOT", "currency": "USD", "name": "Lúa Mỳ Kansas (KC Wheat)"},

    # --- 2. COMEX & NYMEX (Kim loại / Metals) ---
    "SIE": {"ib_symbol": "SI",  "exchange": "COMEX", "currency": "USD", "name": "Bạc tiêu chuẩn (Silver)"},
    "SIL": {"ib_symbol": "SIL", "exchange": "COMEX", "currency": "USD", "name": "Bạc Micro (Micro Silver)"},
    "MQI": {"ib_symbol": "QI",  "exchange": "COMEX", "currency": "USD", "name": "Bạc Mini (Mini Silver)"},
    "CPE": {"ib_symbol": "HG",  "exchange": "COMEX", "currency": "USD", "name": "Đồng tiêu chuẩn (Copper)"},
    "MQC": {"ib_symbol": "QC",  "exchange": "COMEX", "currency": "USD", "name": "Đồng Mini (Mini Copper)"},
    "MHG": {"ib_symbol": "MHG", "exchange": "COMEX", "currency": "USD", "name": "Đồng Micro (Micro Copper)"},
    "ALI": {"ib_symbol": "ALI", "exchange": "COMEX", "currency": "USD", "name": "Nhôm (Aluminum)"},
    "PLE": {"ib_symbol": "PL",  "exchange": "NYMEX", "currency": "USD", "name": "Bạch kim (Platinum)"},

    # --- 3. SGX (Singapore Exchange) ---
    "FEF": {"ib_symbol": "FEF", "exchange": "SGX", "currency": "USD", "name": "Quặng sắt (Iron Ore 62%)"},
    "ZFT": {"ib_symbol": "TF",  "exchange": "SGX", "currency": "USD", "name": "Cao su TSR20 (SGX Rubber)"},

    # --- 4. ICE US (Nguyên liệu công nghiệp Mỹ / NYBOT) ---
    "KCE": {"ib_symbol": "KC", "exchange": "NYBOT", "currency": "USD", "name": "Cà phê Arabica (Coffee C)"},
    "SBE": {"ib_symbol": "SB", "exchange": "NYBOT", "currency": "USD", "name": "Đường 11 (Sugar No. 11)"},
    "CCE": {"ib_symbol": "CC", "exchange": "NYBOT", "currency": "USD", "name": "Ca cao (Cocoa)"},
    "CTE": {"ib_symbol": "CT", "exchange": "NYBOT", "currency": "USD", "name": "Bông Sợi (Cotton No. 2)"},

    # --- 5. ICE EU (Nguyên liệu công nghiệp Châu Âu) ---
    "LRC": {"ib_symbol": "RC", "exchange": "ICEEU", "currency": "USD", "name": "Cà phê Robusta (Robusta Coffee)"},
    "QW":  {"ib_symbol": "W",  "exchange": "ICEEU", "currency": "USD", "name": "Đường trắng (White Sugar)"},

    # --- 6. TOCOM / OSE (Tokyo / Japan) ---
    "TRU": {"ib_symbol": "JRU", "exchange": "OSE.JPN", "currency": "JPY", "name": "Cao su RSS3 (TOCOM Rubber)"},
}


def create_ibkr_contract(symbol_key: str, expiry: Optional[str] = None) -> Contract:
    """
    Creates an IBKR Contract object for a given symbol key (e.g., 'ZME', 'SIE', 'LRC', 'FEF').
    If expiry is not specified, creates a Continuous Future (ContFuture) which automatically tracks the active front month.
    """
    sym = symbol_key.upper().strip()
    info = IBKR_COMMODITY_MAP.get(sym)

    if not info:
        # Fallback to direct symbol and SMART exchange
        if expiry:
            return Future(symbol=sym, lastTradeDateOrContractMonth=expiry)
        return ContFuture(symbol=sym)

    ib_sym = info["ib_symbol"]
    exchange = info["exchange"]
    currency = info.get("currency", "USD")

    if expiry:
        return Future(symbol=ib_sym, lastTradeDateOrContractMonth=expiry, exchange=exchange, currency=currency)
    else:
        return ContFuture(symbol=ib_sym, exchange=exchange, currency=currency)
