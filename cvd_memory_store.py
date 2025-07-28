# cvd_memory_store.py

class CVDMemoryStore:
    def __init__(self):
        self.memory = []

    def log_event(self, timestamp, cvd, price, divergence, score):
        self.memory.append({
            "timestamp": timestamp,
            "cvd": cvd,
            "price": price,
            "divergence": divergence,
            "score": score
        })

    def get_last_n(self, n=5):
        return self.memory[-n:]

    def reset(self):
        self.memory = []
