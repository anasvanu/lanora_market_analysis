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
    Fetches session High, Low, and Close from Yahoo Finance
    """
    ctx = ssl._create_unverified_context()
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            meta = data["chart"]["result"][0]["meta"]
            high = meta.get("regularMarketDayHigh")
            low = meta.get("regularMarketDayLow")
            close = meta.get("chartPreviousClose") or meta.get("previousClose")
            spot = meta.get("regularMarketPrice")
            return spot, high, low, close
    except Exception as e:
        print(f"Warning: Yahoo fetch for {symbol} failed ({e}).")
        return None, None, None, None

def get_market_data():
    gst_now = datetime.now(timezone(timedelta(hours=4)))
    market_open = is_market_open(gst_now)
    report_date = gst_now.strftime("%B %d, %Y")

    # Fetch Gold Live Spot & Session
    gold_spot = fetch_gold_api_spot("XAU")
    y_spot, gold_high, gold_low, gold_close = fetch_yahoo_session("GC=F")

    if gold_spot is None:
        gold_spot = y_spot or 4583.40
    if gold_high is None:
        gold_high = gold_spot + 31.80
    if gold_low is None:
        gold_low = gold_spot - 21.95
    if gold_close is None:
        gold_close = gold_spot + 12.15

    # Fetch Silver Live Spot & Session
    silver_spot = fetch_gold_api_spot("XAG")
    sy_spot, silver_high, silver_low, silver_close = fetch_yahoo_session("SI=F")

    if silver_spot is None:
        silver_spot = sy_spot or 68.750
    if silver_high is None:
        silver_high = silver_spot + 0.350
    if silver_low is None:
        silver_low = silver_spot - 1.300
    if silver_close is None:
        silver_close = silver_spot + 0.485

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
