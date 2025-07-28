# htf_vwap_engine.py

import datetime

class HTFVWAPEngine:
    def __init__(self):
        self.anchors = {
            "weekly": {"pv": 0.0, "volume": 0.0, "vwap": None},
            "monthly": {"pv": 0.0, "volume": 0.0, "vwap": None}
        }
        self.last_reset = {
            "weekly": None,
            "monthly": None
        }

    def _get_reset_time(self, anchor_type, now):
        if anchor_type == "weekly":
            # Monday 00:00 UTC
            return now - datetime.timedelta(days=now.weekday(), hours=now.hour, minutes=now.minute, seconds=now.second)
        elif anchor_type == "monthly":
            # 1st day of month 00:00
            return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    def update(self, price, volume, timestamp):
        now = datetime.datetime.utcfromtimestamp(timestamp)

        for anchor_type in self.anchors:
            reset_time = self._get_reset_time(anchor_type, now)
            if self.last_reset[anchor_type] != reset_time:
                # New period
                self.anchors[anchor_type] = {"pv": 0.0, "volume": 0.0, "vwap": None}
                self.last_reset[anchor_type] = reset_time

            self.anchors[anchor_type]["pv"] += price * volume
            self.anchors[anchor_type]["volume"] += volume

            if self.anchors[anchor_type]["volume"] > 0:
                self.anchors[anchor_type]["vwap"] = (
                    self.anchors[anchor_type]["pv"] / self.anchors[anchor_type]["volume"]
                )

    def get_vwap(self, anchor_type):
        return self.anchors.get(anchor_type, {}).get("vwap")

    def get_relation(self, anchor_type, price, tolerance=0.5):
        vwap = self.get_vwap(anchor_type)
        if vwap is None:
            return "unknown"

        if abs(price - vwap) < tolerance:
            return "near"
        elif price > vwap:
            return "above"
        else:
            return "below"
