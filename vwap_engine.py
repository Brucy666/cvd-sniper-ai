# vwap_engine.py

class VWAPEngine:
    def __init__(self):
        self.total_pv = 0.0     # price × volume
        self.total_volume = 0.0
        self.last_vwap = None
        self.vwap_history = []

    def update(self, price, volume):
        self.total_pv += price * volume
        self.total_volume += volume

        if self.total_volume == 0:
            return None

        vwap = self.total_pv / self.total_volume
        self.last_vwap = vwap
        self.vwap_history.append(vwap)
        return vwap

    def get_vwap(self):
        return self.last_vwap

    def get_relation(self, price, tolerance=0.5):
        """
        Returns 'above', 'below', or 'near'
        You can also use this for 'rejecting' or 'reclaiming' logic later
        """
        if self.last_vwap is None:
            return "unknown"

        if abs(price - self.last_vwap) < tolerance:
            return "near"
        elif price > self.last_vwap:
            return "above"
        else:
            return "below"
