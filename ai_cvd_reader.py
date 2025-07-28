# ai_cvd_reader.py

def ai_cvd_reader(price_series, cvd_series, timeframe="1m"):
    """
    Reads CVD + price behavior and returns interpreted trap signal.

    Args:
        price_series: List[float] (same TF)
        cvd_series: List[float] (same TF)
        timeframe: str (e.g. "1m", "5m", etc.)

    Returns:
        dict {
            timeframe,
            cvd_trend,
            price_trend,
            divergence,
            trap_type,
            confidence
        }
    """
    if len(price_series) < 5 or len(cvd_series) < 5:
        return {
            "timeframe": timeframe,
            "trap_type": "insufficient data",
            "confidence": 0
        }

    price_delta = price_series[-1] - price_series[0]
    cvd_delta = cvd_series[-1] - cvd_series[0]

    price_trend = (
        "up" if price_delta > 0 else
        "down" if price_delta < 0 else "flat"
    )

    cvd_trend = (
        "rising" if cvd_delta > 0 else
        "falling" if cvd_delta < 0 else "flat"
    )

    # Detect divergence
    if price_trend == "up" and cvd_trend == "falling":
        divergence = "bearish"
        trap_type = "aggressive buyer trap (absorption above)"
        confidence = 85
    elif price_trend == "down" and cvd_trend == "rising":
        divergence = "bullish"
        trap_type = "aggressive seller trap (sell pressure fading)"
        confidence = 85
    elif price_trend == "flat" and cvd_trend == "rising":
        divergence = "bearish"
        trap_type = "buyer aggression with no price move"
        confidence = 80
    elif price_trend == "flat" and cvd_trend == "falling":
        divergence = "bullish"
        trap_type = "seller aggression with no price move"
        confidence = 80
    else:
        divergence = "none"
        trap_type = "no clear trap"
        confidence = 40

    return {
        "timeframe": timeframe,
        "cvd_trend": cvd_trend,
        "price_trend": price_trend,
        "divergence": divergence,
        "trap_type": trap_type,
        "confidence": confidence
    }
