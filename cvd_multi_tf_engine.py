# cvd_multi_tf_engine.py

from collections import deque

class MultiTimeframeCVDEngine:
    def __init__(self, timeframes=None):
        if timeframes is None:
            timeframes = ["1m", "3m", "5m", "15m", "30m", "1h"]

        self.timeframes = timeframes

        # Time in seconds per TF
        self.frame_seconds = {
            "1m": 60,
            "3m": 180,
            "5m": 300,
            "15m": 900,
            "30m": 1800,
            "1h": 3600
        }

        # History: rolling CVD per TF
        self.cvd_history = {
            tf: deque(maxlen=200) for tf in self.timeframes
        }

        # Volume buckets waiting to be emitted
        self.volume_buckets = {
            tf: {"buy": 0.0, "sell": 0.0} for tf in self.timeframes
        }

        # Last time CVD bucket emitted for this TF
        self.last_bucket_time = {
            tf: None for tf in self.timeframes
        }

    def _should_emit(self, tf, timestamp):
        last = self.last_bucket_time[tf]
        frame = self.frame_seconds.get(tf, 60)
        if last is None:
            return True
        return timestamp - last >= frame

    def update(self, buy_volume, sell_volume, timestamp):
        for tf in self.timeframes:
            # Accumulate volume
            self.volume_buckets[tf]["buy"] += buy_volume
            self.volume_buckets[tf]["sell"] += sell_volume

            # Emit if time window passed
            if self._should_emit(tf, timestamp):
                delta = self.volume_buckets[tf]["buy"] - self.volume_buckets[tf]["sell"]
                last_cvd = self.cvd_history[tf][-1] if self.cvd_history[tf] else 0.0
                new_cvd = last_cvd + delta

                self.cvd_history[tf].append(new_cvd)
                self.volume_buckets[tf] = {"buy": 0.0, "sell": 0.0}
                self.last_bucket_time[tf] = timestamp

                print(f"🕒 [{tf}] emitted CVD point: {new_cvd:.2f}")

    def get_cvd_series(self, tf):
        if tf not in self.cvd_history:
            print(f"⚠️ Timeframe '{tf}' not initialized.")
            return []
        return list(self.cvd_history[tf])
