# ai_cvd_reader.py

def ai_cvd_reader(price_series, cvd_series):
    """
    Reads CVD behavior across a single timeframe to return interpretation of market behavior.

    Args:
        price_series (List[float])
        cvd_series (List[float])

    Returns:
        dict with:
            - cvd_trend
            - price_trend
            - divergence_type
            - trap_signal
            - confidence_level
    """
    if len(price_series) < 5 or len(cvd_series) < 5:
        return {
            "status": "insufficient data"
        }

    price_change = price_series[-1] - price_series[0]
    cvd_change = cvd_series[-1] - cvd_series[0]

    # Determine trend direction
    price_trend = (
        "up" if price_change > 0 else
        "down" if price_change < 0 else "flat"
    )

    cvd_trend = (
        "rising" if cvd_change > 0 else
        "falling" if cvd_change < 0 else "flat"
    )

    # Detect divergence pattern
    divergence_type = None
    if price_trend == "up" and cvd_trend == "falling":
        divergence_type = "bearish"
    elif price_trend == "down" and cvd_trend == "rising":
        divergence_type = "bullish"

    # Interpret trap likelihood
    if divergence_type == "bearish":
        trap_signal = "buyer trap likely (aggressive buys, no follow-through)"
        confidence = 85
    elif divergence_type == "bullish":
        trap_signal = "seller trap likely (aggressive sells, price holding)"
        confidence = 85
    else:
        trap_signal = "no clear trap"
        confidence = 40

    return {
        "cvd_trend": cvd_trend,
        "price_trend": price_trend,
        "divergence_type": divergence_type or "none",
        "trap_signal": trap_signal,
        "confidence_level": confidence
    }
