# cvd_multi_tf_engine.py

import time
from collections import defaultdict, deque

class MultiTimeframeCVDEngine:
    def __init__(self, timeframes=["1m", "3m", "5m", "15m"]):
        self.timeframes = timeframes
        self.frame_seconds = {
            "1m": 60,
            "3m": 180,
            "5m": 300,
            "15m": 900
        }
        self.cvd_history = {tf: deque(maxlen=20) for tf in self.timeframes}
        self.last_bucket_time = {tf: None for tf in self.timeframes}
        self.volume_buckets = {tf: {"buy": 0.0, "sell": 0.0} for tf in self.timeframes}

    def _should_emit(self, tf, timestamp):
        frame = self.frame_seconds[tf]
        last_time = self.last_bucket_time[tf]
        if last_time is None:
            return True
        return timestamp - last_time >= frame

    def update(self, buy_volume, sell_volume, timestamp):
        for tf in self.timeframes:
            self.volume_buckets[tf]["buy"] += buy_volume
            self.volume_buckets[tf]["sell"] += sell_volume

            if self._should_emit(tf, timestamp):
                delta = self.volume_buckets[tf]["buy"] - self.volume_buckets[tf]["sell"]
                last_cvd = self.cvd_history[tf][-1] if self.cvd_history[tf] else 0.0
                new_cvd = last_cvd + delta

                self.cvd_history[tf].append(new_cvd)
                self.volume_buckets[tf] = {"buy": 0.0, "sell": 0.0}
                self.last_bucket_time[tf] = timestamp

    def get_cvd_series(self, tf):
        return list(self.cvd_history[tf])
