# bias_engine.py

def detect_htf_bias(price_series, cvd_series, vwaps):
    """
    Determines high-timeframe market bias and structure.
    
    Args:
        price_series: List[float] from 1h or 4h
        cvd_series: List[float] from 1h or 4h
        vwaps: dict with "weekly", "monthly" → "above" / "below" / "near"
    
    Returns:
        dict with:
            - htf_bias: bullish, bearish, neutral
            - structure: trending, ranging, compressing
            - preferred_trap: longs / shorts / either
            - confidence: 0–100
    """
    if len(price_series) < 6 or len(cvd_series) < 6:
        return {"htf_bias": "unknown", "structure": "unknown", "preferred_trap": "either", "confidence": 0}

    price_delta = price_series[-1] - price_series[0]
    cvd_delta = cvd_series[-1] - cvd_series[0]

    price_trend = "up" if price_delta > 0 else "down" if price_delta < 0 else "flat"
    cvd_trend = "up" if cvd_delta > 0 else "down" if cvd_delta < 0 else "flat"

    # Determine structure
    structure = "trending" if abs(price_delta) > 0.5 else "ranging"
    if abs(price_delta) < 0.3 and abs(cvd_delta) < 0.3:
        structure = "compressing"

    # Determine directional bias
    if price_trend == "up" and cvd_trend == "up":
        htf_bias = "bullish"
        preferred_trap = "shorts"
        confidence = 85
    elif price_trend == "down" and cvd_trend == "down":
        htf_bias = "bearish"
        preferred_trap = "longs"
        confidence = 85
    else:
        htf_bias = "neutral"
        preferred_trap = "either"
        confidence = 60

    # Adjust if VWAP says opposite
    if vwaps["weekly"] == "above" and htf_bias == "bearish":
        confidence -= 15
    if vwaps["weekly"] == "below" and htf_bias == "bullish":
        confidence -= 15

    return {
        "htf_bias": htf_bias,
        "structure": structure,
        "preferred_trap": preferred_trap,
        "confidence": confidence
    }
