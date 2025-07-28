# bias_engine.py

from typing import Dict

def detect_htf_bias(price_series, cvd_series, vwaps):
    """
    Analyze one timeframe's price + CVD movement to detect:
    - Bias (bullish / bearish / neutral)
    - Structure (trending / compressing / ranging)
    - Trend (uptrend / downtrend / range / transition)
    - Preferred trap (shorts / longs / either)
    """
    if len(price_series) < 6 or len(cvd_series) < 6:
        return {
            "htf_bias": "unknown",
            "structure": "unknown",
            "trend": "unknown",
            "preferred_trap": "either",
            "confidence": 0
        }

    price_delta = price_series[-1] - price_series[0]
    cvd_delta = cvd_series[-1] - cvd_series[0]

    abs_price_move = abs(price_delta)
    abs_cvd_move = abs(cvd_delta)

    # Price & CVD directional flow
    price_trend = "up" if price_delta > 0 else "down" if price_delta < 0 else "flat"
    cvd_trend = "up" if cvd_delta > 0 else "down" if cvd_delta < 0 else "flat"

    # Structure (volatility based)
    if abs_price_move < 0.3 and abs_cvd_move < 0.3:
        structure = "compressing"
    elif abs_price_move < 0.7:
        structure = "ranging"
    else:
        structure = "trending"

    # Trend label (simplified)
    if abs_price_move > 1.0:
        trend = "uptrend" if price_delta > 0 else "downtrend"
    elif abs_price_move < 0.3 and abs_cvd_move < 0.3:
        trend = "range"
    else:
        trend = "transition"

    # Bias logic
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

    # VWAP adjustment (only weekly considered here)
    if vwaps.get("weekly") == "above" and htf_bias == "bearish":
        confidence -= 10
    if vwaps.get("weekly") == "below" and htf_bias == "bullish":
        confidence -= 10

    return {
        "htf_bias": htf_bias,
        "structure": structure,
        "trend": trend,
        "preferred_trap": preferred_trap,
        "confidence": confidence
    }

def detect_multi_level_bias(price_data_map: Dict, cvd_engine, vwaps: Dict):
    """
    Run detect_htf_bias on low, mid, high TFs and return stacked output.
    """
    tf_groups = {
        "low": ["1m", "3m", "5m"],
        "mid": ["15m", "30m", "1h"],
        "high": ["4h"]
    }

    bias_output = {}

    for level, tfs in tf_groups.items():
        biases = []
        structures = []
        trends = []

        for tf in tfs:
            price_series = price_data_map.get(tf, [])[-6:]
            cvd_series = cvd_engine.get_cvd_series(tf)[-6:]
            bias = detect_htf_bias(price_series, cvd_series, vwaps)

            biases.append(bias["htf_bias"])
            structures.append(bias["structure"])
            trends.append(bias["trend"])

        # Majority vote
        dominant_bias = max(set(biases), key=biases.count)
        dominant_structure = max(set(structures), key=structures.count)
        dominant_trend = max(set(trends), key=trends.count)

        bias_output[level] = {
            "bias": dominant_bias,
            "structure": dominant_structure,
            "trend": dominant_trend
        }

    # Alignment
    all_biases = [bias_output["low"]["bias"], bias_output["mid"]["bias"], bias_output["high"]["bias"]]
    if all(x == "bullish" for x in all_biases):
        alignment = "stacked bullish"
    elif all(x == "bearish" for x in all_biases):
        alignment = "stacked bearish"
    else:
        alignment = "conflict"

    bias_output["alignment"] = alignment
    return bias_output
