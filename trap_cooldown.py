# trap_cooldown.py

import time

cooldown_memory = {}

def should_alert(symbol, price, matrix, cooldown_sec=120):
    now = time.time()
    last = cooldown_memory.get(symbol)

    if last:
        same_matrix = matrix == last["matrix"]
        same_price = abs(price - last["price"]) < 10  # $10 wiggle
        recent = now - last["timestamp"] < cooldown_sec

        if same_matrix and same_price and recent:
            return False

    cooldown_memory[symbol] = {
        "matrix": matrix,
        "price": price,
        "timestamp": now
    }

    return True
