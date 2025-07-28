# cvd_engine.py

class CVDEngine:
    def __init__(self):
        self.cvd = 0.0
        self.history = []

    def update(self, buy_volume: float, sell_volume: float, timestamp=None):
        delta = buy_volume - sell_volume
        self.cvd += delta
        self.history.append({
            "timestamp": timestamp,
            "cvd": self.cvd,
            "delta": delta
        })
        return self.cvd

    def get_cvd(self):
        return self.cvd

    def get_recent_deltas(self, n=5):
        return self.history[-n:]

    def reset(self):
        self.cvd = 0.0
        self.history = []
