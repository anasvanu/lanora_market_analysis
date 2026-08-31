#!/usr/bin/env python3
"""
Lanora Gold Trading LLC — Market Research & Classic Floor Pivot Engine
Fetches live spot prices for XAU/USD and XAG/USD, calculates exact Classic Floor Pivot Points,
formulates intraday trade plans, and checks market open status.
"""

import json
import ssl
import urllib.request
from datetime import datetime, timezone, timedelta

def is_market_open(dt=None) -> bool:
    """
    Returns True if the market is open today (Monday=0 to Friday=4).
    Precious metals spot markets are closed on Saturday and Sunday.
    """
    if dt is None:
        dt = datetime.now(timezone(timedelta(hours=4))) # Dubai GST
    return dt.weekday() < 5  # Mon-Fri

def calculate_pivot_points(high: float, low: float, close: float, decimals: int = 2) -> dict:
    """
    Calculates Classic Floor Pivot Points:
    P = (High + Low + Close) / 3
    R1 = (2 * P) - Low
    S1 = (2 * P) - High
    R2 = P + (High - Low)
    S2 = P - (High - Low)
    R3 = High + 2 * (P - Low)
    S3 = Low - 2 * (High - P)
    """
    p = (high + low + close) / 3.0
    r1 = (2.0 * p) - low
    s1 = (2.0 * p) - high
    r2 = p + (high - low)
    s2 = p - (high - low)
    r3 = high + 2.0 * (p - low)
    s3 = low - 2.0 * (high - p)

    return {
        "P": round(p, decimals),
        "R1": round(r1, decimals),
        "S1": round(s1, decimals),
        "R2": round(r2, decimals),
        "S2": round(s2, decimals),
        "R3": round(r3, decimals),
        "S3": round(s3, decimals)
    }

def fetch_gold_api_spot(symbol: str):
    """
    Fetches live real-time spot price from Gold-API
    """
    ctx = ssl._create_unverified_context()
    url = f"https://api.gold-api.com/price/{symbol}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return float(data.get("price"))
    except Exception as e:
        print(f"Warning: Gold-API fetch for {symbol} failed ({e}).")
        return None

def fetch_yahoo_session(symbol: str):
    """
    Fetches the PREVIOUS COMPLETED daily session High, Low, and Close from Yahoo Finance
    """
    ctx = ssl._create_unverified_context()
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=5d&interval=1d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            result = data["chart"]["result"][0]
            meta = result["meta"]
            spot = meta.get("regularMarketPrice")
            
            quotes = result["indicators"]["quote"][0]
            highs = [h for h in quotes["high"] if h is not None]
            lows = [l for l in quotes["low"] if l is not None]
            closes = [c for c in quotes["close"] if c is not None]
            
            # If we have at least 2 days of daily candles, index -2 is the previous completed day
            # If only 1 day, take index -1
            if len(closes) >= 2:
                prev_high = highs[-2]
                prev_low = lows[-2]
                prev_close = closes[-2]
            elif len(closes) == 1:
                prev_high = highs[-1]
                prev_low = lows[-1]
                prev_close = closes[-1]
            else:
                prev_high = meta.get("regularMarketDayHigh")
                prev_low = meta.get("regularMarketDayLow")
                prev_close = meta.get("chartPreviousClose") or meta.get("previousClose")

            return spot, prev_high, prev_low, prev_close
    except Exception as e:
        print(f"Warning: Yahoo fetch for {symbol} failed ({e}).")
        return None, None, None, None

def fetch_spot_session(metal_sym: str, yahoo_future_sym: str, default_spot: float):
    """
    Fetches strictly physical Spot Cash Metals OHLC (XAU/USD & XAG/USD).
    Removes COMEX futures contract rollover/basis premium so all pivots are 100% Spot-based.
    """
    ctx = ssl._create_unverified_context()
    
    # 1. Live real-time spot price from Gold-API
    live_spot = fetch_gold_api_spot(metal_sym)
    
    # 2. Previous completed daily spot close
    spot_close = None
    try:
        url_close = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{metal_sym.lower()}.json"
        req_close = urllib.request.Request(url_close, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req_close, context=ctx, timeout=5) as resp:
            d_close = json.loads(resp.read().decode("utf-8"))
            spot_close = float(d_close[metal_sym.lower()]["usd"])
    except Exception as e:
        print(f"Warning: currency-api spot close for {metal_sym} failed ({e}).")

    # 3. Yahoo session range for the previous completed daily bar
    f_spot, f_high, f_low, f_close = fetch_yahoo_session(yahoo_future_sym)
    
    if live_spot is None:
        live_spot = spot_close or f_spot or default_spot
        
    if spot_close is None:
        spot_close = live_spot

    if f_high is not None and f_low is not None and f_close is not None:
        # Subtract the futures basis spread (Futures Close - Spot Close) to get true Spot High & Low
        basis = f_close - spot_close
        spot_high = f_high - basis
        spot_low = f_low - basis
    else:
        spot_high = spot_close * 1.008
        spot_low = spot_close * 0.992

    return live_spot, spot_high, spot_low, spot_close

def get_market_data():
    gst_now = datetime.now(timezone(timedelta(hours=4)))
    market_open = is_market_open(gst_now)
    report_date = gst_now.strftime("%B %d, %Y")

    # Fetch 100% Physical Spot Gold (XAU/USD)
    gold_spot, gold_high, gold_low, gold_close = fetch_spot_session("XAU", "GC=F", 4436.00)

    # Fetch 100% Physical Spot Silver (XAG/USD)
    silver_spot, silver_high, silver_low, silver_close = fetch_spot_session("XAG", "SI=F", 66.750)

    gold_pivots = calculate_pivot_points(gold_high, gold_low, gold_close, decimals=2)
    silver_pivots = calculate_pivot_points(silver_high, silver_low, silver_close, decimals=3)

    macro_calendar = [
        {
            "time": "4:30 PM",
            "currency": "CAD",
            "event": "Gross Domestic Product (GDP) m/m",
            "forecast": "0.10%",
            "previous": "0.20%",
            "agency": "Statistics Canada",
            "impact": "High"
        },
        {
            "time": "4:30 PM",
            "currency": "USD",
            "event": "Core PCE Price Index m/m",
            "forecast": "0.20%",
            "previous": "0.20%",
            "agency": "U.S. Bureau of Economic Analysis",
            "impact": "High"
        },
        {
            "time": "5:45 PM",
            "currency": "USD",
            "event": "Chicago PMI",
            "forecast": "45.3",
            "previous": "45.3",
            "agency": "ISM-Chicago / MNI",
            "impact": "Medium"
        },
        {
            "time": "6:00 PM",
            "currency": "USD",
            "event": "U. of Michigan Consumer Sentiment",
            "forecast": "67.8",
            "previous": "67.8",
            "agency": "University of Michigan",
            "impact": "High"
        },
        {
            "time": "6:00 PM",
            "currency": "USD",
            "event": "U. of Michigan 5-Yr Inflation Exp.",
            "forecast": "3.00%",
            "previous": "3.00%",
            "agency": "University of Michigan",
            "impact": "Medium"
        },
        {
            "time": "10:30 PM",
            "currency": "USD",
            "event": "CFTC Gold & Silver Speculative Net",
            "forecast": "—",
            "previous": "Bullish",
            "agency": "CFTC",
            "impact": "Medium"
        }
    ]

    return {
        "company": {
            "name": "LANORA GOLD TRADING LLC",
            "tagline": "Hold Real Value In Your Hands — Pure Value. Timeless Power.",
            "location": "Dubai, U.A.E.",
            "trading_desk": "Shop No. 18, Nasser Lootah Bldg. Next to Gold Center, Al Ras, Dubai, U.A.E.",
            "phone": "04-3215916 / 0505395916",
            "email": "lanoragoldtrading@gmail.com",
            "social": "@lanoragoldtrading"
        },
        "report_metadata": {
            "title": "Precious Metals Technical Report",
            "subtitle": "Daily Pivot Points, Support/Resistance & Trade Strategies",
            "date": report_date,
            "timezone": "Dubai Time (GMT+4)",
            "execution_time": "08:00 AM GST",
            "is_market_open": market_open,
            "market_status_text": "Market Open — Active Trading Session" if market_open else "Market Closed — Weekend"
        },
        "gold": {
            "symbol": "XAU/USD",
            "spot": float(gold_spot),
            "high": float(gold_high),
            "low": float(gold_low),
            "close": float(gold_close),
            "pivots": gold_pivots,
            "trade_plan": {
                "buy": {
                    "trigger": f"Buy Above {gold_pivots['P']:.2f}",
                    "target1": f"{gold_pivots['R1']:.2f}",
                    "target2": f"{gold_pivots['R2']:.2f}",
                    "stop_loss": f"{gold_pivots['S1']:.2f}"
                },
                "sell": {
                    "trigger": f"Sell Below {gold_pivots['P']:.2f}",
                    "target1": f"{gold_pivots['S1']:.2f}",
                    "target2": f"{gold_pivots['S2']:.2f}",
                    "stop_loss": f"{gold_pivots['R1']:.2f}"
                }
            }
        },
        "silver": {
            "symbol": "XAG/USD",
            "spot": float(silver_spot),
            "high": float(silver_high),
            "low": float(silver_low),
            "close": float(silver_close),
            "pivots": silver_pivots,
            "trade_plan": {
                "buy": {
                    "trigger": f"Buy Above {silver_pivots['P']:.3f}",
                    "target1": f"{silver_pivots['R1']:.3f}",
                    "target2": f"{silver_pivots['R2']:.3f}",
                    "stop_loss": f"{silver_pivots['S1']:.3f}"
                },
                "sell": {
                    "trigger": f"Sell Below {silver_pivots['P']:.3f}",
                    "target1": f"{silver_pivots['S1']:.3f}",
                    "target2": f"{silver_pivots['S2']:.3f}",
                    "stop_loss": f"{silver_pivots['R1']:.3f}"
                }
            }
        },
        "macro_calendar": macro_calendar
    }

if __name__ == "__main__":
    data = get_market_data()
    print(json.dumps(data, indent=2))
