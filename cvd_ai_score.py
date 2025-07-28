# cvd_ai_score.py

def score_cvd_signal(divergence, vwap_relation, delta_behavior):
    """
    Inputs:
    - divergence: {"divergence": "bullish", "type": "regular"} or None
    - vwap_relation: "above", "below", "failing reclaim"
    - delta_behavior: "spike_no_follow", "steady", "collapse"

    Returns: dict with confidence score and reason
    """
    score = 0
    reasons = []

    if divergence:
        score += 40
        reasons.append(f"{divergence['divergence']} divergence")

    if vwap_relation == "failing reclaim":
        score += 30
        reasons.append("failing VWAP reclaim")

    if delta_behavior == "spike_no_follow":
        score += 20
        reasons.append("delta spike without price follow")

    if score == 0:
        return {"score": 0, "setup": "none"}

    return {
        "score": min(score, 100),
        "setup": "sniper trap" if score >= 60 else "weak signal",
        "reasons": reasons
    }
