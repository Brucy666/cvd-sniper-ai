# bias_engine.py

from typing import Dict
from ai_cvd_reader import ai_cvd_reader

def detect_htf_bias(price_series, cvd_series, vwaps):
    """
    Original single-timeframe bias logic (used below in levels)
    """
    if len(price_series) < 6 or len(cvd_series) < 6:
        return {"htf_bias": "unknown", "structure": "unknown", "preferred_trap": "either", "confidence": 0}

    price_delta = price_series[-1] - price_series[0]
    cvd_delta = cvd_series[-1] - cvd_series[0]

    price_trend = "up" if price_delta > 0 else "down" if price_delta < 0 else "flat"
    cvd_trend = "up" if cvd_delta > 0 else "down" if cvd_delta < 0 else "flat"

    structure = "trending" if abs(price_delta) > 0.5 else "ranging"
    if abs(price_delta) < 0.3 and abs(cvd_delta) < 0.3:
        structure = "compressing"

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

    if vwaps["weekly"] == "above" and htf_bias == "bearish":
        confidence -= 10
    if vwaps["weekly"] == "below" and htf_bias == "bullish":
        confidence -= 10

    return {
        "htf_bias": htf_bias,
        "structure": structure,
        "preferred_trap": preferred_trap,
        "confidence": confidence
    }

def detect_multi_level_bias(price_data_map: Dict, cvd_engine, vwaps: Dict):
    """
    Combines bias from low, mid, and high timeframes.
    """
    bias_output = {}

    # Define groupings
    tf_groups = {
        "low": ["1m", "3m", "5m"],
        "mid": ["15m", "30m", "1h"],
        "high": ["4h"]
    }

    for level, tfs in tf_groups.items():
        all_biases = []
        all_structures = []

        for tf in tfs:
            price_series = price_data_map.get(tf, [])[-6:]
            cvd_series = cvd_engine.get_cvd_series(tf)[-6:]
            bias = detect_htf_bias(price_series, cvd_series, vwaps)

            all_biases.append(bias["htf_bias"])
            all_structures.append(bias["structure"])

        # Majority vote per level
        dominant_bias = max(set(all_biases), key=all_biases.count)
        dominant_structure = max(set(all_structures), key=all_structures.count)

        bias_output[level] = {
            "bias": dominant_bias,
            "structure": dominant_structure
        }

    # Determine alignment across levels
    levels = [bias_output["low"]["bias"], bias_output["mid"]["bias"], bias_output["high"]["bias"]]
    if all(x == "bullish" for x in levels):
        alignment = "stacked bullish"
    elif all(x == "bearish" for x in levels):
        alignment = "stacked bearish"
    else:
        alignment = "conflict"

    bias_output["alignment"] = alignment
    return bias_output
