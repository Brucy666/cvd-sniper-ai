# cvd_divergence_detector.py

def detect_cvd_divergence(price_data, cvd_data, lookback=5):
    """
    Detect divergence over the last `lookback` candles.
    price_data: List of closing prices
    cvd_data: List of CVD values (same length)
    Returns: dict with type of divergence or None
    """
    if len(price_data) < lookback or len(cvd_data) < lookback:
        return None

    price_trend = price_data[-1] - price_data[-lookback]
    cvd_trend = cvd_data[-1] - cvd_data[-lookback]

    if price_trend > 0 and cvd_trend < 0:
        return {"divergence": "bearish", "type": "regular"}
    elif price_trend < 0 and cvd_trend > 0:
        return {"divergence": "bullish", "type": "regular"}
    else:
        return None
