# trap_cooldown.py

import time

cooldown_memory = {}

def should_alert(symbol, price, matrix, cooldown_sec=180):
    """
    Prevents repeated sniper alerts for the same trap conditions within cooldown window.
    """
    now = time.time()
    last = cooldown_memory.get(symbol)

    if last:
        price_diff = abs(price - last["price"])
        same_matrix = matrix == last["matrix"]
        time_elapsed = now - last["timestamp"]

        # Duplicate trap = same matrix + similar price + within X seconds
        if same_matrix and price_diff < 25 and time_elapsed < cooldown_sec:
            print(f"⏳ Cooldown active for {symbol} | ΔPrice: {price_diff:.1f} | Time: {time_elapsed:.1f}s")
            return False

    # Update trap memory
    cooldown_memory[symbol] = {
        "price": price,
        "matrix": matrix,
        "timestamp": now
    }

    return True
