# multi_tf_divergence_matrix.py

from cvd_divergence_detector import detect_cvd_divergence

def detect_multi_tf_divergence_matrix(price_history_map, cvd_engine, lookback=6):
    """
    Detects CVD divergence across multiple timeframes using price and CVD data.

    Args:
        price_history_map (dict): { "1m": [...], "3m": [...], ... } of recent price data.
        cvd_engine (MultiTimeframeCVDEngine): instance with .get_cvd_series(tf)
        lookback (int): number of candles to use for divergence check

    Returns:
        dict: { "1m": "bearish", "3m": "none", ... } for each timeframe
    """
    results = {}

    for tf, price_series in price_history_map.items():
        cvd_series = cvd_engine.get_cvd_series(tf)[-lookback:]
        price_slice = price_series[-lookback:]

        if len(price_slice) < lookback or len(cvd_series) < lookback:
            results[tf] = "none"
            continue

        divergence = detect_cvd_divergence(price_slice, cvd_series)
        results[tf] = divergence["divergence"] if divergence else "none"

    return results
