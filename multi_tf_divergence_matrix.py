# multi_tf_divergence_matrix.py

from cvd_divergence_detector import detect_cvd_divergence

def detect_multi_tf_divergence(price_history, cvd_engine, lookback=6):
    """
    Detect divergence on multiple timeframes using price and CVD data.
    Args:
        price_history: dict of tf → price list
        cvd_engine: MultiTimeframeCVDEngine instance
    Returns:
        dict of tf → "bullish", "bearish", or "none"
    """
    result = {}

    for tf in price_history:
        price_series = price_history[tf][-lookback:]
        cvd_series = cvd_engine.get_cvd_series(tf)[-lookback:]

        if len(price_series) < lookback or len(cvd_series) < lookback:
            result[tf] = "none"
            continue

        div = detect_cvd_divergence(price_series, cvd_series)
        result[tf] = div["divergence"] if div else "none"

    return result
