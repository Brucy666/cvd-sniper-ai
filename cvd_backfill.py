# cvd_backfill.py

import requests
import time

BYBIT_REST_URL = "https://api.bybit.com/v5/market/kline"
TIMEFRAMES = {
    "1m": 1,
    "3m": 3,
    "5m": 5,
    "15m": 15,
    "1h": 60
}

def fetch_kline(symbol, interval, limit=100):
    params = {
        "category": "linear",
        "symbol": symbol,
        "interval": str(interval),
        "limit": str(limit)
    }
    response = requests.get(BYBIT_REST_URL, params=params)
    data = response.json()
    if "result" not in data or "list" not in data["result"]:
        print(f"⚠️ Failed to get data for {symbol} {interval}m: {data}")
        return []

    candles = data["result"]["list"]
    candles.reverse()  # most recent last
    return [
        {
            "timestamp": int(c[0]),
            "open": float(c[1]),
            "high": float(c[2]),
            "low": float(c[3]),
            "close": float(c[4]),
            "volume": float(c[5])
        }
        for c in candles
    ]

def reconstruct_cvd(candles):
    cvd = 0
    history = []
    for c in candles:
        direction = 1 if c["close"] > c["open"] else -1 if c["close"] < c["open"] else 0
        delta = direction * c["volume"]
        cvd += delta
        history.append(cvd)
    return history

def backfill_cvd(symbol):
    tf_price_history = {}
    tf_cvd_history = {}

    for tf, minutes in TIMEFRAMES.items():
        print(f"📥 Backfilling {symbol} - {tf}")
        candles = fetch_kline(symbol, minutes)
        prices = [c["close"] for c in candles]
        cvd_series = reconstruct_cvd(candles)

        tf_price_history[tf] = prices
        tf_cvd_history[tf] = cvd_series

    return tf_price_history, tf_cvd_history

# Example usage
if __name__ == "__main__":
    prices, cvds = backfill_cvd("BTCUSDT")
    for tf in TIMEFRAMES:
        print(f"🧠 {tf} Last Price: {prices[tf][-1]} | Last CVD: {cvds[tf][-1]}")
