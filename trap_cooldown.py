# trap_cooldown.py

import time

cooldown_memory = {}

def should_alert(symbol, price, matrix, cooldown_sec=180, price_tolerance=50):
    """
    Returns True if an alert should be sent for this symbol.
    Blocks duplicates based on price, matrix, and time.
    """
    now = time.time()
    last = cooldown_memory.get(symbol)

    if last:
        time_elapsed = now - last["timestamp"]
        price_diff = abs(price - last["price"])
        same_matrix = matrix == last["matrix"]

        if same_matrix and price_diff < price_tolerance and time_elapsed < cooldown_sec:
            print(f"⏳ Cooldown active for {symbol} | Δ${price_diff:.2f} | ⏱ {time_elapsed:.1f}s")
            return False

    # Update memory
    cooldown_memory[symbol] = {
        "price": price,
        "matrix": matrix,
        "timestamp": now
    }
    return True
