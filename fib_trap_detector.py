# fib_trap_detector.py

from statistics import mean

FIB_ZONE_RANGE = (1.272, 1.414)


def calculate_fib_extension_range(swing_low, swing_high):
    extension = swing_high - swing_low
    fib_1272 = swing_high + extension * 0.272
    fib_1414 = swing_high + extension * 0.414
    return (fib_1272, fib_1414)


def is_price_in_fib_trap_zone(price, fib_zone):
    return fib_zone[0] <= price <= fib_zone[1]


def detect_fib_trap(swing_low, swing_high, current_price, cvd_series_3m, vwap_relation):
    zone = calculate_fib_extension_range(swing_low, swing_high)
    in_zone = is_price_in_fib_trap_zone(current_price, zone)

    # Check for bearish divergence: price made new high but CVD did not
    fib_high = swing_high
    current_cvd = cvd_series_3m[-1] if len(cvd_series_3m) > 0 else 0
    previous_cvd_peak = max(cvd_series_3m[:-1]) if len(cvd_series_3m) > 1 else current_cvd
    cvd_divergence = current_cvd < previous_cvd_peak

    # VWAP trap logic (price above VWAP but rejecting)
    vw_reject = vwap_relation in ["above", "near"]

    if in_zone and cvd_divergence and vw_reject:
        return {
            "triggered": True,
            "zone": zone,
            "cvd_divergence": True,
            "vwap_status": vwap_relation,
            "confidence": 85,
            "reason": "1.41 fib trap: price in zone, CVD divergence, VWAP rejection"
        }
    else:
        return {
            "triggered": False,
            "zone": zone,
            "cvd_divergence": cvd_divergence,
            "vwap_status": vwap_relation,
            "confidence": 0,
            "reason": "conditions not met"
        }
