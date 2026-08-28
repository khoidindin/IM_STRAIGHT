/**
 * CQG REAL-TIME TERMINAL PRO (INSTITUTIONAL BLACK & ORANGE EDITION)
 * Real-Time OHLCV Candle Aggregator Engine (1s, 5s, 1m, 5m, 15m, 1h, 1D),
 * Multi-Contract Expiration Management, Smooth Panning/Zooming, and L2 DOM.
 */

// 26 Commodities with standard active contract expiration months & spreads
const COMMODITY_DATA = {
    // Nông sản (CBOT)
    "ZME": {
        name: "Khô Đậu Tương", exchange: "CBOT", group: "agri", basePrice: 312.4, tickSize: 0.1, digits: 1,
        contracts: [
            { code: "ZMEX26", month: "T11/26", name: "Tháng 11/2026", spread: 0.0 },
            { code: "ZMEF27", month: "T1/27", name: "Tháng 01/2027", spread: 2.7 },
            { code: "ZMEH27", month: "T3/27", name: "Tháng 03/2027", spread: 4.4 },
            { code: "ZMEK27", month: "T5/27", name: "Tháng 05/2027", spread: 6.6 },
        ]
    },
    "ZLE": {
        name: "Dầu Đậu Tương", exchange: "CBOT", group: "agri", basePrice: 42.15, tickSize: 0.01, digits: 2,
        contracts: [
            { code: "ZLEV26", month: "T10/26", name: "Tháng 10/2026", spread: 0.0 },
            { code: "ZLEZ26", month: "T12/26", name: "Tháng 12/2026", spread: 0.37 },
            { code: "ZLEF27", month: "T1/27", name: "Tháng 01/2027", spread: 0.70 },
        ]
    },
    "ZSE": {
        name: "Đậu Tương", exchange: "CBOT", group: "agri", basePrice: 1058.50, tickSize: 0.25, digits: 2,
        contracts: [
            { code: "ZSEX26", month: "T11/26", name: "Tháng 11/2026", spread: 0.0 },
            { code: "ZSEF27", month: "T1/27", name: "Tháng 01/2027", spread: 10.25 },
            { code: "ZSEH27", month: "T3/27", name: "Tháng 03/2027", spread: 17.50 },
            { code: "ZSEK27", month: "T5/27", name: "Tháng 05/2027", spread: 22.75 },
        ]
    },
    "ZCE": {
        name: "Ngô (Corn)", exchange: "CBOT", group: "agri", basePrice: 412.50, tickSize: 0.25, digits: 2,
        contracts: [
            { code: "ZCEZ26", month: "T12/26", name: "Tháng 12/2026", spread: 0.0 },
            { code: "ZCEH27", month: "T3/27", name: "Tháng 03/2027", spread: 9.25 },
            { code: "ZCEK27", month: "T5/27", name: "Tháng 05/2027", spread: 14.50 },
        ]
    },
    "ZWA": {
        name: "Lúa Mỳ", exchange: "CBOT", group: "agri", basePrice: 538.75, tickSize: 0.25, digits: 2,
        contracts: [
            { code: "ZWAZ26", month: "T12/26", name: "Tháng 12/2026", spread: 0.0 },
            { code: "ZWAH27", month: "T3/27", name: "Tháng 03/2027", spread: 9.50 },
            { code: "ZWAK27", month: "T5/27", name: "Tháng 05/2027", spread: 15.75 },
        ]
    },
    "XB": {
        name: "Đậu Tương Mini", exchange: "CBOT", group: "agri", basePrice: 1058.5, tickSize: 0.5, digits: 1,
        contracts: [
            { code: "XBX26", month: "T11/26", name: "Tháng 11/2026", spread: 0.0 },
            { code: "XBF27", month: "T1/27", name: "Tháng 01/2027", spread: 10.5 },
        ]
    },
    "XC": {
        name: "Ngô Mini", exchange: "CBOT", group: "agri", basePrice: 412.5, tickSize: 0.5, digits: 1,
        contracts: [
            { code: "XCZ26", month: "T12/26", name: "Tháng 12/2026", spread: 0.0 },
            { code: "XCH27", month: "T3/27", name: "Tháng 03/2027", spread: 9.5 },
        ]
    },
    "XW": {
        name: "Lúa Mỳ Mini", exchange: "CBOT", group: "agri", basePrice: 538.5, tickSize: 0.5, digits: 1,
        contracts: [
            { code: "XWZ26", month: "T12/26", name: "Tháng 12/2026", spread: 0.0 },
            { code: "XWH27", month: "T3/27", name: "Tháng 03/2027", spread: 9.5 },
        ]
    },
    "KWE": {
        name: "Lúa Mỳ Kansas", exchange: "CBOT", group: "agri", basePrice: 562.25, tickSize: 0.25, digits: 2,
        contracts: [
            { code: "KWEZ26", month: "T12/26", name: "Tháng 12/2026", spread: 0.0 },
            { code: "KWEH27", month: "T3/27", name: "Tháng 03/2027", spread: 8.25 },
        ]
    },

    // Kim loại (COMEX / NYMEX / SGX)
    "SIE": {
        name: "Bạc tiêu chuẩn", exchange: "COMEX", group: "metal", basePrice: 72.250, tickSize: 0.005, digits: 3,
        contracts: [
            { code: "SIEZ26", month: "T12/26", name: "Tháng 12/2026", spread: 0.0 },
            { code: "SIEH27", month: "T3/27", name: "Tháng 03/2027", spread: -0.040 },
            { code: "SIEK27", month: "T5/27", name: "Tháng 05/2027", spread: 0.120 },
        ]
    },
    "SIL": {
        name: "Bạc Micro", exchange: "COMEX", group: "metal", basePrice: 72.250, tickSize: 0.005, digits: 3,
        contracts: [
            { code: "SILZ26", month: "T12/26", name: "Tháng 12/2026", spread: 0.0 },
            { code: "SILH27", month: "T3/27", name: "Tháng 03/2027", spread: 0.260 },
        ]
    },
    "MQI": {
        name: "Bạc Mini", exchange: "COMEX", group: "metal", basePrice: 72.250, tickSize: 0.005, digits: 3,
        contracts: [
            { code: "MQIZ26", month: "T12/26", name: "Tháng 12/2026", spread: 0.0 },
        ]
    },
    "CPE": {
        name: "Đồng tiêu chuẩn", exchange: "COMEX", group: "metal", basePrice: 4.1850, tickSize: 0.0005, digits: 4,
        contracts: [
            { code: "CPEZ26", month: "T12/26", name: "Tháng 12/2026", spread: 0.0 },
            { code: "CPEH27", month: "T3/27", name: "Tháng 03/2027", spread: 0.0370 },
        ]
    },
    "MQC": {
        name: "Đồng Mini", exchange: "COMEX", group: "metal", basePrice: 4.1850, tickSize: 0.0005, digits: 4,
        contracts: [
            { code: "MQCZ26", month: "T12/26", name: "Tháng 12/2026", spread: 0.0 },
        ]
    },
    "MHG": {
        name: "Đồng Micro", exchange: "COMEX", group: "metal", basePrice: 4.1850, tickSize: 0.0005, digits: 4,
        contracts: [
            { code: "MHGZ26", month: "T12/26", name: "Tháng 12/2026", spread: 0.0 },
        ]
    },
    "ALI": {
        name: "Nhôm", exchange: "COMEX", group: "metal", basePrice: 2435.0, tickSize: 0.5, digits: 1,
        contracts: [
            { code: "ALIX26", month: "T11/26", name: "Tháng 11/2026", spread: 0.0 },
            { code: "ALIZ26", month: "T12/26", name: "Tháng 12/2026", spread: 12.5 },
        ]
    },
    "PLE": {
        name: "Bạch kim", exchange: "NYMEX", group: "metal", basePrice: 942.5, tickSize: 0.1, digits: 1,
        contracts: [
            { code: "PLEV26", month: "T10/26", name: "Tháng 10/2026", spread: 0.0 },
            { code: "PLEF27", month: "T1/27", name: "Tháng 01/2027", spread: 8.4 },
        ]
    },
    "FEF": {
        name: "Quặng sắt 62%", exchange: "SGX", group: "metal", basePrice: 98.65, tickSize: 0.01, digits: 2,
        contracts: [
            { code: "FEFU26", month: "T9/26", name: "Tháng 09/2026", spread: 0.0 },
            { code: "FEFV26", month: "T10/26", name: "Tháng 10/2026", spread: -0.40 },
            { code: "FEFX26", month: "T11/26", name: "Tháng 11/2026", spread: -0.75 },
        ]
    },

    // Nguyên liệu công nghiệp (ICE US / ICE EU / SGX / TOCOM)
    "KCE": {
        name: "Cà phê Arabica", exchange: "ICE US", group: "soft", basePrice: 245.80, tickSize: 0.05, digits: 2,
        contracts: [
            { code: "KCEZ26", month: "T12/26", name: "Tháng 12/2026", spread: 0.0 },
            { code: "KCEH27", month: "T3/27", name: "Tháng 03/2027", spread: -3.30 },
            { code: "KCEK27", month: "T5/27", name: "Tháng 05/2027", spread: -5.90 },
        ]
    },
    "LRC": {
        name: "Cà phê Robusta", exchange: "ICE EU", group: "soft", basePrice: 4862.0, tickSize: 1.0, digits: 0,
        contracts: [
            { code: "LRCX26", month: "T11/26", name: "Tháng 11/2026", spread: 0.0 },
            { code: "LRCZ26", month: "T1/27", name: "Tháng 01/2027", spread: -42.0 },
            { code: "LRCH27", month: "T3/27", name: "Tháng 03/2027", spread: -85.0 },
        ]
    },
    "ZFT": {
        name: "Cao su TSR20", exchange: "SGX", group: "soft", basePrice: 168.4, tickSize: 0.1, digits: 1,
        contracts: [
            { code: "ZFTV26", month: "T10/26", name: "Tháng 10/2026", spread: 0.0 },
            { code: "ZFTX26", month: "T11/26", name: "Tháng 11/2026", spread: 1.3 },
        ]
    },
    "TRU": {
        name: "Cao su RSS3", exchange: "TOCOM", group: "soft", basePrice: 325.2, tickSize: 0.1, digits: 1,
        contracts: [
            { code: "TRUV26", month: "T10/26", name: "Tháng 10/2026", spread: 0.0 },
            { code: "TRUX26", month: "T11/26", name: "Tháng 11/2026", spread: 2.2 },
        ]
    },
    "SBE": {
        name: "Đường 11", exchange: "ICE US", group: "soft", basePrice: 18.72, tickSize: 0.01, digits: 2,
        contracts: [
            { code: "SBEV26", month: "T10/26", name: "Tháng 10/2026", spread: 0.0 },
            { code: "SBEH27", month: "T3/27", name: "Tháng 03/2027", spread: 0.45 },
        ]
    },
    "QW": {
        name: "Đường trắng", exchange: "ICE EU", group: "soft", basePrice: 512.4, tickSize: 0.1, digits: 1,
        contracts: [
            { code: "QWV26", month: "T10/26", name: "Tháng 10/2026", spread: 0.0 },
            { code: "QWZ26", month: "T12/26", name: "Tháng 12/2026", spread: 8.5 },
        ]
    },
    "CCE": {
        name: "Ca cao", exchange: "ICE US", group: "soft", basePrice: 5819.0, tickSize: 1.0, digits: 0,
        contracts: [
            { code: "CCEZ26", month: "T12/26", name: "Tháng 12/2026", spread: 0.0 },
            { code: "CCEH27", month: "T3/27", name: "Tháng 03/2027", spread: 95.0 },
            { code: "CCEK27", month: "T5/27", name: "Tháng 05/2027", spread: 180.0 },
        ]
    },
    "CTE": {
        name: "Bông Sợi", exchange: "ICE US", group: "soft", basePrice: 69.45, tickSize: 0.01, digits: 2,
        contracts: [
            { code: "CTEV26", month: "T10/26", name: "Tháng 10/2026", spread: 0.0 },
            { code: "CTEZ26", month: "T12/26", name: "Tháng 12/2026", spread: 0.85 },
        ]
    },
};

// Timeframe mapping in seconds
const TIMEFRAME_SECONDS = {
    "1s": 1,
    "5s": 5,
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "1h": 3600,
    "1D": 86400,
};

let activeSymbol = "ZSE";
let activeContractCode = "ZSEX26";
let activeTimeframe = "1m";
let ws = null;
let chart = null;
let candleSeries = null;
let volumeSeries = null;
let currentCandle = null;
let currentVolume = null;
let activeFilter = "all";
let totalPacketsReceived = 0;

// DOM Elements
const elSymbolCode = document.getElementById("active-symbol-code");
const elSymbolDesc = document.getElementById("active-symbol-desc");
const elExchangeBadge = document.getElementById("active-exchange-badge");
const elStatLast = document.getElementById("stat-last-price");
const elStatChange = document.getElementById("stat-change");
const elStatHigh = document.getElementById("stat-high");
const elStatLow = document.getElementById("stat-low");
const elStatVol = document.getElementById("stat-volume");
const elConnDot = document.getElementById("conn-dot");
const elConnText = document.getElementById("conn-text");
const elLatency = document.getElementById("latency-val");
const elWatchlist = document.getElementById("watchlist-container");
const elOrderbookAsks = document.getElementById("orderbook-asks-container");
const elOrderbookBids = document.getElementById("orderbook-bids-container");
const elSpreadVal = document.getElementById("spread-value");
const elMidPrice = document.getElementById("mid-price-display");
const elSpreadPct = document.getElementById("spread-pct");
const elTape = document.getElementById("tape-container");
const elRawStream = document.getElementById("raw-stream-container");
const elContractPills = document.getElementById("contract-month-pills");
const elMetricPackets = document.getElementById("metric-packets");
const elMetricLatency = document.getElementById("metric-latency");

// Helper to get active contract / commodity specifications
function getActiveSpec() {
    const parent = COMMODITY_DATA[activeSymbol] || COMMODITY_DATA["ZSE"];
    const contract = parent.contracts.find(c => c.code === activeContractCode) || parent.contracts[0];
    const price = parent.basePrice + contract.spread;
    return {
        ...parent,
        contractCode: contract.code,
        month: contract.month,
        contractName: contract.name,
        price: price,
        digits: parent.digits,
        tickSize: parent.tickSize,
    };
}

// Initialize TradingView Lightweight Chart with Smooth Interaction & Panning
function initChart() {
    const container = document.getElementById("chart-container");
    container.innerHTML = "";

    const width = container.clientWidth || 800;
    const height = container.clientHeight || 450;
    const tfSec = TIMEFRAME_SECONDS[activeTimeframe] || 60;
    const isSecondsTf = tfSec < 60;

    chart = LightweightCharts.createChart(container, {
        width: width,
        height: height,
        layout: {
            background: { color: "#08090c" },
            textColor: "#94a3b8",
            fontSize: 11,
            fontFamily: "'Inter', sans-serif",
        },
        grid: {
            vertLines: { color: "rgba(249, 115, 22, 0.04)" },
            horzLines: { color: "rgba(249, 115, 22, 0.04)" },
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
            vertLine: { color: "rgba(249, 115, 22, 0.5)", width: 1, style: 2 },
            horzLine: { color: "rgba(249, 115, 22, 0.5)", width: 1, style: 2 },
        },
        // Smooth Mouse & Touch Dragging / Panning
        handleScroll: {
            mouseWheel: true,
            pressedMouseMove: true,
            horzTouchDrag: true,
            vertTouchDrag: true,
        },
        // Smooth Zooming / Scaling
        handleScale: {
            axisPressedMouseMove: true,
            mouseWheel: true,
            pinch: true,
        },
        rightPriceScale: {
            borderColor: "rgba(249, 115, 22, 0.18)",
            scaleMargins: { top: 0.08, bottom: 0.20 },
            autoScale: true,
        },
        localization: {
            locale: "vi-VN",
            timeFormatter: (timestamp) => {
                const date = new Date(timestamp * 1000);
                return date.toLocaleTimeString("vi-VN", { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit", timeZone: "Asia/Ho_Chi_Minh" });
            },
        },
        timeScale: {
            borderColor: "rgba(249, 115, 22, 0.18)",
            timeVisible: true,
            secondsVisible: isSecondsTf,
            barSpacing: 9,
            minBarSpacing: 2,
            rightOffset: 12,
        },
    });

    if (typeof chart.addCandlestickSeries === "function") {
        candleSeries = chart.addCandlestickSeries({
            upColor: "#10b981",
            downColor: "#f43f5e",
            borderVisible: false,
            wickUpColor: "#10b981",
            wickDownColor: "#f43f5e",
        });
        volumeSeries = chart.addHistogramSeries({
            priceFormat: { type: "volume" },
            priceScaleId: "volume_pane",
        });
    } else if (typeof chart.addSeries === "function") {
        candleSeries = chart.addSeries(LightweightCharts.CandlestickSeries, {
            upColor: "#10b981",
            downColor: "#f43f5e",
            borderVisible: false,
            wickUpColor: "#10b981",
            wickDownColor: "#f43f5e",
        });
        volumeSeries = chart.addSeries(LightweightCharts.HistogramSeries, {
            priceFormat: { type: "volume" },
            priceScaleId: "volume_pane",
        });
    }

    if (chart.priceScale && typeof chart.priceScale === "function") {
        chart.priceScale("volume_pane").applyOptions({
            scaleMargins: {
                top: 0.82,
                bottom: 0.0,
            },
        });
    }

    const resizeObserver = new ResizeObserver((entries) => {
        if (!entries || entries.length === 0) return;
        const { width, height } = entries[0].contentRect;
        if (width > 0 && height > 0 && chart) {
            chart.applyOptions({ width, height });
        }
    });
    resizeObserver.observe(container);

    selectSymbol(activeSymbol);
}

// Render Contract Month Selector Pills
function renderContractPills() {
    const parent = COMMODITY_DATA[activeSymbol];
    if (!parent || !elContractPills) return;

    elContractPills.innerHTML = "";
    parent.contracts.forEach(c => {
        const btn = document.createElement("button");
        btn.className = `contract-pill ${c.code === activeContractCode ? "active" : ""}`;
        btn.textContent = `${c.code} (${c.month})`;
        btn.onclick = () => selectContractMonth(c.code);
        elContractPills.appendChild(btn);
    });
}

function selectContractMonth(contractCode) {
    activeContractCode = contractCode;
    const spec = getActiveSpec();
    
    elSymbolCode.textContent = spec.contractCode;
    document.getElementById("chart-symbol-display").textContent = `${spec.contractCode} · ${spec.name} (${spec.exchange})`;

    renderContractPills();
    loadInitialHistory();

    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: "subscribe", symbols: [activeContractCode, activeSymbol], include_depth: true }));
    }
}

// Load persistent historical bars from server cache
async function loadInitialHistory() {
    const spec = getActiveSpec();
    const tfSec = TIMEFRAME_SECONDS[activeTimeframe] || 60;

    try {
        const res = await fetch(`/api/history?symbol=${activeContractCode}&timeframe=${activeTimeframe}&limit=160`);
        const bars = await res.json();

        if (bars && bars.length > 0) {
            const volBars = bars.map(b => ({
                time: b.time,
                value: b.volume,
                color: b.close >= b.open ? "rgba(16, 185, 129, 0.25)" : "rgba(244, 63, 94, 0.25)"
            }));

            if (candleSeries) {
                candleSeries.setData(bars);
            }
            if (volumeSeries) {
                volumeSeries.setData(volBars);
            }
            currentCandle = { ...bars[bars.length - 1] };
            currentVolume = { ...volBars[volBars.length - 1] };

            if (chart && chart.timeScale) {
                chart.timeScale().applyOptions({
                    secondsVisible: tfSec < 60,
                });
                chart.timeScale().fitContent();
            }

            elStatLast.textContent = currentCandle.close.toFixed(spec.digits);
            elStatChange.textContent = "+0.52%";
            elStatHigh.textContent = (spec.price * 1.008).toFixed(spec.digits);
            elStatLow.textContent = (spec.price * 0.992).toFixed(spec.digits);
            elStatVol.textContent = (24580).toLocaleString();

            populateInitialTape(spec);
        }
    } catch (e) {
        console.error("Error loading server history:", e);
    }
}

function roundToTick(price, tickSize, digits) {
    return Number((Math.round(price / tickSize) * tickSize).toFixed(digits));
}

function populateInitialTape(spec) {
    elTape.innerHTML = "";
    const baseP = spec.price;
    const now = Date.now();
    for (let i = 0; i < 15; i++) {
        const ts = new Date(now - i * 1200).toTimeString().substr(0, 8);
        const price = roundToTick(baseP + (Math.random() - 0.5) * (spec.tickSize * 4), spec.tickSize, spec.digits);
        const vol = Math.floor(Math.random() * 12) + 1;
        const side = Math.random() > 0.5 ? "BUY" : "SELL";
        appendTapeRow(ts, price, vol, side, spec.digits);
    }
}

// Render Watchlist
function renderWatchlist() {
    elWatchlist.innerHTML = "";
    const filter = activeFilter;
    const search = document.getElementById("watchlist-search").value.toUpperCase();

    const symbols = Object.keys(COMMODITY_DATA);
    const filtered = symbols.filter(sym => {
        const c = COMMODITY_DATA[sym];
        const matchGroup = filter === "all" || c.group === filter;
        const matchSearch = sym.includes(search) || c.name.toUpperCase().includes(search) || c.exchange.includes(search);
        return matchGroup && matchSearch;
    });

    filtered.forEach(sym => {
        const item = COMMODITY_DATA[sym];
        const div = document.createElement("div");
        div.className = `watchlist-item ${sym === activeSymbol ? "active" : ""}`;
        div.id = `wl-item-${sym}`;
        div.onclick = () => selectSymbol(sym);

        div.innerHTML = `
            <div class="wl-left">
                <span class="wl-symbol">${sym}</span>
                <span class="wl-name">${item.name} (${item.exchange})</span>
            </div>
            <div class="wl-right">
                <span class="wl-price" id="wl-price-${sym}">${item.basePrice.toFixed(item.digits)}</span>
                <span class="wl-change text-green" id="wl-change-${sym}">+0.52%</span>
            </div>
        `;
        elWatchlist.appendChild(div);
    });
}

function selectSymbol(symCode) {
    activeSymbol = symCode;
    const symInfo = COMMODITY_DATA[symCode];
    if (!symInfo) return;

    activeContractCode = symInfo.contracts[0].code;

    elSymbolCode.textContent = symInfo.contracts[0].code;
    elSymbolDesc.textContent = `${symInfo.name} (${symInfo.exchange})`;
    elExchangeBadge.textContent = symInfo.exchange;
    document.getElementById("chart-symbol-display").textContent = `${symInfo.contracts[0].code} · ${symInfo.name} (${symInfo.exchange})`;

    document.querySelectorAll(".watchlist-item").forEach(el => el.classList.remove("active"));
    const activeEl = document.getElementById(`wl-item-${symCode}`);
    if (activeEl) activeEl.classList.add("active");

    renderContractPills();
    loadInitialHistory();

    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: "subscribe", symbols: [activeContractCode, symCode], include_depth: true }));
    }
}

// Connect to WebSocket Server
function connectWebSocket() {
    const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${wsProtocol}//${window.location.host}/ws`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        elConnDot.className = "pulse-dot active";
        elConnText.textContent = "LIVE STREAMING";
        elConnText.style.color = "var(--trade-buy)";
        ws.send(JSON.stringify({ action: "subscribe", symbols: [activeContractCode, activeSymbol], include_depth: true }));
    };

    ws.onmessage = (event) => {
        try {
            totalPacketsReceived++;
            if (elMetricPackets) {
                elMetricPackets.textContent = totalPacketsReceived.toLocaleString();
            }
            const data = JSON.parse(event.data);
            handleIncomingPacket(data);
        } catch (e) {
            console.error("Packet parse error:", e);
        }
    };

    ws.onclose = () => {
        elConnDot.className = "pulse-dot";
        elConnText.textContent = "RECONNECTING...";
        elConnText.style.color = "var(--amber-accent)";
        setTimeout(connectWebSocket, 2000);
    };
}

// Handle Incoming WebSocket Events
function handleIncomingPacket(data) {
    logRawStream(data);

    if (data.type === "connection_status") {
        if (data.status.includes("LIVE_CQG") || data.status.includes("LIVE_STREAMING")) {
            elConnText.textContent = "LIVE STREAMING";
            elConnText.style.color = "var(--trade-buy)";
        }
        if (data.latency_ms) {
            elLatency.textContent = `${data.latency_ms} ms`;
            if (elMetricLatency) elMetricLatency.textContent = `${data.latency_ms} ms`;
        }
        return;
    }

    const sym = data.symbol || activeSymbol;
    const isTarget = (sym === activeSymbol || sym === activeContractCode);

    if (data.type === "trade" && isTarget) {
        handleTrade(data);
    } else if (data.type === "orderbook" && isTarget) {
        handleOrderbook(data);
    } else if (data.type === "bbo" && isTarget) {
        handleBBO(data);
    } else if (data.type === "market_values" && isTarget) {
        handleMarketValues(data);
    }
}

// Real-Time OHLCV Candle Aggregator Engine
function handleTrade(data) {
    const spec = getActiveSpec();
    const price = Number(data.price);
    const vol = data.volume || 1;
    const side = data.side || (Math.random() > 0.5 ? "BUY" : "SELL");
    const ts = data.timestamp ? data.timestamp.substr(11, 8) : new Date().toTimeString().substr(0, 8);

    // Update Header Stats
    elStatLast.textContent = price.toFixed(spec.digits);
    elStatLast.className = `stat-value ${side === "BUY" ? "text-green" : "text-red"}`;

    const wlP = document.getElementById(`wl-price-${activeSymbol}`);
    if (wlP) wlP.textContent = price.toFixed(spec.digits);

    // --- TIMEFRAME BUCKET AGGREGATION LOGIC ---
    const tfSec = TIMEFRAME_SECONDS[activeTimeframe] || 60;
    const nowSec = Math.floor(Date.now() / 1000);
    const bucketTime = Math.floor(nowSec / tfSec) * tfSec;

    if (!currentCandle || bucketTime > currentCandle.time) {
        // CLOSE PREVIOUS CANDLE -> START NEW CANDLE!
        currentCandle = {
            time: bucketTime,
            open: currentCandle ? currentCandle.close : price,
            high: Math.max(currentCandle ? currentCandle.close : price, price),
            low: Math.min(currentCandle ? currentCandle.close : price, price),
            close: price,
        };
        currentVolume = {
            time: bucketTime,
            value: vol,
            color: currentCandle.close >= currentCandle.open ? "rgba(16, 185, 129, 0.25)" : "rgba(244, 63, 94, 0.25)",
        };
    } else {
        // UPDATE CURRENT IN-FLIGHT CANDLE
        currentCandle.high = Math.max(currentCandle.high, price);
        currentCandle.low = Math.min(currentCandle.low, price);
        currentCandle.close = price;

        if (currentVolume) {
            currentVolume.value += vol;
            currentVolume.color = currentCandle.close >= currentCandle.open ? "rgba(16, 185, 129, 0.25)" : "rgba(244, 63, 94, 0.25)";
        }
    }

    if (candleSeries) {
        candleSeries.update(currentCandle);
    }
    if (volumeSeries && currentVolume) {
        volumeSeries.update(currentVolume);
    }

    appendTapeRow(ts, price, vol, side, spec.digits);
}

function handleBBO(data) {
    const spec = getActiveSpec();
    if (data.bid && data.ask) {
        const spread = Math.abs(data.ask - data.bid);
        const mid = (data.ask + data.bid) / 2;
        elSpreadVal.textContent = spread.toFixed(spec.digits);
        elMidPrice.textContent = mid.toFixed(spec.digits);
        elSpreadPct.textContent = ((spread / mid) * 100).toFixed(2) + "%";
    }
}

function handleMarketValues(data) {
    const spec = getActiveSpec();
    if (data.high) elStatHigh.textContent = Number(data.high).toFixed(spec.digits);
    if (data.low) elStatLow.textContent = Number(data.low).toFixed(spec.digits);
    if (data.total_volume) elStatVol.textContent = data.total_volume.toLocaleString();
}

function handleOrderbook(data) {
    const spec = getActiveSpec();
    const bids = data.bids || [];
    const asks = data.asks || [];

    const topAsks = asks.slice(0, 10).reverse();
    const maxAskVol = Math.max(...topAsks.map(a => a.size), 50);

    let asksHtml = "";
    let cumAsk = 0;
    topAsks.forEach(a => {
        cumAsk += a.size;
        const depthPct = Math.min(100, (a.size / maxAskVol) * 100);
        asksHtml += `
            <div class="orderbook-row ask-row">
                <div class="ob-depth-bar ask-bar" style="width: ${depthPct}%"></div>
                <span class="ob-price ask-price">${Number(a.price).toFixed(spec.digits)}</span>
                <span class="ob-size">${a.size}</span>
                <span class="ob-total">${cumAsk}</span>
            </div>
        `;
    });
    elOrderbookAsks.innerHTML = asksHtml;

    const topBids = bids.slice(0, 10);
    const maxBidVol = Math.max(...topBids.map(b => b.size), 50);

    let bidsHtml = "";
    let cumBid = 0;
    topBids.forEach(b => {
        cumBid += b.size;
        const depthPct = Math.min(100, (b.size / maxBidVol) * 100);
        bidsHtml += `
            <div class="orderbook-row bid-row">
                <div class="ob-depth-bar bid-bar" style="width: ${depthPct}%"></div>
                <span class="ob-price bid-price">${Number(b.price).toFixed(spec.digits)}</span>
                <span class="ob-size">${b.size}</span>
                <span class="ob-total">${cumBid}</span>
            </div>
        `;
    });
    elOrderbookBids.innerHTML = bidsHtml;

    if (topBids.length > 0 && topAsks.length > 0) {
        const bestBid = topBids[0].price;
        const bestAsk = topAsks[topAsks.length - 1].price;
        const spread = Math.abs(bestAsk - bestBid);
        const mid = (bestAsk + bestBid) / 2;
        elSpreadVal.textContent = spread.toFixed(spec.digits);
        elMidPrice.textContent = mid.toFixed(spec.digits);
        elSpreadPct.textContent = ((spread / mid) * 100).toFixed(2) + "%";
    }
}

function appendTapeRow(time, price, vol, side, digits) {
    const row = document.createElement("div");
    row.className = "tape-row";
    row.innerHTML = `
        <span class="tape-time">${time}</span>
        <span class="tape-price ${side === "BUY" ? "text-green" : "text-red"}">${Number(price).toFixed(digits)}</span>
        <span class="tape-size">${vol}</span>
        <span class="tape-side ${side === "BUY" ? "side-buy" : "side-sell"}">${side}</span>
    `;
    elTape.prepend(row);

    while (elTape.children.length > 30) {
        elTape.removeChild(elTape.lastChild);
    }
}

function logRawStream(packet) {
    if (!elRawStream) return;
    const p = document.createElement("div");
    p.className = "raw-packet";
    p.textContent = `[${new Date().toTimeString().substr(0, 8)}] ${JSON.stringify(packet)}`;
    elRawStream.prepend(p);

    while (elRawStream.children.length > 20) {
        elRawStream.removeChild(elRawStream.lastChild);
    }
}

// Watchlist Filter Tab handlers
document.querySelectorAll(".filter-tab").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".filter-tab").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        activeFilter = btn.getAttribute("data-filter");
        renderWatchlist();
    });
});

// Timeframe Buttons Click Handler (1s, 5s, 1m, 5m, 15m, 1h, 1D)
document.querySelectorAll(".tf-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".tf-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        activeTimeframe = btn.getAttribute("data-tf") || "1m";
        loadInitialHistory();
    });
});

document.getElementById("watchlist-search").addEventListener("input", renderWatchlist);

// Raw Drawer Toggle Handlers
const rawDrawer = document.getElementById("raw-stream-drawer");
const btnToggleRaw = document.getElementById("btn-toggle-raw");
const btnCloseRaw = document.getElementById("btn-close-raw");

if (btnToggleRaw) {
    btnToggleRaw.onclick = () => {
        rawDrawer.classList.toggle("hidden");
    };
}
if (btnCloseRaw) {
    btnCloseRaw.onclick = () => {
        rawDrawer.classList.add("hidden");
    };
}

// Modal & Config API Handlers
const modal = document.getElementById("modal-config");
document.getElementById("btn-toggle-config").onclick = async () => {
    modal.classList.remove("hidden");
    try {
        const res = await fetch("/api/config");
        const data = await res.json();
        if (data.mode) document.getElementById("cfg-mode").value = data.mode;
        if (data.cqg_username) document.getElementById("cfg-username").value = data.cqg_username;
    } catch (e) {}
};

document.getElementById("btn-close-modal").onclick = () => modal.classList.add("hidden");

document.getElementById("btn-save-config").onclick = async () => {
    const mode = document.getElementById("cfg-mode").value;
    const username = document.getElementById("cfg-username").value;
    const password = document.getElementById("cfg-password").value;

    const btn = document.getElementById("btn-save-config");
    btn.textContent = "Đang kết nối...";
    btn.disabled = true;

    try {
        const res = await fetch("/api/config", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                mode: mode,
                username: username,
                password: password,
                host: "wss://api.cqg.com:443"
            })
        });
        const resp = await res.json();
        if (resp.status === "ok") {
            alert("✓ Cấu hình đã lưu! Server đang kết nối luồng CQG.");
            modal.classList.add("hidden");
        } else {
            alert("Lỗi: " + resp.message);
        }
    } catch (e) {
        alert("Lỗi kết nối tới Server: " + e);
    } finally {
        btn.textContent = "LƯU & KẾT NỐI LẠI";
        btn.disabled = false;
    }
};

// Bootstrap Application
window.addEventListener("DOMContentLoaded", () => {
    initChart();
    renderWatchlist();
    connectWebSocket();
});
