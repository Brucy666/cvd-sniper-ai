# cvd_ai_score.py

def score_cvd_signal_from_matrix(divergence_matrix, vwap_relation, delta_behavior):
    """
    Scores sniper trap based on multi-timeframe CVD divergence + context.

    divergence_matrix: {"1m": "bearish", "3m": "bearish", "5m": "none", ...}
    vwap_relation: "failing reclaim", "above", "below"
    delta_behavior: "spike_no_follow", "steady", "collapse"
    """
    score = 0
    reasons = []

    # Timeframe weights
    tf_weights = {
        "1m": 30,
        "3m": 20,
        "5m": 20,
        "15m": 10
    }

    # Apply divergence scores
    for tf, result in divergence_matrix.items():
        if result == "bearish":
            score += tf_weights.get(tf, 0)
            reasons.append(f"bearish divergence on {tf}")
        elif result == "bullish":
            score += tf_weights.get(tf, 0)
            reasons.append(f"bullish divergence on {tf}")

    # VWAP context
    if vwap_relation == "failing reclaim":
        score += 20
        reasons.append("failing VWAP reclaim")

    # Delta behavior
    if delta_behavior == "spike_no_follow":
        score += 10
        reasons.append("delta spike without follow-through")

    setup_type = "none"
    if score >= 60:
        setup_type = "sniper trap"
    elif score >= 40:
        setup_type = "weak signal"

    return {
        "score": min(score, 100),
        "setup": setup_type,
        "reasons": reasons
    }
